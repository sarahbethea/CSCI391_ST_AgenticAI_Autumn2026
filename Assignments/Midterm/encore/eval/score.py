"""
Scorer (Part 7): turns the traces recorded by run_eval.py into results.csv and summary.md.

    python eval/score.py

It only reads files (eval/runs.jsonl and the traces it points to). It makes no model or API
calls, so you can re-score as often as you like without spending requests.
"""

import csv
import json
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parent
MANIFEST = EVAL_DIR / "runs.jsonl"
RESULTS_CSV = EVAL_DIR / "results.csv"
SUMMARY_MD = EVAL_DIR / "summary.md"

# The results.csv columns, in the order Part 7 lists them.
COLUMNS = ["request_id", "run", "category", "status", "correct", "tool_calls", "llm_calls", "retries",
           "compressions", "memory_reads", "peak_tokens_in", "total_tokens_in", "total_tokens_out",
           "est_cost_usd", "latency_s"]

# Used only when OpenRouter didn't report a call's cost. Models ending in ":free" cost $0.
# Fill in from each model's OpenRouter page:  "model string as in the trace": (input $, output $) per million tokens
PRICES_PER_MILLION: dict[str, tuple[float, float]] = {
}

EXPECT_KEYS = {"status", "must_call", "must_not_succeed", "asks_approval", "recalls_memory",
               "answer_contains", "answer_excludes"}
CATEGORY_ORDER = ["happy", "boundary", "failure", "memory"]


# ---------------------------------------------------------------- reading

def read_trace(path) -> list[dict]:
    events = []
    with open(ROOT / path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


def latest_runs() -> list[dict]:
    """Every run in the manifest; if a run was repeated, keep only the newest one."""
    by_key = {}
    with open(MANIFEST, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                by_key[(entry["id"], entry["run"])] = entry       # a later line replaces an earlier one
    return list(by_key.values())


# ---------------------------------------------------------------- measuring one session

def event_cost(event: dict):
    """The dollar cost of one model call, or None if we can't tell."""
    if event.get("cost") is not None:
        return float(event["cost"])                    # OpenRouter reported it: the most accurate number
    model = event.get("model") or ""
    if model.endswith(":free"):
        return 0.0
    if model in PRICES_PER_MILLION:
        price_in, price_out = PRICES_PER_MILLION[model]
        tokens_in = event.get("tokens_in") or 0
        tokens_out = event.get("tokens_out") or 0
        return (tokens_in * price_in + tokens_out * price_out) / 1_000_000
    return None


def measure(events: list[dict]) -> dict:
    """Everything results.csv needs from one session's trace."""
    m = {"tool_calls": 0, "retries": 0, "llm_calls": 0, "compressions": 0, "memory_reads": 0,
         "peak_tokens_in": 0, "total_tokens_in": 0, "total_tokens_out": 0,
         "cost": 0.0, "unpriced_models": set(),
         "status": None, "answer": "", "tools_called": [], "tools_succeeded": set(),
         "approvals": [], "recalled_memory": False}

    for event in events:
        kind = event["event"]

        if kind == "tool_call":
            if event.get("attempt", 1) == 1:
                m["tool_calls"] += 1                       # a new call
                m["tools_called"].append(event["tool"])
            else:
                m["retries"] += 1                          # the loop trying the same call again
            if event.get("success"):
                m["tools_succeeded"].add(event["tool"])

        elif kind in ("route", "llm_call"):
            # Every model call: the router, each loop step, final answers, and session summaries.
            m["llm_calls"] += 1
            tokens_in = event.get("tokens_in") or 0
            m["total_tokens_in"] += tokens_in
            m["total_tokens_out"] += event.get("tokens_out") or 0
            if tokens_in > m["peak_tokens_in"]:
                m["peak_tokens_in"] = tokens_in
            if event.get("model"):                         # a call that failed before reaching a model costs nothing
                cost = event_cost(event)
                if cost is None:
                    m["unpriced_models"].add(event["model"])
                else:
                    m["cost"] += cost

        elif kind == "compression":
            m["compressions"] += 1

        elif kind == "memory_read":
            m["memory_reads"] += 1
            if event.get("store") == "episodic" and event.get("results"):
                m["recalled_memory"] = True

        elif kind == "approval":
            m["approvals"].append(event.get("decision"))

        elif kind == "final":
            # The last final event is the session's outcome.
            m["status"] = event.get("status")
            m["answer"] = event.get("answer") or event.get("message") or ""

    return m


# ---------------------------------------------------------------- checking against "expect"

def check(expect: dict, m: dict) -> tuple[bool, list[str]]:
    """Compare a session with its expected outcome. Returns (correct?, the reasons it isn't)."""
    unknown = set(expect) - EXPECT_KEYS
    if unknown:
        # A typo like "must_cal" would otherwise be ignored, and the request would pass for free.
        raise ValueError(f"unknown expect key(s): {sorted(unknown)}; use {sorted(EXPECT_KEYS)}")

    reasons = []

    if "status" in expect:
        allowed = expect["status"]
        if isinstance(allowed, str):
            allowed = [allowed]
        if m["status"] not in allowed:
            reasons.append(f"status was {m['status']}, expected {' or '.join(allowed)}")

    for tool in expect.get("must_call", []):
        if tool not in m["tools_called"]:
            reasons.append(f"never called {tool}")

    for tool in expect.get("must_not_succeed", []):
        if tool in m["tools_succeeded"]:
            reasons.append(f"{tool} succeeded but must not")

    if "asks_approval" in expect:
        asked = "approved" in m["approvals"] or "declined" in m["approvals"]
        if expect["asks_approval"] and not asked:
            reasons.append("no write went to the approval prompt")
        elif not expect["asks_approval"] and asked:
            reasons.append("asked for approval but shouldn't have")

    if "recalls_memory" in expect:
        if expect["recalls_memory"] and not m["recalled_memory"]:
            reasons.append("episodic retrieval returned nothing")
        elif not expect["recalls_memory"] and m["recalled_memory"]:
            reasons.append("episodic retrieval returned a memory but shouldn't have")

    answer = m["answer"].lower()
    for words in expect.get("answer_contains", []):
        if words.lower() not in answer:
            reasons.append(f"answer doesn't mention '{words}'")

    for words in expect.get("answer_excludes", []):
        if words.lower() in answer:
            reasons.append(f"answer mentions '{words}' but must not")

    if reasons:
        return False, reasons
    else:
        return True, []


# ---------------------------------------------------------------- building the outputs

def score_runs(runs: list[dict]) -> list[dict]:
    """One row per run, with the measurements, the verdict, and why."""
    rows = []
    for entry in runs:
        m = measure(read_trace(entry["trace"]))

        if entry.get("expect"):
            correct, reasons = check(entry["expect"], m)
            correct_text = "yes" if correct else "no"
        else:
            correct_text, reasons = "", []          # e.g. memory session 1, which only sets things up

        if m["unpriced_models"]:
            cost = None
        else:
            cost = round(m["cost"], 6)

        rows.append({
            "request_id": entry["id"], "run": entry["run"], "category": entry["category"],
            "status": m["status"], "correct": correct_text,
            "tool_calls": m["tool_calls"], "llm_calls": m["llm_calls"], "retries": m["retries"],
            "compressions": m["compressions"], "memory_reads": m["memory_reads"],
            "peak_tokens_in": m["peak_tokens_in"], "total_tokens_in": m["total_tokens_in"],
            "total_tokens_out": m["total_tokens_out"],
            "est_cost_usd": "" if cost is None else cost,
            "latency_s": round(sum(entry.get("latencies", [])), 2),
            # Not CSV columns: used by summary.md.
            "_reasons": reasons, "_trace": entry["trace"], "_answer": m["answer"],
            "_tools": m["tools_called"], "_unpriced": m["unpriced_models"],
        })

    def sort_key(row):
        if row["category"] in CATEGORY_ORDER:
            position = CATEGORY_ORDER.index(row["category"])
        else:
            position = len(CATEGORY_ORDER)
        return (position, row["request_id"], row["run"])

    rows.sort(key=sort_key)
    return rows


def write_csv(rows: list[dict]) -> None:
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def mean(values):
    if not values:
        return None
    return sum(values) / len(values)


def category_table(rows: list[dict]) -> list[str]:
    """The Workbook C table. Only run 1 counts here; runs 2-3 go in the variance table."""
    lines = ["| Category | Runs | Correct | Mean Latency (s) | Mean Cost ($) | Peak Tokens In |",
             "|---|---|---|---|---|---|"]
    for category in CATEGORY_ORDER:
        group = [row for row in rows if row["category"] == category and row["run"] == 1]
        if not group:
            continue
        judged = [row for row in group if row["correct"] in ("yes", "no")]
        correct = len([row for row in judged if row["correct"] == "yes"])
        latency = mean([row["latency_s"] for row in group])
        costs = [row["est_cost_usd"] for row in group]
        if "" in costs:
            cost_text = "unknown (see below)"
        else:
            cost_text = f"{mean(costs):.5f}"
        peak = max(row["peak_tokens_in"] for row in group)
        lines.append(f"| {category} | {len(group)} | {correct}/{len(judged)} | {latency:.1f} | {cost_text} | {peak} |")
    return lines


def variance_table(rows: list[dict]) -> list[str]:
    """For each request run more than once: statuses per run, tool-call range, same tools each time?"""
    by_id = {}
    for row in rows:
        by_id.setdefault(row["request_id"], []).append(row)

    lines = ["| Request | Statuses (run 1 / 2 / 3) | Tool Calls (min–max) | Same tools each run? |",
             "|---|---|---|---|"]
    answers = []
    for request_id, group in by_id.items():
        if len(group) < 2:
            continue
        group.sort(key=lambda row: row["run"])
        statuses = " / ".join(str(row["status"]) for row in group)
        counts = [row["tool_calls"] for row in group]
        sequences = [tuple(row["_tools"]) for row in group]
        if len(set(sequences)) == 1:
            same = "yes"
        else:
            same = "no"
        lines.append(f"| {request_id} | {statuses} | {min(counts)}–{max(counts)} | {same} |")
        answers.append(f"\n**{request_id}**")
        for row in group:
            answers.append(f"- run {row['run']}: {row['_answer']}")
    if len(lines) == 2:
        return ["No request has more than one run yet (python eval/run_eval.py online --variance)."]
    return lines + ["", "Answers, for judging \"Same answer?\" yourself:"] + answers


def write_summary(rows: list[dict]) -> None:
    out = ["# Encore evaluation summary", "", "Generated by eval/score.py from eval/runs.jsonl.", "",
           "## Results by category (run 1)", ""]
    out += category_table(rows)
    out += ["", "## Variance", ""]
    out += variance_table(rows)

    out += ["", "## Runs that were not correct", ""]
    wrong = [row for row in rows if row["correct"] == "no"]
    if not wrong:
        out.append("None.")
    for row in wrong:
        out.append(f"- **{row['request_id']}** (run {row['run']}, `{row['_trace']}`): " + "; ".join(row["_reasons"]))

    unpriced = set()
    for row in rows:
        unpriced |= row["_unpriced"]
    if unpriced:
        out += ["", "## Models without a price",
                "", "OpenRouter didn't report a cost for these. Add them to PRICES_PER_MILLION in eval/score.py:", ""]
        for model in sorted(unpriced):
            out.append(f"- `{model}`")

    SUMMARY_MD.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    rows = score_runs(latest_runs())
    write_csv(rows)
    write_summary(rows)
    print(f"Scored {len(rows)} run(s): wrote eval/results.csv and eval/summary.md")
    print()
    print("\n".join(category_table(rows)))


if __name__ == "__main__":
    main()

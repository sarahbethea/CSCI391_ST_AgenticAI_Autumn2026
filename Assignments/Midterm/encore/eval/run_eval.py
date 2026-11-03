"""
Evaluation runner (Part 7): runs Encore on the eval set with no one at the keyboard, and records
which trace each run wrote. score.py turns those traces into results.csv and summary.md.

    python eval/run_eval.py online                  # every request in eval/requests.json (run 1)
    python eval/run_eval.py online --only H01,F03   # just these requests
    python eval/run_eval.py online --variance       # requests marked "variance": runs 2 and 3
    python eval/run_eval.py online --memory         # the two-session scenarios in memory_scenarios.json

Every run is a real Encore session (run_session), so routing, approvals, retries, hot state,
episodic memory, and traces behave exactly as they do for a person. Three things are swapped:

  - input():    requests come from the eval file instead of the keyboard
  - ask_user(): approvals are answered by the eval file ("approve": true/false) instead of a person
  - memory:     the stores live in memory/eval/, so evaluation never reads or pollutes your own
                memories. Each request starts from empty memory; a memory scenario keeps its memory
                between its two sessions (that is the point of it).

A request in requests.json looks like this ("expect" is written BEFORE running anything):

    {"id": "F01", "category": "failure", "request": "Delete all my playlists.",
     "approve": false,                        # how the scripted user answers approval prompts (default false)
     "inject": "inject/flaky.json",           # optional: fault injection for this run
     "variance": true,                        # optional: include in the 3-run variance check
     "expect": {"status": ["policy_halt"],    # any of these statuses counts as correct
                "must_call": ["find_playlists"],          # tools that must be called
                "must_not_succeed": ["delete_playlist"],  # tools that must not succeed
                "asks_approval": true,                    # a write went to the approval prompt
                "recalls_memory": true,                   # episodic retrieval returned something
                "answer_contains": ["Encore"],            # words the answer must include
                "answer_excludes": ["GUNSHIP"]}}          # words the answer must NOT include
"""

import argparse
import json
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parent
sys.path.insert(0, str(ROOT))           # so "import encore" finds encore.py next to eval/

import encore      # noqa: E402  (must come after the sys.path line above)
import episodic    # noqa: E402
import hot_state   # noqa: E402
import tracer      # noqa: E402

REQUESTS_FILE = EVAL_DIR / "requests.json"
SCENARIOS_FILE = EVAL_DIR / "memory_scenarios.json"
MANIFEST = EVAL_DIR / "runs.jsonl"              # one line per run: which trace it wrote, how long it took
EVAL_MEMORY_DIR = ROOT / "memory" / "eval"      # inside memory/, so it stays out of git
CATEGORIES = ("happy", "boundary", "failure")
DEFAULT_MAX_STEPS = encore.MAX_STEPS            # remembered so an inject file's max_steps can be undone


# ---------------------------------------------------------------- loading the eval files

def load_requests() -> list[dict]:
    """Read requests.json and check every entry, so a typo fails here, not halfway through a run."""
    entries = json.loads(REQUESTS_FILE.read_text(encoding="utf-8"))
    seen_ids = set()
    for entry in entries:
        for key in ("id", "category", "request", "expect"):
            if key not in entry:
                raise ValueError(f"{entry.get('id', entry)}: missing '{key}'")
        if entry["category"] not in CATEGORIES:
            raise ValueError(f"{entry['id']}: category must be one of {CATEGORIES}")
        if entry["id"] in seen_ids:
            raise ValueError(f"{entry['id']}: the same id is used twice")
        seen_ids.add(entry["id"])
    return entries


def load_scenarios() -> list[dict]:
    """Read memory_scenarios.json: each scenario has an id and exactly two sessions."""
    scenarios = json.loads(SCENARIOS_FILE.read_text(encoding="utf-8"))
    for scenario in scenarios:
        if len(scenario.get("sessions", [])) != 2:
            raise ValueError(f"{scenario.get('id')}: a memory scenario needs exactly two sessions")
        for session in scenario["sessions"]:
            if not session.get("requests"):
                raise ValueError(f"{scenario['id']}: every session needs at least one request")
    return scenarios


# ---------------------------------------------------------------- memory and fault injection

def use_eval_memory(memory_dir: Path) -> None:
    """Point hot state and episodic memory at their own folder for the whole evaluation."""
    hot_state.close()
    episodic.close()
    memory_dir.mkdir(parents=True, exist_ok=True)
    hot_state.DB_PATH = memory_dir / "hot_state.db"
    episodic.CHROMA_PATH = memory_dir / "chroma"


def wipe_memory() -> None:
    """Start from empty memory, so one eval request can't help (or hurt) the next."""
    hot_state.forget_user(encore.ENCORE_USER_ID)
    episodic.forget_user(encore.ENCORE_USER_ID)


def set_injection(inject_path) -> None:
    """Turn fault injection off, then on again with this file if one is given."""
    encore.INJECT.clear()
    encore.MAX_STEPS = DEFAULT_MAX_STEPS
    if inject_path:
        encore.load_injection(str(ROOT / inject_path))


# ---------------------------------------------------------------- one scripted session

def run_scripted_session(requests: list[str], approve: bool, mode: str, inject=None,
                         save_episodic: bool = True, trace_dir: Path = tracer.TRACE_DIR) -> dict:
    """Run one real Encore session with these requests typed in, then end it.

    Returns the session ID, its trace file, and how long each request took.
    """
    queue = list(requests)
    latencies = []

    def scripted_input(prompt=""):
        # Hand run_session the next request, as if someone typed it.
        if queue:
            text = queue.pop(0)
            print(f"{prompt}{text}")
            return text
        # No requests left: end the session the way a closed terminal does.
        raise EOFError

    def scripted_ask_user(summary):
        # The eval file decides, so every run of this request answers the same way.
        print(f"\n{summary}\nProceed? [y/n] {'y' if approve else 'n'}   (scripted by the evaluation)")
        return approve

    original_run_request = encore.run_request

    def timed_run_request(*args, **kwargs):
        # Time each request here, to the hundredth of a second (trace timestamps are whole seconds).
        start = time.monotonic()
        try:
            return original_run_request(*args, **kwargs)
        finally:
            latencies.append(round(time.monotonic() - start, 2))

    original_ask_user = encore.ask_user
    original_write_session = episodic.write_session
    original_start_session = tracer.start_session

    def start_session_in_trace_dir():
        return original_start_session(trace_dir)

    def skip_episodic_write(*args, **kwargs):
        return {"action": "skipped"}

    # Swap in the scripted parts. encore.input shadows the built-in input() inside encore.py only.
    encore.input = scripted_input
    encore.ask_user = scripted_ask_user
    encore.run_request = timed_run_request
    tracer.start_session = start_session_in_trace_dir
    if not save_episodic:
        # Single requests skip the end-of-session summary: it isn't part of answering the request,
        # and it would cost two extra model calls per request.
        episodic.write_session = skip_episodic_write

    try:
        set_injection(inject)
        encore.run_session(mode)
    finally:
        # Put everything back, even if the session crashed.
        del encore.input
        encore.ask_user = original_ask_user
        encore.run_request = original_run_request
        tracer.start_session = original_start_session
        episodic.write_session = original_write_session
        set_injection(None)

    session_id = tracer._session_id
    trace_files = sorted(trace_dir.glob(f"*_{session_id}.jsonl"))
    if trace_files:
        trace = trace_files[-1]
    else:
        trace = None
    return {"session_id": session_id, "trace": str(trace) if trace else None, "latencies": latencies}


def record(entry: dict) -> None:
    """Add one run to the manifest that score.py reads."""
    with open(MANIFEST, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def relative(path):
    """traces/<file>.jsonl rather than a full path: shorter, and the form the workbook cites."""
    if path is None:
        return None
    try:
        return str(Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------- the two kinds of evaluation

def run_requests(mode: str, only: set, variance: bool, pause_s: float) -> int:
    entries = load_requests()
    if variance:
        # Run 1 comes from the normal pass; the variance check adds runs 2 and 3.
        entries = [entry for entry in entries if entry.get("variance")]
        runs = [2, 3]
    else:
        runs = [1]
    if only:
        entries = [entry for entry in entries if entry["id"] in only]

    count = 0
    for entry in entries:
        for run in runs:
            print(f"\n=== {entry['id']} (run {run}, {entry['category']}) ===")
            wipe_memory()
            result = run_scripted_session([entry["request"]], entry.get("approve", False), mode,
                                          inject=entry.get("inject"), save_episodic=False)
            record({"id": entry["id"], "run": run, "category": entry["category"],
                    "trace": relative(result["trace"]), "latencies": result["latencies"],
                    "expect": entry["expect"]})
            count += 1
            time.sleep(pause_s)          # be gentle with the free tier and MusicBrainz
    return count


def run_memory_scenarios(mode: str, only: set, pause_s: float) -> int:
    scenarios = load_scenarios()
    if only:
        scenarios = [scenario for scenario in scenarios if scenario["id"] in only]

    count = 0
    for scenario in scenarios:
        wipe_memory()          # empty before session 1 only: session 2 must find what session 1 left
        for number, session in enumerate(scenario["sessions"], start=1):
            print(f"\n=== {scenario['id']} session {number} ===")
            result = run_scripted_session(session["requests"], session.get("approve", False), mode,
                                          inject=session.get("inject"), save_episodic=True)
            record({"id": f"{scenario['id']}-s{number}", "run": 1, "category": "memory",
                    "trace": relative(result["trace"]), "latencies": result["latencies"],
                    "expect": session.get("expect")})
            count += 1
            time.sleep(pause_s)
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Encore's evaluation set (Part 7).")
    parser.add_argument("mode", choices=["online", "offline"])
    parser.add_argument("--only", default="", help="comma-separated ids, e.g. H01,F03 or M02")
    parser.add_argument("--variance", action="store_true", help="runs 2 and 3 of the requests marked variance")
    parser.add_argument("--memory", action="store_true", help="run the two-session memory scenarios")
    parser.add_argument("--pause", type=float, default=5.0, help="seconds to wait between sessions")
    args = parser.parse_args()

    only = set()
    for item in args.only.split(","):
        if item.strip():
            only.add(item.strip())

    encore.CACHE_ENABLED = True          # the same configuration a real session uses
    use_eval_memory(EVAL_MEMORY_DIR)

    if args.memory:
        count = run_memory_scenarios(args.mode, only, args.pause)
    else:
        count = run_requests(args.mode, only, args.variance, args.pause)

    print(f"\nRecorded {count} run(s) in {relative(MANIFEST)}. Next: python eval/score.py")


if __name__ == "__main__":
    main()

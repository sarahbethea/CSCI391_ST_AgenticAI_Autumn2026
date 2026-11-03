"""
Show the evaluation tables with pandas: accuracy / latency / cost by category, variance, the runs
that weren't correct, and semantic retrieval recall.

    python eval/tables.py              # plain tables in the terminal
    python eval/tables.py --markdown   # Markdown tables, to paste into the workbook or slides

Reads eval/results.csv (written by eval/score.py) and knowledge/results.md (written by
knowledge/experiment.py). Run those first; this script only reads and displays.
"""

import argparse
from pathlib import Path

import pandas as pd

EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parent
RESULTS_CSV = EVAL_DIR / "results.csv"
RETRIEVAL_MD = ROOT / "knowledge" / "results.md"

CATEGORY_ORDER = ["happy", "boundary", "failure", "memory"]


def load_results() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_CSV)
    # est_cost_usd is blank when a model had no known price; make it a number (NaN when unknown).
    df["est_cost_usd"] = pd.to_numeric(df["est_cost_usd"], errors="coerce")
    df["correct"] = df["correct"].fillna("")
    return df


def category_table(df: pd.DataFrame) -> pd.DataFrame:
    """The Workbook C table: one row per category, run 1 only, plus an overall row for the 30 requests."""
    first_runs = df[df["run"] == 1]
    rows = []
    for category in CATEGORY_ORDER:
        group = first_runs[first_runs["category"] == category]
        if group.empty:
            continue
        rows.append(summarize(category, group))

    # Overall: the three request categories together (memory sessions are a different kind of test).
    requests = first_runs[first_runs["category"].isin(["happy", "boundary", "failure"])]
    if not requests.empty:
        rows.append(summarize("overall (requests)", requests))
    return pd.DataFrame(rows)


def summarize(name: str, group: pd.DataFrame) -> dict:
    """One table row. Only runs with an expected outcome count toward Correct (memory session 1 has none)."""
    judged = group[group["correct"].isin(["yes", "no"])]
    correct = int((judged["correct"] == "yes").sum())
    if len(judged):
        accuracy = f"{correct}/{len(judged)} ({100 * correct / len(judged):.0f}%)"
    else:
        accuracy = "n/a"
    return {
        "Category": name,
        "Runs": len(group),
        "Correct": accuracy,
        "Mean Latency (s)": round(group["latency_s"].mean(), 1),
        "Mean Cost ($)": round(group["est_cost_usd"].mean(), 5),
        "Total Cost ($)": round(group["est_cost_usd"].sum(), 4),
        "Peak Tokens In": int(group["peak_tokens_in"].max()),
    }


def variance_table(df: pd.DataFrame) -> pd.DataFrame:
    """Requests run more than once: their status on each run and the range of tool calls."""
    counts = df.groupby("request_id")["run"].nunique()
    repeated = counts[counts > 1].index
    rows = []
    for request_id in repeated:
        runs = df[df["request_id"] == request_id].sort_values("run")
        rows.append({
            "Request": request_id,
            "Statuses (run 1 / 2 / 3)": " / ".join(runs["status"].astype(str)),
            "Tool Calls (min–max)": f"{runs['tool_calls'].min()}–{runs['tool_calls'].max()}",
            "Mean Latency (s)": round(runs["latency_s"].mean(), 1),
            "Latency Range (s)": f"{runs['latency_s'].min():.1f}–{runs['latency_s'].max():.1f}",
        })
    return pd.DataFrame(rows)


def incorrect_table(df: pd.DataFrame) -> pd.DataFrame:
    wrong = df[df["correct"] == "no"]
    return wrong[["request_id", "run", "category", "status", "tool_calls", "peak_tokens_in", "latency_s"]]


def retrieval_table() -> pd.DataFrame:
    """The recall table from knowledge/results.md (the first Markdown table in the file)."""
    if not RETRIEVAL_MD.exists():
        return pd.DataFrame()
    table_lines = []
    for line in RETRIEVAL_MD.read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            table_lines.append(line)
        elif table_lines:
            break                                  # the first table has ended
    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[2:]:                   # skip the header and the |---| line
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return pd.DataFrame(rows, columns=header)


def show(title: str, table: pd.DataFrame, markdown: bool) -> None:
    print(f"\n{title}\n")
    if table.empty:
        print("(nothing yet)")
    elif markdown:
        print(table.to_markdown(index=False))      # needs the tabulate package
    else:
        print(table.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Display Encore's evaluation tables.")
    parser.add_argument("--markdown", action="store_true", help="print Markdown tables")
    args = parser.parse_args()

    df = load_results()
    show("Accuracy, latency, and cost by category (run 1)", category_table(df), args.markdown)
    show("Variance (requests run 3 times)", variance_table(df), args.markdown)
    show("Runs that were not correct (reasons and traces: eval/summary.md)", incorrect_table(df), args.markdown)
    show("Semantic retrieval (knowledge/results.md)", retrieval_table(), args.markdown)


if __name__ == "__main__":
    main()

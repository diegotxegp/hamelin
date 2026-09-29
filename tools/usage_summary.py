"""
Summarise workspace/logs/usage_log.csv for the usability study.

Per session (one participant run) and per dataset it reports:
  - time from choosing the dataset (Data > "File path") to the trained model
    appearing (Training > "created Model"), and the pure training time
    (Training "started" -> "created");
  - number of warning / error banners shown (the participant's mistakes and
    blocked actions), by page;
  - number of help-button opens and page navigations (hesitation / lostness);
  - task-level metrics for the questionnaire's observer sheet.

Usage:
    python tools/usage_summary.py [path/to/usage_log.csv] [--out summary.csv]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_LOG = Path(__file__).resolve().parent.parent / "workspace" / "logs" / "usage_log.csv"


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp")


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for session, s in df.groupby("session_id"):
        s = s.reset_index(drop=True)
        errors = s[s["action"] == "error_shown"]
        warnings = s[s["action"] == "warning_shown"]
        base = {
            "session_id": session,
            "session_minutes": round((s["timestamp"].max() - s["timestamp"].min()).total_seconds() / 60, 1),
            "errors": len(errors),
            "warnings": len(warnings),
            "help_opens": int(s["element"].str.contains("help", case=False).sum()),
            "navigations": int((s["action"] == "navigate").sum()),
            "errors_by_page": "; ".join(f"{k}:{v}" for k, v in errors["page"].value_counts().items()),
        }
        picks = s[(s["page"] == "Data") & (s["element"] == "File path")]
        created = s[(s["page"] == "Training") & (s["action"] == "created") & (s["element"] == "Model")]
        started = s[(s["page"] == "Training") & (s["action"] == "started")]
        if picks.empty:
            rows.append({**base, "dataset": "", "task_minutes": None, "training_minutes": None})
            continue
        for _, pick in picks.iterrows():
            dataset = Path(pick["detail"]).name
            end = created[created["timestamp"] > pick["timestamp"]]
            task = train = None
            if not end.empty:
                e = end.iloc[0]
                task = round((e["timestamp"] - pick["timestamp"]).total_seconds() / 60, 2)
                st = started[(started["timestamp"] > pick["timestamp"]) & (started["timestamp"] <= e["timestamp"])]
                if not st.empty:
                    train = round((e["timestamp"] - st.iloc[-1]["timestamp"]).total_seconds() / 60, 2)
            rows.append({**base, "dataset": dataset, "task_minutes": task, "training_minutes": train})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", nargs="?", default=str(DEFAULT_LOG))
    ap.add_argument("--out", help="also write the summary to this CSV")
    args = ap.parse_args()
    summary = summarise(load(Path(args.log)))
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(summary.to_string(index=False))
    if args.out:
        summary.to_csv(args.out, index=False)
        print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()

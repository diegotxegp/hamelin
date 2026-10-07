"""Analysis of the Ludwig benchmark results (reads the CSVs, trains nothing).

Usage, from the benchmarks/ folder:

    python analyze_results.py <run_mode>            # e.g. full_1000s_test20pct, a folder of results/

Reads results/<run_mode>/ludwig/<dataset>_runs.csv (and parameters.json, which the notebook
saves with the results: time limit, datasets, seeds) and writes results/<run_mode>/analysis/.
The notebook calls run_analysis() at its end; its `outputs` argument chooses which of
these files are written:

  summary_metrics.csv    one row per dataset, every metric: mean, std, median, worst, best run and
                         95% CI (t, n runs); also runs expected/failed and the time vs the limit
  datasets_summary.csv   size, feature types, classes and majority-class share of each dataset

The metrics are Ludwig's own, on its test split (20% of the dataset, see the notebook).
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")  # results/<run mode>/{ludwig,analysis,logs}
# Ludwig's `accuracy_micro` is the plain fraction of correct predictions;
# its own `accuracy` is a different quantity.
LUDWIG_RENAME = {"accuracy": "accuracy_ludwig_native", "accuracy_micro": "accuracy"}
ID_COLS = ["dataset", "group", "seed"]

PAPER_METRICS = {  # metric -> label, in the order they appear in the table
    "classification": [("accuracy", "Accuracy"), ("roc_auc", "ROC AUC")],
    "regression": [("root_mean_squared_error", "RMSE"), ("mean_absolute_error", "MAE"),
                   ("r2", "R2")],
}
ALL_OUTPUTS = ("summary_metrics", "datasets_summary")


def load_runs(mode_dir):
    """Every run of every dataset (one row each), or None if there are none."""
    folder = os.path.join(mode_dir, "ludwig")
    if not os.path.isdir(folder):
        return None
    frames = [pd.read_csv(os.path.join(folder, f)) for f in sorted(os.listdir(folder))
              if f.endswith("_runs.csv")]
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True).rename(columns=LUDWIG_RENAME)


def metric_columns(df):
    return [c for c in df.columns if c not in ID_COLS and pd.api.types.is_numeric_dtype(df[c])]


def task_kind(group):
    return "regression" if group == "Regression" else "classification"


LOWER_IS_BETTER = ("loss", "error", "time", "failed")  # in a column name: best = min, worst = max


def summary_metrics(runs, parameters):
    """One row per dataset, every numeric column of the runs, and how complete the dataset is.

    Per metric: mean, std (sample, empty with one run), median, worst, best and the 95% CI of
    the mean (t, n runs; empty with one run). Columns keep Ludwig's own names (accuracy_micro
    is the plain accuracy). Best is the minimum for losses, errors, times and failed trials
    and the maximum for the rest. Also runs_expected / runs_failed (from the seeds in
    parameters.json) and the mean time as a percentage of the time limit.
    """
    runs = runs.rename(columns={v: k for k, v in LUDWIG_RENAME.items()})
    cols = [c for c in metric_columns(runs) if c != "seed"]
    rows = []
    for (name, group), g in runs.groupby(["dataset", "group"], sort=False):
        expected = len(parameters["seeds_per_dataset"][name])
        row = {"dataset_name": name, "task_type": group, "n_runs": len(g),
               "runs_expected": expected, "runs_failed": max(0, expected - len(g))}
        for c in cols:
            x = g[c].dropna()
            if x.empty:
                continue
            low = any(k in c for k in LOWER_IS_BETTER)
            sd = x.std(ddof=1) if len(x) > 1 else np.nan
            half = stats.t.ppf(0.975, len(x) - 1) * sd / np.sqrt(len(x)) if len(x) > 1 else np.nan
            row.update({f"{c}_mean": x.mean(), f"{c}_std": sd, f"{c}_median": x.median(),
                        f"{c}_worst": x.max() if low else x.min(),
                        f"{c}_best": x.min() if low else x.max(),
                        f"{c}_ci95_low": x.mean() - half, f"{c}_ci95_high": x.mean() + half})
        row["time_taken_pct_of_limit"] = 100 * g["time_taken"].mean() / parameters["time_limit_s"]
        rows.append(row)
    return pd.DataFrame(rows)


def summary_table(runs, digits=3):
    """One row per dataset: 'mean ± sd' per metric over its seeds, and the mean time."""
    rows = []
    for (name, group), g in runs.groupby(["dataset", "group"], sort=False):
        kind = task_kind(group)
        row = {"dataset": name, "type": kind, "n_runs": len(g)}
        for m, label in PAPER_METRICS[kind]:
            if m in g and g[m].notna().any():
                x = g[m].dropna()
                sd = x.std(ddof=1) if len(x) > 1 else float("nan")
                row[label] = f"{x.mean():.{digits}f} ± {sd:.{digits}f}"
        row["Time (s)"] = f"{g['time_taken'].mean():.0f}"
        rows.append(row)
    return pd.DataFrame(rows)


def dataset_summary(parameters):
    """One row per dataset of the run: size, feature types, classes, missing values.

    Read straight from the CSVs (`datasets` and `datasets_dir` in parameters.json). The
    majority-class share is the accuracy of the constant predictor, the reference any
    classifier has to beat. Feature types are the CSV column types (numeric or not).
    """
    from common_utils import load_dataset
    datasets, rows = parameters["datasets"], []
    for name in datasets:
        data = load_dataset(name, datasets, parameters["datasets_dir"])
        if data is None:
            continue
        df, target = data["df"], data["target_column"]
        features = df.drop(columns=[target])
        n_numeric = features.select_dtypes("number").shape[1]
        row = dict(dataset=name, group=data["group"], target=target, instances=len(df),
                   features=features.shape[1], numeric_features=int(n_numeric),
                   categorical_features=int(features.shape[1] - n_numeric),
                   missing_values_pct=round(100 * features.isna().to_numpy().mean(), 2))
        if data["task_type"] == "classification":
            row["classes"] = int(df[target].nunique())
            row["majority_class_pct"] = round(100 * df[target].value_counts(normalize=True).iloc[0], 2)
        else:
            row.update(target_mean=round(float(df[target].mean()), 4), target_sd=round(float(df[target].std()), 4))
        rows.append(row)
    return pd.DataFrame(rows)


def run_analysis(mode_dir, outputs=ALL_OUTPUTS, verbose=True):
    """Writes <mode_dir>/analysis/ (mode_dir = results/<run mode>) and returns the summary table.

    `outputs` chooses which files are written (names in ALL_OUTPUTS); the notebook
    exposes it so the author decides what a reader gets. The summary table is always
    returned, whether or not it is written.
    """
    unknown = set(outputs) - set(ALL_OUTPUTS)
    if unknown:
        raise ValueError(f"Unknown analysis outputs {sorted(unknown)}; choose from {ALL_OUTPUTS}")
    runs = load_runs(mode_dir)
    if runs is None:
        raise SystemExit(f"No results in {mode_dir}/ludwig")
    with open(os.path.join(mode_dir, "ludwig", "parameters.json")) as f:
        parameters = json.load(f)

    out = os.path.join(mode_dir, "analysis")
    os.makedirs(out, exist_ok=True)
    say = print if verbose else (lambda *a, **k: None)
    written = []
    # Files of an earlier analysis (maybe with other `outputs`, or from older versions) must not linger
    for name in ("summary_table.csv", "summary_table.md", "summary_metrics.csv", "per_dataset_stats.csv",
                 "time_and_failures.csv", "ludwig_diagnostics.csv", "datasets_summary.csv"):
        if os.path.isfile(os.path.join(out, name)):
            os.remove(os.path.join(out, name))

    def write(name, df):
        df.to_csv(os.path.join(out, f"{name}.csv"), index=False)
        written.append(f"{name}.csv")

    metrics = summary_metrics(runs, parameters)
    if "summary_metrics" in outputs:
        write("summary_metrics", metrics)
    for _, r in metrics[metrics["runs_failed"] > 0].iterrows():
        say(f"[WARN] {r['dataset_name']}: {r['n_runs']} of {r['runs_expected']} runs completed. "
            f"Launch the benchmark again to redo it.")

    if "datasets_summary" in outputs:
        write("datasets_summary", dataset_summary(parameters))

    table = summary_table(runs)  # "mean ± sd" view of summary_metrics; shown by the notebook, not saved

    say(f"Analysis written to {out}: {', '.join(written)}")
    return table


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("run_mode", help="a folder of results/ (e.g. full_1000s_test20pct) or the path to one")
    args = ap.parse_args()

    sys.path.insert(0, HERE)
    mode_dir = args.run_mode if os.path.isdir(args.run_mode) else os.path.join(RESULTS, args.run_mode)
    run_analysis(mode_dir)


if __name__ == "__main__":
    main()

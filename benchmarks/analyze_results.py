"""Analysis of the Ludwig benchmark results (reads the CSVs, trains nothing).

Usage, from the benchmarks/ folder:

    python analyze_results.py <run_mode>            # e.g. full_1000s_test20pct, a folder of results/

Reads results/<run_mode>/ludwig/<dataset>_runs.csv (and parameters.json, which the notebook
saves with the results: time limit, datasets, seeds) and writes results/<run_mode>/analysis/.
The notebook calls run_analysis() at its end; its `outputs` argument chooses which of
these files are written:

  summary_table.csv/.md  one row per dataset, "mean ± sd" of the main metrics over the
                         seeds and the mean time, ready to paste into the paper
  per_dataset_stats.csv  per dataset and metric: mean, sd, 95% CI (t, n runs), median, min, max
  time_and_failures.csv  runs completed vs expected per dataset, and the time used vs the limit
  datasets_summary.csv   size, feature types, classes and majority-class share of each dataset
  ludwig_diagnostics.csv trials launched/failed, epochs of the best trial, model type,
                         from ludwig_run_diagnostics.json (what Ludwig did in each run)

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
ALL_OUTPUTS = ("summary_table", "per_dataset_stats", "time_and_failures", "ludwig_diagnostics",
               "datasets_summary")


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


def per_dataset_stats(df):
    rows = []
    for name, g in df.groupby("dataset", sort=False):
        for m in metric_columns(df):
            x = g[m].dropna().to_numpy(dtype=float)
            if len(x) == 0:
                continue
            sd = x.std(ddof=1) if len(x) > 1 else np.nan
            half = stats.t.ppf(0.975, len(x) - 1) * sd / np.sqrt(len(x)) if len(x) > 1 else np.nan
            rows.append(dict(dataset=name, metric=m, n=len(x), mean=x.mean(), sd=sd,
                             ci95_low=x.mean() - half, ci95_high=x.mean() + half,
                             median=np.median(x), min=x.min(), max=x.max()))
    return pd.DataFrame(rows)


def time_and_failures(df, parameters):
    limit_s = parameters["time_limit_s"]
    rows = []
    for name, g in df.groupby("dataset", sort=False):
        expected = len(parameters["seeds_per_dataset"][name])
        rows.append(dict(dataset=name, runs_ok=len(g), runs_expected=expected,
                         runs_failed=max(0, expected - len(g)),
                         time_mean_s=g["time_taken"].mean(), time_sd_s=g["time_taken"].std(ddof=1),
                         time_min_s=g["time_taken"].min(), time_max_s=g["time_taken"].max(),
                         time_mean_pct_of_limit=100 * g["time_taken"].mean() / limit_s))
    return pd.DataFrame(rows)


def ludwig_diagnostics_table(mode_dir):
    """Flattens ludwig_run_diagnostics.json: one row per run."""
    path = os.path.join(mode_dir, "ludwig", "ludwig_run_diagnostics.json")
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        log = json.load(f)
    rows = []
    for key, d in log.items():
        trainer = d.get("trainer") or {}
        res = d.get("ray_resources") or {}
        rows.append(dict(run=key, n_trials=d.get("n_trials"),
                         trials_by_status=d.get("trials_by_status"),
                         best_trial_epochs=d.get("best_trial_epochs"),
                         best_trial_time_s=d.get("best_trial_time_s"),
                         sum_trial_time_s=d.get("sum_trial_time_s"),
                         model_type=d.get("model_type"), combiner=d.get("combiner"),
                         max_epochs=trainer.get("epochs"), batch_size=trainer.get("batch_size"),
                         early_stop=trainer.get("early_stop"),
                         ray_cpus=res.get("CPU"), ray_gpus=res.get("GPU")))
    return pd.DataFrame(rows)


def summary_table(runs, times, digits=3):
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
        row["Time (s)"] = f"{times.loc[times['dataset'] == name, 'time_mean_s'].iloc[0]:.0f}"
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
    # Files of an earlier analysis (maybe with other `outputs`) must not linger
    for name in ("summary_table.csv", "summary_table.md", "per_dataset_stats.csv",
                 "time_and_failures.csv", "ludwig_diagnostics.csv", "datasets_summary.csv"):
        if os.path.isfile(os.path.join(out, name)):
            os.remove(os.path.join(out, name))

    def write(name, df):
        df.to_csv(os.path.join(out, f"{name}.csv"), index=False)
        written.append(f"{name}.csv")

    if "per_dataset_stats" in outputs:
        write("per_dataset_stats", per_dataset_stats(runs))

    tf = time_and_failures(runs, parameters)
    if "time_and_failures" in outputs:
        write("time_and_failures", tf)
    for _, r in tf[tf["runs_failed"] > 0].iterrows():
        say(f"[WARN] {r['dataset']}: {r['runs_ok']} of {r['runs_expected']} runs completed. "
            f"Launch the benchmark again to redo it.")

    if "ludwig_diagnostics" in outputs:
        diag = ludwig_diagnostics_table(mode_dir)
        if diag is not None:
            write("ludwig_diagnostics", diag)

    if "datasets_summary" in outputs:
        write("datasets_summary", dataset_summary(parameters))

    table = summary_table(runs, tf)
    if "summary_table" in outputs:
        write("summary_table", table)
        with open(os.path.join(out, "summary_table.md"), "w") as f:
            cols = list(table.columns)
            f.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
            for _, r in table.fillna("").iterrows():
                f.write("| " + " | ".join(str(r[c]) for c in cols) + " |\n")
        written.append("summary_table.md")

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

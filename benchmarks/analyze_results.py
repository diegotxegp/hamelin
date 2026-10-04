"""Statistical analysis of the benchmark results (reads the CSVs, trains nothing).

Usage, from the benchmarks/ folder:

    python analyze_results.py <run_mode>            # e.g. full_all_folds_1000s
    python analyze_results.py <run_mode> --no-baseline
    python analyze_results.py --datasets            # dataset table only (needs OpenML, no results)

Reads  ludwig/results/<run_mode>/task_*_ludwig_all_runs.csv  (and the sklearn
ones if present) and writes analysis_<run_mode>/ next to this script:

  per_task_stats.csv   mean, sd, 95% CI (t, n runs), median, min, max per task/metric
  baseline.csv         constant-predictor reference on the same folds (majority
                       class / training mean); a tool at or below it is broken
  paired_tests.csv     Ludwig vs scikit-learn on the same folds (Wilcoxon per task)
  across_tasks.csv     Ludwig vs scikit-learn across tasks (Wilcoxon on task means, Holm)
  time_and_failures.csv  time used vs the limit and failed runs per task
  ludwig_diagnostics.csv trials launched/failed, epochs of the best trial, model type,
                       from ludwig_run_diagnostics.json (what Ludwig did in each run)
  summary_table.csv/.md  one row per task, "mean ± sd" (+ constant baseline and
                       mean time), ready to paste into the paper

Wilcoxon p-values with 10 overlapping folds are slightly optimistic (training
sets overlap); report them with that caveat.
"""
import argparse
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
# Ludwig's `accuracy_micro` is the plain fraction of correct predictions
# (what scikit-learn calls accuracy); its own `accuracy` is a different quantity.
LUDWIG_RENAME = {"accuracy": "accuracy_ludwig_native", "accuracy_micro": "accuracy"}
ID_COLS = ["task_id", "method", "repeat", "fold", "seed", "dataset_name",
           "task_type", "evaluation_measure"]
EXPECTED_RUNS = 10  # official OpenML folds per task; main() adjusts it for test/limited runs


def load_runs(tool, run_mode):
    folder = os.path.join(HERE, tool, "results", run_mode)
    if not os.path.isdir(folder):
        return None
    frames = [pd.read_csv(os.path.join(folder, f)) for f in sorted(os.listdir(folder))
              if f.startswith("task_") and f.endswith(f"_{tool}_all_runs.csv")]
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    return df.rename(columns=LUDWIG_RENAME) if tool == "ludwig" else df


def metric_columns(df):
    skip = set(ID_COLS)
    return [c for c in df.columns if c not in skip and pd.api.types.is_numeric_dtype(df[c])]


def per_task_stats(df, tool):
    rows = []
    for (tid, name), g in df.groupby(["task_id", "dataset_name"], sort=False):
        for m in metric_columns(df):
            x = g[m].dropna().to_numpy(dtype=float)
            if len(x) == 0:
                continue
            sd = x.std(ddof=1) if len(x) > 1 else np.nan
            half = stats.t.ppf(0.975, len(x) - 1) * sd / np.sqrt(len(x)) if len(x) > 1 else np.nan
            rows.append(dict(tool=tool, task_id=tid, dataset=name, metric=m, n=len(x),
                             mean=x.mean(), sd=sd, ci95_low=x.mean() - half,
                             ci95_high=x.mean() + half, median=np.median(x),
                             min=x.min(), max=x.max()))
    return pd.DataFrame(rows)


def baseline(df):
    """Constant predictor on the very same (repeat, fold) splits the tool was run on."""
    import openml
    from sklearn.dummy import DummyClassifier, DummyRegressor
    from sklearn.metrics import (accuracy_score, balanced_accuracy_score, f1_score,
                                 mean_squared_error, r2_score)
    from common_utils import download_openml_task_split

    rows = []
    for tid, g in df.groupby("task_id", sort=False):
        task = openml.tasks.get_task(int(tid))
        per_fold = []
        for _, r in g.iterrows():
            sp = download_openml_task_split(task, int(r["repeat"]), int(r["fold"]))
            if sp is None:
                continue
            tgt = sp["target_column"]
            Xtr, ytr = sp["train_df"][[tgt]], sp["train_df"][tgt]
            yte = sp["test_df"][tgt]
            if "classification" in sp["task_type"].lower():
                pred = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(sp["test_df"][[tgt]])
                a, b = yte.astype(str), pd.Series(pred).astype(str)
                per_fold.append(dict(accuracy=accuracy_score(a, b),
                                     balanced_accuracy=balanced_accuracy_score(a, b),
                                     f1_macro=f1_score(a, b, average="macro")))
            else:
                pred = DummyRegressor(strategy="mean").fit(Xtr, ytr).predict(sp["test_df"][[tgt]])
                per_fold.append(dict(root_mean_squared_error=float(np.sqrt(mean_squared_error(yte, pred))),
                                     r2=r2_score(yte, pred)))
        if per_fold:
            m = pd.DataFrame(per_fold).mean()
            rows.append(dict(task_id=tid, dataset=g["dataset_name"].iloc[0], n=len(per_fold),
                             **{f"{k}_mean": v for k, v in m.items()}))
    return pd.DataFrame(rows)


def holm(p):
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


def wilcoxon(a, b):
    d = np.asarray(a) - np.asarray(b)
    if len(d) < 2 or np.allclose(d, 0):
        return np.nan
    return stats.wilcoxon(a, b).pvalue


def paired(lud, skl):
    keys = ["task_id", "repeat", "fold"]
    both = lud.merge(skl, on=keys, suffixes=("_ludwig", "_sklearn"))
    shared = [m for m in metric_columns(lud) if m in metric_columns(skl)
              and m not in ("time_taken",)]
    per_task, across = [], []
    for m in shared:
        for tid, g in both.groupby("task_id", sort=False):
            a, b = g[f"{m}_ludwig"], g[f"{m}_sklearn"]
            ok = a.notna() & b.notna()
            if ok.sum() < 2:
                continue
            per_task.append(dict(task_id=tid, dataset=g["dataset_name_ludwig"].iloc[0], metric=m,
                                 n=int(ok.sum()), ludwig_mean=a[ok].mean(), sklearn_mean=b[ok].mean(),
                                 mean_diff=(a[ok] - b[ok]).mean(), p_wilcoxon=wilcoxon(a[ok], b[ok])))
        means = both.groupby("task_id")[[f"{m}_ludwig", f"{m}_sklearn"]].mean().dropna()
        if len(means) >= 2:
            across.append(dict(metric=m, n_tasks=len(means),
                               ludwig_better=int((means.iloc[:, 0] > means.iloc[:, 1]).sum()),
                               p_wilcoxon=wilcoxon(means.iloc[:, 0], means.iloc[:, 1])))
    pt, ac = pd.DataFrame(per_task), pd.DataFrame(across)
    if not pt.empty:
        pt["p_holm_within_metric"] = pt.groupby("metric")["p_wilcoxon"].transform(
            lambda s: pd.Series(holm(s.fillna(1.0)), index=s.index))
    if not ac.empty:
        ac["p_holm"] = holm(ac["p_wilcoxon"].fillna(1.0))
        ac["note"] = "'ludwig_better' counts tasks with higher mean; for error metrics lower is better"
    return pt, ac


def time_and_failures(df, limit_s):
    rows = []
    for (tid, name), g in df.groupby(["task_id", "dataset_name"], sort=False):
        rows.append(dict(task_id=tid, dataset=name, runs_ok=len(g),
                         runs_failed=max(0, EXPECTED_RUNS - len(g)),
                         time_mean_s=g["time_taken"].mean(), time_sd_s=g["time_taken"].std(ddof=1),
                         time_min_s=g["time_taken"].min(), time_max_s=g["time_taken"].max(),
                         time_mean_pct_of_limit=100 * g["time_taken"].mean() / limit_s))
    return pd.DataFrame(rows)


def dataset_summary(task_ids):
    """One row per OpenML task: size, types, classes, majority-class share, missing values.

    The majority-class share is the accuracy of the constant predictor, the
    reference any classifier has to beat. Feature counts follow OpenML's
    convention (they include the target column and leave out the row id and the
    ignored attributes, which the models never see: cloud's `period`,
    liver-disorders' `selector`).
    """
    import openml
    rows = []
    for tid in task_ids:
        try:
            task = openml.tasks.get_task(int(tid))
            ds = task.get_dataset()
            X, y, cat, _ = ds.get_data(dataset_format="dataframe", target=task.target_name)
            is_clf = "classification" in str(task.task_type).lower()
            row = dict(task_id=tid, dataset=ds.name, task_type=task.task_type,
                       evaluation_measure=task.evaluation_measure, instances=len(X),
                       features_total=X.shape[1] + 1, features_input=X.shape[1],
                       numeric_features=int(len(cat) - sum(cat)), categorical_features=int(sum(cat)),
                       missing_values_pct=round(100 * X.isna().to_numpy().mean(), 2),
                       classes=int(y.nunique()) if is_clf else None,
                       # columns OpenML keeps out of the models (row id, ignored attributes)
                       excluded_columns=", ".join(
                           [c for c in [ds.row_id_attribute] if c] +
                           [c for c in (ds.ignore_attribute or []) if c]) or "-")
            if is_clf:
                row["majority_class_pct"] = round(100 * y.value_counts(normalize=True).iloc[0], 2)
            else:
                row.update(target_mean=round(float(y.mean()), 4), target_sd=round(float(y.std()), 4))
            rows.append(row)
        except Exception as e:
            print(f"[WARN] Could not summarise task {tid}: {e}")
    return pd.DataFrame(rows)


def ludwig_diagnostics_table(run_mode):
    """Flattens ludwig_run_diagnostics.json: one row per run."""
    import json
    path = os.path.join(HERE, "ludwig", "results", run_mode, "ludwig_run_diagnostics.json")
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


PAPER_METRICS = {  # metric -> label, in the order they appear in the table
    "classification": [("accuracy", "Accuracy"), ("roc_auc", "ROC AUC"),
                       ("balanced_accuracy", "Balanced acc."), ("f1_macro", "Macro-F1")],
    "regression": [("root_mean_squared_error", "RMSE"), ("mean_absolute_error", "MAE"),
                   ("r2", "R2")],
}


def summary_table(runs, tool, base, times, digits=3):
    """One row per task: 'mean ± sd' per metric, the constant baseline and mean time."""
    rows = []
    for (tid, name, ttype), g in runs.groupby(["task_id", "dataset_name", "task_type"], sort=False):
        kind = "classification" if "classification" in str(ttype).lower() else "regression"
        row = {"task_id": tid, "dataset": name, "type": kind, "n_runs": len(g)}
        for m, label in PAPER_METRICS[kind]:
            if m in g and g[m].notna().any():
                x = g[m].dropna()
                sd = x.std(ddof=1) if len(x) > 1 else float("nan")
                row[label] = f"{x.mean():.{digits}f} ± {sd:.{digits}f}"
                if base is not None and f"{m}_mean" in base.columns:
                    b = base.loc[base["task_id"] == tid, f"{m}_mean"]
                    if len(b):
                        row[f"{label} (constant)"] = f"{b.iloc[0]:.{digits}f}"
        t = times.loc[times["task_id"] == tid, "time_mean_s"]
        if len(t):
            row["Time (s)"] = f"{t.iloc[0]:.0f}"
        rows.append(row)
    table = pd.DataFrame(rows)
    if "Time (s)" in table.columns:
        table = table[[c for c in table.columns if c != "Time (s)"] + ["Time (s)"]]
    return table


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("run_mode", nargs="?", help="results subfolder, e.g. full_all_folds_1000s")
    ap.add_argument("--datasets", action="store_true",
                    help="write datasets_summary.csv for the 14 benchmark tasks and exit")
    ap.add_argument("--no-baseline", action="store_true", help="skip the OpenML download for the baseline")
    ap.add_argument("--time-limit", type=float, default=1000.0, help="time limit per run (s), default 1000")
    args = ap.parse_args()

    import sys
    sys.path.insert(0, HERE)
    if args.datasets:
        from common_utils import ALL_TASK_IDS
        path = os.path.join(HERE, "datasets_summary.csv")
        dataset_summary(ALL_TASK_IDS).to_csv(path, index=False)
        print(f"Dataset table written to {path}")
        return
    if not args.run_mode:
        ap.error("give a run_mode (or --datasets)")

    out = os.path.join(HERE, f"analysis_{args.run_mode}")
    os.makedirs(out, exist_ok=True)
    global EXPECTED_RUNS
    import common_utils
    EXPECTED_RUNS = 1 if common_utils.TEST_MODE else (common_utils.MAX_FOLDS or 10)
    lud, skl = load_runs("ludwig", args.run_mode), load_runs("sklearn", args.run_mode)
    if lud is None:
        raise SystemExit(f"No Ludwig results in ludwig/results/{args.run_mode}")

    parts = [per_task_stats(lud, "ludwig")]
    if skl is not None:
        parts.append(per_task_stats(skl, "sklearn"))
    pd.concat(parts).to_csv(os.path.join(out, "per_task_stats.csv"), index=False)

    tf = time_and_failures(lud, args.time_limit)
    tf.to_csv(os.path.join(out, "time_and_failures.csv"), index=False)
    for _, r in tf[tf["runs_failed"] > 0].iterrows():
        print(f"[WARN] Ludwig, task {r['task_id']} ({r['dataset']}): {r['runs_ok']} of {EXPECTED_RUNS} runs "
              f"completed. Launch the benchmark again to retry the missing ones.")

    diag = ludwig_diagnostics_table(args.run_mode)
    if diag is not None:
        diag.to_csv(os.path.join(out, "ludwig_diagnostics.csv"), index=False)

    base = None
    if not args.no_baseline:
        base = baseline(lud)
        base.to_csv(os.path.join(out, "baseline.csv"), index=False)

    table = summary_table(lud, "ludwig", base, time_and_failures(lud, args.time_limit))
    table.to_csv(os.path.join(out, "summary_table.csv"), index=False)
    with open(os.path.join(out, "summary_table.md"), "w") as f:
        cols = list(table.columns)
        f.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
        for _, r in table.fillna("").iterrows():
            f.write("| " + " | ".join(str(r[c]) for c in cols) + " |\n")

    if skl is not None:
        pt, ac = paired(lud, skl)
        pt.to_csv(os.path.join(out, "paired_tests.csv"), index=False)
        ac.to_csv(os.path.join(out, "across_tasks.csv"), index=False)
    else:
        print("[INFO] No scikit-learn results for this run mode: paired tests skipped.")
    print(f"Analysis written to {out}")


if __name__ == "__main__":
    main()

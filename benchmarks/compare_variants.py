"""Compares the Ludwig variants fold by fold against Ludwig `default`, and
against scikit-learn as the reference.

Usage (from benchmarks/):
    python compare_variants.py [run_mode_name] [task_id]

Verdict per variant (fixed beforehand, see README "How to read the results"):
  DISCARD    >= 2 paired folds and the variant is worse than default by more than
             DISCARD_MARGIN (relative) in ALL of them.
  PROMISING  >= 3 paired folds and the variant is better than default in ALL of them.
  UNCLEAR    anything else: not enough evidence either way.

Defaults come from common_utils (RUN_MODE_NAME, first task of TASK_IDS).
Reads ludwig/results/<mode>/<variant>/task_<id>_ludwig_all_runs.csv and
sklearn/results/<mode>/task_<id>_sklearn_all_runs.csv, pairs the runs by
(repeat, fold) and prints, per variant: mean metric, mean paired difference
against `default`, folds won, a Wilcoxon signed-rank p-value and mean time.
"""

import os
import sys

import pandas as pd

import common_utils as cu

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = "default"
# Primary metric per task type and whether higher is better.
CLASSIFICATION = ("roc_auc", True)
REGRESSION = ("root_mean_squared_error", False)
# Default Ludwig alone swung 0.77 -> 0.85 AUC between two identical runs, so a
# variant is only dropped when it is worse by more than 10% in every paired fold.
DISCARD_MARGIN = 0.10


def _read(path):
    return pd.read_csv(path) if os.path.isfile(path) else None


def _pvalue(diffs):
    """Wilcoxon signed-rank p-value; None when it cannot be reliable."""
    from scipy.stats import wilcoxon
    d = [x for x in diffs if x != 0]
    if len(d) < 6:
        return None  # with <6 non-zero pairs p can never go below 0.05
    return float(wilcoxon(d).pvalue)


def _verdict(rel_diff):
    """rel_diff: per-fold relative improvement over default (positive = better)."""
    n = len(rel_diff)
    if n >= 2 and all(x < -DISCARD_MARGIN for x in rel_diff):
        return "DISCARD"
    if n >= 3 and all(x > 0 for x in rel_diff):
        return "PROMISING"
    return "UNCLEAR"


def compare(mode, task_id):
    lud_root = os.path.join(HERE, "ludwig", "results", mode)
    if not os.path.isdir(lud_root):
        sys.exit(f"No Ludwig results in {lud_root}")
    runs = {}
    for variant in sorted(os.listdir(lud_root)):
        df = _read(os.path.join(lud_root, variant, f"task_{task_id}_ludwig_all_runs.csv"))
        if df is not None:
            runs[variant] = df
    sk = _read(os.path.join(HERE, "sklearn", "results", mode, f"task_{task_id}_sklearn_all_runs.csv"))
    if BASELINE not in runs:
        sys.exit(f"Missing the '{BASELINE}' variant: nothing to compare against.")

    metric, higher = CLASSIFICATION if "roc_auc" in runs[BASELINE].columns else REGRESSION
    key = ["repeat", "fold"]
    base = runs[BASELINE].set_index(key)
    sign = 1 if higher else -1  # positive diff = better than the reference
    print(f"Task {task_id} | mode {mode} | metric {metric} "
          f"({'higher' if higher else 'lower'} is better)\n")

    rows = []
    sets = dict(runs)
    if sk is not None:
        sets["sklearn (ref)"] = sk
    for name, df in sets.items():
        d = df.set_index(key)
        common = d.index.intersection(base.index)
        row = {"variant": name, "folds": len(d), "mean_" + metric: d[metric].mean(),
               "mean_time_s": d["time_taken"].mean() if "time_taken" in d else None}
        if name != BASELINE and len(common):
            diff = sign * (d.loc[common, metric] - base.loc[common, metric])
            rel = diff / base.loc[common, metric].abs()
            row.update({"diff_vs_default": diff.mean(),
                        "folds_better": f"{int((diff > 0).sum())}/{len(diff)}",
                        "p_wilcoxon": _pvalue(diff.tolist()),
                        "time_vs_default": (d["time_taken"].mean() / base["time_taken"].mean()
                                            if "time_taken" in d else None)})
            if not name.startswith("sklearn"):
                row["verdict"] = _verdict(rel.tolist())
                if len(d) < len(base):
                    row["verdict"] += f" (only {len(d)} of {len(base)} folds)"
        rows.append(row)
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(out.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(
        "\nHow to read it:\n"
        "  folds           number of folds with a result for that variant\n"
        "  diff_vs_default mean paired difference vs Ludwig default; > 0 = better\n"
        "  folds_better   folds where it beat default\n"
        "  p_wilcoxon      empty with < 6 informative folds (cannot reach 0.05)\n"
        "  time_vs_default mean run time relative to default (2.0 = twice as slow)\n"
        f"  verdict         DISCARD = worse than default by > {DISCARD_MARGIN:.0%} in every paired fold (>= 2);\n"
        "                  PROMISING = better in every paired fold (>= 3); UNCLEAR = anything else.\n"
        "  The sklearn row is the reference, it gets no verdict."
    )
    if sk is not None:
        s = sk.set_index(key)
        print("\nGap to sklearn (positive = Ludwig variant better than sklearn):")
        for name, df in runs.items():
            d = df.set_index(key)
            common = d.index.intersection(s.index)
            if len(common):
                gap = sign * (d.loc[common, metric] - s.loc[common, metric])
                print(f"  {name:>10}: {gap.mean():+.4f} (better in {int((gap > 0).sum())}/{len(gap)} folds)")
    out.to_csv(os.path.join(lud_root, f"comparison_task_{task_id}.csv"), index=False)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else cu.RUN_MODE_NAME
    task = int(sys.argv[2]) if len(sys.argv) > 2 else cu.TASK_IDS[0]
    compare(mode, task)

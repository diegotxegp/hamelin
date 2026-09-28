from pathlib import Path
import json

import hamelin.interface.utils.get_model_paths as gmp

def load_run_metrics(model_dir: str, results_dir=None):
    # results_dir defaults to None (not gmp.RESULTS_DIR directly) so it's
    # resolved fresh on every call instead of being frozen to whatever
    # gmp.RESULTS_DIR was when this module was first imported.
    root = Path(results_dir if results_dir is not None else gmp.RESULTS_DIR) / model_dir

    report_file = root / "training_report.json"

    if not report_file.exists():
        print(f"[WARN] Missing file: {report_file}")
        return {}

    try:
        with open(report_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[WARN] Failed reading {report_file}: {e}")
        return {}

    metrics_tree = data.get("metrics", {})

    flat_metrics = {}

    def flatten(prefix, obj):
        for k, v in obj.items():
            if isinstance(v, dict):
                flatten(f"{prefix}{k}/" if prefix else f"{k}/", v)
            else:
                flat_metrics[f"{prefix}{k}" if prefix else k] = v

    flatten("", metrics_tree)

    return flat_metrics


def get_target_column(model_dir: str, results_dir=None):
    """The name of the column a model actually predicts (its Ludwig output
    feature, e.g. "sentiment"), read straight from training_report.json's
    config - no new instrumentation needed. Returns None if the report or
    the field is missing, so callers can just skip showing an annotation
    rather than show a stale/wrong one.

    Meant for surfacing next to a model's name wherever models get picked
    for comparison or averaging, so it's harder to mix models that don't
    even predict the same thing without noticing."""
    root = Path(results_dir if results_dir is not None else gmp.RESULTS_DIR) / model_dir
    report_file = root / "training_report.json"

    if not report_file.exists():
        return None

    try:
        with open(report_file, "r") as f:
            data = json.load(f)
    except Exception:
        return None

    try:
        return data["config"]["output_features"][0]["column"]
    except (KeyError, IndexError, TypeError):
        return None

# The two splits a user can look at in the comparison views. "test" is how
# the model performs on patients it never saw during training - the honest
# measure of real-world performance. "training" is how it performs on the
# patients it directly learned from - usually higher, and not a reliable
# measure of how it'll do on someone new.
SPLIT_LABELS = {"test": "Test", "training": "Train"}

SPLIT_EXPLANATIONS = {
    "test": (
        "You're looking at test performance: how the model does on patients "
        "it never saw during training. This is the measure of how it would "
        "perform on a new patient."
    ),
    "training": (
        "You're looking at training performance: how the model does on the "
        "same patients it directly learned from. It's usually higher than "
        "test performance, and on its own doesn't tell you how the model "
        "will do on a patient it hasn't seen before."
    ),
}


def extract_split_metrics(metrics, split="test"):
    """
    Returns:
        display_names: list of metric names (loss, accuracy...)
        full_keys: list of full metric keys (<split>/.../best or last)
    """
    prefix = f"{split}/"
    families = {}

    for key, value in metrics.items():
        if not key.startswith(prefix):
            continue
        if not isinstance(value, (int, float)):
            continue

        parts = key.split("/")
        metric_name = parts[-2]   # loss, accuracy, f1...
        label = parts[-1]         # best or last
        family = "/".join(parts[:-1])

        # prefer best over last
        if family not in families:
            families[family] = key
        else:
            if label == "best":
                families[family] = key

    display_names = []
    full_keys = []

    for full in families.values():
        parts = full.split("/")
        display_names.append(parts[-2])  # loss, accuracy...
        full_keys.append(full)

    return display_names, full_keys


def extract_test_metrics(metrics):
    """Backwards-compatible alias for extract_split_metrics(metrics, "test")."""
    return extract_split_metrics(metrics, "test")


def build_comparison_data(models, split="test"):
    """Shared by every comparison view (table/graph/heatmap): loads each
    model's metrics, builds one data row per model plus the sorted list of
    metric names/keys available across all of them. Used to live as three
    near-identical copies of this loop, one per view - kept here instead so
    a future fix to how metrics are picked can't land in only one of them.

    `split` is "test" (default) or "training" - see SPLIT_LABELS/SPLIT_EXPLANATIONS.

    Returns (data, metric_names, metrics_keys):
        data: list of {"model": name, **flat_metrics} dicts, one per model
        metric_names: sorted display names (e.g. "accuracy") present on at
            least one model, for the requested split
        metrics_keys: the matching full metric key (e.g. "test/accuracy/best")
            for each entry in metric_names
    """
    data = []
    metric_map = {}

    for m in models:
        metrics = load_run_metrics(m) or {}

        row = {"model": m}
        row.update(metrics)
        data.append(row)

        names, keys = extract_split_metrics(metrics, split)
        for name, key in zip(names, keys):
            if name not in metric_map:
                metric_map[name] = key

    metric_names = sorted(metric_map.keys())
    metrics_keys = [metric_map[n] for n in metric_names]

    return data, metric_names, metrics_keys


# Metric name fragments where a LOWER value is better. Anything not listed
# here is assumed higher-is-better (accuracy, f1, precision, recall, auc...).
# Used by every view that highlights the "best" model/direction for a
# metric (table, graph, heatmap, radar) - kept in one place so they can't
# quietly disagree with each other on the same metric.
LOWER_IS_BETTER_KEYWORDS = ("loss", "error", "err", "cost", "mse", "mae", "rmse", "mape", "perte")


def is_lower_better(metric_name):
    name = metric_name.lower()
    return any(kw in name for kw in LOWER_IS_BETTER_KEYWORDS)


def checkpoint_disclosure(full_keys):
    """Human-readable note on which checkpoint the shown numbers come from.
    extract_test_metrics() silently prefers .../best over .../last, which
    is invisible in a table/heatmap that just labels a column "accuracy" -
    say so explicitly instead."""
    labels = {k.rsplit("/", 1)[-1] for k in full_keys if "/" in k}

    if labels == {"best"}:
        return "Values shown are each model's best checkpoint on this metric (not necessarily the final epoch)."
    if labels == {"last"}:
        return "Values shown are each model's final-epoch checkpoint."
    if labels:
        return "Values shown mix best- and final-epoch checkpoints across metrics/models - check individual runs before comparing closely."
    return ""

"""
Evaluation data
~~~~~~~~~~~~~~~

Qt-free helpers behind the Evaluation page: reading a saved model's metrics,
favourites and notes (stored in plain files next to the models, so other
tools can read them), and the shared comparison logic.

Layout, per project:

    results/models/favorites.json        starred model names
    results/models/<name>/notes.txt      free-text note for that model
    results/models/<name>/training_report.json   metrics tree (test/train/val)
"""

from __future__ import annotations

import json
from pathlib import Path

from hamelin.core.model_history import ModelTraining
from hamelin.utils.logger import log

FAVORITES_FILE = "favorites.json"
NOTES_FILE = "notes.txt"

# Metric-name fragments where a LOWER value is better; anything else is
# assumed higher-is-better. One list so every comparison view agrees.
LOWER_IS_BETTER = ("loss", "error", "err", "cost", "mse", "mae", "rmse", "mape", "perte")

SPLIT_LABELS = {"test": "Test", "training": "Train"}
SPLIT_EXPLANATIONS = {
    "test": (
        "Test performance: how the model does on patients it never saw during "
        "training. This is the measure of how it would perform on a new patient."
    ),
    "training": (
        "Training performance: how the model does on the same patients it "
        "learned from. It is usually higher than test performance and, on its "
        "own, doesn't say how the model will do on a new patient."
    ),
}


def is_lower_better(metric_name: str) -> bool:
    name = metric_name.lower()
    return any(k in name for k in LOWER_IS_BETTER)


# ── Model folder / metrics ────────────────────────────────────────────────

def model_folder(rec: ModelTraining) -> Path | None:
    """The saved-model folder of *rec*, or None if it isn't on disk."""
    if not rec.checkpoint_path:
        return None
    p = Path(rec.checkpoint_path)
    return p if p.is_dir() else None


def _flatten(prefix: str, obj: dict, out: dict) -> None:
    for k, v in obj.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            _flatten(f"{key}/", v, out)
        else:
            out[key] = v


def flat_metrics(rec: ModelTraining) -> dict:
    """{"test/<target>/<metric>/best": value, ...} for *rec*: read from the
    model's training_report.json, or rebuilt from the run's stored metrics
    when the report is missing."""
    folder = model_folder(rec)
    if folder is not None:
        report = folder / "training_report.json"
        if report.is_file():
            try:
                tree = json.loads(report.read_text(encoding="utf-8")).get("metrics", {})
                out: dict = {}
                _flatten("", tree, out)
                if out:
                    return out
            except Exception as exc:  # noqa: BLE001
                log.warning(f"Cannot read {report}: {exc}")
    out = {}
    target = rec.target_variable or "target"
    for split, metrics in (("training", rec.train_metrics), ("validation", rec.val_metrics),
                           ("test", rec.test_metrics)):
        for name, value in (metrics or {}).items():
            if isinstance(value, (int, float)):
                out[f"{split}/{target}/{name}/best"] = value
    return out


def split_metrics(metrics: dict, split: str = "test") -> tuple[list[str], list[str]]:
    """(metric names, full keys) for one split, preferring ".../best" over
    ".../last"."""
    prefix = f"{split}/"
    families: dict[str, str] = {}
    for key, value in metrics.items():
        if not key.startswith(prefix) or not isinstance(value, (int, float)):
            continue
        parts = key.split("/")
        family = "/".join(parts[:-1])
        if family not in families or parts[-1] == "best":
            families[family] = key
    names = [k.split("/")[-2] for k in families.values()]
    return names, list(families.values())


def build_comparison(recs: list[ModelTraining], split: str = "test"):
    """(rows, metric_names, metric_keys): one row per model
    ({"model": name, **flat metrics}) plus the sorted metric names/keys
    available on at least one model for *split*."""
    rows, metric_map = [], {}
    for rec in recs:
        metrics = flat_metrics(rec)
        rows.append({"model": model_label(rec), **metrics})
        for name, key in zip(*split_metrics(metrics, split)):
            metric_map.setdefault(name, key)
    names = sorted(metric_map)
    return rows, names, [metric_map[n] for n in names]


def local_time(rec: ModelTraining) -> str:
    """The run's start time as "YYYY-MM-DD HH:MM" in the user's own time
    zone (ModelTraining stores naive UTC)."""
    from datetime import timezone

    ts = rec.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone().strftime("%Y-%m-%d %H:%M")


def model_label(rec: ModelTraining) -> str:
    return rec.model_name or rec.model_id[:8]


def checkpoint_disclosure(keys: list[str]) -> str:
    labels = {k.rsplit("/", 1)[-1] for k in keys if "/" in k}
    if labels == {"best"}:
        return "Values are each model's best checkpoint for that metric (not necessarily the final epoch)."
    if labels == {"last"}:
        return "Values are each model's final-epoch checkpoint."
    return ""


# ── Favourites ────────────────────────────────────────────────────────────

def load_favorites(models_dir: Path) -> set[str]:
    path = Path(models_dir) / FAVORITES_FILE
    if not path.is_file():
        return set()
    try:
        return set(json.loads(path.read_text(encoding="utf-8")))
    except Exception:  # noqa: BLE001
        return set()


def toggle_favorite(models_dir: Path, name: str) -> bool:
    """Star/unstar *name*; returns whether it is now a favourite."""
    favs = load_favorites(models_dir)
    favs.symmetric_difference_update({name})
    path = Path(models_dir) / FAVORITES_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(favs), indent=2), encoding="utf-8")
    return name in favs


# ── Notes ─────────────────────────────────────────────────────────────────

def load_note(rec: ModelTraining) -> str:
    folder = model_folder(rec)
    if folder is None or not (folder / NOTES_FILE).is_file():
        return ""
    try:
        return (folder / NOTES_FILE).read_text(encoding="utf-8")
    except OSError:
        return ""


def save_note(rec: ModelTraining, text: str) -> bool:
    """Write *text* as the note; an empty note removes the file."""
    folder = model_folder(rec)
    if folder is None:
        return False
    path = folder / NOTES_FILE
    text = (text or "").strip()
    try:
        if not text:
            path.unlink(missing_ok=True)
            return True
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
        return True
    except OSError:
        return False


# ── Project info (for the exported report) ────────────────────────────────

def project_info(project_dir: Path | None) -> dict:
    if project_dir is None:
        return {}
    meta = Path(project_dir) / "metadata.json"
    if not meta.is_file():
        return {}
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    keys = ("name", "protocol_number", "institution", "principal_investigator",
            "study_type", "primary_objective")
    info = {k: data.get(k) for k in keys}
    info["secondary_objectives"] = data.get("secondary_objectives") or []
    return info


# ── Prediction-based views ────────────────────────────────────────────────

SMALL_SUBGROUP_N = 30


def subgroup_table(pred_df, column: str) -> list[dict]:
    """One row per value of *column*: group, n, accuracy (exact-match of
    y_true/y_pred computed from the saved test predictions)."""
    rows = []
    for value in sorted(pred_df[column].dropna().unique(), key=str):
        sub = pred_df[pred_df[column] == value]
        n = len(sub)
        acc = float((sub["y_true"].astype(str) == sub["y_pred"].astype(str)).mean()) if n else None
        rows.append({"group": value, "n": n, "accuracy": acc, "small": n < SMALL_SUBGROUP_N})
    return rows


def roc_points(pred_df):
    """(fpr, tpr, auc) for a binary run with saved class probabilities, or
    None."""
    from sklearn.metrics import auc, roc_curve

    y_true = pred_df["y_true"].astype(str)
    labels = sorted(y_true.unique())
    if len(labels) != 2:
        return None
    pos = labels[-1]
    prob = None
    for col in (f"y_prob_{pos}", "y_prob_True"):
        if col in pred_df.columns:
            prob = pred_df[col]
            break
    if prob is None or prob.isna().any():
        return None
    fpr, tpr, _ = roc_curve(y_true == pos, prob)
    return fpr, tpr, float(auc(fpr, tpr))


# ── Fast bootstrap confidence intervals ───────────────────────────────────

def bootstrap_ci_fast(pred_df, metric_name: str, n_bootstrap: int = 1000,
                      confidence: float = 0.95, seed: int = 42):
    """95 % bootstrap CI for accuracy / R² / RMSE / MAE from a saved
    test_predictions frame: (point, low, high), or (None, None, None) if the
    metric isn't supported or there are too few rows.

    Same statistics as hamelin.interface.utils.bootstrap_ci, but all
    resamples are drawn and evaluated as one numpy array instead of 1000
    pandas slices: ~5 s per metric became a few milliseconds, which matters
    because Evaluation computes one per metric tile every time a model is
    selected.
    """
    import numpy as np
    from hamelin.interface.utils import bootstrap_ci as bc

    n = str(metric_name).lower().replace("-", "").replace("_", "").replace(" ", "")
    fn = next((f for match, f in bc._SUPPORTED_METRICS if match(n)), None)
    rows = len(pred_df)
    if fn is None or rows < bc.MIN_ROWS:
        return None, None, None

    if fn is bc._accuracy:
        per_row = (pred_df["y_true"].astype(str) == pred_df["y_pred"].astype(str)).to_numpy(float)

        def stat(idx):
            return per_row[idx].mean(axis=-1)
    else:
        y = pred_df["y_true"].astype(float).to_numpy()
        p = pred_df["y_pred"].astype(float).to_numpy()

        def stat(idx):
            yb, pb = y[idx], p[idx]
            err = yb - pb
            if fn is bc._mae:
                return np.abs(err).mean(axis=-1)
            if fn is bc._rmse:
                return np.sqrt((err ** 2).mean(axis=-1))
            ss_tot = ((yb - yb.mean(axis=-1, keepdims=True)) ** 2).sum(axis=-1)
            with np.errstate(divide="ignore", invalid="ignore"):
                return 1.0 - (err ** 2).sum(axis=-1) / ss_tot

    point = float(stat(np.arange(rows)))
    idx = np.random.default_rng(seed).integers(0, rows, (n_bootstrap, rows))
    boots = stat(idx)
    boots = boots[np.isfinite(boots)]
    if len(boots) < n_bootstrap // 2:
        return point, None, None
    alpha = (1 - confidence) / 2
    return point, float(np.percentile(boots, alpha * 100)), float(np.percentile(boots, (1 - alpha) * 100))


def bootstrap_auc_ci(pred_df, n_bootstrap: int = 1000, confidence: float = 0.95, seed: int = 42):
    """(auc, low, high) for a binary run whose saved test predictions carry
    the positive-class probability, else (None, None, None). Resamples are
    ranked all at once (Mann-Whitney form of the AUC), so it takes tens of
    milliseconds."""
    import numpy as np
    from scipy.stats import rankdata

    y_true = pred_df["y_true"].astype(str)
    labels = sorted(y_true.unique())
    if len(labels) != 2 or len(pred_df) < 10:
        return None, None, None
    pos = labels[-1]
    prob = next((pred_df[c] for c in (f"y_prob_{pos}", "y_prob_True") if c in pred_df.columns), None)
    if prob is None or prob.isna().any():
        return None, None, None
    y = (y_true == pos).to_numpy()
    p = prob.to_numpy(float)

    def auc(idx):
        yb, pb = y[idx], p[idx]
        n_pos = yb.sum(axis=-1)
        n_neg = yb.shape[-1] - n_pos
        ranks = rankdata(pb, axis=-1)
        with np.errstate(divide="ignore", invalid="ignore"):
            return ((ranks * yb).sum(axis=-1) - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)

    point = float(auc(np.arange(len(y))))
    idx = np.random.default_rng(seed).integers(0, len(y), (n_bootstrap, len(y)))
    boots = auc(idx)
    boots = boots[np.isfinite(boots)]
    if len(boots) < n_bootstrap // 2:
        return point, None, None
    alpha = (1 - confidence) / 2
    return point, float(np.percentile(boots, alpha * 100)), float(np.percentile(boots, (1 - alpha) * 100))

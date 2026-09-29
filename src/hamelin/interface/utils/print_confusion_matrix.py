from pathlib import Path

import numpy as np
import pandas as pd
from hamelin.utils.lazy import LazyModule

_skm = LazyModule("sklearn.metrics")
import hamelin.interface.utils.get_model_paths as gmp

_ludwig_model_cache = {}


def _get_ludwig_model(model_path: str):
    """Import Ludwig and load the model only when needed, and cache it."""
    if model_path not in _ludwig_model_cache:
        from ludwig.api import LudwigModel
        _ludwig_model_cache[model_path] = LudwigModel.load(model_path)
    return _ludwig_model_cache[model_path]


def supports_threshold_adjustment(model_path: str) -> bool:
    """True if this run's saved predictions carry a per-class probability
    (y_prob_<class>) for exactly two classes - the only shape a decision
    threshold can be meaningfully applied to (binary: "count it as class A
    once its probability crosses X"). False for anything saved before
    LudwigBackend started keeping per-class probabilities, for regression
    (no such columns), and for more than 2 classes (thresholding one class
    against several others isn't a single well-defined slider)."""
    predictions_csv = Path(model_path) / "test_predictions.csv"
    if not predictions_csv.exists():
        return False
    try:
        columns = pd.read_csv(predictions_csv, nrows=0).columns
    except Exception:
        return False
    return sum(1 for c in columns if c.startswith("y_prob_")) == 2


def _confusion_matrix_from_saved_predictions(predictions_csv: Path, threshold: float = None):
    """Build the same {"labels", "matrix", "rows"} shape as
    compute_confusion_matrix()'s live path, but from test_predictions.csv -
    saved once at training time (see LudwigBackend.run() /
    TrainingPage._on_training_finished in hamelin-v2) instead of reloading
    the model and calling predict() again every time this page opens.

    threshold (0-1), when given, ignores Ludwig's own saved y_pred and
    reclassifies every row itself from the saved per-class probabilities
    instead: whichever of the two classes has probability >= threshold
    wins. Only meaningful for a genuinely binary run - see
    supports_threshold_adjustment(); callers are expected to check that
    before passing a threshold, but this degrades to the saved y_pred
    (i.e. ignores an unusable threshold) rather than raising, since a
    stale threshold value on a newly-selected model shouldn't break the
    page.

    Raises on anything unexpected (missing/malformed columns) so the caller
    falls back to the live path rather than silently showing wrong data."""
    df = pd.read_csv(predictions_csv)
    y_true = df["y_true"].astype(str).values

    prob_cols = [c for c in df.columns if c.startswith("y_prob_")]
    if threshold is not None and len(prob_cols) == 2:
        class_a = prob_cols[0][len("y_prob_"):]
        class_b = prob_cols[1][len("y_prob_"):]
        prob_a = df[prob_cols[0]].values
        y_pred = np.where(prob_a >= threshold, class_a, class_b)
    else:
        y_pred = df["y_pred"].astype(str).values

    has_score = "y_score" in df.columns and df["y_score"].notna().any()
    y_conf = df["y_score"].values if has_score else None

    labels = list(np.unique(np.concatenate([y_true, y_pred])))
    cm = _skm.confusion_matrix(y_true, y_pred, labels=labels)

    # Same row-level detail as the live path, minus the y_true/y_pred/
    # y_score columns folded back into _true_label/_predicted_label/
    # _confidence instead, so callers can't tell which path built this.
    # _predicted_label reflects the threshold above when one was applied,
    # not necessarily the same value as the saved y_pred column.
    rows = df.drop(columns=["y_true", "y_pred", "y_score"], errors="ignore").to_dict(orient="records")
    for i, row in enumerate(rows):
        row["_true_label"] = y_true[i]
        row["_predicted_label"] = y_pred[i]
        if y_conf is not None:
            row["_confidence"] = float(y_conf[i])

    return {"labels": labels, "matrix": cm.tolist(), "rows": rows}


def compute_confusion_matrix(model_path: str, dataset_path: str, threshold: float = None):
    # Read what training already computed and saved, when available,
    # instead of reloading the model and re-running inference on the whole
    # dataset just to get numbers it already has. Falls through to the live
    # path below for anything trained before this existed, or if the saved
    # file turns out to be missing an expected column. threshold only
    # applies on this saved-predictions path (see
    # _confusion_matrix_from_saved_predictions) - the live fallback below
    # always uses Ludwig's own default classification.
    predictions_csv = Path(model_path) / "test_predictions.csv"
    if predictions_csv.exists():
        try:
            return _confusion_matrix_from_saved_predictions(predictions_csv, threshold=threshold)
        except Exception:
            pass

    # The live path below needs the original dataset - not available for
    # anything saved without test_predictions.csv AND without a resolvable
    # dataset_path (e.g. description.json - the only place that's recorded -
    # doesn't exist for models saved straight via LudwigModel.save(), i.e.
    # results/models/, as opposed to Ludwig's own train()/auto_train()
    # run output). Raise clearly here instead of pd.read_csv(None) blowing
    # up with a confusing traceback.
    if not dataset_path:
        raise ValueError(
            f"No saved predictions and no resolvable dataset for {model_path!r} - "
            "cannot compute a confusion matrix for this model."
        )

    df = pd.read_csv(dataset_path)
    y_true = df.iloc[:, -1].values.astype(str)

    model = _get_ludwig_model(model_path)
    preds = model.predict(dataset=dataset_path)

    preds_df = preds[0] if isinstance(preds, tuple) else preds
    pred_col = next(col for col in preds_df.columns if col.endswith("_predictions"))
    # Ludwig also reports the winning class's confidence as "<feature>_probability"
    # (distinct from "<feature>_probabilities", which holds the full per-class
    # vector) - surface it when present instead of throwing it away.
    prob_col = next((col for col in preds_df.columns if col.endswith("_probability")), None)

    y_pred = preds_df[pred_col].values.astype(str)
    y_conf = preds_df[prob_col].values if prob_col else None

    labels = list(np.unique(np.concatenate([y_true, y_pred])))
    cm = _skm.confusion_matrix(y_true, y_pred, labels=labels)

    # Row-level detail behind the aggregate counts, so a UI can let someone
    # click a (true, predicted) cell and see the actual examples that landed
    # there instead of just the number. Row order is assumed to match
    # y_true/y_pred, which holds as long as predict() doesn't shuffle - true
    # for Ludwig's plain (non-distributed) predict path used here.
    rows = df.to_dict(orient="records")
    for i, row in enumerate(rows):
        row["_true_label"] = y_true[i]
        row["_predicted_label"] = y_pred[i]
        if y_conf is not None:
            row["_confidence"] = float(y_conf[i])

    return {"labels": labels, "matrix": cm.tolist(), "rows": rows}

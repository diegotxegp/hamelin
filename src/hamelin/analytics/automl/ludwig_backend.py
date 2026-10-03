"""
Ludwig AutoML Backend — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implements ``AutoMLBackend`` using Ludwig's ``auto_train`` (pinned to
``ludwig>=0.17.9`` in pyproject.toml).
Ludwig is imported lazily so the app startup is not penalised.

Author: GitHub Copilot AI
Date: February 20, 2026
"""

from __future__ import annotations

import json
import os
import shutil
import time

import numpy as np
import pandas as pd

from hamelin.analytics.automl.base import AutoMLBackend, AutoMLResult
from hamelin.utils.logger import log


# ---------------------------------------------------------------------------
# Private helpers (Ludwig-specific)
# ---------------------------------------------------------------------------

def _extract_model_type(best_model) -> str:
    """Best-effort extraction of model type from a LudwigModel."""
    try:
        combiner_type = best_model.config.get("combiner", {}).get("type", "")
        if combiner_type:
            return f"Ludwig/{combiner_type.capitalize()}"
    except Exception:
        pass
    try:
        return best_model.config.get("model_name", "Ludwig/AutoML")
    except Exception:
        pass
    return "Ludwig/AutoML"


def _extract_hyperparameters(best_model) -> dict:
    """Extract a JSON-serialisable hyperparameter dict from a LudwigModel."""
    try:
        cfg = best_model.config
        return json.loads(json.dumps(cfg, default=str))
    except Exception:
        return {}


_EPOCH = pd.Timestamp("1970-01-01")


def _numericize_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert any native datetime64 column to a plain integer (days since
    epoch) before handing the dataframe to Ludwig.

    DataModel's own type auto-detection (see DataModel._auto_detect_types)
    parses date-looking string columns (e.g. a birth date column in
    "%Y-%m-%d" format) into real pandas datetime64 columns. Ludwig's own
    dataset profiler assigns such columns the Ludwig feature type "date"
    - but this Ludwig version's own feature-type registry doesn't
    actually include "date" (only category, binary, number, sequence,
    set, text, timeseries, vector, category_distribution, image,
    anomaly), so config validation fails with "'date' is not one of
    [...]" before training ever starts.

    Reformatting the column back to a date-shaped *string* ("YYYY-MM-DD")
    doesn't help - Ludwig's profiler pattern-matches the string content
    itself and still assigns "date". Converting to a plain integer avoids
    that: Ludwig correctly infers "number" for it instead, which it does
    support, while still preserving the column's relative ordering as a
    usable feature.
    """
    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns
    if len(datetime_cols) == 0:
        return df
    df = df.copy()
    for col in datetime_cols:
        df[col] = (df[col] - _EPOCH).dt.days
    return df


def _flatten_eval_stats(eval_stats: dict, target: str) -> dict:
    """
    Convert Ludwig's nested eval_stats to a flat metric dict.

    Ludwig returns ``{target_col: {metric: value, ...}}`` or a flat dict
    for older versions.
    """
    if target in eval_stats and isinstance(eval_stats[target], dict):
        raw = eval_stats[target]
    else:
        raw = eval_stats

    flat: dict = {}
    for k, v in raw.items():
        if isinstance(v, (int, float)):
            flat[k] = round(float(v), 6)
        elif isinstance(v, list) and len(v) == 1 and isinstance(v[0], (int, float)):
            flat[k] = round(float(v[0]), 6)
    return flat


def _zscore_number_outputs(config: dict) -> None:
    """Ludwig leaves a number OUTPUT feature unnormalized by default (input
    number features get zscore). A target in the hundreds (e.g. plasma
    retinol ~600) then starts from predictions near 0 and 100 epochs are
    not enough to reach its scale: MAE ended up ~3x worse than always
    predicting the median."""
    for out_feat in config.get("output_features", []):
        if out_feat.get("type") == "number":
            preprocessing = out_feat.setdefault("preprocessing", {})
            if not preprocessing.get("normalization"):
                preprocessing["normalization"] = "zscore"


def _target_is_normalized(config: dict, target: str) -> bool:
    for out_feat in config.get("output_features", []):
        if out_feat.get("name") == target and out_feat.get("type") == "number":
            return bool((out_feat.get("preprocessing") or {}).get("normalization"))
    return False


def _original_scale_regression_metrics(df: pd.DataFrame, predictions, target: str) -> dict:
    """Ludwig computes a number feature's metrics on its preprocessed values,
    so with a normalized target they come out in standard deviations; only
    the predictions are transformed back. Recompute them in the target's
    own units so they stay comparable with every other regression run.
    Same metric names and definitions as Ludwig's. Empty when rows don't
    line up (Ludwig dropped rows with a missing target)."""
    if predictions is None or len(predictions) != len(df):
        return {}
    pred_col = f"{target}_predictions"
    if pred_col not in predictions.columns:
        return {}
    y_true = pd.to_numeric(df[target], errors="coerce").to_numpy(dtype=float)
    y_pred = pd.to_numeric(predictions[pred_col], errors="coerce").to_numpy(dtype=float)
    if np.isnan(y_true).any() or np.isnan(y_pred).any():
        return {}
    err = y_true - y_pred
    mse = float(np.mean(err ** 2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
    metrics = {
        "mean_absolute_error": float(np.mean(np.abs(err))),
        "mean_squared_error": mse,
        "root_mean_squared_error": float(np.sqrt(mse)),
        "r2": 1.0 - float(np.sum(err ** 2)) / ss_tot if ss_tot else 0.0,
    }
    nonzero = y_true != 0
    if nonzero.any():
        rel = err[nonzero] / y_true[nonzero]
        metrics["mean_absolute_percentage_error"] = float(np.mean(np.abs(rel)))
        metrics["root_mean_squared_percentage_error"] = float(np.sqrt(np.mean(rel ** 2)))
    return {k: round(v, 6) for k, v in metrics.items()}


def _extract_confusion_matrix(eval_stats: dict, target: str) -> dict:
    """
    Extract confusion matrix and class labels from Ludwig eval_stats.

    Returns a dict with keys:
        ``confusion_matrix``        list[list[int]]
        ``confusion_matrix_labels`` list[str]

    Returns empty dict on failure (non-classifier, Ludwig version mismatch, etc.)
    """
    try:
        ts = eval_stats.get(target, eval_stats)
        cm_raw = ts.get("confusion_matrix")
        if cm_raw is None:
            return {}
        # Ensure JSON-serialisable (list of lists of int)
        cm = [[int(v) for v in row] for row in cm_raw]
        labels = [str(l) for l in ts.get("class_names", list(range(len(cm))))]
        return {"confusion_matrix": cm, "confusion_matrix_labels": labels}
    except Exception as exc:
        log.debug(f"LudwigBackend: confusion_matrix extraction skipped — {exc}")
        return {}


def _held_out_test_set(df: pd.DataFrame, target: str, test_split: float, random_seed: int):
    """Splits off a genuinely untouched test set BEFORE any training
    happens, instead of the two run() paths' previous behaviour of handing
    Ludwig the WHOLE dataframe for training and then also evaluating on
    that exact same dataframe. Ludwig's own auto_train/hyperopt does its
    own internal train/val/test split for its own validation purposes, but
    never hands that split back to this caller - so evaluate(dataset=df)
    on the original, unsplit df silently included rows the model was
    directly trained on. Every "test" metric shown anywhere in Hamelin
    (and, since LudwigBackend.run() started saving test_predictions.csv,
    every saved prediction too) was computed this way until now, which
    means it wasn't a genuine held-out measurement.

    Stratifies by target when possible (every class needs >=2 rows) so a
    small/imbalanced clinical outcome doesn't end up with a near-empty
    positive class in the held-out set purely by chance; falls back to a
    plain split for continuous targets or classes too small to stratify.
    """
    from sklearn.model_selection import train_test_split

    test_split = min(max(float(test_split), 0.05), 0.5)
    try:
        return train_test_split(
            df, test_size=test_split, random_state=random_seed, stratify=df[target],
        )
    except ValueError:
        return train_test_split(df, test_size=test_split, random_state=random_seed)


def _binary_output_mapping(df: pd.DataFrame, target: str, pred_series: pd.Series):
    """{False: raw_value, True: raw_value} for a numeric-looking binary
    *target* column in *df* (same sorted-values convention as
    _normalize_binary_columns), or None if it doesn't apply.

    Ludwig only ever reports a binary feature's predictions back as
    literal True/False - never decoded to the dataset's own raw labels -
    when that feature's raw values look numeric to pandas (see
    _normalize_binary_columns' docstring: no str2bool/bool2str mapping
    ever gets built for a numeric dtype column, "1"/"2" no more than any
    other pair). That's true regardless of whether those raw values
    happened to already be {0, 1}. Without this, _build_predictions_frame
    below would save y_true as the dataset's own raw values ("1"/"2") and
    y_pred as Ludwig's un-decoded "True"/"False" - two different label
    spaces for what's supposed to be the same two classes, which is
    exactly what made a "1"/"2"/"False"/"True" 4-label confusion matrix
    show up instead of a normal 2x2 one.

    *pred_series* (the raw predictions column, before the .astype(str) in
    _build_predictions_frame) has to actually BE boolean for this to
    apply - checking only "df[target] happens to have 2 distinct values"
    isn't enough on its own: a regression target can easily have exactly
    2 distinct values in a small dataframe (e.g. a 2-row test split) by
    pure coincidence, and mapping its (numeric) predictions through a
    True/False-keyed dict would silently turn every one of them into NaN.
    """
    if pred_series.dtype != bool:
        return None
    if target not in df.columns:
        return None
    values = df[target].dropna().unique()
    if len(values) != 2:
        return None
    try:
        numeric = pd.to_numeric(pd.Series(values))
    except (TypeError, ValueError):
        return None
    lo, hi = (v for _, v in sorted(zip(numeric, values)))
    return {False: lo, True: hi}


def _build_predictions_frame(df: pd.DataFrame, predictions: pd.DataFrame, target: str):
    """Combine the original rows with Ludwig's per-row predictions into one
    dataframe: every original column, plus y_true/y_pred/y_score appended -
    y_score is the winning class's confidence for classification, absent
    (None) for regression, where there's no such thing. For classification,
    also appends one y_prob_<class> column per class (Ludwig names these
    "<feature>_probabilities_<classname>") - the full per-class probability,
    not just the winning one - so a decision threshold other than Ludwig's
    own default can be explored later (see
    interface/utils/print_confusion_matrix.py's threshold support) without
    reloading the model and re-running inference.

    Saved to disk as test_predictions.csv (see TrainingPage._on_training_finished)
    so downstream consumers - the confusion matrix, a bootstrap confidence
    interval - can read it back instead of reloading the model and
    re-running inference every time they need row-level detail.
    interface/utils/print_confusion_matrix.py reads this exact shape
    instead of calling model.predict() live when it's present.

    Row order is assumed to match df's, which holds as long as evaluate()
    doesn't shuffle - true for Ludwig's plain (non-distributed) path used
    here. Returns None if that assumption doesn't hold (row count
    mismatch) or no prediction column is found, so callers can skip saving
    rather than write misaligned data - logged, not silent, since the
    caller's own None-check has no way to tell "nothing to save" apart
    from "something went wrong" on its own (this was silent until a run
    on a target with missing values hit exactly this and nobody could
    tell why its confusion matrix was just gone).
    """
    if predictions is None or len(predictions) != len(df):
        hint = ""
        if predictions is not None and target in df.columns:
            missing = int(df[target].isna().sum())
            if missing:
                # The likely cause: Ludwig's own preprocessing default for
                # a missing OUTPUT value is to drop that row entirely
                # (missing_value_strategy "drop_row") before it ever
                # reaches evaluate() - so its predictions end up with
                # fewer rows than our held-out test split, which still
                # has them. Not fixable here (silently re-aligning would
                # mean guessing which predictions belong to which surviving
                # row), but worth explaining rather than just going quiet.
                hint = (
                    f" - likely cause: {missing} row(s) have a missing "
                    f"'{target}' value, which Ludwig drops before "
                    "evaluating rather than predicting for"
                )
        log.warning(
            f"LudwigBackend: not saving test_predictions.csv - row count "
            f"mismatch (predictions: {0 if predictions is None else len(predictions)}, "
            f"dataset: {len(df)}){hint}"
        )
        return None

    try:
        pred_col = next(c for c in predictions.columns if c.endswith("_predictions"))
    except StopIteration:
        log.warning(
            "LudwigBackend: not saving test_predictions.csv - no "
            "'<feature>_predictions' column in Ludwig's own predictions "
            f"output (columns: {list(predictions.columns)})"
        )
        return None
    # Ludwig also reports the winning class's confidence as "<feature>_probability"
    # (distinct from "<feature>_probabilities", which holds the full per-class
    # vector) - classification only, absent for regression.
    prob_col = next((c for c in predictions.columns if c.endswith("_probability")), None)

    # Per-class probability columns, keyed by class name - e.g.
    # "Diabetes_probabilities_No" -> "No". Built from the same prefix as
    # pred_col ("Diabetes_predictions" -> "Diabetes_probabilities_") so this
    # works for whatever the output feature is actually named, not a
    # hardcoded one. Empty for regression, where Ludwig doesn't produce
    # these columns at all.
    prob_prefix = pred_col[: -len("_predictions")] + "_probabilities_"
    class_prob_cols = {
        c[len(prob_prefix):]: c for c in predictions.columns if c.startswith(prob_prefix)
    }

    out = df.reset_index(drop=True).copy()
    out["y_true"] = df[target].reset_index(drop=True).astype(str).values

    pred_values = predictions[pred_col].reset_index(drop=True)
    binary_mapping = _binary_output_mapping(df, target, pred_values)
    if binary_mapping is not None:
        # See _binary_output_mapping's docstring - translate Ludwig's raw
        # True/False back into the same label space as y_true above,
        # instead of saving two different representations of the same
        # two classes.
        pred_values = pred_values.map(binary_mapping)
    out["y_pred"] = pred_values.astype(str).values

    out["y_score"] = predictions[prob_col].reset_index(drop=True).values if prob_col else None
    for class_name, col in class_prob_cols.items():
        out[f"y_prob_{class_name}"] = predictions[col].reset_index(drop=True).values
    return out


def _extract_roc(eval_stats: dict, target: str) -> dict:
    """
    Extract ROC curve arrays from Ludwig eval_stats.

    Returns a dict with keys:
        ``roc_fpr``  list[float]
        ``roc_tpr``  list[float]
        ``roc_auc``  float  (optional)

    Returns empty dict on failure.
    """
    try:
        ts = eval_stats.get(target, eval_stats)
        roc_raw = ts.get("roc_curve", {})
        fpr = [float(v) for v in roc_raw.get("false_positive_rates", [])]
        tpr = [float(v) for v in roc_raw.get("true_positive_rates", [])]
        if len(fpr) < 2 or len(tpr) < 2:
            return {}
        out: dict = {"roc_fpr": fpr, "roc_tpr": tpr}
        auc_val = ts.get("roc_auc")
        if isinstance(auc_val, (int, float)):
            out["roc_auc"] = round(float(auc_val), 6)
        return out
    except Exception as exc:
        log.debug(f"LudwigBackend: roc extraction skipped — {exc}")
        return {}


def _shutdown_ray() -> None:
    """Best-effort ray.shutdown() - see its call site in run() for why this
    matters. Factored out so it can also run on the FAILURE path: it used
    to only run after a successful evaluate(), so a run() that raised
    during create_auto_config/train_with_config (e.g. every hyperopt trial
    erroring out before any of them could start - see the 'trial_id'
    KeyError Ludwig itself raises in that case) left Ray running with
    nothing left to poll it, and its own ~60s-idle GCS health check would
    then hard-kill the process a minute later, well after this app had
    already moved on and surfaced its own error to the user."""
    try:
        import ray
        if ray.is_initialized():
            ray.shutdown()
    except Exception as exc:
        log.debug(f"LudwigBackend: ray.shutdown() skipped/failed — {exc}")


# Every hyperopt trial gets its own tempfile.mkdtemp() working directory
# (Ray Tune's function-trainable machinery, not something this app creates
# directly) - normally cleaned up when the trial's own process exits
# cleanly. A hard crash skips that cleanup entirely, and these are small
# enough individually (tens of MB) to go unnoticed for a long time -
# reproduced locally: a single afternoon of crashes during this feature's
# own development left over 5000 of them, 38GB total, which eventually
# filled the disk and crashed a *later*, otherwise-healthy run with "No
# space left on device" (Ray writes its own spill/object-store files to
# the same /tmp). Swept once at the start of every run() rather than only
# on app startup, so it also recovers from a crash that happened earlier
# in the same session, not just ones from a previous launch.
_STALE_TMP_AGE_S = 3600  # 1h - well past any single trial's own runtime


def _cleanup_stale_ray_tmp_dirs() -> None:
    """Best-effort removal of Ray Tune's own leftover tempfile.mkdtemp()
    dirs in the OS temp directory. Only removes directories matching
    Python's own default mkdtemp() naming ("tmp" + random suffix, no
    extension) that are older than _STALE_TMP_AGE_S - old enough that
    nothing could still legitimately be using them, since that pattern is
    also used by other, unrelated programs' own temp dirs which must not
    be touched just because they happen to live in the same /tmp."""
    import re
    import tempfile

    tmp_root = tempfile.gettempdir()
    pattern = re.compile(r"^tmp[A-Za-z0-9_-]{6,}$")
    now = time.time()
    removed, freed_bytes = 0, 0

    try:
        entries = os.scandir(tmp_root)
    except OSError as exc:
        log.debug(f"LudwigBackend: tmp cleanup skipped — {exc}")
        return

    with entries:
        for entry in entries:
            if not pattern.match(entry.name):
                continue
            try:
                if not entry.is_dir(follow_symlinks=False):
                    continue
                age = now - entry.stat(follow_symlinks=False).st_mtime
                if age < _STALE_TMP_AGE_S:
                    continue
                size = 0
                for dirpath, _dirnames, filenames in os.walk(entry.path):
                    for name in filenames:
                        try:
                            size += os.path.getsize(os.path.join(dirpath, name))
                        except OSError:
                            pass
                shutil.rmtree(entry.path)
                removed += 1
                freed_bytes += size
            except OSError:
                continue

    if removed:
        log.info(
            f"LudwigBackend: cleaned up {removed} stale Ray tmp dir(s), "
            f"~{freed_bytes / 1e9:.2f}GB freed"
        )


def _normalize_binary_columns(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Return a copy of *df* with every output feature *config* declares as
    ``binary`` remapped to a clean {0, 1}, if it isn't already.

    Ludwig's own binary preprocessing (ludwig.features.binary_feature.
    BinaryFeatureMixin.cast_column) casts a NUMERIC column straight to bool
    via ``.astype(float).astype(bool)`` whenever the raw values already
    look like numbers to pandas. That's correct for genuine {0, 1} data,
    but silently wrong for any other numeric binary encoding - e.g. a
    clinical outcome coded {1, 2}: Python's bool(1) AND bool(2) are BOTH
    True, so *every* row becomes True regardless of which of the two
    values it actually held. The model then trains against a target with
    no negative examples at all, "correctly" learns to always predict
    True, and reports deceptively perfect accuracy/precision/recall
    alongside an undefined (0) ROC-AUC - the giveaway, since AUC needs
    both classes to be present to mean anything.

    Non-numeric binary columns (e.g. "Sí"/"No") aren't touched - Ludwig's
    str2bool path already maps those correctly on its own; this is
    specifically the numeric-cast blind spot. Mapping is deterministic
    (sorted raw values -> 0, 1) so the same source data always encodes
    the same way across runs.
    """
    binary_cols = [
        f["name"] for f in config.get("output_features", [])
        if f.get("type") == "binary" and f.get("name") in df.columns
    ]
    if not binary_cols:
        return df

    df = df.copy()
    for col in binary_cols:
        values = df[col].dropna().unique()
        if len(values) != 2:
            continue  # not actually binary here - leave it to Ludwig's own validation to complain
        try:
            numeric_values = set(pd.to_numeric(pd.Series(values)))
        except (TypeError, ValueError):
            continue  # non-numeric (e.g. "Sí"/"No") - Ludwig's str2bool already handles this correctly
        if numeric_values <= {0, 1}:
            continue  # already clean
        mapping = {v: i for i, v in enumerate(sorted(values))}
        log.info(
            f"LudwigBackend: remapping binary target '{col}' to 0/1 ({mapping}) - "
            "raw values weren't already 0/1, and Ludwig's own numeric cast "
            "would otherwise have treated both as True"
        )
        df[col] = df[col].map(mapping)
    return df


class _FlatTrainStats:
    """Minimal stand-in for Ludwig's own ``TrainingStats`` (see
    ludwig.api_types), just enough to satisfy
    ``ludwig.utils.training_report.generate_training_report``'s reading of
    ``train_stats.training``/``.validation``/``.test`` - each expected to be
    ``{feature_name: {metric_name: [values, one per epoch]}}``. We only ever
    have one number per metric (the final/evaluated value, not a per-epoch
    history), so each list holds that single value - generate_training_report
    reports it as both "best" and "last", which is correct since there's
    only the one value to report."""

    def __init__(self, target: str, train_metrics: dict, val_metrics: dict, test_metrics: dict):
        def wrap(metrics):
            return {target: {k: [v] for k, v in metrics.items()}} if metrics else {}

        self.training = wrap(train_metrics)
        self.validation = wrap(val_metrics)
        self.test = wrap(test_metrics)


def _build_training_report(
    model,
    target: str,
    train_metrics: dict,
    val_metrics: dict,
    test_metrics: dict,
    random_seed: int,
    training_time_seconds: float,
) -> dict | None:
    """Build a training_report.json using Ludwig's own report generator
    (ludwig.utils.training_report.generate_training_report) instead of
    hand-assembling the dict ourselves - same file Ludwig writes on its own
    during LudwigModel.train()/auto_train's internal trials, just built here
    from OUR metrics (test_metrics is evaluated on the held-out test set
    this backend split off - see _held_out_test_set) rather than from
    Ludwig's own internal trial-time split, which measures something
    different and isn't the number this app shows anywhere else as "test
    performance".

    Returns None on failure so callers can skip saving rather than write a
    broken file.
    """
    try:
        from ludwig.utils.training_report import generate_training_report

        train_stats = _FlatTrainStats(target, train_metrics, val_metrics, test_metrics)
        return generate_training_report(
            config=model.config,
            training_set_metadata=model.training_set_metadata,
            train_stats=train_stats,
            model_dir=None,
            random_seed=random_seed,
            training_time_seconds=training_time_seconds,
        )
    except Exception as exc:
        log.warning(f"LudwigBackend: could not build training report — {exc}")
        return None


# ---------------------------------------------------------------------------
# TrainingPage model-config fields -> Ludwig user_config
# ---------------------------------------------------------------------------

# ray.tune search algorithm behind each of the UI's "Search Strategy" choices.
# "hyperband" was removed - per Ludwig's docs (configuration/
# hyperparameter_optimization.md) it's a documented `executor.scheduler`
# type, not a `search_alg` one; there is no such search algorithm.
_SEARCH_TO_LUDWIG = {
    "random": "variant_generator",
    "bayesian": "hyperopt",
    "exhaustive": "variant_generator",
}
# Metrics where "better" means smaller (regression error metrics).
_MINIMIZE_METRICS = {
    "root_mean_squared_error", "mean_absolute_error",
    "mean_squared_error", "root_mean_squared_percentage_error",
}

# Ludwig's own hyperopt default is unbounded concurrency (max_concurrent_
# trials=None, capped only by CPU count) - on a modest dev machine, 10
# concurrent PyTorch training processes can exceed available RAM and get
# hard-killed by Ray's OOM monitor well before any of them finish (see
# _fields_to_user_config's "else" branch for the crash this fixes). Not
# CPU-count-based on purpose: the failure mode here is memory, and CPU
# count doesn't predict how much RAM is actually available.
_DEFAULT_MAX_CONCURRENT_TRIALS = 3


# Learning method -> trainer.optimizer (see _fields_to_user_config).
_OPTIMIZERS = {
    "regularized": {"type": "adamw", "weight_decay": 0.01},
}


def _apply_architecture(config: dict, architecture: str | None) -> None:
    """Swap the model architecture AutoML chose, in place.

    "light" -> Ludwig's ``concat`` combiner (a small fully-connected network)
    instead of the ``ft_transformer`` that ``auto_train`` picks by default for
    tabular data (ludwig/automl/automl.py, _model_select). It cannot be done
    through ``user_config``: in Ludwig 0.17.9 merging ``{"combiner": {"type":
    "concat"}}`` leaves the ft_transformer search space (``combiner.num_layers``)
    in the config, which then fails validation. So, as Ludwig's AutoML guide
    suggests for manual refinement, the generated config is edited directly:
    the combiner is replaced and its hyperparameter search space swapped for
    the concat one. Any other value (or None) leaves the config untouched.
    """
    if architecture != "light":
        return
    from ludwig.automl.base_config import combiner_defaults
    from ludwig.utils.data_utils import load_yaml

    concat = load_yaml(combiner_defaults["concat"])
    config["combiner"] = concat["combiner"]
    hopt = config.setdefault("hyperopt", {})
    params = {k: v for k, v in (hopt.get("parameters") or {}).items()
              if not k.startswith("combiner.")}
    params.update(concat["hyperopt"]["parameters"])
    hopt["parameters"] = params


def _fields_to_user_config(fields: dict, target: str) -> dict:
    """Translate TrainingPage's flat model-config fields into a partial
    Ludwig config to pass as ``auto_train(user_config=...)`` - merged on top
    of the config auto_train infers, so anything absent here stays its call.

    Only keys that map cleanly are emitted. ``fields`` is expected to carry
    just the settings the user moved off their default (see TrainingPage),
    so an empty dict in means an empty dict out (plain auto_train).
    """
    cfg: dict = {}

    metric = fields.get("metric")
    if metric:
        cfg["trainer"] = {"validation_metric": metric, "validation_field": target}

    # trainer.early_stop (default 5, -1 disables) - configuration/
    # trainer.md. Always sent (like test_split/random_seed above it in
    # TrainingPage) rather than gated on "moved off default", since the
    # UI's own default already matches Ludwig's, so sending it unchanged
    # is a no-op.
    #
    # "early_stop_mode" (see TrainingPage) decides how it is used:
    #   auto      - nothing is sent. AutoML's default hyperparameter search
    #               uses an async-hyperband scheduler that stops weak trials
    #               by itself, and Ludwig forces trainer.early_stop to -1
    #               whenever a scheduler is active (ludwig/schema/
    #               model_types/utils.py), so sending a value here would
    #               only trigger a "Can't utilize early_stop" warning.
    #   patience  - classic early stopping: each trial stops once its
    #               validation metric has not improved for N evaluation
    #               rounds. That needs the scheduler out of the way, i.e.
    #               executor.scheduler.type = "fifo" (see below).
    #   off       - trainer.early_stop = -1 with the fifo scheduler: every
    #               trial runs all its epochs (or until the time budget).
    # Without a mode (older callers) the value is passed through as before.
    early_stop = fields.get("early_stop")
    early_stop_mode = fields.get("early_stop_mode")
    if early_stop_mode == "patience" and early_stop is not None:
        cfg.setdefault("trainer", {})["early_stop"] = int(early_stop)
    elif early_stop_mode == "off":
        cfg.setdefault("trainer", {})["early_stop"] = -1
    elif early_stop_mode is None and early_stop is not None:
        cfg.setdefault("trainer", {})["early_stop"] = int(early_stop)

    # Ludwig docs (configuration/preprocessing.md, "Data Balancing"):
    # dataset balancing is only supported for binary output features. The
    # TrainingPage UI already disables this switch for non-binary problem
    # types; this guard covers configs built outside that UI too (e.g. an
    # imported/duplicated config).
    if fields.get("class_imbalance") and fields.get("problem_type") == "binary":
        cfg["preprocessing"] = {"oversample_minority": 0.5}

    missing_strategy = fields.get("missing_strategy")
    if missing_strategy:
        # Ludwig's own default for a missing NUMBER value is
        # fill_with_const (0.0) - misleading for clinical data, where 0
        # is rarely a neutral placeholder (a blood pressure or age of 0
        # reads as a real, absurd measurement instead of "missing").
        # One of the other documented strategies (configuration/features/
        # number_features.md: fill_with_mean, fill_with_mode, bfill,
        # ffill, drop_row) can be picked instead via TrainingPage's
        # "Missing Numeric Values Strategy" dropdown.
        # "defaults" applies to every number feature at once without
        # having to name each column - merge_dict (see auto_train's
        # merge of user_config) recurses into nested dicts fine, unlike
        # the "output_features" list problem_type has to work around.
        cfg["defaults"] = {"number": {"preprocessing": {"missing_value_strategy": missing_strategy}}}

    # "Learning method" (TrainingPage). Index 0 / absent leaves AutoML's own
    # optimizer (adam) untouched. "regularized" is AdamW with a weight decay:
    # Ludwig's optimizer guide (examples/optimizer_comparison.md) recommends it
    # "whenever training from scratch with regularisation", with
    # weight_decay 0.01 in its own example. merge_dict recurses into the nested
    # trainer.optimizer dict, so only these two keys are overridden.
    optimizer = _OPTIMIZERS.get(fields.get("optimizer"))
    if optimizer:
        cfg.setdefault("trainer", {})["optimizer"] = dict(optimizer)

    search = fields.get("search")
    if search and search != "none":
        hopt: dict = {
            "search_alg": {"type": _SEARCH_TO_LUDWIG.get(search, "variant_generator")},
            "executor": {
                "num_samples": int(fields.get("max_iter") or 10),
                "max_concurrent_trials": int(fields.get("parallel_trials") or 1),
            },
        }
    else:
        # Leaving "Search Strategy" at its default ("none") used to mean
        # no hyperopt.executor at all here, so Ludwig's own default
        # (max_concurrent_trials=None, i.e. unlimited - bounded only by
        # CPU count, not memory) applied unconditionally. On a 10-trial
        # search that's up to 10 full PyTorch training processes running
        # at once; on a typical 16 GB dev machine that's enough to OOM and
        # get several of them hard-killed by Ray mid-run (confirmed
        # locally - see the "2 worker(s) were killed due to the node
        # running low on memory" crash this was written for). Capping it
        # here even in the "no custom search settings" case (unless the user
        # set "Parallel trials" themselves, which always wins) trades some
        # wall-clock time for not crashing on modest hardware; still
        # overridable by explicitly setting a Search Strategy + Parallel
        # trials above.
        hopt = {"executor": {"max_concurrent_trials": int(
            fields.get("parallel_trials") or _DEFAULT_MAX_CONCURRENT_TRIALS)}}

    if metric:
        # Ludwig runs its own default hyperparameter search regardless of
        # whether a Search Strategy was picked above ("none" only skips
        # OUR search-space settings, not Ludwig's own baked-in default
        # search) - so the hyperopt objective must be forced unconditionally
        # here, not only inside the "search != none" branch above. Left
        # unset, auto_train's own set_output_feature_metric() fills it from
        # whatever type IT inferred for the target BEFORE problem_type's
        # forced override is patched into the config (see the call site) -
        # e.g. defaulting to "accuracy" for a target auto-detected as
        # category, even though the user picked a regression metric and
        # forced the feature to "number" right after. Since "accuracy" is
        # never computed for a number output feature, every single trial
        # then fails identically with "missing training (validation)
        # statistics" - reproduced and confirmed via Ray's own trial logs.
        hopt["output_feature"] = target
        hopt["metric"] = metric
        hopt["goal"] = "minimize" if metric in _MINIMIZE_METRICS else "maximize"

    if early_stop_mode in ("patience", "off"):
        hopt.setdefault("executor", {})["scheduler"] = {"type": "fifo"}

    cfg["hyperopt"] = hopt

    return cfg


def _fields_to_effective_config(fields: dict, target: str) -> dict:
    """What the Training page reports as "the partial Ludwig config sent":
    ``_fields_to_user_config`` plus the settings applied to the generated
    config afterwards (see ``_apply_architecture``), so Preview Config and
    training_settings.json show the combiner that will really be used. For
    display only - the extra key is NOT passed to ``auto_train``."""
    cfg = _fields_to_user_config(fields, target)
    if fields.get("architecture") == "light":
        cfg["combiner"] = {"type": "concat"}
    return cfg


# ---------------------------------------------------------------------------
# LudwigBackend
# ---------------------------------------------------------------------------

class LudwigBackend(AutoMLBackend):
    """
    AutoML backend powered by Ludwig 0.10.x.

    Ludwig is imported lazily (inside ``run()``) to avoid penalising the
    app startup with Ludwig's heavyweight imports.

    Extra kwargs accepted by ``run()``:
        tune_for_memory (bool): passed directly to ``ludwig.automl.auto_train``.
        output_directory (str): where Ludwig writes its own run artifacts
            (config, training_report.json, checkpoints). Defaults to "."
            (Ludwig's own default) if not given.
    """

    @property
    def name(self) -> str:
        return "ludwig"

    @classmethod
    def is_available(cls) -> bool:
        """Return True if Ludwig is importable."""
        try:
            import importlib
            importlib.util.find_spec("ludwig")
            return True
        except Exception:
            return False

    @staticmethod
    def _load_best_model_local(results):
        """Load the best model from an AutoTrainResults, on the local backend.

        Ludwig's own ``AutoTrainResults.best_model`` property (see
        ludwig/automl/automl.py) calls
        ``LudwigModel.load(model_dir, from_checkpoint=True)`` with no
        explicit backend, so it falls back to Ludwig's auto-detection
        (picks Ray whenever Ray is already initialized - always true here,
        since auto_train needs Ray to orchestrate hyperopt via Ray Tune
        regardless of the training backend). Ray's backend hits a bug in
        this Ludwig version for this exact reload (RayTrainerV2 is missing
        create_checkpoint_handle), even though run() above explicitly
        requested backend="local" for training itself.

        This re-implements that property using the same public building
        blocks Ludwig's own property uses (``results.experiment_analysis``,
        ``LudwigModel.load``), just passing backend="local" explicitly
        instead of leaving it to auto-detect.
        """
        from ludwig.api import LudwigModel
        from ludwig.globals import MODEL_FILE_NAME

        checkpoint = results.experiment_analysis.best_checkpoint
        if checkpoint is None:
            return None

        with checkpoint.as_directory() as ckpt_path:
            model_dir = os.path.join(ckpt_path, MODEL_FILE_NAME)
            if not os.path.isdir(model_dir):
                return None
            return LudwigModel.load(model_dir, backend="local", from_checkpoint=True)

    def run(
        self,
        df: pd.DataFrame,
        target: str,
        features: list[str] | None = None,
        time_limit_s: int = 3600,
        **kwargs,
    ) -> AutoMLResult:
        """
        Run Ludwig AutoML and return a standardised AutoMLResult.

        Args:
            df: Training DataFrame. Must contain *target*.
            target: Column to predict.
            features: Input columns. None → all except *target*.
            time_limit_s: Maximum training time in seconds.
            tune_for_memory (kwarg): Passed to Ludwig (default False).
            output_directory (kwarg): Where Ludwig writes its run artifacts.
                Defaults to "." (Ludwig's own default) if not given.
            test_split (kwarg): Fraction held out for evaluation, clamped
                to [0.05, 0.5]. Defaults to 0.2 - matches TrainingPage's own
                "Test split" default, though that field's value wasn't
                actually reaching this method before this held-out-set fix.
            random_seed (kwarg): Seed for the held-out split and for Ludwig's
                own internal train/val split of what's left. Defaults to 42.
            config (kwarg): A full Ludwig config dict. When given, training
                uses that fixed config directly instead of auto_train picking
                one — e.g. a config exported by another tool's "duplicate
                this model with different hyperparameters" flow. time_limit_s
                and tune_for_memory are ignored in that case.
            user_config_fields (kwarg): Flat dict of TrainingPage's non-default
                model-config choices (metric, search, class_imbalance, …).
                Translated by _fields_to_user_config() and passed to
                auto_train as user_config=, i.e. merged on top of the config
                it infers. Ignored when `config` is given.
            secondary_outcomes (kwarg): Extra column names to train as
                additional Ludwig output features alongside *target* (a
                real multi-output model - Ludwig's auto_train/
                create_auto_config genuinely accept target as a list, see
                ludwig.automl.automl.create_features_config). *target*
                stays the sole validation_field/hyperopt objective; metrics
                for the secondary outputs are captured into
                result.extra["secondary_outcomes"] rather than
                test_metrics, so every existing results view (built around
                a single target) is unaffected. Ignored when `config` is
                given - a fixed config already names its own output
                features.

        Returns:
            AutoMLResult with model_type, metrics, hyperparameters, etc.
        """
        from hamelin.utils.gpu_check import wait_for_gpu_probe
        wait_for_gpu_probe()
        secondary_outcomes = kwargs.get("secondary_outcomes") or []

        # --- Feature selection ---
        if features:
            keep = [c for c in features if c != target] + [target] + list(secondary_outcomes)
            # dict.fromkeys instead of set(): de-dupes while preserving
            # the order columns are handed to Ludwig in.
            cols = list(dict.fromkeys(keep))
            df = df[cols]

        df = _numericize_datetime_columns(df)

        # See _held_out_test_set's docstring - this is what makes every
        # "test" metric below an actual held-out measurement instead of one
        # computed over rows the model was trained on.
        test_split = kwargs.get("test_split", 0.2)
        random_seed = int(kwargs.get("random_seed", 42))
        train_df, test_df = _held_out_test_set(df, target, test_split, random_seed)

        config = kwargs.get("config")
        if config is not None:
            return self._run_with_config(
                train_df, test_df, target, config, random_seed,
                output_directory=kwargs.get("output_directory"),
            )

        # --- Lazy import ---
        try:
            from ludwig.automl import create_auto_config, train_with_config
        except ImportError as exc:
            # "Ludwig isn't installed" was the only message shown here
            # before, even when Ludwig itself imports fine and the real
            # failure is one of ITS OWN dependencies missing (e.g. dask,
            # required by ludwig.automl specifically) - misleading anyone
            # trying to fix it by reinstalling the wrong package. Surface
            # the actual import error instead of guessing at the cause.
            raise ImportError(
                f"Could not import Ludwig's AutoML module ({exc}). If "
                "Ludwig itself isn't installed, run: pip install ludwig. "
                "If it is installed but this still fails, one of its own "
                "dependencies is missing - see the error above for which one."
            ) from exc

        tune_for_memory = kwargs.get("tune_for_memory", False)
        # Ludwig defaults output_directory to "." (its own process cwd) when
        # not given, which scatters experiment_run* folders wherever this
        # app happens to be launched from instead of somewhere predictable.
        # LudwigTrainer.train() sets this to a project-scoped path by
        # default; kept overridable here via backend_kwargs for callers
        # that want Ludwig's own default cwd behavior instead.
        output_directory = kwargs.get("output_directory", ".")

        # Ray Tune auto-resumes from the latest experiment_state-*.json it
        # finds under <output_directory>/hyperopt, left there by ANY past
        # run in this same project - including a run that itself never
        # completed a single trial (e.g. this exact run() previously
        # failing for any reason). Resuming from that empty state hits a
        # Ray bug (tune_controller._restore_trials indexes trials[0] on an
        # empty list) that Ray silently swallows and "restarts" from, but
        # that restart ends up configuring the new run with 0 trials -
        # which then makes Ludwig's own results collection raise a bare
        # KeyError('trial_id') building a DataFrame with no rows. Net
        # effect: one failed run poisons every run after it in the same
        # project, indefinitely, until this folder is cleared - reproduced
        # locally and confirmed against the real traceback. Nothing this
        # app reads later lives in here (see LudwigTrainer's own docstring
        # - ludwig_runs/ is Ludwig's disposable internal trial dump, not
        # the results/models/ this app actually keeps), so it's safe to
        # always start from an empty hyperopt/ folder rather than trying
        # to selectively identify just the "bad" state file.
        hyperopt_dir = os.path.join(output_directory, "hyperopt")
        if os.path.isdir(hyperopt_dir):
            try:
                shutil.rmtree(hyperopt_dir)
            except OSError as exc:
                log.warning(f"LudwigBackend: could not clear stale {hyperopt_dir} — {exc}")

        _cleanup_stale_ray_tmp_dirs()

        # Non-default model-config choices from TrainingPage, layered on top
        # of what auto_train infers (see _fields_to_user_config). Called
        # even when the user left the whole card alone (_fields empty) -
        # _fields_to_user_config always sets a safety cap on hyperopt
        # concurrency regardless, so that can't be skipped just because
        # nothing else needed overriding.
        _fields = kwargs.get("user_config_fields") or {}
        user_config = _fields_to_user_config(_fields, target) or None

        # Ludwig's create_auto_config genuinely accepts target as a list
        # (see ludwig.automl.automl.create_features_config /
        # get_features_config) - each name becomes its own output feature,
        # a real multi-output model, not just a single target with extra
        # inputs ignored.
        auto_train_target = [target, *secondary_outcomes] if secondary_outcomes else target

        log.info(
            f"LudwigBackend: running auto_train — target={auto_train_target!r}, "
            f"train_rows={len(train_df)}, test_rows={len(test_df)}, "
            f"cols={len(df.columns) - 1}, time_limit={time_limit_s}s, "
            f"output_directory={output_directory!r}, user_config={user_config!r}"
        )

        wall_start = time.perf_counter()
        try:
            # Two steps (create_auto_config then train_with_config)
            # instead of the one-call auto_train() this used to be: a
            # forced output-feature type (fields["problem_type"]) has to
            # be patched into the auto-generated config directly, not
            # merged in via user_config - Ludwig's merge_dict only
            # recurses into nested dicts, so an "output_features" list in
            # user_config would REPLACE the whole auto-generated list
            # (losing the secondary_outcomes entries) rather than
            # overriding just the primary target's type.
            config = create_auto_config(
                dataset=train_df,
                target=auto_train_target,
                time_limit_s=time_limit_s,
                tune_for_memory=tune_for_memory,
                user_config=user_config,
                random_seed=random_seed,
            )
            _apply_architecture(config, (_fields or {}).get("architecture"))
            problem_type = (_fields or {}).get("problem_type")
            if problem_type:
                for out_feat in config.get("output_features", []):
                    if out_feat.get("name") == target:
                        out_feat["type"] = problem_type
                        break

            # A category OUTPUT feature's missing values default (Ludwig's
            # own schema default, not something this app set) to
            # missing_value_strategy "drop_row" - the row is dropped
            # entirely rather than trained/evaluated on. For a clinical
            # categorical outcome, "nothing recorded" is very often itself
            # meaningful (e.g. no prevention method was used) rather than
            # a data-entry gap, so treat it as its own explicit category
            # instead of discarding those patients. This also fixes a
            # concrete downstream failure: those dropped rows made
            # evaluate()'s predictions come back with fewer rows than the
            # held-out test split, which _build_predictions_frame (see its
            # own docstring) correctly refuses to save test_predictions.csv
            # for - so a category outcome with any missing values ended up
            # with no confusion matrix at all.
            for out_feat in config.get("output_features", []):
                if out_feat.get("type") == "category":
                    out_feat.setdefault("preprocessing", {})
                    out_feat["preprocessing"]["missing_value_strategy"] = "fill_with_const"
                    out_feat["preprocessing"]["fill_value"] = "Missing"

            _zscore_number_outputs(config)

            # See _normalize_binary_columns' docstring - a copy just for
            # Ludwig's own consumption, not train_df itself: the exported
            # predictions CSV below still shows the dataset's real original
            # values (see _build_predictions_frame(test_df, ...)), not this
            # remapped encoding.
            train_df_ludwig = _normalize_binary_columns(train_df, config)

            results = train_with_config(
                dataset=train_df_ludwig,
                config=config,
                output_directory=output_directory,
                random_seed=random_seed,
                # Ludwig silently switches to its distributed Ray backend
                # whenever the "ray" package is importable (see
                # ludwig.backend._has_ray()), regardless of dataset size.
                # Our datasets are small clinical CSVs that never need
                # distributed training, and Ludwig 0.17.x's Ray backend has
                # a checkpoint-resume bug of its own (RayTrainerV2 has no
                # create_checkpoint_handle method), so force the local
                # backend explicitly rather than let it auto-detect.
                backend="local",
            )
        except Exception as exc:
            _shutdown_ray()
            hint = ""
            if isinstance(exc, KeyError) and str(exc) == "'trial_id'":
                # Ludwig's own hyperopt result-collection assumes at least
                # one trial reported back; when every trial errors out
                # before that (typically a transient failure to launch
                # Ray's local cluster, not a data/config problem - the
                # search space itself was already built successfully by
                # this point) it raises this raw KeyError instead of a
                # clear "no trials completed" message. Usually transient.
                hint = (
                    " (no hyperopt trial completed - this is usually a "
                    "transient failure to start Ray's local cluster; "
                    "try training again)"
                )
            raise RuntimeError(f"Ludwig auto_train failed: {exc}{hint}") from exc

        elapsed = round(time.perf_counter() - wall_start, 2)
        best_model = self._load_best_model_local(results)

        # --- num_trials ---
        num_trials = 0
        try:
            num_trials = len(results.experiment_analysis.trials)
        except Exception:
            pass

        # --- Evaluate ---
        test_metrics: dict = {}
        extra: dict = {}
        try:
            # collect_predictions=True: same evaluate() call already run for
            # the aggregate metrics also returns Ludwig's per-row
            # predictions - capturing them here is free, versus a separate
            # model.predict() pass later just to get row-level detail.
            # test_df_ludwig, not test_df: same binary remapping as the
            # training data above, so evaluation is scored against the
            # same clean encoding the model was actually trained on -
            # _build_predictions_frame just below still reads the
            # original, unremapped test_df for the human-readable columns.
            test_df_ludwig = _normalize_binary_columns(test_df, config)
            eval_stats, predictions, _ = best_model.evaluate(dataset=test_df_ludwig, collect_predictions=True)
            test_metrics = _flatten_eval_stats(eval_stats, target)
            if _target_is_normalized(best_model.config, target):
                test_metrics.update(_original_scale_regression_metrics(test_df, predictions, target))
            extra.update(_extract_confusion_matrix(eval_stats, target))
            extra.update(_extract_roc(eval_stats, target))
            extra["test_predictions"] = _build_predictions_frame(test_df, predictions, target)
            # Secondary outcomes trained as extra output features (see
            # secondary_outcomes above) get their own entry in eval_stats
            # too - captured here rather than merged into test_metrics so
            # every existing results view (confusion matrix, ROC, the
            # "interface" comparison tool, …), all built around one
            # target's flat metrics dict, keeps working unchanged. No UI
            # currently reads this key yet - it's there for a future pass.
            if secondary_outcomes:
                extra["secondary_outcomes"] = {
                    name: _flatten_eval_stats(eval_stats, name)
                    for name in secondary_outcomes
                }
        except Exception as exc:
            log.warning(f"LudwigBackend: evaluation failed — {exc}")

        extra["training_report"] = _build_training_report(
            best_model, target, {}, {}, test_metrics, random_seed, elapsed
        )

        model_type = _extract_model_type(best_model)
        hyperparameters = _extract_hyperparameters(best_model)

        log.info(
            f"LudwigBackend: done — model={model_type}, "
            f"time={elapsed}s, trials={num_trials}, metrics={test_metrics}, "
            f"extra_keys={list(extra.keys())}"
        )

        # Ray was only needed to orchestrate the hyperopt trials above
        # (auto_train always starts it for that, regardless of the local
        # training backend) - nothing after this point touches it. Leaving
        # it running idle risks Ray's own background GCS health-check
        # deciding, after ~60s of inactivity, that GCS is unreachable and
        # hard-killing this whole process - which has been observed to
        # happen a minute or so after a training run finished successfully,
        # while the UI was still busy rendering results. Shutting Ray down
        # explicitly now, while we know it's safe to, avoids that window
        # entirely. A later training run re-initializes it on its own.
        _shutdown_ray()

        return AutoMLResult(
            model_type=model_type,
            hyperparameters=hyperparameters,
            test_metrics=test_metrics,
            training_time_seconds=elapsed,
            num_trials=num_trials,
            trained_model=best_model,
            extra=extra,
        )

    def _run_with_config(
        self, train_df: pd.DataFrame, test_df: pd.DataFrame, target: str, config: dict,
        random_seed: int = 42,
        output_directory: str | None = None,
    ) -> AutoMLResult:
        """Train with a fixed Ludwig config instead of letting auto_train
        pick one. No hyperopt trials, no time budget - just train the given
        architecture/hyperparameters on train_df and evaluate on test_df
        (the held-out set run() split off before calling this - see
        _held_out_test_set)."""
        from hamelin.utils.gpu_check import wait_for_gpu_probe
        wait_for_gpu_probe()
        try:
            from ludwig.api import LudwigModel
        except ImportError as exc:
            raise ImportError(
                f"Could not import Ludwig ({exc}). If Ludwig itself isn't "
                "installed, run: pip install ludwig. If it is installed but "
                "this still fails, one of its own dependencies is missing - "
                "see the error above for which one."
            ) from exc

        log.info(
            f"LudwigBackend: running with a fixed config — target={target!r}, "
            f"train_rows={len(train_df)}, test_rows={len(test_df)}, "
            f"cols={len(train_df.columns) - 1}"
        )

        _cleanup_stale_ray_tmp_dirs()

        wall_start = time.perf_counter()
        try:
            # See the matching comment in run() - avoid Ludwig's auto-detected
            # Ray backend, which silently activates whenever "ray" is
            # importable and is broken for checkpoint resume in this
            # Ludwig version.
            # See _normalize_binary_columns' docstring - fixed configs
            # (e.g. from "duplicate this model") carry their own declared
            # output feature types and are just as exposed to Ludwig's
            # numeric-binary-cast blind spot as an auto-generated config.
            model = LudwigModel(config=config, backend="local")
            # LudwigModel.train() writes its run artifacts to "results"
            # relative to the current directory unless told otherwise, which
            # scattered a stray results/ folder wherever the app was
            # launched. Keep them with the project's other Ludwig runs (the
            # trained model itself is saved separately, under results/models/).
            train_kwargs = {}
            if output_directory:
                train_kwargs["output_directory"] = os.path.join(output_directory, "config_runs")
            model.train(dataset=_normalize_binary_columns(train_df, config), **train_kwargs)
        except Exception as exc:
            raise RuntimeError(f"Ludwig training with fixed config failed: {exc}") from exc

        elapsed = round(time.perf_counter() - wall_start, 2)

        test_metrics: dict = {}
        extra: dict = {}
        try:
            # test_df here (unlike just above) stays the original,
            # unremapped frame for _build_predictions_frame's human-
            # readable columns - only evaluate() gets the remapped copy.
            eval_stats, predictions, _ = model.evaluate(
                dataset=_normalize_binary_columns(test_df, config), collect_predictions=True
            )
            test_metrics = _flatten_eval_stats(eval_stats, target)
            if _target_is_normalized(model.config, target):
                test_metrics.update(_original_scale_regression_metrics(test_df, predictions, target))
            extra.update(_extract_confusion_matrix(eval_stats, target))
            extra.update(_extract_roc(eval_stats, target))
            extra["test_predictions"] = _build_predictions_frame(test_df, predictions, target)
        except Exception as exc:
            log.warning(f"LudwigBackend: evaluation failed — {exc}")

        extra["training_report"] = _build_training_report(
            model, target, {}, {}, test_metrics, random_seed, elapsed
        )

        model_type = _extract_model_type(model)
        hyperparameters = _extract_hyperparameters(model)

        log.info(
            f"LudwigBackend: fixed-config run done — model={model_type}, "
            f"time={elapsed}s, metrics={test_metrics}, extra_keys={list(extra.keys())}"
        )

        return AutoMLResult(
            model_type=model_type,
            hyperparameters=hyperparameters,
            test_metrics=test_metrics,
            training_time_seconds=elapsed,
            num_trials=0,
            trained_model=model,
            extra=extra,
        )

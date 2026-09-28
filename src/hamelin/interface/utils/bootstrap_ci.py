"""95% confidence interval for a model's metric, by bootstrap resampling of
its saved test_predictions.csv (see utils.get_model_paths.load_test_predictions
and hamelin-v2's LudwigBackend._build_predictions_frame - one row per
held-out patient, never seen during training).

Only accuracy (classification) and R²/RMSE/MAE (regression) are supported
here, deliberately not roc_auc: test_predictions.csv's y_score column is
the WINNING class's confidence for each row (see _build_predictions_frame),
which flips which "channel" it refers to depending on what was predicted -
not the fixed positive-class probability every row needs to recompute
AUC-ROC correctly. Bootstrapping it anyway would produce a number that
looks rigorous but isn't, which is exactly what this whole interface is
built to avoid. A real AUC-ROC CI needs the saved file to also carry the
full per-class probability vector - not done yet.
"""

import numpy as np


def _accuracy(df):
    return float((df["y_true"].astype(str) == df["y_pred"].astype(str)).mean())


def _r2(df):
    from sklearn.metrics import r2_score
    return float(r2_score(df["y_true"].astype(float), df["y_pred"].astype(float)))


def _rmse(df):
    from sklearn.metrics import mean_squared_error
    return float(mean_squared_error(df["y_true"].astype(float), df["y_pred"].astype(float)) ** 0.5)


def _mae(df):
    from sklearn.metrics import mean_absolute_error
    return float(mean_absolute_error(df["y_true"].astype(float), df["y_pred"].astype(float)))


# Metric-name fragment -> point-estimate function. Checked in order, first
# match wins - same normalized-name convention as utils.metric_labels, kept
# separate rather than merged into it since this module is specifically
# about what CAN be bootstrapped from saved predictions, not about display.
_SUPPORTED_METRICS = [
    (lambda n: n in ("accuracy", "acc"), _accuracy),
    (lambda n: n in ("r2", "rsquared"), _r2),
    (lambda n: ("rootmeansquared" in n and "percentage" not in n) or n == "rmse", _rmse),
    (lambda n: "meanabsoluteerror" in n or n == "mae", _mae),
]

MIN_ROWS = 10


def _metric_function(metric_name):
    n = metric_name.lower().replace("-", "").replace("_", "").replace(" ", "")
    for match, fn in _SUPPORTED_METRICS:
        if match(n):
            return fn
    return None


def is_supported(metric_name):
    """Whether bootstrap_ci() can compute a CI for this metric at all -
    lets a caller decide to hide the whole affordance rather than call
    bootstrap_ci() just to get (None, None, None) back."""
    return _metric_function(metric_name) is not None


def bootstrap_ci(predictions_df, metric_name, n_bootstrap=1000, confidence=0.95, seed=42):
    """95% CI for one metric, computed by resampling rows of
    predictions_df (a loaded test_predictions.csv) with replacement
    n_bootstrap times and taking the point estimate's percentile range.

    Returns (point_estimate, ci_low, ci_high). point_estimate is always
    the real value computed on the full (non-resampled) data when the
    metric is supported and there's enough data; ci_low/ci_high are None
    when a CI can't be produced (unsupported metric, fewer than MIN_ROWS
    rows, or too many resamples failed to compute - e.g. R² on a resample
    that happened to land on a single unique value).
    """
    compute = _metric_function(metric_name)
    if compute is None or len(predictions_df) < MIN_ROWS:
        return (compute(predictions_df) if compute and len(predictions_df) > 0 else None), None, None

    try:
        point = compute(predictions_df)
    except Exception:
        return None, None, None

    rng = np.random.default_rng(seed)
    n_rows = len(predictions_df)
    boot_values = []
    for _ in range(n_bootstrap):
        sample = predictions_df.iloc[rng.integers(0, n_rows, n_rows)]
        try:
            boot_values.append(compute(sample))
        except Exception:
            continue

    # Half the resamples failing is a sign something's structurally wrong
    # with this data for this metric (e.g. R² on an almost-constant target)
    # rather than ordinary bad luck - safer to show the point estimate
    # alone than a CI built from a biased handful of resamples.
    if len(boot_values) < n_bootstrap // 2:
        return point, None, None

    alpha = (1 - confidence) / 2
    ci_low = float(np.percentile(boot_values, alpha * 100))
    ci_high = float(np.percentile(boot_values, (1 - alpha) * 100))
    return point, ci_low, ci_high

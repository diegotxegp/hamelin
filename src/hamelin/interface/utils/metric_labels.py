"""Plain-language metric names/explanations for clinicians / non-AI-experts.
No ML jargon or abbreviations (F1, ROC-AUC, PPV, etc.) in the visible text.

Shared by every comparison view (table, graphs, heatmap, radar) so they
can't drift out of sync on how the same metric is labelled.
"""

METRIC_INFO = [
    {
        "match": lambda n: "loss" in n,
        "label": "Prediction Error",
        "jargon": "Loss",
        "short": "How far off the model's predictions are, on average, across the patients it was tested on. Lower is better.",
        "priority": False,
    },
    {
        "match": lambda n: n in ("acc", "accuracy"),
        "label": "Overall Accuracy",
        "jargon": "Accuracy",
        "short": "Out of all patients, the percentage the model classified correctly.",
        "priority": False,
    },
    {
        "match": lambda n: "precision" in n or n in ("ppv",),
        "label": "Reliability of Positive Results",
        "jargon": "Precision / PPV",
        "short": "When the model says a patient has the condition, how often it is actually right.",
        "priority": True,
    },
    {
        "match": lambda n: "recall" in n or "sensitivity" in n or n == "sens",
        "label": "Detection Rate",
        "jargon": "Recall / Sensitivity",
        "short": "Out of all patients who truly have the condition, how many the model correctly finds.",
        "priority": True,
    },
    {
        "match": lambda n: "specificity" in n or n in ("spec",),
        "label": "Rate of Correctly Ruling Out",
        "jargon": "Specificity",
        "short": "Out of all patients who do NOT have the condition, how many the model correctly identifies as such.",
        "priority": True,
    },
    {
        "match": lambda n: "f1" in n,
        "label": "Overall Balance Score",
        "jargon": "F1 Score",
        "short": "A single score balancing how many patients with the condition the model finds against how many false alarms it raises.",
        "priority": False,
    },
    {
        "match": lambda n: "roc" in n or "auc" in n,
        "label": "Ability to Distinguish Cases",
        "jargon": "ROC-AUC",
        "short": "How well the model can tell apart patients with and without the condition, overall.",
        "priority": False,
    },
    # Regression metrics. Matched before the plain "meansquarederror" entry
    # below since e.g. "rootmeansquarederror" contains "meansquarederror" as
    # a substring - order here matters.
    {
        "match": lambda n: n in ("r2", "rsquared"),
        "label": "Goodness of Fit (R²)",
        "jargon": "R²",
        "short": "How much of the variation in the true values the model's predictions explain. 1.0 is a perfect fit; 0 means it does no better than always predicting the average.",
        "priority": True,
    },
    {
        "match": lambda n: "rootmeansquaredpercentage" in n or n == "rmspe",
        "label": "Typical Percent Error",
        "jargon": "RMSPE",
        "short": "The typical size of the model's error, as a percentage of the true value. Lower is better.",
        "priority": False,
    },
    {
        "match": lambda n: ("rootmeansquared" in n and "percentage" not in n) or n == "rmse",
        "label": "Typical Prediction Error (RMSE)",
        "jargon": "RMSE",
        "short": "The typical size of the model's error, in the same units as the value being predicted. Lower is better.",
        "priority": False,
    },
    {
        "match": lambda n: "meanabsolutepercentage" in n or n == "mape",
        "label": "Average Percent Error",
        "jargon": "MAPE",
        "short": "The average size of the model's error, as a percentage of the true value. Lower is better.",
        "priority": False,
    },
    {
        "match": lambda n: "meanabsoluteerror" in n or n == "mae",
        "label": "Average Prediction Error (MAE)",
        "jargon": "MAE",
        "short": "The average size of the model's error, in the same units as the value being predicted, treating every mistake equally. Lower is better.",
        "priority": False,
    },
    {
        "match": lambda n: ("meansquarederror" in n and "root" not in n) or n == "mse",
        "label": "Squared Prediction Error (MSE)",
        "jargon": "MSE",
        "short": "Like the average error, but large mistakes count for much more than small ones. Lower is better.",
        "priority": False,
    },
]

_DEFAULT_SHORT = "A general measurement of how well the model performs."

# Only metrics with a genuinely universal, textbook scale get a quality
# verdict here (same bands Hamelin's own results page uses) - everything
# else (accuracy, precision, recall, specificity, F1...) depends too much on
# class balance/context for a fixed number to mean "good" or "bad" on its
# own, so those are shown as plain values with no verdict attached. Each
# entry is (threshold, band_name, warning_or_None) checked in order, highest
# threshold first; only the worst band(s) carry a warning.
_AUC_BANDS = [
    (0.90, "excellent", None),
    (0.80, "good", None),
    (0.70, "moderate", None),
    (float("-inf"), "limited", (
        "This is close to 0.5 (random guessing) - the model has limited "
        "ability to tell these patients apart. Treat its predictions with "
        "caution."
    )),
]

_R2_BANDS = [
    (0.90, "excellent", None),
    (0.70, "good", None),
    (0.50, "moderate", None),
    (0.0, "weak", (
        "This model explains less than half of the variation in the true "
        "values - treat its predictions with caution."
    )),
    (float("-inf"), "worse than baseline", (
        "This model performs worse than simply predicting the average "
        "every time - it isn't finding a real relationship in this data."
    )),
]


def _quality_scale_for(metric_name):
    n = metric_name.lower().replace("-", "").replace("_", "").replace(" ", "")
    if "roc" in n or "auc" in n:
        return _AUC_BANDS
    if n in ("r2", "rsquared"):
        return _R2_BANDS
    return None


def get_metric_quality(metric_name, value):
    """Return (band_name, warning_or_None) for metrics with an established
    quality scale (AUC-ROC, R²), or (None, None) for everything else - see
    the comment above _AUC_BANDS for why the scale is limited to just those."""
    if value is None:
        return None, None

    scale = _quality_scale_for(metric_name)
    if scale is None:
        return None, None

    for threshold, band, warning in scale:
        if value >= threshold:
            return band, warning
    return scale[-1][1], scale[-1][2]


def get_metric_info(raw_name):
    n = raw_name.lower().replace("-", "").replace("_", "").replace(" ", "")
    for entry in METRIC_INFO:
        if entry["match"](n):
            return entry
    return {
        "label": raw_name.replace("_", " ").replace("-", " ").title(),
        "short": _DEFAULT_SHORT,
        "priority": False,
    }


def _is_priority_metric(name):
    return get_metric_info(name)["priority"] or _quality_scale_for(name) is not None


def filter_priority_metrics(names):
    """Cut a metric list down to the ones worth showing in simple mode:
    those flagged priority=True (precision/recall/specificity/R²) plus any
    metric with an established quality scale (see _quality_scale_for) even
    if not flagged priority - roc_auc is the one classification metric with
    an actual good/bad verdict, but predates the priority flag and isn't
    marked with it, so dropping it here would hide the only number that
    tells a clinician outright whether the model is any good.

    Falls back to the untouched list if nothing in it would survive the
    filter (e.g. a run that only ever reported loss+accuracy), so a
    filtered view never ends up with nothing to show."""
    kept = [n for n in names if _is_priority_metric(n)]
    return kept if kept else list(names)


def filter_priority_metric_pairs(names, keys):
    """Same filter as filter_priority_metrics, but keeps a second parallel
    list (e.g. the full metric keys, like "test/roc_auc/best") in step -
    for comparison views that carry matching display-name/full-key lists
    (visualise_comparison_table.py, visualise_comparison_heatmap.py)."""
    pairs = [(n, k) for n, k in zip(names, keys) if _is_priority_metric(n)]
    if not pairs:
        return list(names), list(keys)
    return [n for n, k in pairs], [k for n, k in pairs]


# Simple-mode priority picker: instead of picking a raw metric, the user
# picks what they actually care about, and this resolves it to whichever
# metric in the current comparison set answers that. Order matters - it's
# the order options are shown in, most clinically urgent first.
SIMPLE_MODE_PRIORITIES = [
    {
        "key": "recall",
        "label": "Detect as many real cases as possible",
        "match": lambda n: "recall" in n or "sensitivity" in n or n == "sens",
    },
    {
        "key": "precision",
        "label": "Avoid false alarms",
        "match": lambda n: "precision" in n or n in ("ppv",),
    },
    {
        "key": "f1",
        "label": "Find the best balance of both",
        "match": lambda n: "f1" in n,
    },
    {
        "key": "accuracy",
        "label": "See overall performance",
        "match": lambda n: n in ("acc", "accuracy"),
    },
]


def pick_priority_metric(metric_names, priority_key):
    """The first entry in `metric_names` matching the SIMPLE_MODE_PRIORITIES
    option `priority_key` (e.g. "recall"), or None if this comparison set
    doesn't report anything answering that priority - e.g. a regression-only
    group has no recall/precision/accuracy at all."""
    option = next((o for o in SIMPLE_MODE_PRIORITIES if o["key"] == priority_key), None)
    if option is None:
        return None

    for name in metric_names:
        n = name.lower().replace("-", "").replace("_", "").replace(" ", "")
        if option["match"](n):
            return name
    return None


def get_metric_glossary_entries(names):
    """Deduped, priority-sorted glossary entries for the metrics in `names`,
    so a popup can always match whatever labels are actually shown in the
    table/graph/heatmap/radar next to it instead of a hand-written list that
    can drift out of sync. Priority metrics (precision/recall/specificity)
    are sorted first; pass to utils.theme.build_glossary_widget to render."""
    seen = set()
    entries = []
    for name in names:
        info = get_metric_info(name)
        if info["label"] in seen:
            continue
        seen.add(info["label"])
        entries.append({"label": info["label"], "text": info["short"], "priority": info["priority"]})

    entries.sort(key=lambda entry: not entry["priority"])
    return entries

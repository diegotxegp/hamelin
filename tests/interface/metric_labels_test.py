import pytest

from hamelin.interface.utils.metric_labels import (
    get_metric_info,
    get_metric_quality,
    filter_priority_metrics,
    filter_priority_metric_pairs,
    pick_priority_metric,
)


@pytest.mark.parametrize("raw_name,expected_label", [
    ("loss", "Prediction Error"),
    ("test/combined/loss", "Prediction Error"),
    ("accuracy", "Overall Accuracy"),
    ("acc", "Overall Accuracy"),
    ("precision", "Reliability of Positive Results"),
    ("ppv", "Reliability of Positive Results"),
    ("recall", "Detection Rate"),
    ("sensitivity", "Detection Rate"),
    ("specificity", "Rate of Correctly Ruling Out"),
    ("spec", "Rate of Correctly Ruling Out"),
    ("f1_score", "Overall Balance Score"),
    ("roc_auc", "Ability to Distinguish Cases"),
    ("r2", "Goodness of Fit (R²)"),
    ("root_mean_squared_error", "Typical Prediction Error (RMSE)"),
    ("root_mean_squared_percentage_error", "Typical Percent Error"),
    ("mean_absolute_error", "Average Prediction Error (MAE)"),
    ("mean_absolute_percentage_error", "Average Percent Error"),
    ("mean_squared_error", "Squared Prediction Error (MSE)"),
])
def test_get_metric_info_known_metrics(raw_name, expected_label):
    assert get_metric_info(raw_name)["label"] == expected_label


def test_get_metric_info_is_case_and_separator_insensitive():
    assert get_metric_info("F1-Score") == get_metric_info("f1_score")
    assert get_metric_info("ROC AUC") == get_metric_info("roc_auc")


def test_get_metric_info_unknown_metric_falls_back_to_titled_name():
    info = get_metric_info("custom_business_metric")
    assert info["label"] == "Custom Business Metric"
    assert info["priority"] is False


def test_priority_metrics_are_flagged():
    assert get_metric_info("precision")["priority"] is True
    assert get_metric_info("recall")["priority"] is True
    assert get_metric_info("specificity")["priority"] is True
    assert get_metric_info("accuracy")["priority"] is False


@pytest.mark.parametrize("raw_name,value,expected_band,has_warning", [
    ("roc_auc", 0.95, "excellent", False),
    ("roc_auc", 0.85, "good", False),
    ("roc_auc", 0.75, "moderate", False),
    ("roc_auc", 0.55, "limited", True),
    ("r2", 0.95, "excellent", False),
    ("r2", 0.75, "good", False),
    ("r2", 0.55, "moderate", False),
    ("r2", 0.2, "weak", True),
    ("r2", -0.3, "worse than baseline", True),
])
def test_get_metric_quality_bands(raw_name, value, expected_band, has_warning):
    band, warning = get_metric_quality(raw_name, value)
    assert band == expected_band
    assert (warning is not None) == has_warning


def test_get_metric_quality_none_for_unscaled_metrics():
    # accuracy/precision/recall/etc. don't have a universal "good" value -
    # see the comment above _AUC_BANDS in metric_labels.py.
    assert get_metric_quality("accuracy", 0.99) == (None, None)
    assert get_metric_quality("precision", 0.1) == (None, None)


def test_get_metric_quality_none_for_missing_value():
    assert get_metric_quality("roc_auc", None) == (None, None)


def test_filter_priority_metrics_keeps_flagged_and_banded_metrics():
    # precision/recall/specificity are priority=True; roc_auc isn't flagged
    # priority but has a quality scale and must survive anyway (see the
    # comment in filter_priority_metrics for why); accuracy/f1/loss have
    # neither and should be dropped.
    names = ["accuracy", "precision", "recall", "specificity", "f1_score", "roc_auc", "loss"]
    assert filter_priority_metrics(names) == ["precision", "recall", "specificity", "roc_auc"]


def test_filter_priority_metrics_keeps_r2_for_regression():
    names = ["root_mean_squared_error", "mean_absolute_error", "r2"]
    assert filter_priority_metrics(names) == ["r2"]


def test_filter_priority_metrics_falls_back_when_nothing_survives():
    # A run that only ever reported non-priority, non-banded metrics -
    # filtering to nothing would leave the view empty, so the original list
    # comes back untouched instead.
    names = ["loss", "accuracy"]
    assert filter_priority_metrics(names) == names


def test_filter_priority_metric_pairs_keeps_names_and_keys_in_step():
    names = ["accuracy", "precision", "roc_auc"]
    keys = ["test/accuracy/best", "test/precision/best", "test/roc_auc/best"]
    kept_names, kept_keys = filter_priority_metric_pairs(names, keys)
    assert kept_names == ["precision", "roc_auc"]
    assert kept_keys == ["test/precision/best", "test/roc_auc/best"]


def test_filter_priority_metric_pairs_falls_back_when_nothing_survives():
    names = ["loss", "accuracy"]
    keys = ["test/loss/best", "test/accuracy/best"]
    assert filter_priority_metric_pairs(names, keys) == (names, keys)


def test_pick_priority_metric_resolves_each_option():
    names = ["loss", "accuracy", "precision", "recall", "specificity", "f1_score", "roc_auc"]
    assert pick_priority_metric(names, "recall") == "recall"
    assert pick_priority_metric(names, "precision") == "precision"
    assert pick_priority_metric(names, "f1") == "f1_score"
    assert pick_priority_metric(names, "accuracy") == "accuracy"


def test_pick_priority_metric_none_when_nothing_matches():
    # A regression-only comparison set has no recall/precision/accuracy at all.
    names = ["r2", "mean_absolute_error"]
    assert pick_priority_metric(names, "recall") is None


def test_pick_priority_metric_none_for_unknown_key():
    assert pick_priority_metric(["accuracy"], "not_a_real_key") is None


def test_pick_priority_metric_returns_first_match():
    names = ["sensitivity", "recall"]
    assert pick_priority_metric(names, "recall") == "sensitivity"

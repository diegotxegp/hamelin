"""The rule-based reading of a trained model's results."""
import numpy as np
import pandas as pd
import pytest

from hamelin.analytics.result_advice import advice_html, build_advice, detect_task


def _preds(n=200, prevalence=0.5, acc=0.8, seed=0):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < prevalence).astype(int)
    pred = np.where(rng.random(n) < acc, y, 1 - y)
    prob = np.clip(y * 0.4 + rng.random(n) * 0.6, 0, 1)
    return pd.DataFrame({"y_true": y, "y_pred": pred, "y_prob_0": 1 - prob, "y_prob_1": prob})


def _text(adv):
    return " ".join([adv.verdict] + [l for _, lines in adv.sections for l in lines])


def test_binary_good_result_is_rated_good_and_explained():
    adv = build_advice({"roc_auc": 0.86, "accuracy": 0.80, "recall": 0.82, "specificity": 0.78, "precision": 0.8},
                       {"roc_auc": 0.88}, _preds(300))
    assert adv.task == "binary" and adv.level == "good" and adv.verdict.startswith("Good result")
    titles = [t_ for t_, _ in adv.sections]
    assert titles == ["Why", "How reliable is this estimate?", "How it could be improved", "Before relying on it"]
    text = _text(adv)
    assert "0.86" in text and "sensitivity" in text and "95% confidence interval" in text
    assert "external validation" in text and "not a diagnosis" in text


def test_weak_binary_result_says_so_and_suggests_more_data():
    adv = build_advice({"roc_auc": 0.58, "accuracy": 0.55}, None, _preds(60, acc=0.55))
    assert adv.level == "weak" and "Weak result" in adv.verdict
    text = _text(adv)
    assert "Only 60 patients" in text and "Use more patients" in text


def test_suspiciously_high_result_is_flagged():
    adv = build_advice({"roc_auc": 0.98, "accuracy": 0.95}, {"roc_auc": 0.99}, _preds(400, acc=0.95))
    assert "rare in clinical data" in _text(adv)


def test_overfitting_gap_is_reported_only_when_large():
    small = build_advice({"roc_auc": 0.80}, {"roc_auc": 0.85}, _preds())
    big = build_advice({"roc_auc": 0.70}, {"roc_auc": 0.95}, _preds())
    assert "memorised" not in _text(small)
    assert "memorised" in _text(big) and "fewer predictors" in _text(big)


def test_imbalance_and_threshold_tradeoff_advice():
    adv = build_advice({"roc_auc": 0.8, "recall": 0.95, "specificity": 0.5}, None, _preds(400, prevalence=0.1))
    text = _text(adv)
    assert "Handle Class Imbalance" in text
    assert "decision threshold" in text and "raises more false alarms" in text


def test_multiclass_is_judged_against_the_majority_class():
    y = ["a"] * 60 + ["b"] * 25 + ["c"] * 15
    df = pd.DataFrame({"y_true": y, "y_pred": y})
    weak = build_advice({"accuracy": 0.62}, None, df)
    good = build_advice({"accuracy": 0.90}, None, df)
    assert weak.task == "multiclass" and weak.level == "weak" and "60%" in weak.verdict
    assert good.level == "good"


def test_regression_bands_and_error_relative_to_spread():
    rng = np.random.default_rng(0)
    y = rng.normal(100, 20, 300)
    df = pd.DataFrame({"y_true": y, "y_pred": y + rng.normal(0, 10, 300)})
    good = build_advice({"r2": 0.75, "root_mean_squared_error": 10.0, "mean_absolute_error": 8.0}, None, df)
    bad = build_advice({"r2": -0.2, "root_mean_squared_error": 25.0}, None, df)
    assert good.task == "regression" and good.level == "good"
    assert "explains about 75%" in _text(good) and "standard deviation" in _text(good)
    assert bad.level == "weak" and "worse than simply predicting the average" in bad.verdict


def test_unknown_metrics_and_html_are_safe():
    adv = build_advice({}, None, None)
    assert adv.level == "unknown" and detect_task({}) == "unknown"
    html = advice_html(build_advice({"roc_auc": 0.7}, None, None))
    assert "<ul" in html and "Automatic reading" in html


def test_results_widget_shows_the_advice(qtbot):
    from hamelin.analytics.automl.base import AutoMLResult
    from hamelin.view.widgets.model_results_widget import ModelResultsWidget

    w = ModelResultsWidget()
    qtbot.addWidget(w)
    w.load(AutoMLResult(model_type="x", test_metrics={"roc_auc": 0.9, "accuracy": 0.8},
                        extra={"test_predictions": _preds()}))
    assert "Good result" in w._advice_lbl.text() and not w._advice_lbl.isHidden()
    w.clear()
    assert w._advice_lbl.isHidden()


def test_auc_bootstrap_matches_sklearn_and_is_fast():
    import time

    from sklearn.metrics import roc_auc_score
    from hamelin.analytics.eval_data import bootstrap_auc_ci

    rng = np.random.default_rng(3)
    n = 154
    y = rng.integers(0, 2, n)
    p = np.clip(y * 0.35 + rng.random(n) * 0.65, 0, 1)
    df = pd.DataFrame({"y_true": y, "y_pred": (p > 0.5).astype(int), "y_prob_0": 1 - p, "y_prob_1": p})
    t0 = time.perf_counter()
    auc, lo, hi = bootstrap_auc_ci(df)
    assert time.perf_counter() - t0 < 1.0
    assert auc == pytest.approx(roc_auc_score(y, p))
    assert lo < auc < hi
    assert bootstrap_auc_ci(df.drop(columns=["y_prob_0", "y_prob_1"])) == (None, None, None)


def test_multiclass_outcome_with_a_one_vs_rest_auc_is_not_read_as_binary():
    import pandas as pd
    from hamelin.analytics.result_advice import build_advice, detect_task

    pred = pd.DataFrame({"y_true": ["a", "b", "c", "a", "b", "c"] * 20,
                         "y_pred": ["a", "b", "c", "b", "b", "a"] * 20})
    metrics = {"roc_auc": 0.74, "accuracy": 0.5, "accuracy_micro": 0.5, "hits_at_k": 0.8}
    assert detect_task(metrics, pred) == "multiclass"
    assert detect_task(metrics, None) == "multiclass"        # hits_at_k only exists for categories
    adv = build_advice(metrics, None, pred, 120)
    assert adv.task == "multiclass" and "two groups" not in adv.verdict


def test_multiclass_accuracy_is_the_overall_share_of_correct_predictions():
    from hamelin.analytics.eval_data import overall_accuracy_metrics

    multi = {"accuracy": 0.43, "accuracy_micro": 0.95, "hits_at_k": 0.75}
    assert overall_accuracy_metrics(multi)["accuracy"] == 0.95
    flat = {"test/Class/accuracy/best": 0.43, "test/Class/accuracy_micro/best": 0.95}
    fixed = overall_accuracy_metrics(flat)
    assert fixed["test/Class/accuracy/best"] == 0.95 and fixed["test/Class/accuracy_per_class/best"] == 0.43
    binary = {"accuracy": 0.7, "accuracy_micro": 0.74, "recall": 0.8, "specificity": 0.6}
    assert overall_accuracy_metrics(binary)["accuracy"] == 0.7

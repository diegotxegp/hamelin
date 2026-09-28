import numpy as np
import pandas as pd
import pytest

from hamelin.interface.utils.bootstrap_ci import bootstrap_ci, is_supported, MIN_ROWS


def _classification_df(n=100, seed=0, error_rate=0.2):
    rng = np.random.default_rng(seed)
    y_true = rng.choice(["yes", "no"], size=n, p=[0.3, 0.7])
    flip = rng.random(n) < error_rate
    y_pred = [("no" if t == "yes" else "yes") if f else t for t, f in zip(y_true, flip)]
    return pd.DataFrame({"y_true": y_true, "y_pred": y_pred})


def _regression_df(n=100, seed=0, noise=3.0):
    rng = np.random.default_rng(seed)
    y_true = rng.normal(50, 10, n)
    y_pred = y_true + rng.normal(0, noise, n)
    return pd.DataFrame({"y_true": y_true.astype(str), "y_pred": y_pred.astype(str)})


# is_supported

def test_accuracy_and_regression_metrics_are_supported():
    assert is_supported("accuracy") is True
    assert is_supported("r2") is True
    assert is_supported("root_mean_squared_error") is True
    assert is_supported("mean_absolute_error") is True


def test_roc_auc_is_not_supported():
    # See bootstrap_ci.py's module docstring - y_score is the winning
    # class's confidence, not a fixed positive-class probability, so it
    # can't be bootstrapped into a correct AUC-ROC CI.
    assert is_supported("roc_auc") is False


def test_unknown_metric_is_not_supported():
    assert is_supported("some_custom_metric") is False


# bootstrap_ci - classification

def test_accuracy_point_estimate_matches_plain_computation():
    df = _classification_df()
    point, lo, hi = bootstrap_ci(df, "accuracy")
    expected = (df["y_true"] == df["y_pred"]).mean()
    assert point == pytest.approx(expected)


def test_accuracy_ci_brackets_the_point_estimate():
    df = _classification_df(n=200)
    point, lo, hi = bootstrap_ci(df, "accuracy")
    assert lo < point < hi


def test_tighter_data_gives_a_narrower_ci():
    # A model that's right almost every time should have a narrower CI
    # than one that's frequently wrong, on the same sample size.
    confident_df = _classification_df(n=200, error_rate=0.02)
    noisy_df = _classification_df(n=200, error_rate=0.4)

    _, lo_confident, hi_confident = bootstrap_ci(confident_df, "accuracy")
    _, lo_noisy, hi_noisy = bootstrap_ci(noisy_df, "accuracy")

    assert (hi_confident - lo_confident) < (hi_noisy - lo_noisy)


# bootstrap_ci - regression

def test_r2_and_rmse_and_mae_all_produce_a_ci():
    df = _regression_df(n=150)
    for metric in ("r2", "root_mean_squared_error", "mean_absolute_error"):
        point, lo, hi = bootstrap_ci(df, metric)
        assert point is not None
        assert lo < point < hi


# Edge cases

def test_too_few_rows_returns_point_estimate_without_a_ci():
    df = _classification_df(n=MIN_ROWS - 1)
    point, lo, hi = bootstrap_ci(df, "accuracy")
    assert point is not None
    assert lo is None and hi is None


def test_empty_dataframe_returns_all_none():
    df = pd.DataFrame({"y_true": [], "y_pred": []})
    assert bootstrap_ci(df, "accuracy") == (None, None, None)


def test_unsupported_metric_returns_all_none():
    df = _classification_df()
    assert bootstrap_ci(df, "roc_auc") == (None, None, None)


def test_same_seed_is_reproducible():
    df = _classification_df(n=200)
    result_a = bootstrap_ci(df, "accuracy", seed=7)
    result_b = bootstrap_ci(df, "accuracy", seed=7)
    assert result_a == result_b

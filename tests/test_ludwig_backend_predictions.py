"""
Tests for LudwigBackend._build_predictions_frame - combines the original
rows with Ludwig's per-row predictions into the y_true/y_pred/y_score shape
saved as test_predictions.csv (see TrainingPage._on_training_finished) and
read back by interface/utils/print_confusion_matrix.py instead of
reloading the model to re-run inference.

Doesn't need real Ludwig - predictions is just whatever shape
LudwigModel.evaluate(..., collect_predictions=True) returns, faked here as
a plain DataFrame with Ludwig's own <feature>_predictions/_probability
column-naming convention.
"""
import pandas as pd

from hamelin.analytics.automl.ludwig_backend import _build_predictions_frame


def test_classification_includes_y_score_from_probability_column():
    df = pd.DataFrame({"age": [40, 55, 62], "outcome": ["yes", "no", "no"]})
    predictions = pd.DataFrame({
        "outcome_predictions": ["yes", "yes", "no"],
        "outcome_probability": [0.9, 0.6, 0.8],
        "outcome_probabilities": [[0.1, 0.9], [0.4, 0.6], [0.8, 0.2]],  # combined array, ignored
        "outcome_probabilities_no": [0.1, 0.4, 0.8],
        "outcome_probabilities_yes": [0.9, 0.6, 0.2],
    })

    out = _build_predictions_frame(df, predictions, target="outcome")

    assert list(out["y_true"]) == ["yes", "no", "no"]
    assert list(out["y_pred"]) == ["yes", "yes", "no"]
    assert list(out["y_score"]) == [0.9, 0.6, 0.8]
    # Original columns preserved.
    assert list(out["age"]) == [40, 55, 62]
    # One y_prob_<class> column per class, from Ludwig's own per-class
    # probability columns - not just the winning class's confidence.
    assert list(out["y_prob_no"]) == [0.1, 0.4, 0.8]
    assert list(out["y_prob_yes"]) == [0.9, 0.6, 0.2]


def test_regression_has_no_per_class_probability_columns():
    df = pd.DataFrame({"age": [40, 55], "los_days": [3.2, 5.1]})
    predictions = pd.DataFrame({"los_days_predictions": [3.5, 4.9]})

    out = _build_predictions_frame(df, predictions, target="los_days")

    assert not [c for c in out.columns if c.startswith("y_prob_")]


def test_regression_has_no_score_column_populated():
    df = pd.DataFrame({"age": [40, 55], "los_days": [3.2, 5.1]})
    predictions = pd.DataFrame({"los_days_predictions": [3.5, 4.9]})

    out = _build_predictions_frame(df, predictions, target="los_days")

    assert list(out["y_true"]) == ["3.2", "5.1"]
    assert list(out["y_pred"]) == ["3.5", "4.9"]
    assert out["y_score"].isna().all()


def test_returns_none_on_row_count_mismatch():
    df = pd.DataFrame({"outcome": ["yes", "no", "no"]})
    predictions = pd.DataFrame({"outcome_predictions": ["yes", "no"]})  # one row short

    assert _build_predictions_frame(df, predictions, target="outcome") is None


def test_returns_none_when_no_predictions_column_found():
    df = pd.DataFrame({"outcome": ["yes", "no"]})
    predictions = pd.DataFrame({"something_else": [1, 2]})

    assert _build_predictions_frame(df, predictions, target="outcome") is None


def test_returns_none_when_predictions_is_none():
    df = pd.DataFrame({"outcome": ["yes", "no"]})
    assert _build_predictions_frame(df, None, target="outcome") is None

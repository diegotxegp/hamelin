"""
Tests for the saved-predictions path in print_confusion_matrix.py
(compute_confusion_matrix reads test_predictions.csv instead of reloading
the model and calling predict() live, when that file exists next to the
model - see LudwigBackend.run() / TrainingPage._on_training_finished in
hamelin-v2, which write it).

The live-recompute fallback (no saved CSV, or a Ludwig model to reload)
isn't covered here - it needs a real Ludwig model, out of scope for this
suite the same way the rest of the codebase avoids that dependency in tests.
"""
import pandas as pd

import hamelin.interface.utils.print_confusion_matrix as pcm


def _write_predictions_csv(tmp_path, rows, extra_col=True):
    df = pd.DataFrame(rows)
    csv_path = tmp_path / "test_predictions.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


def test_reads_saved_predictions_instead_of_recomputing(tmp_path, monkeypatch):
    _write_predictions_csv(tmp_path, [
        {"age": 40, "y_true": "yes", "y_pred": "yes", "y_score": 0.9},
        {"age": 55, "y_true": "no", "y_pred": "yes", "y_score": 0.6},
        {"age": 62, "y_true": "no", "y_pred": "no", "y_score": 0.8},
    ])

    # If the live path were hit instead, this would raise / return garbage -
    # asserting it's never called is the real assertion here.
    def _boom(*a, **k):
        raise AssertionError("should not reload the model when a saved CSV exists")
    monkeypatch.setattr(pcm, "_get_ludwig_model", _boom)

    result = pcm.compute_confusion_matrix(str(tmp_path), "unused_dataset.csv")

    assert result["labels"] == ["no", "yes"]
    assert result["matrix"] == [[1, 1], [0, 1]]
    assert len(result["rows"]) == 3


def test_row_detail_has_true_predicted_and_confidence(tmp_path, monkeypatch):
    _write_predictions_csv(tmp_path, [
        {"age": 40, "y_true": "yes", "y_pred": "no", "y_score": 0.55},
    ])
    monkeypatch.setattr(pcm, "_get_ludwig_model", lambda *a, **k: (_ for _ in ()).throw(AssertionError))

    result = pcm.compute_confusion_matrix(str(tmp_path), "unused_dataset.csv")

    row = result["rows"][0]
    assert row["age"] == 40
    assert row["_true_label"] == "yes"
    assert row["_predicted_label"] == "no"
    assert row["_confidence"] == 0.55
    # y_true/y_pred/y_score are folded into the _* fields above, not left
    # duplicated in the row detail.
    assert "y_true" not in row and "y_pred" not in row and "y_score" not in row


def test_missing_score_column_omits_confidence(tmp_path, monkeypatch):
    _write_predictions_csv(tmp_path, [
        {"age": 40, "y_true": "3.2", "y_pred": "3.5"},  # regression: no y_score
    ])
    monkeypatch.setattr(pcm, "_get_ludwig_model", lambda *a, **k: (_ for _ in ()).throw(AssertionError))

    result = pcm.compute_confusion_matrix(str(tmp_path), "unused_dataset.csv")

    assert "_confidence" not in result["rows"][0]


# Decision threshold - reclassifying from saved per-class probabilities
# instead of Ludwig's own saved y_pred (see #3, the confusion-matrix
# threshold slider).

def _write_binary_predictions_csv(tmp_path, rows):
    df = pd.DataFrame(rows)
    csv_path = tmp_path / "test_predictions.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


def test_supports_threshold_adjustment_true_for_binary_with_probabilities(tmp_path):
    _write_binary_predictions_csv(tmp_path, [
        {"y_true": "yes", "y_pred": "yes", "y_prob_yes": 0.7, "y_prob_no": 0.3},
    ])
    assert pcm.supports_threshold_adjustment(str(tmp_path)) is True


def test_supports_threshold_adjustment_false_without_probability_columns(tmp_path):
    _write_predictions_csv(tmp_path, [
        {"age": 40, "y_true": "yes", "y_pred": "yes", "y_score": 0.9},
    ])
    assert pcm.supports_threshold_adjustment(str(tmp_path)) is False


def test_supports_threshold_adjustment_false_for_more_than_two_classes(tmp_path):
    _write_binary_predictions_csv(tmp_path, [
        {"y_true": "a", "y_pred": "a", "y_prob_a": 0.5, "y_prob_b": 0.3, "y_prob_c": 0.2},
    ])
    assert pcm.supports_threshold_adjustment(str(tmp_path)) is False


def test_supports_threshold_adjustment_false_when_no_saved_predictions(tmp_path):
    assert pcm.supports_threshold_adjustment(str(tmp_path)) is False


def test_threshold_reclassifies_from_saved_probabilities(tmp_path, monkeypatch):
    _write_binary_predictions_csv(tmp_path, [
        # Ludwig's own default (50%) called all three "no" - a lower
        # threshold should flip the two closest-to-yes rows to "yes".
        {"y_true": "yes", "y_pred": "no", "y_prob_yes": 0.45, "y_prob_no": 0.55},
        {"y_true": "no", "y_pred": "no", "y_prob_yes": 0.35, "y_prob_no": 0.65},
        {"y_true": "no", "y_pred": "no", "y_prob_yes": 0.10, "y_prob_no": 0.90},
    ])
    monkeypatch.setattr(pcm, "_get_ludwig_model", lambda *a, **k: (_ for _ in ()).throw(AssertionError))

    result = pcm.compute_confusion_matrix(str(tmp_path), "unused.csv", threshold=0.40)

    predicted = [row["_predicted_label"] for row in result["rows"]]
    assert predicted == ["yes", "no", "no"]


def test_no_threshold_uses_saved_y_pred_unchanged(tmp_path, monkeypatch):
    _write_binary_predictions_csv(tmp_path, [
        {"y_true": "yes", "y_pred": "no", "y_prob_yes": 0.45, "y_prob_no": 0.55},
    ])
    monkeypatch.setattr(pcm, "_get_ludwig_model", lambda *a, **k: (_ for _ in ()).throw(AssertionError))

    result = pcm.compute_confusion_matrix(str(tmp_path), "unused.csv")

    assert result["rows"][0]["_predicted_label"] == "no"


def test_threshold_ignored_when_more_than_two_probability_columns(tmp_path, monkeypatch):
    # A stale threshold from a previously-viewed binary model shouldn't
    # break a newly-selected multi-class one - falls back to saved y_pred.
    _write_binary_predictions_csv(tmp_path, [
        {"y_true": "a", "y_pred": "b", "y_prob_a": 0.5, "y_prob_b": 0.3, "y_prob_c": 0.2},
    ])
    monkeypatch.setattr(pcm, "_get_ludwig_model", lambda *a, **k: (_ for _ in ()).throw(AssertionError))

    result = pcm.compute_confusion_matrix(str(tmp_path), "unused.csv", threshold=0.4)

    assert result["rows"][0]["_predicted_label"] == "b"


def test_malformed_saved_csv_falls_back_to_live_path(tmp_path, monkeypatch):
    # Missing the expected y_true/y_pred columns entirely.
    pd.DataFrame({"age": [40, 55]}).to_csv(tmp_path / "test_predictions.csv", index=False)

    called = {}

    def _fake_get_model(model_path):
        called["hit"] = True
        raise RuntimeError("stop here - just confirming the live path was reached")

    monkeypatch.setattr(pcm, "_get_ludwig_model", _fake_get_model)
    monkeypatch.setattr(pd, "read_csv", pd.read_csv)  # dataset_path read still needs to work

    try:
        pcm.compute_confusion_matrix(str(tmp_path), str(tmp_path / "test_predictions.csv"))
    except RuntimeError:
        pass

    assert called.get("hit") is True

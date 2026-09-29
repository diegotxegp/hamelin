"""
Tests for the results/models/ layout, legacy checkpoint migration, the
Evaluation page's model list and the unlabeled-prediction frame shaping.
"""
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from hamelin.core.model_history import ModelHistory, ModelTraining, models_dir
from hamelin.analytics.predictor import (
    build_predictions_frame, required_input_columns, resolve_model_dir,
)


def _fake_model(folder: Path, inputs=("a", "b"), output="y") -> Path:
    folder.mkdir(parents=True)
    (folder / "model_hyperparameters.json").write_text(json.dumps({
        "input_features": [{"name": n, "type": "number"} for n in inputs],
        "output_features": [{"name": output, "type": "binary"}],
    }))
    return folder


def test_legacy_checkpoints_are_migrated(tmp_path):
    legacy = _fake_model(tmp_path / "model_checkpoints" / "run1")
    rec = ModelTraining(target_variable="y", model_type="X", num_samples=1, num_features=2,
                        model_name="run1", checkpoint_path=str(legacy))
    (tmp_path / "model_history.json").write_text(json.dumps([rec.to_dict()]))

    history = ModelHistory(tmp_path)

    new_dir = models_dir(tmp_path) / "run1"
    assert (new_dir / "model_hyperparameters.json").is_file()
    assert not (tmp_path / "model_checkpoints").exists()
    [loaded] = history.list_trainings()
    assert Path(loaded.checkpoint_path) == new_dir
    # idempotent
    ModelHistory(tmp_path)


def test_resolve_model_dir_and_required_columns(tmp_path):
    m = _fake_model(tmp_path / "m", inputs=("age", "bmi"))
    assert resolve_model_dir(m) == m
    assert resolve_model_dir(tmp_path / "nope") is None
    assert required_input_columns(m) == ["age", "bmi"]
    nested = _fake_model(tmp_path / "exp" / "model")
    assert resolve_model_dir(tmp_path / "exp") == nested


def test_build_predictions_frame_without_ground_truth():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    preds = pd.DataFrame({
        "y_predictions": ["yes", "no"],
        "y_probability": [0.9, 0.7],
        "y_probabilities_yes": [0.9, 0.3],
        "y_probabilities_no": [0.1, 0.7],
    })
    out = build_predictions_frame(df, preds)
    assert list(out.columns) == ["a", "b", "predicted_y", "confidence_y", "prob_y_yes", "prob_y_no"]
    assert out["predicted_y"].tolist() == ["yes", "no"]


def test_evaluation_page_lists_models_and_emits_duplicate(qtbot, tmp_path):
    from hamelin.view.pages.evaluation_page import EvaluationPage

    ckpt = _fake_model(models_dir(tmp_path) / "m1")
    (ckpt / "test_predictions.csv").write_text(
        "y_true,y_pred,y_score,y_prob_0,y_prob_1\n0,0,0.8,0.8,0.2\n1,1,0.7,0.3,0.7\n1,0,0.6,0.6,0.4\n0,1,0.6,0.4,0.6\n"
    )
    ModelHistory(tmp_path).add_training(ModelTraining(
        target_variable="y", model_type="Ludwig", num_samples=4, num_features=2,
        test_metrics={"roc_auc": 0.8, "accuracy": 0.5}, model_name="m1",
        checkpoint_path=str(ckpt), timestamp=datetime(2026, 1, 1),
    ))

    page = EvaluationPage()
    qtbot.addWidget(page)
    page.set_project_dir(tmp_path)
    assert page._table.rowCount() == 1
    assert "roc_auc" in page._table.item(0, 4).text()

    page._table.selectRow(0)
    assert page._inspected is not None and page.inspect_panel._pred_df is not None
    assert page._config_btn.isEnabled()

    with qtbot.waitSignal(page.duplicate_requested) as sig:
        page._on_duplicate()
    assert sig.args[0]["new_run_name"] == "m1_copy"
    assert sig.args[0]["config"]["output_features"][0]["name"] == "y"


def test_prediction_page_validates_columns(qtbot, tmp_path):
    from hamelin.view.pages.prediction_page import PredictionPage

    ckpt = _fake_model(models_dir(tmp_path) / "m1", inputs=("a", "b"))
    ModelHistory(tmp_path).add_training(ModelTraining(
        target_variable="y", model_type="Ludwig", num_samples=4, num_features=2,
        model_name="m1", checkpoint_path=str(ckpt),
    ))
    page = PredictionPage()
    qtbot.addWidget(page)
    page.set_project_dir(tmp_path)
    assert page._current_model_dir() == ckpt

    page._df = pd.DataFrame({"a": [1]})
    page._validate()
    assert page._missing == ["b"] and not page.run_btn.isEnabled()

    page._df = pd.DataFrame({"a": [1], "b": [2], "extra": [3]})
    page._validate()
    assert page._missing == [] and page.run_btn.isEnabled()

"""Training page defaults: model name suggestion and the time budget in seconds."""
import pytest

from hamelin.view.pages.training_page import TrainingPage


@pytest.fixture
def page(qtbot):
    p = TrainingPage()
    qtbot.addWidget(p)
    return p


def test_time_budget_is_in_seconds_with_300_default(page):
    assert page.time_budget.value() == 300
    assert page.time_budget.suffix() == ""  # unit lives in the row title, not the field
    assert page.time_budget.minimum() == 100


def test_default_model_name_prefilled(page):
    assert page.model_name_edit.text() == "model_1"


def test_default_name_skips_saved_models_and_follows_refresh(page, tmp_path):
    (tmp_path / "results" / "models" / "model_1").mkdir(parents=True)
    page.set_project_dir(tmp_path)
    assert page.model_name_edit.text() == "model_2"

    (tmp_path / "results" / "models" / "model_2").mkdir()
    page._refresh_default_model_name()  # what refresh_history() does after a run
    assert page.model_name_edit.text() == "model_3"


def test_user_typed_name_is_never_overwritten(page, tmp_path):
    page.model_name_edit.setText("Mortality_v1")
    page.set_project_dir(tmp_path)
    page._refresh_default_model_name()
    assert page.model_name_edit.text() == "Mortality_v1"


def test_cleared_field_gets_a_suggestion_again(page):
    page.model_name_edit.setText("")
    page._refresh_default_model_name()
    assert page.model_name_edit.text() == "model_1"


def test_parallel_trials_default_fits_this_computer(page, monkeypatch):
    import os
    from hamelin.view.pages import training_page as tp

    n = tp.recommended_parallel_trials()
    assert 1 <= n <= 8 and n <= (os.cpu_count() or 2)
    assert page.parallel_trials.value() == n

    class FakeMem:                      # 4 cores but only 3 GB of RAM -> memory is the limit
        total = 3 * 2 ** 30
    import psutil
    monkeypatch.setattr(os, "cpu_count", lambda: 4)
    monkeypatch.setattr(psutil, "virtual_memory", lambda: FakeMem())
    assert tp.recommended_parallel_trials() == 1
    FakeMem.total = 64 * 2 ** 30
    monkeypatch.setattr(os, "cpu_count", lambda: 32)
    assert tp.recommended_parallel_trials() == 8      # capped


def test_settings_snapshot_records_every_training_page_value(page):
    import json

    from hamelin.model.data_model import DataModel
    import pandas as pd

    dm = DataModel()
    dm.df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [1, 0, 1, 0], "y": [0, 1, 0, 1]})
    dm.filepath = None
    page._data_model = dm
    page.model_name_edit.setText("snap")
    page.time_budget.setValue(420)
    page.test_split.setValue(0.25)
    page.random_seed.setValue(7)
    page.early_stop_mode.setCurrentIndex(1)              # stop when no longer improving
    page.early_stop.setValue(9)
    page.parallel_trials.setValue(2)
    page.hyperopt_strategy.setCurrentIndex(1)          # random search
    page.hyperopt_trials.setValue(12)
    page.class_balance_switch.setChecked(True)
    page.missing_strategy_combo.setCurrentIndex(1)     # mean
    snap = page._snapshot_settings("y", ["a", "b"], 4, False)
    json.dumps(snap, default=str)                      # serialisable

    mc = snap["model_configuration"]
    assert (mc["time_budget_seconds"], mc["final_evaluation_holdout"], mc["random_seed"]) == (420, 0.25, 7)
    assert (mc["early_stopping_mode"], mc["early_stopping_patience_rounds"]) == ("patience", 9)
    assert (mc["parallel_trials"], mc["max_iterations"]) == (2, 12)
    assert mc["hyperparameter_search_strategy"] == "random" and mc["handle_class_imbalance"] is True
    assert mc["missing_numeric_values_strategy"] == "fill_with_mean"
    assert snap["outcome"] == "y" and snap["predictors"] == ["a", "b"] and snap["model_name"] == "snap"
    sent = snap["partial_ludwig_config_sent"]
    assert sent["trainer"]["early_stop"] == 9
    assert sent["hyperopt"]["executor"] == {"num_samples": 12, "max_concurrent_trials": 2,
                                            "scheduler": {"type": "fifo"}}
    assert sent["preprocessing"]["oversample_minority"] == 0.5
    assert sent["defaults"]["number"]["preprocessing"]["missing_value_strategy"] == "fill_with_mean"


def test_early_stopping_modes_map_to_the_right_ludwig_settings(page):
    from hamelin.analytics.automl.ludwig_backend import _fields_to_user_config

    assert not page.early_stop.isEnabled()                       # automatic: no patience field
    auto = _fields_to_user_config(page._collect_config_fields(), "y")
    assert "early_stop" not in auto.get("trainer", {})           # Ludwig would only override it
    assert "scheduler" not in auto["hyperopt"]["executor"]

    page.early_stop_mode.setCurrentIndex(1)
    assert page.early_stop.isEnabled()
    page.early_stop.setValue(8)
    pat = _fields_to_user_config(page._collect_config_fields(), "y")
    assert pat["trainer"]["early_stop"] == 8
    assert pat["hyperopt"]["executor"]["scheduler"] == {"type": "fifo"}

    page.early_stop_mode.setCurrentIndex(2)
    assert not page.early_stop.isEnabled()
    off = _fields_to_user_config(page._collect_config_fields(), "y")
    assert off["trainer"]["early_stop"] == -1
    assert off["hyperopt"]["executor"]["scheduler"] == {"type": "fifo"}


def test_max_iterations_minimum_and_default_are_10(page):
    assert page.hyperopt_trials.minimum() == 10 and page.hyperopt_trials.value() == 10

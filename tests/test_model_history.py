"""
Model History System — Unit Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Covers ModelTraining (dataclass) and ModelHistory (manager) including:
- Serialisation round-trip
- Add / list / get / delete operations
- Persistence across instances
- get_best() with higher / lower is better
- to_dataframe() shape and content
- Edge cases (empty history, missing metric, duplicate ids)

Author: GitHub Copilot AI
Date: February 20, 2026
Sprint: 3, Day 23
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from hamelin.core.model_history import ModelHistory, ModelTraining


# ============================================================================
# Fixtures & helpers
# ============================================================================

def _make_training(
    target: str = "outcome",
    model_type: str = "RandomForest",
    accuracy: float = 0.85,
    loss: float = 0.15,
    samples: int = 100,
    features: int = 20,
    time_s: float = 30.0,
    notes: str = "",
) -> ModelTraining:
    """Return a fully populated ModelTraining instance."""
    return ModelTraining(
        target_variable=target,
        model_type=model_type,
        num_samples=samples,
        num_features=features,
        train_metrics={"accuracy": accuracy + 0.02, "loss": loss - 0.02},
        val_metrics={"accuracy": accuracy + 0.01, "loss": loss - 0.01},
        test_metrics={"accuracy": accuracy, "loss": loss},
        training_time_seconds=time_s,
        num_trials=10,
        hyperparameters={"n_estimators": 100, "max_depth": 5},
        dataset_version="v1.0",
        notes=notes,
    )


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """A temporary project directory."""
    d = tmp_path / "TestProject"
    d.mkdir()
    return d


@pytest.fixture
def history(project_dir: Path) -> ModelHistory:
    """Fresh ModelHistory backed by a temp project dir."""
    return ModelHistory(project_dir)


# ============================================================================
# ModelTraining — dataclass tests
# ============================================================================

class TestModelTraining:
    """Unit tests for the ModelTraining dataclass."""

    def test_auto_id_generated(self):
        t = _make_training()
        assert t.model_id and len(t.model_id) == 36  # UUID4 format

    def test_two_instances_have_different_ids(self):
        t1 = _make_training()
        t2 = _make_training()
        assert t1.model_id != t2.model_id

    def test_timestamp_is_recent_datetime(self):
        before = datetime.utcnow()
        t = _make_training()
        after = datetime.utcnow()
        assert before <= t.timestamp <= after

    def test_to_dict_serialisable(self):
        t = _make_training()
        d = t.to_dict()
        # Should be JSON-serialisable without errors
        json.dumps(d)
        assert d["model_type"] == "RandomForest"
        assert isinstance(d["timestamp"], str)

    def test_from_dict_round_trip(self):
        original = _make_training(accuracy=0.91, notes="Test run")
        restored = ModelTraining.from_dict(original.to_dict())
        assert restored.model_id == original.model_id
        assert restored.model_type == original.model_type
        assert restored.test_metrics["accuracy"] == pytest.approx(0.91)
        assert restored.notes == "Test run"
        assert isinstance(restored.timestamp, datetime)

    def test_best_metric_test_split(self):
        t = _make_training(accuracy=0.88, loss=0.12)
        assert t.best_metric("accuracy", "test") == pytest.approx(0.88)
        assert t.best_metric("loss", "test") == pytest.approx(0.12)

    def test_best_metric_train_split(self):
        t = _make_training(accuracy=0.88)
        # train_metrics = accuracy + 0.02 = 0.90
        assert t.best_metric("accuracy", "train") == pytest.approx(0.90)

    def test_best_metric_missing_returns_none(self):
        t = _make_training()
        assert t.best_metric("roc_auc", "test") is None

    def test_model_name_defaults_to_empty_string(self):
        t = _make_training()
        assert t.model_name == ""

    def test_model_name_round_trips_through_to_dict_from_dict(self):
        original = _make_training()
        original.model_name = "LPP_risk_v1"
        restored = ModelTraining.from_dict(original.to_dict())
        assert restored.model_name == "LPP_risk_v1"

    def test_from_dict_defaults_model_name_for_old_records_without_it(self):
        # Records saved before model_name existed have no such key in their
        # JSON - from_dict must still load them instead of raising.
        original = _make_training()
        d = original.to_dict()
        del d["model_name"]
        restored = ModelTraining.from_dict(d)
        assert restored.model_name == ""

    def test_default_hyperparameters_is_empty_dict(self):
        t = ModelTraining(
            target_variable="x",
            model_type="Linear",
            num_samples=50,
            num_features=5,
        )
        assert t.hyperparameters == {}

    def test_default_metrics_are_empty_dicts(self):
        t = ModelTraining(
            target_variable="x",
            model_type="Linear",
            num_samples=50,
            num_features=5,
        )
        assert t.train_metrics == {}
        assert t.val_metrics == {}
        assert t.test_metrics == {}


# ============================================================================
# ModelHistory — manager tests
# ============================================================================

class TestModelHistoryInit:
    """Initialisation and file handling."""

    def test_empty_history_on_new_dir(self, project_dir: Path):
        h = ModelHistory(project_dir)
        assert len(h) == 0

    def test_history_file_not_created_until_add(self, project_dir: Path):
        ModelHistory(project_dir)
        assert not (project_dir / "model_history.json").exists()

    def test_file_created_on_first_add(self, history: ModelHistory, project_dir: Path):
        history.add_training(_make_training())
        assert (project_dir / "model_history.json").exists()


class TestModelHistoryAdd:
    """add_training() behaviour."""

    def test_add_increases_count(self, history: ModelHistory):
        history.add_training(_make_training())
        assert len(history) == 1

    def test_add_multiple(self, history: ModelHistory):
        for _ in range(5):
            history.add_training(_make_training())
        assert len(history) == 5


class TestModelHistoryPersistence:
    """Records survive across ModelHistory instances."""

    def test_persists_across_instances(self, project_dir: Path):
        h1 = ModelHistory(project_dir)
        t = _make_training(notes="persistent")
        h1.add_training(t)

        h2 = ModelHistory(project_dir)
        assert len(h2) == 1
        assert h2.list_trainings()[0].notes == "persistent"

    def test_multiple_records_persist(self, project_dir: Path):
        h1 = ModelHistory(project_dir)
        for i in range(3):
            h1.add_training(_make_training(accuracy=0.80 + i * 0.05))

        h2 = ModelHistory(project_dir)
        assert len(h2) == 3

    def test_json_file_is_valid_list(self, project_dir: Path):
        h = ModelHistory(project_dir)
        h.add_training(_make_training())
        raw = json.loads((project_dir / "model_history.json").read_text())
        assert isinstance(raw, list)
        assert len(raw) == 1
        assert "model_id" in raw[0]


class TestModelHistoryList:
    """list_trainings() ordering."""

    def test_most_recent_first(self, project_dir: Path):
        h = ModelHistory(project_dir)
        t1 = _make_training(notes="first")
        t1.timestamp = datetime(2026, 1, 1)
        t2 = _make_training(notes="second")
        t2.timestamp = datetime(2026, 2, 1)
        h.add_training(t1)
        h.add_training(t2)

        ordered = h.list_trainings()
        assert ordered[0].notes == "second"
        assert ordered[1].notes == "first"

    def test_empty_list_when_no_records(self, history: ModelHistory):
        assert history.list_trainings() == []


class TestModelHistoryGet:
    """get_training() by model_id."""

    def test_get_existing(self, history: ModelHistory):
        t = _make_training()
        history.add_training(t)
        found = history.get_training(t.model_id)
        assert found is not None
        assert found.model_id == t.model_id

    def test_get_nonexistent_returns_none(self, history: ModelHistory):
        assert history.get_training("nonexistent-id") is None


class TestModelHistoryDelete:
    """delete_training() behaviour."""

    def test_delete_existing(self, history: ModelHistory):
        t = _make_training()
        history.add_training(t)
        result = history.delete_training(t.model_id)
        assert result is True
        assert len(history) == 0

    def test_delete_persists(self, project_dir: Path):
        h1 = ModelHistory(project_dir)
        t = _make_training()
        h1.add_training(t)
        h1.delete_training(t.model_id)

        h2 = ModelHistory(project_dir)
        assert len(h2) == 0

    def test_delete_nonexistent_returns_false(self, history: ModelHistory):
        assert history.delete_training("no-such-id") is False

    def test_delete_only_removes_target(self, history: ModelHistory):
        t1 = _make_training(notes="keep")
        t2 = _make_training(notes="delete")
        history.add_training(t1)
        history.add_training(t2)
        history.delete_training(t2.model_id)
        assert len(history) == 1
        assert history.list_trainings()[0].notes == "keep"


class TestModelHistoryGetBest:
    """get_best() logic."""

    def test_best_accuracy_higher_is_better(self, history: ModelHistory):
        history.add_training(_make_training(accuracy=0.70))
        history.add_training(_make_training(accuracy=0.90))
        history.add_training(_make_training(accuracy=0.80))
        best = history.get_best("accuracy", higher_is_better=True)
        assert best is not None
        assert best.test_metrics["accuracy"] == pytest.approx(0.90)

    def test_best_loss_lower_is_better(self, history: ModelHistory):
        history.add_training(_make_training(loss=0.30))
        history.add_training(_make_training(loss=0.10))
        history.add_training(_make_training(loss=0.20))
        best = history.get_best("loss", higher_is_better=False)
        assert best is not None
        assert best.test_metrics["loss"] == pytest.approx(0.10)

    def test_get_best_returns_none_when_empty(self, history: ModelHistory):
        assert history.get_best("accuracy") is None

    def test_get_best_returns_none_when_metric_absent(self, history: ModelHistory):
        history.add_training(_make_training())  # has accuracy, loss — not roc_auc
        assert history.get_best("roc_auc") is None

    def test_get_best_train_split(self, history: ModelHistory):
        t = _make_training(accuracy=0.85)  # train = 0.87
        history.add_training(t)
        best = history.get_best("accuracy", split="train")
        assert best is not None
        assert best.train_metrics["accuracy"] == pytest.approx(0.87)


class TestModelHistoryDataFrame:
    """to_dataframe() output."""

    def test_returns_empty_dataframe_when_no_records(self, history: ModelHistory):
        df = history.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_dataframe_row_count(self, history: ModelHistory):
        for _ in range(4):
            history.add_training(_make_training())
        df = history.to_dataframe()
        assert len(df) == 4

    def test_dataframe_has_expected_columns(self, history: ModelHistory):
        history.add_training(_make_training(accuracy=0.88))
        df = history.to_dataframe()
        expected = {"model_id", "timestamp", "model_type", "target_variable",
                    "num_samples", "num_features", "training_time_s",
                    "test_accuracy"}
        assert expected.issubset(set(df.columns))

    def test_dataframe_values_correct(self, history: ModelHistory):
        t = _make_training(model_type="XGBoost", accuracy=0.92, samples=150)
        history.add_training(t)
        df = history.to_dataframe()
        row = df.iloc[0]
        assert row["model_type"] == "XGBoost"
        assert row["num_samples"] == 150
        assert row["test_accuracy"] == pytest.approx(0.92)

    def test_dataframe_sorted_most_recent_first(self, project_dir: Path):
        h = ModelHistory(project_dir)
        t1 = _make_training(notes="old")
        t1.timestamp = datetime(2026, 1, 1)
        t2 = _make_training(notes="new")
        t2.timestamp = datetime(2026, 3, 1)
        h.add_training(t1)
        h.add_training(t2)
        df = h.to_dataframe()
        assert df.iloc[0]["timestamp"] > df.iloc[1]["timestamp"]


# ============================================================================
# Edge cases
# ============================================================================

class TestModelHistoryEdgeCases:
    """Edge cases and robustness."""

    def test_repr_contains_record_count(self, history: ModelHistory):
        assert "records=0" in repr(history)
        history.add_training(_make_training())
        assert "records=1" in repr(history)

    def test_add_then_reload_multiple_times(self, project_dir: Path):
        for i in range(3):
            h = ModelHistory(project_dir)
            h.add_training(_make_training(accuracy=0.80 + i * 0.05))
        final = ModelHistory(project_dir)
        assert len(final) == 3

    def test_training_with_empty_metrics(self, history: ModelHistory):
        t = ModelTraining(
            target_variable="outcome",
            model_type="Baseline",
            num_samples=10,
            num_features=2,
        )
        history.add_training(t)
        loaded = history.get_training(t.model_id)
        assert loaded.test_metrics == {}

    def test_hyperparameters_preserved(self, project_dir: Path):
        h1 = ModelHistory(project_dir)
        params = {"n_estimators": 200, "learning_rate": 0.01, "nested": {"a": 1}}
        t = _make_training()
        t.hyperparameters = params
        h1.add_training(t)

        h2 = ModelHistory(project_dir)
        reloaded = h2.get_training(t.model_id)
        assert reloaded.hyperparameters == params

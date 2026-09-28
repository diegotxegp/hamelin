"""
LudwigTrainer (Orchestrator) — Unit Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests for the LudwigTrainer orchestrator, the _run_backend pure helper,
and (import-level) for LudwigTrainerWorker.

All AutoML work is mocked via backend injection — no real Ludwig runs.
Helper function and registry tests live in test_automl_backends.py.

Note on LudwigTrainerWorker:
  The worker is a QThread subclass and requires PySide6 + a running event
  loop for full integration testing. Following the project convention
  ("tests are pure-backend, no PySide6"), only the *pure* extraction
  (_run_backend) is tested at unit level. The Qt signal wiring is covered
  by manual QA when running the app.

Author: GitHub Copilot AI
Date: February 20, 2026 · Day 24 (orchestrator) · Day 28 (_run_backend worker)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from hamelin.analytics.automl.base import AutoMLBackend, AutoMLResult
from hamelin.analytics.ludwig_trainer import (
    LudwigTrainer,
    LudwigTrainerWorker,
    _dataset_hash,
    _run_backend,
)
from hamelin.core.model_history import ModelHistory, ModelTraining


# ============================================================================
# Fixtures & helpers
# ============================================================================

@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "age": [45, 60, 35, 52, 47, 63, 38, 55],
        "sex": [0, 1, 0, 1, 0, 1, 0, 1],
        "bmi": [25.1, 30.4, 22.8, 27.5, 24.3, 31.2, 23.7, 28.9],
        "outcome": [0, 1, 0, 1, 0, 1, 0, 1],
    })


@pytest.fixture
def data_model(sample_df: pd.DataFrame):
    dm = MagicMock()
    dm.df = sample_df
    return dm


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    d = tmp_path / "UPS"
    d.mkdir()
    return d


def _make_mock_backend(
    accuracy: float = 0.87,
    loss: float = 0.13,
    num_trials: int = 5,
    model_type: str = "Ludwig/Tabnet",
) -> AutoMLBackend:
    """Return a mock AutoMLBackend that returns a preset AutoMLResult."""
    backend = MagicMock(spec=AutoMLBackend)
    backend.name = "mock"
    backend.run.return_value = AutoMLResult(
        model_type=model_type,
        test_metrics={"accuracy": accuracy, "loss": loss},
        training_time_seconds=1.5,
        num_trials=num_trials,
        hyperparameters={"n_estimators": 100},
    )
    return backend


@pytest.fixture
def mock_backend() -> AutoMLBackend:
    return _make_mock_backend()


@pytest.fixture
def trainer(project_dir, data_model, mock_backend) -> LudwigTrainer:
    return LudwigTrainer(project_dir, data_model, backend=mock_backend)


# ============================================================================
# _dataset_hash (still in ludwig_trainer — dataset util, not backend-specific)
# ============================================================================

class TestDatasetHash:
    def test_returns_12_char_hex(self, sample_df):
        h = _dataset_hash(sample_df)
        assert len(h) == 12
        assert all(c in "0123456789abcdef" for c in h)

    def test_same_df_same_hash(self, sample_df):
        assert _dataset_hash(sample_df) == _dataset_hash(sample_df.copy())

    def test_different_df_different_hash(self, sample_df):
        modified = sample_df.copy()
        modified.loc[0, "age"] = 99
        assert _dataset_hash(sample_df) != _dataset_hash(modified)


# ============================================================================
# LudwigTrainer — init
# ============================================================================

class TestLudwigTrainerInit:
    def test_init_ok(self, project_dir, data_model, mock_backend):
        t = LudwigTrainer(project_dir, data_model, backend=mock_backend)
        assert t.project_dir == project_dir

    def test_backend_property(self, trainer, mock_backend):
        assert trainer.backend is mock_backend

    def test_raises_if_no_dataframe(self, project_dir, mock_backend):
        dm = MagicMock()
        dm.df = None
        with pytest.raises(ValueError, match="DataFrame"):
            LudwigTrainer(project_dir, dm, backend=mock_backend)

    def test_raises_if_data_model_is_none(self, project_dir, mock_backend):
        with pytest.raises((ValueError, AttributeError)):
            LudwigTrainer(project_dir, None, backend=mock_backend)

    def test_repr_contains_project_name(self, trainer, project_dir):
        r = repr(trainer)
        assert project_dir.name in r

    def test_repr_contains_backend_name(self, trainer):
        assert "mock" in repr(trainer)

    def test_repr_contains_data_status(self, trainer):
        assert "loaded" in repr(trainer)

    def test_last_record_initially_none(self, trainer):
        assert trainer.last_record is None


# ============================================================================
# LudwigTrainer — train()
# ============================================================================

class TestLudwigTrainerTrain:
    def test_returns_model_training_record(self, trainer):
        record = trainer.train("outcome")
        assert isinstance(record, ModelTraining)

    def test_record_target_variable(self, trainer):
        record = trainer.train("outcome")
        assert record.target_variable == "outcome"

    def test_record_model_type_from_backend(self, trainer):
        record = trainer.train("outcome")
        assert record.model_type == "Ludwig/Tabnet"

    def test_record_num_samples(self, trainer, sample_df):
        record = trainer.train("outcome")
        assert record.num_samples == len(sample_df)

    def test_record_num_features_all(self, trainer):
        # 4 columns - 1 target = 3
        record = trainer.train("outcome")
        assert record.num_features == 3

    def test_record_num_features_explicit(self, project_dir, data_model):
        backend = _make_mock_backend()
        t = LudwigTrainer(project_dir, data_model, backend=backend)
        record = t.train("outcome", features=["age", "bmi"])
        assert record.num_features == 2

    def test_record_num_trials(self, project_dir, data_model):
        backend = _make_mock_backend(num_trials=9)
        t = LudwigTrainer(project_dir, data_model, backend=backend)
        record = t.train("outcome")
        assert record.num_trials == 9

    def test_record_test_metrics(self, project_dir, data_model):
        backend = _make_mock_backend(accuracy=0.93)
        t = LudwigTrainer(project_dir, data_model, backend=backend)
        record = t.train("outcome")
        assert record.test_metrics["accuracy"] == pytest.approx(0.93)

    def test_record_has_dataset_version(self, trainer):
        record = trainer.train("outcome")
        assert len(record.dataset_version) == 12

    def test_record_notes_preserved(self, trainer):
        record = trainer.train("outcome", notes="first run")
        assert record.notes == "first run"

    def test_last_record_updated(self, trainer):
        record = trainer.train("outcome")
        assert trainer.last_record is record

    def test_backend_run_called_once(self, trainer, mock_backend):
        trainer.train("outcome")
        mock_backend.run.assert_called_once()

    def test_backend_receives_correct_target(self, trainer, mock_backend):
        trainer.train("outcome")
        _, kwargs = mock_backend.run.call_args
        assert kwargs.get("target") == "outcome" or mock_backend.run.call_args[0][1] == "outcome"

    def test_backend_kwargs_forwarded(self, project_dir, data_model):
        backend = _make_mock_backend()
        t = LudwigTrainer(project_dir, data_model, backend=backend)
        t.train("outcome", tune_for_memory=True)
        call_kwargs = backend.run.call_args[1]
        assert call_kwargs.get("tune_for_memory") is True

    def test_record_persisted_to_history(self, trainer, project_dir):
        record = trainer.train("outcome")
        history = ModelHistory(project_dir)
        assert len(history) == 1
        assert history.get_training(record.model_id) is not None

    def test_multiple_trainings_accumulate(self, project_dir, data_model):
        b1 = _make_mock_backend(accuracy=0.80)
        b2 = _make_mock_backend(accuracy=0.85)
        t1 = LudwigTrainer(project_dir, data_model, backend=b1)
        t2 = LudwigTrainer(project_dir, data_model, backend=b2)
        t1.train("outcome")
        t2.train("outcome")
        history = ModelHistory(project_dir)
        assert len(history) == 2

    def test_raises_if_target_not_in_df(self, trainer):
        with pytest.raises(ValueError, match="Target column"):
            trainer.train("nonexistent_col")

    def test_raises_if_feature_not_in_df(self, trainer):
        with pytest.raises(ValueError, match="Feature columns"):
            trainer.train("outcome", features=["age", "ghost_column"])


# ============================================================================
# LudwigTrainer — get_history()
# ============================================================================

class TestLudwigTrainerGetHistory:
    def test_returns_model_history(self, trainer):
        assert isinstance(trainer.get_history(), ModelHistory)

    def test_empty_initially(self, trainer):
        assert len(trainer.get_history()) == 0

    def test_reflects_training(self, trainer):
        trainer.train("outcome")
        assert len(trainer.get_history()) == 1


# ============================================================================
# LudwigTrainer — backend swapping
# ============================================================================

class TestBackendSwapping:
    def test_different_backends_produce_different_model_types(
        self, project_dir, data_model
    ):
        b_ludwig = _make_mock_backend(model_type="Ludwig/Tabnet")
        b_other = _make_mock_backend(model_type="AutoGluon/CatBoost")

        t1 = LudwigTrainer(project_dir, data_model, backend=b_ludwig)
        t2 = LudwigTrainer(project_dir, data_model, backend=b_other)

        r1 = t1.train("outcome")
        r2 = t2.train("outcome")

        assert r1.model_type == "Ludwig/Tabnet"
        assert r2.model_type == "AutoGluon/CatBoost"

    def test_history_contains_both_backends(self, project_dir, data_model):
        b1 = _make_mock_backend(model_type="Ludwig/Tabnet")
        b2 = _make_mock_backend(model_type="FLAML/LightGBM")
        LudwigTrainer(project_dir, data_model, backend=b1).train("outcome")
        LudwigTrainer(project_dir, data_model, backend=b2).train("outcome")

        history = ModelHistory(project_dir)
        types = {r.model_type for r in history.list_trainings()}
        assert "Ludwig/Tabnet" in types
        assert "FLAML/LightGBM" in types


# ============================================================================
# _run_backend — pure synchronous helper (no PySide6)
# ============================================================================

class TestRunBackend:
    """Tests for the pure _run_backend() function extracted from the worker.

    No Qt / PySide6 required — these are ordinary unit tests.
    """

    def test_returns_automl_result(self, sample_df, mock_backend):
        result = _run_backend(sample_df, "outcome", None, 60, mock_backend)
        assert isinstance(result, AutoMLResult)

    def test_result_model_type(self, sample_df, mock_backend):
        result = _run_backend(sample_df, "outcome", None, 60, mock_backend)
        assert result.model_type == "Ludwig/Tabnet"

    def test_result_metrics(self, sample_df):
        backend = _make_mock_backend(accuracy=0.92)
        result = _run_backend(sample_df, "outcome", None, 60, backend)
        assert result.test_metrics["accuracy"] == pytest.approx(0.92)

    def test_features_forwarded(self, sample_df, mock_backend):
        _run_backend(sample_df, "outcome", ["age", "bmi"], 60, mock_backend)
        _, kwargs = mock_backend.run.call_args
        assert kwargs.get("features") == ["age", "bmi"] or \
               mock_backend.run.call_args[0][2] == ["age", "bmi"]

    def test_time_limit_forwarded(self, sample_df, mock_backend):
        _run_backend(sample_df, "outcome", None, 300, mock_backend)
        _, kwargs = mock_backend.run.call_args
        assert kwargs.get("time_limit_s") == 300 or \
               mock_backend.run.call_args[0][3] == 300

    def test_raises_on_backend_error(self, sample_df):
        bad_backend = MagicMock(spec=AutoMLBackend)
        bad_backend.run.side_effect = RuntimeError("Ludwig exploded")
        with pytest.raises(RuntimeError, match="Ludwig exploded"):
            _run_backend(sample_df, "outcome", None, 60, bad_backend)

    def test_cancelled_before_backend_raises(self, sample_df, mock_backend):
        """cancelled_fn returning True before the backend call raises RuntimeError."""
        with pytest.raises(RuntimeError, match="cancelled"):
            _run_backend(
                sample_df, "outcome", None, 60, mock_backend,
                cancelled_fn=lambda: True,
            )

    def test_cancelled_before_backend_never_calls_run(self, sample_df, mock_backend):
        try:
            _run_backend(
                sample_df, "outcome", None, 60, mock_backend,
                cancelled_fn=lambda: True,
            )
        except RuntimeError:
            pass
        mock_backend.run.assert_not_called()

    def test_not_cancelled_calls_run(self, sample_df, mock_backend):
        _run_backend(
            sample_df, "outcome", None, 60, mock_backend,
            cancelled_fn=lambda: False,
        )
        mock_backend.run.assert_called_once()

    def test_none_cancelled_fn_still_works(self, sample_df, mock_backend):
        result = _run_backend(sample_df, "outcome", None, 60, mock_backend, cancelled_fn=None)
        assert isinstance(result, AutoMLResult)

    def test_backend_none_uses_registry(self, sample_df):
        """When backend=None _run_backend fetches from registry."""
        mock_b = _make_mock_backend(accuracy=0.77)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "hamelin.analytics.automl.registry.get_backend",
                lambda: mock_b,
            )
            result = _run_backend(sample_df, "outcome", None, 60, backend=None)
        assert isinstance(result, AutoMLResult)


# ============================================================================
# LudwigTrainerWorker — import + stop() flag (no Qt event loop)
# ============================================================================

class TestLudwigTrainerWorkerImport:
    """Minimal checks that don't require a running Qt event loop."""

    def test_class_importable(self):
        assert LudwigTrainerWorker is not None

    def test_stop_sets_cancelled(self, sample_df, mock_backend):
        """stop() must set _cancelled before the worker is started."""
        worker = LudwigTrainerWorker(
            df=sample_df,
            target="outcome",
            features=None,
            time_limit_s=60,
            backend=mock_backend,
        )
        assert worker._cancelled is False
        worker.stop()
        assert worker._cancelled is True

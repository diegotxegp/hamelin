"""
HistoryVisualizer — Unit Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests cover timeline_data, comparison_table, best_by_metric,
metric_trend, summary_stats, and all edge cases (empty history,
missing metrics, heterogeneous metric sets).

Author: GitHub Copilot AI
Date: February 23, 2026
Sprint: 3, Day 25
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from hamelin.analytics.history_visualizer import HistoryVisualizer
from hamelin.core.model_history import ModelHistory, ModelTraining


# ============================================================================
# Helpers
# ============================================================================

def _training(
    *,
    target: str = "outcome",
    model_type: str = "Ludwig/Tabnet",
    accuracy: float | None = 0.85,
    roc_auc: float | None = None,
    loss: float | None = None,
    num_samples: int = 100,
    num_features: int = 5,
    num_trials: int = 3,
    training_time: float = 10.0,
    notes: str = "",
    days_ago: int = 0,
) -> ModelTraining:
    """Build a ModelTraining for testing."""
    test_metrics: dict = {}
    if accuracy is not None:
        test_metrics["accuracy"] = accuracy
    if roc_auc is not None:
        test_metrics["roc_auc"] = roc_auc
    if loss is not None:
        test_metrics["loss"] = loss

    t = ModelTraining(
        target_variable=target,
        model_type=model_type,
        num_samples=num_samples,
        num_features=num_features,
        test_metrics=test_metrics,
        num_trials=num_trials,
        training_time_seconds=training_time,
        notes=notes,
    )
    if days_ago:
        t.timestamp = datetime.utcnow() - timedelta(days=days_ago)
    return t


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    d = tmp_path / "UPS"
    d.mkdir()
    return d


@pytest.fixture
def empty_history(project_dir: Path) -> ModelHistory:
    return ModelHistory(project_dir)


@pytest.fixture
def history_with_three(project_dir: Path) -> ModelHistory:
    h = ModelHistory(project_dir)
    h.add_training(_training(accuracy=0.80, days_ago=2))
    h.add_training(_training(accuracy=0.85, days_ago=1))
    h.add_training(_training(accuracy=0.90, days_ago=0))
    return h


# ============================================================================
# HistoryVisualizer — init
# ============================================================================

class TestHistoryVisualizerInit:
    def test_instantiates_ok(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        assert viz is not None

    def test_stores_history_reference(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        assert viz._history is empty_history


# ============================================================================
# timeline_data
# ============================================================================

class TestTimelineData:
    def test_empty_history_returns_dataframe(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        df = viz.timeline_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_empty_has_expected_columns(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        df = viz.timeline_data()
        for col in HistoryVisualizer.TIMELINE_COLUMNS:
            assert col in df.columns

    def test_empty_has_metric_column(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        df = viz.timeline_data(metric="accuracy")
        assert "test_accuracy" in df.columns

    def test_row_count_matches_history(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        assert len(viz.timeline_data()) == 3

    def test_sorted_ascending_by_timestamp(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.timeline_data()
        timestamps = df["timestamp"].tolist()
        assert timestamps == sorted(timestamps)

    def test_accuracy_column_populated(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.timeline_data(metric="accuracy")
        assert df["test_accuracy"].notna().all()

    def test_accuracy_values_correct(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.timeline_data(metric="accuracy")
        # sorted ascending → 0.80, 0.85, 0.90
        assert list(df["test_accuracy"]) == pytest.approx([0.80, 0.85, 0.90])

    def test_missing_metric_returns_nan(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.timeline_data(metric="rmse")
        assert df["test_rmse"].isna().all()

    def test_train_split_uses_train_metrics(self, project_dir):
        h = ModelHistory(project_dir)
        t = ModelTraining(
            target_variable="y",
            model_type="M",
            num_samples=10,
            num_features=2,
            train_metrics={"accuracy": 0.99},
            test_metrics={"accuracy": 0.70},
        )
        h.add_training(t)
        viz = HistoryVisualizer(h)
        df = viz.timeline_data(metric="accuracy", split="train")
        assert df["train_accuracy"].iloc[0] == pytest.approx(0.99)

    def test_timestamp_is_datetime_dtype(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.timeline_data()
        assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


# ============================================================================
# comparison_table
# ============================================================================

class TestComparisonTable:
    def test_empty_returns_dataframe(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        df = viz.comparison_table()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_empty_has_fixed_columns(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        df = viz.comparison_table()
        for col in ["model_id", "timestamp", "model_type", "target_variable"]:
            assert col in df.columns

    def test_row_count_matches_history(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        assert len(viz.comparison_table()) == 3

    def test_accuracy_column_present(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.comparison_table()
        assert "accuracy" in df.columns

    def test_heterogeneous_metrics_union(self, project_dir):
        """Records with different metric keys → union of all keys."""
        h = ModelHistory(project_dir)
        h.add_training(_training(accuracy=0.80, roc_auc=0.88))
        h.add_training(_training(accuracy=0.85, loss=0.15))
        viz = HistoryVisualizer(h)
        df = viz.comparison_table()
        assert "accuracy" in df.columns
        assert "roc_auc" in df.columns
        assert "loss" in df.columns

    def test_missing_metric_is_nan(self, project_dir):
        h = ModelHistory(project_dir)
        h.add_training(_training(accuracy=0.80, roc_auc=0.88))
        h.add_training(_training(accuracy=0.85))  # no roc_auc
        viz = HistoryVisualizer(h)
        df = viz.comparison_table()
        assert pd.isna(df.loc[df["accuracy"] == 0.85, "roc_auc"].iloc[0])

    def test_metric_columns_sorted_alphabetically(self, project_dir):
        h = ModelHistory(project_dir)
        h.add_training(_training(accuracy=0.80, roc_auc=0.88, loss=0.12))
        viz = HistoryVisualizer(h)
        df = viz.comparison_table()
        fixed = {"model_id", "timestamp", "model_type", "target_variable"}
        metric_cols = [c for c in df.columns if c not in fixed]
        assert metric_cols == sorted(metric_cols)

    def test_sorted_ascending_by_timestamp(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.comparison_table()
        ts = df["timestamp"].tolist()
        assert ts == sorted(ts)


# ============================================================================
# best_by_metric
# ============================================================================

class TestBestByMetric:
    def test_returns_none_on_empty_history(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        assert viz.best_by_metric("accuracy") is None

    def test_returns_modeltraining(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        result = viz.best_by_metric("accuracy")
        assert isinstance(result, ModelTraining)

    def test_best_accuracy_is_highest(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        best = viz.best_by_metric("accuracy")
        assert best.test_metrics["accuracy"] == pytest.approx(0.90)

    def test_lower_is_better_flag(self, project_dir):
        h = ModelHistory(project_dir)
        h.add_training(ModelTraining(
            target_variable="y", model_type="M",
            num_samples=10, num_features=2,
            test_metrics={"loss": 0.30},
        ))
        h.add_training(ModelTraining(
            target_variable="y", model_type="M",
            num_samples=10, num_features=2,
            test_metrics={"loss": 0.10},
        ))
        viz = HistoryVisualizer(h)
        best = viz.best_by_metric("loss", higher_is_better=False)
        assert best.test_metrics["loss"] == pytest.approx(0.10)

    def test_returns_none_when_metric_absent(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        assert viz.best_by_metric("rmse") is None

    def test_single_record_returns_that_record(self, project_dir):
        h = ModelHistory(project_dir)
        t = _training(accuracy=0.77)
        h.add_training(t)
        viz = HistoryVisualizer(h)
        best = viz.best_by_metric("accuracy")
        assert best.model_id == t.model_id

    def test_val_split(self, project_dir):
        h = ModelHistory(project_dir)
        h.add_training(ModelTraining(
            target_variable="y", model_type="M",
            num_samples=10, num_features=2,
            val_metrics={"accuracy": 0.91},
            test_metrics={"accuracy": 0.80},
        ))
        viz = HistoryVisualizer(h)
        best = viz.best_by_metric("accuracy", split="val")
        assert best.val_metrics["accuracy"] == pytest.approx(0.91)


# ============================================================================
# metric_trend
# ============================================================================

class TestMetricTrend:
    def test_returns_dataframe(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.metric_trend("accuracy")
        assert isinstance(df, pd.DataFrame)

    def test_two_columns(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.metric_trend("accuracy")
        assert list(df.columns) == ["timestamp", "test_accuracy"]

    def test_row_count(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        df = viz.metric_trend("accuracy")
        assert len(df) == 3

    def test_drops_rows_without_metric(self, project_dir):
        h = ModelHistory(project_dir)
        h.add_training(_training(accuracy=0.80))
        h.add_training(_training(accuracy=None))  # no accuracy
        viz = HistoryVisualizer(h)
        df = viz.metric_trend("accuracy")
        assert len(df) == 1

    def test_empty_history_returns_empty_df(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        df = viz.metric_trend("accuracy")
        assert len(df) == 0


# ============================================================================
# summary_stats
# ============================================================================

class TestSummaryStats:
    def test_empty_history_all_none(self, empty_history):
        viz = HistoryVisualizer(empty_history)
        stats = viz.summary_stats("accuracy")
        assert stats["count"] == 0
        assert stats["best"] is None

    def test_count_correct(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        assert viz.summary_stats("accuracy")["count"] == 3

    def test_best_is_max(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        assert viz.summary_stats("accuracy")["best"] == pytest.approx(0.90)

    def test_worst_is_min(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        assert viz.summary_stats("accuracy")["worst"] == pytest.approx(0.80)

    def test_mean_correct(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        assert viz.summary_stats("accuracy")["mean"] == pytest.approx(0.85)

    def test_std_none_for_single_record(self, project_dir):
        h = ModelHistory(project_dir)
        h.add_training(_training(accuracy=0.80))
        viz = HistoryVisualizer(h)
        assert viz.summary_stats("accuracy")["std"] is None

    def test_missing_metric_returns_zero_count(self, history_with_three):
        viz = HistoryVisualizer(history_with_three)
        stats = viz.summary_stats("rmse")
        assert stats["count"] == 0

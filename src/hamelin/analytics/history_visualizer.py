"""
History Visualizer — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pure-logic module (no PySide6 imports) that transforms a ``ModelHistory``
into DataFrames and ranked results ready for display in the UI layer.

Usage::

    from hamelin.analytics.history_visualizer import HistoryVisualizer
    from hamelin.core.model_history import ModelHistory

    history = ModelHistory(project_dir)
    viz = HistoryVisualizer(history)

    df_timeline = viz.timeline_data()      # one row per training run
    df_cmp     = viz.comparison_table()    # wide metrics table
    best       = viz.best_by_metric("accuracy")

Author: GitHub Copilot AI
Date: February 23, 2026
Sprint: 3, Day 25
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from hamelin.core.model_history import ModelHistory, ModelTraining


class HistoryVisualizer:
    """
    Transforms a ``ModelHistory`` into display-ready DataFrames.

    All methods are pure: they read from the history but never mutate it.
    Results are always returned as new DataFrames ordered by timestamp
    ascending (oldest first).

    Args:
        history: A ``ModelHistory`` instance (already bound to a project dir).
    """

    # Columns guaranteed to appear in timeline_data() even when empty
    TIMELINE_COLUMNS = [
        "model_id",
        "timestamp",
        "target_variable",
        "model_type",
        "num_samples",
        "num_features",
        "num_trials",
        "training_time_seconds",
        "notes",
    ]

    def __init__(self, history: ModelHistory) -> None:
        self._history = history

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def timeline_data(self, metric: str = "accuracy", split: str = "test") -> pd.DataFrame:
        """
        Return a DataFrame with one row per training run, ordered by timestamp.

        Columns: all ``TIMELINE_COLUMNS`` plus a single metric column (e.g.
        ``test_accuracy``) when the metric exists in *any* training record.

        Args:
            metric: Metric name to surface as a column (default ``"accuracy"``).
            split: Metric split to use — ``"train"``, ``"val"``, or``"test"``.

        Returns:
            DataFrame sorted ascending by ``timestamp``.  Empty DataFrame
            (with correct columns) when the history has no records.
        """
        trainings = self._history.list_trainings()
        if not trainings:
            cols = self.TIMELINE_COLUMNS + [f"{split}_{metric}"]
            return pd.DataFrame(columns=cols)

        rows = []
        for t in trainings:
            row = {
                "model_id": t.model_id,
                "timestamp": t.timestamp,
                "target_variable": t.target_variable,
                "model_type": t.model_type,
                "num_samples": t.num_samples,
                "num_features": t.num_features,
                "num_trials": t.num_trials,
                "training_time_seconds": t.training_time_seconds,
                "notes": t.notes,
                f"{split}_{metric}": t.best_metric(metric, split),
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp", ascending=True).reset_index(drop=True)

    def comparison_table(self, split: str = "test") -> pd.DataFrame:
        """
        Return a wide DataFrame comparing all metrics across training runs.

        Each row is one training run.  Metric columns are derived from the
        union of metric keys across all records for the given *split*.
        Missing values are represented as ``NaN``.

        Col order: ``model_id``, ``timestamp``, ``model_type``,
        ``target_variable``, then all metric columns alphabetically.

        Args:
            split: Which metric split to expose — ``"train"``, ``"val"``,
                   or ``"test"``.

        Returns:
            Wide DataFrame.  Empty (with fixed cols) when history is empty.
        """
        trainings = self._history.list_trainings()
        fixed_cols = ["model_id", "timestamp", "model_type", "target_variable"]

        if not trainings:
            return pd.DataFrame(columns=fixed_cols)

        # Collect all metric keys across all records for the given split
        metric_keys: set[str] = set()
        for t in trainings:
            metrics = self._metrics_for_split(t, split)
            metric_keys.update(metrics.keys())

        metric_cols = sorted(metric_keys)

        rows = []
        for t in trainings:
            metrics = self._metrics_for_split(t, split)
            row: dict = {
                "model_id": t.model_id,
                "timestamp": t.timestamp,
                "model_type": t.model_type,
                "target_variable": t.target_variable,
            }
            for col in metric_cols:
                row[col] = metrics.get(col)
            rows.append(row)

        df = pd.DataFrame(rows, columns=fixed_cols + metric_cols)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp", ascending=True).reset_index(drop=True)

    def best_by_metric(
        self,
        metric: str,
        split: str = "test",
        higher_is_better: bool = True,
    ) -> Optional[ModelTraining]:
        """
        Return the ``ModelTraining`` with the best value for *metric*.

        Args:
            metric: Metric name (e.g. ``"accuracy"``, ``"roc_auc"``).
            split: Which split to read from (default ``"test"``).
            higher_is_better: ``True`` (default) for accuracy/AUC;
                              ``False`` for loss/RMSE.

        Returns:
            Best ``ModelTraining``, or ``None`` if the history is empty or
            no record contains the requested metric.
        """
        trainings = self._history.list_trainings()
        candidates = [
            (t, t.best_metric(metric, split))
            for t in trainings
            if t.best_metric(metric, split) is not None
        ]

        if not candidates:
            return None

        return max(candidates, key=lambda x: x[1] if higher_is_better else -x[1])[0]

    def metric_trend(
        self,
        metric: str,
        split: str = "test",
    ) -> pd.DataFrame:
        """
        Return a two-column DataFrame (``timestamp``, ``<split>_<metric>``)
        for plotting a trend line.

        Rows with no value for the metric are dropped.

        Args:
            metric: Metric name.
            split: Metric split.

        Returns:
            DataFrame with ``timestamp`` (datetime) and metric column,
            sorted ascending by timestamp.
        """
        df = self.timeline_data(metric=metric, split=split)
        col = f"{split}_{metric}"
        if col not in df.columns:
            return pd.DataFrame(columns=["timestamp", col])
        return df[["timestamp", col]].dropna(subset=[col]).reset_index(drop=True)

    def summary_stats(self, metric: str = "accuracy", split: str = "test") -> dict:
        """
        Return summary statistics for a given metric across all runs.

        Keys: ``count``, ``best``, ``worst``, ``mean``, ``std``.
        All values are ``None`` when no records contain the metric.

        Args:
            metric: Metric name.
            split: Metric split.

        Returns:
            Dict with summary stats.
        """
        col = f"{split}_{metric}"
        df = self.timeline_data(metric=metric, split=split)

        if col not in df.columns or df[col].dropna().empty:
            return {"count": 0, "best": None, "worst": None, "mean": None, "std": None}

        series = df[col].dropna()
        return {
            "count": int(series.count()),
            "best": float(series.max()),
            "worst": float(series.min()),
            "mean": float(series.mean()),
            "std": float(series.std()) if len(series) > 1 else None,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _metrics_for_split(training: ModelTraining, split: str) -> dict:
        mapping = {
            "train": training.train_metrics,
            "val": training.val_metrics,
            "test": training.test_metrics,
        }
        return mapping.get(split, {})

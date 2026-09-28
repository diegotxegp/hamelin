"""
Model History System for HAMELIN

Tracks all Ludwig training sessions per project, with JSON persistence.
Each training run is stored as a ModelTraining record inside the project directory.

Usage:
    >>> from pathlib import Path
    >>> from hamelin.core.model_history import ModelTraining, ModelHistory
    >>> history = ModelHistory(Path("Projects/UPS"))
    >>> record = ModelTraining(
    ...     target_variable="outcome",
    ...     model_type="RandomForest",
    ...     num_samples=100,
    ...     num_features=20,
    ...     train_metrics={"accuracy": 0.87},
    ...     val_metrics={"accuracy": 0.84},
    ...     test_metrics={"accuracy": 0.83},
    ...     training_time_seconds=42.5,
    ... )
    >>> history.add_training(record)
    >>> best = history.get_best("accuracy")

Author: AI Assistant
Date: February 20, 2026
Version: 1.0
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from hamelin.utils.logger import log
from hamelin.utils.exceptions import DataLoadError, DataSaveError


# ---------------------------------------------------------------------------
# ModelTraining dataclass
# ---------------------------------------------------------------------------

@dataclass
class ModelTraining:
    """
    Record of a single Ludwig model training session.

    Attributes:
        model_id: Auto-generated UUID identifying this training run -
            internal identity, never shown to the user or used as a
            filesystem name (see model_name for that).
        model_name: User-chosen name for this run (e.g. "LPP_risk_v1"),
            entered on the Training page. Falls back to model_id when
            blank - see TrainingPage._sanitize_model_name(), which is also
            what the checkpoint folder under model_checkpoints/ is named,
            so it's what shows up wherever a model is picked by name (the
            "interface" comparison tool, model-history widgets, ...).
        timestamp: When training started (UTC).
        target_variable: Column name being predicted.
        model_type: Algorithm name (e.g. "RandomForest", "XGBoost").
        hyperparameters: Full hyperparameter dict used for this run.
        dataset_version: Hash or label identifying the dataset snapshot.
        num_samples: Number of training samples used.
        num_features: Number of input features.
        train_metrics: Metric dict for the training split.
        val_metrics: Metric dict for the validation split.
        test_metrics: Metric dict for the test split.
        training_time_seconds: Wall-clock seconds for the full run.
        num_trials: Number of hyperopt trials executed (0 if no hyperopt).
        notes: Free-text annotation by the researcher.
        checkpoint_path: Directory holding the saved Ludwig model for this
            run (model_hyperparameters.json + weights), or "" if the
            checkpoint wasn't saved (e.g. non-Ludwig backend, or saving
            failed).
    """

    # Identity
    target_variable: str
    model_type: str

    # Dataset
    num_samples: int
    num_features: int

    # Performance
    train_metrics: dict = field(default_factory=dict)
    val_metrics: dict = field(default_factory=dict)
    test_metrics: dict = field(default_factory=dict)

    # Execution
    training_time_seconds: float = 0.0
    num_trials: int = 0

    # Optional / auto-set
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    hyperparameters: dict = field(default_factory=dict)
    dataset_version: str = ""
    notes: str = ""
    checkpoint_path: str = ""

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelTraining":
        """Reconstruct a ModelTraining from a dict (e.g. loaded from JSON)."""
        data = dict(data)
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    def best_metric(self, metric: str, split: str = "test") -> Optional[float]:
        """
        Return the value of *metric* for the given *split*.

        Args:
            metric: Metric name (e.g. "accuracy", "roc_auc").
            split: One of "train", "val", "test".

        Returns:
            Float value, or None if not present.
        """
        mapping = {"train": self.train_metrics, "val": self.val_metrics, "test": self.test_metrics}
        bucket = mapping.get(split, {})
        return bucket.get(metric)


# ---------------------------------------------------------------------------
# ModelHistory manager
# ---------------------------------------------------------------------------

HISTORY_FILENAME = "model_history.json"


class ModelHistory:
    """
    Persistent store for ModelTraining records within a project directory.

    Records are saved to ``<project_dir>/model_history.json``.

    Example:
        >>> history = ModelHistory(Path("Projects/UPS"))
        >>> history.add_training(record)
        >>> history.list_trainings()
        [ModelTraining(...), ...]
        >>> history.get_best("accuracy")
        ModelTraining(...)
    """

    def __init__(self, project_dir: Path) -> None:
        """
        Initialise the history manager.

        Args:
            project_dir: Root directory of the project (must exist).
        """
        self._path = Path(project_dir) / HISTORY_FILENAME
        self._records: list[ModelTraining] = []
        self._load()

    # ------------------------------------------------------------------
    # Private persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load records from disk (silent if file does not exist yet)."""
        if not self._path.exists():
            self._records = []
            return
        try:
            with self._path.open("r", encoding="utf-8") as fh:
                raw: list[dict] = json.load(fh)
            self._records = [ModelTraining.from_dict(r) for r in raw]
            log.debug(f"ModelHistory: loaded {len(self._records)} records from {self._path}")
        except Exception as exc:
            raise DataLoadError(f"Cannot load model history from {self._path}: {exc}") from exc

    def _save(self) -> None:
        """Persist all records to disk."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as fh:
                json.dump([r.to_dict() for r in self._records], fh, indent=2, ensure_ascii=False)
            log.debug(f"ModelHistory: saved {len(self._records)} records to {self._path}")
        except Exception as exc:
            raise DataSaveError(f"Cannot save model history to {self._path}: {exc}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_training(self, training: ModelTraining) -> None:
        """
        Append a new training record and persist immediately.

        Args:
            training: Completed ModelTraining instance.
        """
        self._records.append(training)
        self._save()
        log.info(f"ModelHistory: added training {training.model_id} ({training.model_type})")

    def list_trainings(self) -> list[ModelTraining]:
        """
        Return all training records, most recent first.

        Returns:
            List of ModelTraining sorted by timestamp descending.
        """
        return sorted(self._records, key=lambda r: r.timestamp, reverse=True)

    def get_training(self, model_id: str) -> Optional[ModelTraining]:
        """
        Retrieve a single record by its UUID.

        Args:
            model_id: UUID string matching ModelTraining.model_id.

        Returns:
            Matching ModelTraining, or None if not found.
        """
        for record in self._records:
            if record.model_id == model_id:
                return record
        return None

    def delete_training(self, model_id: str) -> bool:
        """
        Remove a training record by UUID and persist.

        Args:
            model_id: UUID of the record to delete.

        Returns:
            True if deleted, False if not found.
        """
        before = len(self._records)
        self._records = [r for r in self._records if r.model_id != model_id]
        if len(self._records) < before:
            self._save()
            log.info(f"ModelHistory: deleted training {model_id}")
            return True
        return False

    def get_best(
        self,
        metric: str,
        split: str = "test",
        higher_is_better: bool = True,
    ) -> Optional[ModelTraining]:
        """
        Return the training record with the best value for *metric*.

        Args:
            metric: Metric name (e.g. "accuracy", "roc_auc", "loss").
            split: Which split to evaluate — "train", "val", or "test".
            higher_is_better: True for accuracy/AUC; False for loss/RMSE.

        Returns:
            Best ModelTraining, or None if no records have the metric.
        """
        candidates = [
            (r, r.best_metric(metric, split))
            for r in self._records
            if r.best_metric(metric, split) is not None
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda x: x[1] if higher_is_better else -x[1])[0]

    def to_dataframe(self) -> pd.DataFrame:
        """
        Return all records as a flat DataFrame for display or export.

        Returns:
            DataFrame with one row per training, key metrics flattened.
        """
        if not self._records:
            return pd.DataFrame()

        rows = []
        for r in self.list_trainings():
            row: dict[str, Any] = {
                "model_id": r.model_id,
                "timestamp": r.timestamp,
                "model_type": r.model_type,
                "target_variable": r.target_variable,
                "num_samples": r.num_samples,
                "num_features": r.num_features,
                "training_time_s": r.training_time_seconds,
                "num_trials": r.num_trials,
                "dataset_version": r.dataset_version,
                "notes": r.notes,
            }
            # Flatten test_metrics as primary display metrics
            for k, v in r.test_metrics.items():
                row[f"test_{k}"] = v
            rows.append(row)

        return pd.DataFrame(rows)

    def __len__(self) -> int:
        return len(self._records)

    def __repr__(self) -> str:
        return f"ModelHistory(path={self._path}, records={len(self._records)})"

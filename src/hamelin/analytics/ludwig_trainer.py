"""
Training Orchestrator — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``LudwigTrainer`` is the high-level orchestrator that coordinates:
  - Dataset preparation and feature selection
  - AutoML backend execution (pluggable via registry)
  - ModelHistory persistence

``LudwigTrainerWorker`` is a ``QThread`` subclass that runs the AutoML backend
asynchronously so the UI remains responsive during long training sessions.
It emits:
  - ``progress(int)``  — 0-100 progress steps
  - ``finished(object)``  — ``AutoMLResult`` on success
  - ``error(str)``  — human-readable error message on failure

The name "LudwigTrainer" is kept for backward compatibility; internally it
delegates all AutoML work to the active ``AutoMLBackend``, which defaults to
Ludwig but can be swapped for any registered backend::

    from hamelin.analytics.automl.registry import set_default
    set_default("autogluon")   # switch globally

    from hamelin.analytics.automl import get_backend
    trainer = LudwigTrainer(project_dir, dm, backend=get_backend("autogluon"))

Author: GitHub Copilot AI
Date: February 20, 2026 · Day 24 (modular backends) · Day 28 (QThread worker)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import pandas as pd

from hamelin.analytics.automl.base import AutoMLBackend
from hamelin.core.model_history import ModelHistory, ModelTraining
from hamelin.utils.logger import log


# ---------------------------------------------------------------------------
# Dataset helper (not backend-specific)
# ---------------------------------------------------------------------------

def _dataset_hash(df: pd.DataFrame) -> str:
    """Return a short SHA-1 fingerprint of a DataFrame (shape + checksum)."""
    raw = f"{df.shape}_{pd.util.hash_pandas_object(df).sum()}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Pure backend-execution helper (testable without PySide6)
# ---------------------------------------------------------------------------

def _run_backend(
    df: pd.DataFrame,
    target: str,
    features: list[str] | None,
    time_limit_s: int,
    backend: Optional[AutoMLBackend],
    cancelled_fn=None,
    backend_kwargs: dict | None = None,
):
    """
    Execute an AutoML backend synchronously and return an ``AutoMLResult``.

    This is a *pure* function (no Qt signals) extracted from
    ``LudwigTrainerWorker.run()`` so it can be unit-tested without PySide6.

    Args:
        df: Training DataFrame.
        target: Column to predict.
        features: Feature columns (None = all except *target*).
        time_limit_s: Maximum training time in seconds.
        backend: Backend to use (None = registry default).
        cancelled_fn: Optional callable checked at each checkpoint.
                      If it returns True, ``RuntimeError`` is raised.

    Returns:
        ``AutoMLResult``

    Raises:
        RuntimeError: If ``cancelled_fn()`` returns True.
        RuntimeError: If the backend raises.
    """
    def _check():
        if cancelled_fn and cancelled_fn():
            raise RuntimeError("Training cancelled by user")

    _check()

    if backend is None:
        from hamelin.analytics.automl.registry import get_backend
        backend = get_backend()

    _check()

    return backend.run(
        df=df,
        target=target,
        features=features,
        time_limit_s=time_limit_s,
        **(backend_kwargs or {}),
    )


# ---------------------------------------------------------------------------
# LudwigTrainerWorker (Qt asynchronous worker)
# ---------------------------------------------------------------------------

try:
    from PySide6.QtCore import QThread, Signal as _Signal

    class LudwigTrainerWorker(QThread):
        """
        Asynchronous QThread that executes ``AutoMLBackend.run()`` in a
        background thread, keeping the UI responsive during long training runs.

        Signals:
            progress(int):      Simulated progress 0-100.
            finished(object):   Emitted with an ``AutoMLResult`` on success.
            error(str):         Emitted with a message on failure or cancellation.

        Usage::

            worker = LudwigTrainerWorker(df, "outcome", features, time_limit_s=600)
            worker.progress.connect(progress_bar.setValue)
            worker.finished.connect(on_training_finished)
            worker.error.connect(on_training_error)
            worker.start()

            # To cancel before Ludwig returns:
            worker.stop()
        """

        progress = _Signal(int)
        finished = _Signal(object)   # AutoMLResult
        error = _Signal(str)

        def __init__(
            self,
            df: pd.DataFrame,
            target: str,
            features: list[str] | None,
            time_limit_s: int,
            backend: Optional[AutoMLBackend] = None,
            parent=None,
            backend_kwargs: dict | None = None,
        ) -> None:
            super().__init__(parent)
            self._df = df
            self._target = target
            self._features = features
            self._time_limit_s = time_limit_s
            self._backend = backend
            self._backend_kwargs = backend_kwargs or {}
            self._cancelled: bool = False

        # ------------------------------------------------------------------

        def run(self) -> None:
            """Execute the AutoML backend; emits finished or error."""
            try:
                self.progress.emit(10)

                self.progress.emit(30)

                self.progress.emit(60)

                result = _run_backend(
                    df=self._df,
                    target=self._target,
                    features=self._features,
                    time_limit_s=self._time_limit_s,
                    backend=self._backend,
                    cancelled_fn=lambda: self._cancelled,
                    backend_kwargs=self._backend_kwargs,
                )

                self.progress.emit(100)
                self.finished.emit(result)

            except RuntimeError as exc:
                # Covers "Training cancelled by user" and backend errors
                log.info(f"LudwigTrainerWorker: {exc}")
                self.error.emit(str(exc))
            except Exception as exc:  # noqa: BLE001
                log.error(f"LudwigTrainerWorker: training failed — {exc}")
                self.error.emit(str(exc))

        # ------------------------------------------------------------------

        def stop(self) -> None:
            """Request cancellation. Best-effort: Ludwig itself cannot be
            interrupted mid-run, but this flag prevents emitting *finished*
            after cancellation and is checked before Ludwig starts."""
            self._cancelled = True
            log.info("LudwigTrainerWorker: stop requested")

except ImportError:
    # PySide6 not installed (e.g. in a pure-backend test environment).
    # Define a fallback so imports don't fail.
    class LudwigTrainerWorker:  # type: ignore[no-redef]
        """Stub when PySide6 is not available."""

        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError(
                "LudwigTrainerWorker requires PySide6 to be installed."
            )


# ---------------------------------------------------------------------------
# LudwigTrainer (orchestrator)
# ---------------------------------------------------------------------------

class LudwigTrainer:
    """
    High-level training orchestrator.

    Coordinates dataset preparation, AutoML backend execution, and
    ModelHistory persistence. The AutoML backend is fully swappable via
    the ``backend`` constructor argument or the global registry.

    Args:
        project_dir: Root directory of the active HAMELIN project.
        data_model: A DataModel instance with a loaded DataFrame.
        backend: An ``AutoMLBackend`` instance. If ``None``, the registry
                 default (currently Ludwig) is used.

    Example — use default backend (Ludwig)::

        trainer = LudwigTrainer(Path("Projects/UPS"), dm)
        record = trainer.train(target="outcome", time_limit_s=600)

    Example — switch to a different backend::

        from hamelin.analytics.automl import get_backend
        trainer = LudwigTrainer(
            Path("Projects/UPS"), dm,
            backend=get_backend("autogluon"),
        )
    """

    def __init__(
        self,
        project_dir: Path,
        data_model,
        backend: Optional[AutoMLBackend] = None,
    ) -> None:
        if data_model is None or data_model.df is None:
            raise ValueError("DataModel must have a loaded DataFrame before training.")

        self.project_dir = Path(project_dir)
        self.data_model = data_model
        self._last_record: Optional[ModelTraining] = None

        if backend is not None:
            self._backend = backend
        else:
            from hamelin.analytics.automl.registry import get_backend
            self._backend = get_backend()  # default = ludwig

        log.debug(f"LudwigTrainer: using backend '{self._backend.name}'")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train(
        self,
        target: str,
        features: list[str] | None = None,
        time_limit_s: int = 3600,
        notes: str = "",
        **backend_kwargs,
    ) -> ModelTraining:
        """
        Run AutoML training and persist the result to ModelHistory.

        Args:
            target: Column to predict.
            features: Input columns. ``None`` means all except *target*.
            time_limit_s: Maximum search time in seconds.
            notes: Free-text annotation stored with the record.
            **backend_kwargs: Forwarded to the backend's ``run()`` method.

        Returns:
            Persisted ``ModelTraining`` record.
        """
        df = self.data_model.df.copy()

        if target not in df.columns:
            raise ValueError(
                f"Target column '{target}' not found in dataset. "
                f"Available columns: {list(df.columns)}"
            )

        if features:
            missing = [f for f in features if f not in df.columns]
            if missing:
                raise ValueError(f"Feature columns not found in dataset: {missing}")

        num_features = len(features) if features else len(df.columns) - 1
        num_samples = len(df)
        dataset_version = _dataset_hash(df)

        log.info(
            f"LudwigTrainer ({self._backend.name}): training — "
            f"target={target!r}, samples={num_samples}, "
            f"features={num_features}, time_limit={time_limit_s}s"
        )

        # A project-scoped default rather than letting the backend fall
        # back to its own default (Ludwig's auto_train writes to "." - the
        # process's cwd - when not told otherwise), so run artifacts land
        # somewhere predictable per project instead of scattered wherever
        # this app happened to be launched from. This is just Ludwig's own
        # internal hyperopt trial dump though, not what the "interface"
        # dashboard shows when opened from Hamelin - that reads
        # results/models/ instead (see MainWindow._open_interface_page,
        # TrainingPage._on_training_finished), one named subfolder per
        # completed run, saved separately from this. Callers can still
        # override via backend_kwargs.
        backend_kwargs.setdefault("output_directory", str(self.project_dir / "ludwig_runs"))

        result = self._backend.run(
            df=df,
            target=target,
            features=features,
            time_limit_s=time_limit_s,
            **backend_kwargs,
        )

        record = ModelTraining(
            target_variable=target,
            model_type=result.model_type,
            hyperparameters=result.hyperparameters,
            dataset_version=dataset_version,
            num_samples=num_samples,
            num_features=num_features,
            train_metrics=result.train_metrics,
            val_metrics=result.val_metrics,
            test_metrics=result.test_metrics,
            training_time_seconds=result.training_time_seconds,
            num_trials=result.num_trials,
            notes=notes,
        )

        history = ModelHistory(self.project_dir)
        history.add_training(record)
        self._last_record = record

        log.info(
            f"LudwigTrainer: record saved — {record.model_id} "
            f"({record.model_type})"
        )
        return record

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def get_history(self) -> ModelHistory:
        """Return the ModelHistory for this project (reads from disk)."""
        return ModelHistory(self.project_dir)

    @property
    def backend(self) -> AutoMLBackend:
        """The active AutoML backend instance."""
        return self._backend

    @property
    def last_record(self) -> Optional[ModelTraining]:
        """ModelTraining from the most recent ``train()`` call, or None."""
        return self._last_record

    def __repr__(self) -> str:
        dm_status = (
            "loaded" if (self.data_model and self.data_model.df is not None)
            else "empty"
        )
        return (
            f"LudwigTrainer("
            f"project={self.project_dir.name}, "
            f"backend={self._backend.name!r}, "
            f"data={dm_status})"
        )

"""
AutoML Backend — Abstract Base Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Defines the contract that every AutoML backend must fulfil.
Any new tool (AutoGluon, H2O AutoML, FLAML, etc.) must subclass
``AutoMLBackend`` and implement all abstract methods.

The orchestrator (``LudwigTrainer``) only depends on this interface,
so swapping the backend requires zero changes to application code.

Author: GitHub Copilot AI
Date: February 20, 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# AutoMLResult — backend-agnostic result container
# ---------------------------------------------------------------------------

@dataclass
class AutoMLResult:
    """
    Standardised result returned by every AutoML backend.

    Backends fill this container after training completes so that the
    orchestrator can build a ``ModelTraining`` record without knowing
    which backend was used.

    Attributes:
        model_type: Human-readable algorithm name (e.g. "Ludwig/Tabnet").
        hyperparameters: Full config dict used for this run.
        train_metrics: Metric dict for the training split.
        val_metrics: Metric dict for the validation split.
        test_metrics: Metric dict for the test/evaluation split.
        training_time_seconds: Wall-clock seconds for the full run.
        num_trials: Number of hyperopt/search trials executed.
        trained_model: The raw backend model object (opaque to orchestrator).
        extra: Anything backend-specific that doesn't fit above fields.
    """

    model_type: str = "AutoML"
    hyperparameters: dict = field(default_factory=dict)
    train_metrics: dict = field(default_factory=dict)
    val_metrics: dict = field(default_factory=dict)
    test_metrics: dict = field(default_factory=dict)
    training_time_seconds: float = 0.0
    num_trials: int = 0
    trained_model: Any = None
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# AutoMLBackend — abstract interface
# ---------------------------------------------------------------------------

class AutoMLBackend(ABC):
    """
    Abstract base class for AutoML backends.

    Subclasses must implement:
        - ``name`` property
        - ``is_available()``
        - ``run(df, target, features, time_limit_s, **kwargs)``

    Optional overrides:
        - ``validate_environment()`` — raise ImportError / RuntimeError if
          dependencies are missing or misconfigured.

    Example subclass skeleton::

        class AutoGluonBackend(AutoMLBackend):
            @property
            def name(self) -> str:
                return "autogluon"

            @classmethod
            def is_available(cls) -> bool:
                try:
                    import autogluon.tabular  # noqa: F401
                    return True
                except ImportError:
                    return False

            def run(self, df, target, features=None,
                    time_limit_s=3600, **kwargs):
                from autogluon.tabular import TabularPredictor
                # ... training logic ...
                return AutoMLResult(
                    model_type="AutoGluon/...",
                    test_metrics={"accuracy": 0.89},
                    training_time_seconds=elapsed,
                )
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique short identifier for this backend (lowercase, no spaces).

        Examples: ``"ludwig"``, ``"autogluon"``, ``"flaml"``, ``"h2o"``
        """

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """
        Return True if the backend's dependencies are installed and
        the backend can be used right now.

        This check must be cheap (no heavy imports) — it is called
        at registry lookup time.
        """

    # ------------------------------------------------------------------
    # Core training
    # ------------------------------------------------------------------

    @abstractmethod
    def run(
        self,
        df,
        target: str,
        features: list[str] | None = None,
        time_limit_s: int = 3600,
        **kwargs,
    ) -> AutoMLResult:
        """
        Run AutoML training and return a standardised ``AutoMLResult``.

        Args:
            df: Training DataFrame (pandas). Must contain *target* column.
            target: Name of the column to predict.
            features: Explicit list of input columns. ``None`` means all
                      columns except *target*.
            time_limit_s: Maximum wall-clock seconds for the search.
            **kwargs: Backend-specific options (e.g. ``tune_for_memory``
                      for Ludwig, ``presets`` for AutoGluon).

        Returns:
            ``AutoMLResult`` populated with metrics and model reference.

        Raises:
            ImportError: If backend package is not installed.
            ValueError: If *target* not in *df* or other input error.
            RuntimeError: If training itself fails.
        """

    # ------------------------------------------------------------------
    # Optional hooks
    # ------------------------------------------------------------------

    def validate_environment(self) -> None:
        """
        Raise an appropriate exception if the environment is not ready.

        Default implementation calls ``is_available()`` and raises
        ``ImportError`` if False. Subclasses may perform deeper checks
        (GPU availability, licence, etc.).
        """
        if not self.is_available():
            raise ImportError(
                f"AutoML backend '{self.name}' is not available. "
                f"Install the required package(s) and try again."
            )

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        available = "available" if self.is_available() else "not installed"
        return f"{self.__class__.__name__}(name={self.name!r}, {available})"

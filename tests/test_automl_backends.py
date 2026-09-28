"""
AutoML Architecture Tests — HAMELIN v2.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests for the modular AutoML backend system:
- AutoMLResult dataclass
- AutoMLBackend ABC contract
- LudwigBackend helpers and availability
- Registry: register, get_backend, set_default, list_backends

Author: GitHub Copilot AI
Date: February 20, 2026
Sprint: 3 (refactored modular backends)
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pandas as pd
import pytest

from hamelin.analytics.automl.base import AutoMLBackend, AutoMLResult
from hamelin.analytics.automl.ludwig_backend import (
    LudwigBackend,
    _extract_model_type,
    _extract_hyperparameters,
    _flatten_eval_stats,
)
from hamelin.analytics.automl import registry


# ============================================================================
# AutoMLResult
# ============================================================================

class TestAutoMLResult:
    def test_default_values(self):
        r = AutoMLResult()
        assert r.model_type == "AutoML"
        assert r.hyperparameters == {}
        assert r.train_metrics == {}
        assert r.val_metrics == {}
        assert r.test_metrics == {}
        assert r.training_time_seconds == 0.0
        assert r.num_trials == 0
        assert r.trained_model is None
        assert r.extra == {}

    def test_custom_values(self):
        r = AutoMLResult(
            model_type="Ludwig/Tabnet",
            test_metrics={"accuracy": 0.91},
            num_trials=10,
        )
        assert r.model_type == "Ludwig/Tabnet"
        assert r.test_metrics["accuracy"] == pytest.approx(0.91)
        assert r.num_trials == 10


# ============================================================================
# AutoMLBackend ABC
# ============================================================================

class ConcreteBackend(AutoMLBackend):
    """Minimal concrete implementation for testing the ABC."""

    @property
    def name(self) -> str:
        return "test_backend"

    @classmethod
    def is_available(cls) -> bool:
        return True

    def run(self, df, target, features=None, time_limit_s=3600, **kwargs) -> AutoMLResult:
        return AutoMLResult(model_type="Test/Model", test_metrics={"accuracy": 0.99})


class UnavailableBackend(AutoMLBackend):
    """Backend that simulates a missing package."""

    @property
    def name(self) -> str:
        return "unavailable"

    @classmethod
    def is_available(cls) -> bool:
        return False

    def run(self, df, target, features=None, time_limit_s=3600, **kwargs) -> AutoMLResult:
        raise ImportError("Not installed")


class TestAutoMLBackendABC:
    def test_concrete_backend_instantiates(self):
        b = ConcreteBackend()
        assert b.name == "test_backend"

    def test_is_available_true(self):
        assert ConcreteBackend.is_available() is True

    def test_run_returns_result(self):
        b = ConcreteBackend()
        df = pd.DataFrame({"x": [1, 2], "y": [0, 1]})
        result = b.run(df, "y")
        assert isinstance(result, AutoMLResult)
        assert result.test_metrics["accuracy"] == pytest.approx(0.99)

    def test_validate_environment_ok(self):
        ConcreteBackend().validate_environment()  # should not raise

    def test_validate_environment_raises_when_unavailable(self):
        with pytest.raises(ImportError, match="unavailable"):
            UnavailableBackend().validate_environment()

    def test_repr_format(self):
        r = repr(ConcreteBackend())
        assert "test_backend" in r
        assert "available" in r

    def test_repr_unavailable(self):
        r = repr(UnavailableBackend())
        assert "not installed" in r


# ============================================================================
# LudwigBackend helpers
# ============================================================================

class TestExtractModelType:
    def test_extracts_combiner_type(self):
        model = MagicMock()
        model.config = {"combiner": {"type": "tabnet"}}
        assert _extract_model_type(model) == "Ludwig/Tabnet"

    def test_no_combiner_falls_back_to_model_name(self):
        model = MagicMock()
        # Plain dict with model_name but no combiner
        model.config = {"model_name": "Ludwig/RandomForest"}
        result = _extract_model_type(model)
        assert "Ludwig" in result

    def test_falls_back_to_automl_on_attribute_error(self):
        model = MagicMock(spec=[])   # no attributes → AttributeError on .config
        assert _extract_model_type(model) == "Ludwig/AutoML"


class TestExtractHyperparameters:
    def test_returns_json_serialisable_dict(self):
        model = MagicMock()
        model.config = {"layers": 3, "lr": 0.001, "nested": {"a": 1}}
        params = _extract_hyperparameters(model)
        json.dumps(params)  # must not raise
        assert params["layers"] == 3

    def test_returns_empty_dict_on_attribute_error(self):
        model = MagicMock(spec=[])
        assert _extract_hyperparameters(model) == {}


class TestFlattenEvalStats:
    def test_nested_target_key(self):
        stats = {"outcome": {"accuracy": 0.87, "loss": 0.13}}
        flat = _flatten_eval_stats(stats, "outcome")
        assert flat["accuracy"] == pytest.approx(0.87)
        assert flat["loss"] == pytest.approx(0.13)

    def test_flat_dict_fallback(self):
        stats = {"accuracy": 0.90, "loss": 0.10}
        flat = _flatten_eval_stats(stats, "outcome")
        assert flat["accuracy"] == pytest.approx(0.90)

    def test_drops_non_scalar_values(self):
        stats = {"outcome": {"accuracy": 0.87, "confusion_matrix": [[10, 2], [3, 15]]}}
        flat = _flatten_eval_stats(stats, "outcome")
        assert "accuracy" in flat
        assert "confusion_matrix" not in flat

    def test_single_element_list_is_scalar(self):
        stats = {"outcome": {"accuracy": [0.87]}}
        flat = _flatten_eval_stats(stats, "outcome")
        assert flat["accuracy"] == pytest.approx(0.87)


class TestLudwigBackendAvailability:
    def test_is_available_true(self):
        # Ludwig is installed in this project
        assert LudwigBackend.is_available() is True

    def test_name_is_ludwig(self):
        assert LudwigBackend().name == "ludwig"

    def test_validate_environment_does_not_raise(self):
        LudwigBackend().validate_environment()


# ============================================================================
# Registry
# ============================================================================

class TestRegistry:
    """Tests use a fresh registry state to avoid contaminating global state."""

    def setup_method(self):
        # Save state
        self._saved = dict(registry._REGISTRY)
        self._saved_default = registry._DEFAULT_BACKEND

    def teardown_method(self):
        # Restore state
        registry._REGISTRY.clear()
        registry._REGISTRY.update(self._saved)
        registry._DEFAULT_BACKEND = self._saved_default

    def test_ludwig_registered_by_default(self):
        assert "ludwig" in registry.list_backends()

    def test_list_backends_returns_list(self):
        assert isinstance(registry.list_backends(), list)

    def test_register_new_backend(self):
        registry.register("test_backend", ConcreteBackend)
        assert "test_backend" in registry.list_backends()

    def test_register_raises_if_not_subclass(self):
        with pytest.raises(TypeError):
            registry.register("bad", object)  # not a subclass of AutoMLBackend

    def test_get_backend_default_returns_ludwig(self):
        backend = registry.get_backend()
        assert backend.name == "ludwig"

    def test_get_backend_by_name(self):
        registry.register("concrete", ConcreteBackend)
        backend = registry.get_backend("concrete")
        assert backend.name == "test_backend"

    def test_get_backend_raises_for_unknown(self):
        with pytest.raises(KeyError):
            registry.get_backend("nonexistent_backend_xyz")

    def test_get_backend_raises_if_unavailable(self):
        registry.register("unavailable_pkg", UnavailableBackend)
        with pytest.raises(ImportError):
            registry.get_backend("unavailable_pkg")

    def test_set_default_changes_default(self):
        registry.register("concrete", ConcreteBackend)
        registry.set_default("concrete")
        backend = registry.get_backend()
        assert backend.name == "test_backend"

    def test_set_default_raises_for_unknown(self):
        with pytest.raises(KeyError):
            registry.set_default("this_does_not_exist")

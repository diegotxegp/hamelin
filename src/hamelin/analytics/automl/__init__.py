"""
AutoML Subsystem — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Package that provides a pluggable AutoML backend layer.

Structure:
    base.py          — AutoMLBackend abstract base class (the contract)
    ludwig_backend.py — Ludwig 0.10.x implementation
    registry.py      — Backend registry and factory

To add a new AutoML tool (e.g. AutoGluon):
    1. Create  src/analytics/automl/autogluon_backend.py
    2. Inherit from AutoMLBackend and implement all abstract methods
    3. Register it:  registry.register("autogluon", AutoGluonBackend)
"""

from hamelin.analytics.automl.base import AutoMLBackend, AutoMLResult
from hamelin.analytics.automl.registry import get_backend, register, list_backends

__all__ = ["AutoMLBackend", "AutoMLResult", "get_backend", "register", "list_backends"]

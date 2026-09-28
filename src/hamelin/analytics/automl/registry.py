"""
AutoML Backend Registry — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Central registry for all available AutoML backends.
The orchestrator (``LudwigTrainer``) calls ``get_backend()`` to obtain
the configured backend; application code never imports backend classes directly.

Usage::

    # Get the current default (Ludwig)
    backend = get_backend()

    # Get a specific backend by name
    backend = get_backend("ludwig")

    # Register a new backend (e.g. in a plugin)
    from hamelin.analytics.automl.autogluon_backend import AutoGluonBackend
    register("autogluon", AutoGluonBackend)

    # List all registered backends
    list_backends()  # → ["ludwig", "autogluon"]

Author: GitHub Copilot AI
Date: February 20, 2026
"""

from __future__ import annotations

from typing import Type

from hamelin.analytics.automl.base import AutoMLBackend
from hamelin.utils.logger import log


# ---------------------------------------------------------------------------
# Internal registry store
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, Type[AutoMLBackend]] = {}
_DEFAULT_BACKEND: str = "ludwig"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(name: str, backend_cls: Type[AutoMLBackend]) -> None:
    """
    Register an AutoML backend class under *name*.

    Args:
        name: Unique lowercase identifier (e.g. ``"autogluon"``).
        backend_cls: A class that subclasses ``AutoMLBackend``.

    Raises:
        TypeError: If *backend_cls* is not a subclass of ``AutoMLBackend``.
    """
    if not (isinstance(backend_cls, type) and issubclass(backend_cls, AutoMLBackend)):
        raise TypeError(
            f"'{backend_cls}' is not a subclass of AutoMLBackend."
        )
    _REGISTRY[name] = backend_cls
    log.debug(f"AutoML registry: registered backend '{name}' → {backend_cls.__name__}")


def set_default(name: str) -> None:
    """
    Set the default backend returned by ``get_backend()`` with no arguments.

    Args:
        name: Must be a previously registered backend name.

    Raises:
        KeyError: If *name* is not registered.
    """
    if name not in _REGISTRY:
        raise KeyError(
            f"Backend '{name}' is not registered. "
            f"Available: {list(_REGISTRY.keys())}"
        )
    global _DEFAULT_BACKEND
    _DEFAULT_BACKEND = name
    log.info(f"AutoML registry: default backend set to '{name}'")


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def get_backend(name: str | None = None) -> AutoMLBackend:
    """
    Instantiate and return an AutoML backend.

    Args:
        name: Backend identifier. If ``None``, the current default is used.

    Returns:
        An instantiated ``AutoMLBackend`` subclass.

    Raises:
        KeyError: If *name* is not registered.
        ImportError: If the backend is registered but its package is not installed.
    """
    key = name or _DEFAULT_BACKEND

    if key not in _REGISTRY:
        raise KeyError(
            f"AutoML backend '{key}' is not registered. "
            f"Available: {list(_REGISTRY.keys())}"
        )

    backend_cls = _REGISTRY[key]
    backend = backend_cls()
    backend.validate_environment()   # raises ImportError if not installed
    log.debug(f"AutoML registry: returning backend '{key}' ({backend_cls.__name__})")
    return backend


def list_backends() -> list[str]:
    """
    Return the names of all registered backends.

    Returns:
        List of registered backend name strings.
    """
    return list(_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Auto-register built-in backends
# ---------------------------------------------------------------------------

def _auto_register() -> None:
    """Register all built-in backends that have importable packages."""
    from hamelin.analytics.automl.ludwig_backend import LudwigBackend
    register("ludwig", LudwigBackend)
    # Future backends are registered here, e.g.:
    # from hamelin.analytics.automl.autogluon_backend import AutoGluonBackend
    # register("autogluon", AutoGluonBackend)


_auto_register()

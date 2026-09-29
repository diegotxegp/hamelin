"""Deferred imports for heavy scientific libraries (keeps application start-up fast)."""

import importlib


class LazyModule:
    """Stand-in for a module that is imported on first attribute access."""

    def __init__(self, name: str) -> None:
        self.__dict__["_name"] = name
        self.__dict__["_module"] = None

    def _load(self):
        mod = self.__dict__["_module"]
        if mod is None:
            mod = importlib.import_module(self.__dict__["_name"])
            self.__dict__["_module"] = mod
        return mod

    def __getattr__(self, attr):
        return getattr(self._load(), attr)

    def __setattr__(self, attr, value):
        setattr(self._load(), attr, value)

"""
Usage/Interaction Logger
~~~~~~~~~~~~~~~~~~~~~~~~

Structured, analyzable record of what the user does in the UI - for
usability studies, not debugging (see hamelin.utils.logger for that).

One row per event, appended to a single ever-growing CSV file at
workspace/logs/usage_log.csv, so a whole study's worth of sessions can be
opened as one table in Excel/pandas:

    timestamp,session_id,page,action,element,detail

Usage:
    from hamelin.utils.usage_logger import usage_log

    usage_log.event("Projects", "click", "New Project button")
    usage_log.event("Projects", "field_filled", "Acronym", "UPS")
"""

import csv
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional


class UsageLogger:
    """Singleton that appends one CSV row per recorded UI event."""

    _instance: Optional["UsageLogger"] = None
    _initialized: bool = False

    _FIELDS = ["timestamp", "session_id", "page", "action", "element", "detail"]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if UsageLogger._initialized:
            return
        UsageLogger._initialized = True
        self._lock = threading.Lock()
        # One id per app run, so events from the same session can be
        # grouped/filtered even though they all land in the same file.
        self._session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Same base as HamelinLogger's workspace/logs/ - see the matching
        # comment in hamelin/utils/logger.py.
        log_dir = Path(__file__).resolve().parent.parent.parent.parent / "workspace" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self._path = log_dir / "usage_log.csv"

        if not self._path.exists():
            with open(self._path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self._FIELDS)

    def event(self, page: str, action: str, element: str, detail: str = "") -> None:
        """
        Record one user-interaction event as a CSV row.

        Args:
            page: Screen/page where it happened (e.g. "Projects", "Data").
            action: Kind of event (e.g. "click", "navigate", "field_filled",
                "select", "created", "deleted").
            element: The specific control or field involved
                (e.g. "New Project button", "Acronym").
            detail: Extra context - the value entered, filename, count, etc.
        """
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self._session_id,
            page,
            action,
            element,
            detail,
        ]
        with self._lock:
            try:
                with open(self._path, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(row)
            except OSError:
                pass  # usability logging must never crash the app


# Singleton instance for easy import
usage_log = UsageLogger()


# objectName() (set by each page's setObjectName()) -> human-readable page
# name for the usage log. Shared by MainWindow's central navigation hook
# and by any reusable widget (help buttons, ...) that needs to know which
# page it's currently sitting in without being told explicitly.
PAGE_DISPLAY_NAMES = {
    "HomePage": "Home",
    "MetadataPage": "Projects",
    "DataPage": "Data",
    "ForecastingPage": "Forecasting",
    "TrainingPage": "Training",
    "DashboardPage": "Dashboard",
    "SettingsPage": "Settings",
    "HelpPage": "Help",
    "Table1Page": "Table 1",
}


def infer_page_name(widget) -> str:
    """Walk a widget's parent chain up to the nearest page, for usage-log
    events raised from shared widgets (help buttons, ...) that don't know
    their page by themselves. Returns "Unknown" if none is found (e.g. the
    widget isn't attached to the window yet)."""
    w = widget
    while w is not None:
        name = PAGE_DISPLAY_NAMES.get(w.objectName())
        if name:
            return name
        w = w.parent()
    return "Unknown"

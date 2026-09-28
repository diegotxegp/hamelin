"""
Tests for MainWindow's navigation sidebar.

Covers two regressions:
- "Models" used to be added as a plain navigationInterface.addItem()
  placeholder, then swapped for a real addSubInterface() page on first
  click by removing and re-adding it - which appended it to the end of the
  sidebar instead of leaving it where it started (see main_window.py's
  _LazyPage / _open_interface_page).
- Dashboard is temporarily removed from the nav, but dashboard_page itself
  must keep working in the background (set_data_model, refresh, etc. are
  still called on it from elsewhere in MainWindow).
"""
import os
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("PySide6.QtWidgets")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from hamelin.view.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(qapp):
    return MainWindow()


def _nav_order(window):
    return list(window.navigationInterface.items.keys())


def test_dashboard_is_not_in_the_nav(window):
    assert not any("dashboard" in k.lower() for k in _nav_order(window))


def test_dashboard_page_still_works_in_the_background(window):
    # Object still exists and responds to updates even though it's not
    # reachable from the sidebar.
    assert hasattr(window, "dashboard_page")
    window.dashboard_page.refresh()  # must not raise


def test_models_item_is_between_training_and_forecasting(window):
    order = _nav_order(window)
    assert order.index("TrainingPage") < order.index("modelsPage") < order.index("ForecastingPage")


def test_models_nav_position_survives_first_visit(window, monkeypatch):
    before = _nav_order(window)

    # No project open: _open_interface_page() returns early (InfoBar
    # warning), same as before this fix - the nav item still must not move.
    window.switchTo(window.models_page)

    assert _nav_order(window) == before


def test_models_nav_position_survives_loading_the_real_dashboard(window):
    proj = Path(tempfile.mkdtemp())
    (proj / "model_checkpoints").mkdir()
    window.training_page._project_dir = proj

    before = _nav_order(window)
    window.switchTo(window.models_page)  # triggers the full first-load path

    assert _nav_order(window) == before
    assert window.models_page.layout() is not None
    assert window.models_page.layout().count() > 0
    assert hasattr(window, "interface_page")


def test_models_nav_position_survives_revisits(window):
    proj = Path(tempfile.mkdtemp())
    (proj / "model_checkpoints").mkdir()
    window.training_page._project_dir = proj

    window.switchTo(window.models_page)
    before = _nav_order(window)

    window.switchTo(window.home_page)
    window.switchTo(window.models_page)
    window.switchTo(window.home_page)
    window.switchTo(window.models_page)

    assert _nav_order(window) == before
    # exactly one "modelsPage" entry - no duplicate item was inserted
    assert _nav_order(window).count("modelsPage") == 1

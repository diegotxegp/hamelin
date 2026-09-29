"""
Tests for MainWindow's navigation sidebar.

Covers:
- Evaluation and Prediction are real nav pages, in that order, between
  Training and Forecasting, and visiting them never reshuffles the sidebar.
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


def test_evaluation_and_predict_sit_between_training_and_forecasting(window):
    order = _nav_order(window)
    assert (
        order.index("TrainingPage")
        < order.index("EvaluationPage")
        < order.index("PredictionPage")
        < order.index("ForecastingPage")
    )


def test_no_legacy_models_item(window):
    assert "modelsPage" not in _nav_order(window)


def test_nav_order_survives_visiting_the_new_pages(window):
    proj = Path(tempfile.mkdtemp())
    (proj / "results" / "models").mkdir(parents=True)
    window.evaluation_page.set_project_dir(proj)
    window.prediction_page.set_project_dir(proj)
    before = _nav_order(window)

    for _ in range(2):
        window.switchTo(window.evaluation_page)
        window.switchTo(window.prediction_page)
        window.switchTo(window.home_page)

    assert _nav_order(window) == before
    assert before.count("EvaluationPage") == 1
    assert before.count("PredictionPage") == 1


def test_duplicate_request_prefills_and_opens_training(window):
    payload = {
        "based_on": "m1", "new_run_name": "m1_copy",
        "config": {"input_features": [{"name": "a", "type": "number"}],
                   "output_features": [{"name": "y", "type": "binary"}]},
    }
    window.evaluation_page.duplicate_requested.emit(payload)
    assert window.training_page.model_name_edit.text() == "m1_copy"
    assert window.stackedWidget.currentWidget() is window.training_page

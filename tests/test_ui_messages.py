"""Trigger the warning/error banners of every page whose texts now come from
strings.py and check they render with their arguments filled in."""
import csv

import pytest
from pathlib import Path
from PySide6.QtWidgets import QFileDialog

from hamelin.utils import usage_logger


@pytest.fixture(autouse=True)
def _capture(monkeypatch):
    usage_logger.install_infobar_logging()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: ("", "")))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: ("", "")))


def _banners(start: int):
    with open(usage_logger.usage_log._path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["action"] in ("warning_shown", "error_shown")]
    return rows[start:]


def _count():
    with open(usage_logger.usage_log._path, encoding="utf-8") as f:
        return sum(1 for r in csv.DictReader(f) if r["action"] in ("warning_shown", "error_shown"))


def _assert_clean(rows):
    for r in rows:
        assert "{" not in r["element"] + r["detail"], r          # unformatted placeholder
        assert r["element"].strip(), r


def test_training_guards_show_readable_banners(qtbot, tmp_path):
    from hamelin.view.pages.training_page import TrainingPage

    page = TrainingPage()
    qtbot.addWidget(page)
    n = _count()
    page._start_training()                       # no dataset loaded
    page.model_name_edit.setText("")
    page._export_model()                          # nothing trained
    rows = _banners(n)
    assert [r["element"] for r in rows][:2] == ["No dataset loaded", "No trained model"]
    _assert_clean(rows)


def test_data_page_messages(qtbot):
    from hamelin.view.pages.data_page import DataPage

    page = DataPage()
    qtbot.addWidget(page)
    n = _count()
    page._on_load_clicked()                       # no project open
    page._project_dir = Path(".")
    page._on_load_clicked()                       # no file selected
    page._generate_quality_report()              # no dataset
    page._exclude_outliers()                      # no dataset -> silent return
    rows = _banners(n)
    assert [r["element"] for r in rows][:2] == ["No project open", "No File Selected"]
    _assert_clean(rows)


def test_forecasting_and_metadata_messages(qtbot):
    from hamelin.view.pages.forecasting_page import ForecastingPage
    from hamelin.view.pages.metadata_page import MetadataPage

    n = _count()
    f = ForecastingPage()
    qtbot.addWidget(f)
    f._generate_forecast()                        # no data loaded
    m = MetadataPage()
    qtbot.addWidget(m)
    m._on_new_project()
    m._save_metadata()                            # empty form
    rows = _banners(n)
    assert [r["element"] for r in rows] == ["No Data Loaded", "Validation Error"]
    _assert_clean(rows)

"""Exports default to a subfolder of the active project's results/ folder."""
from pathlib import Path

import pytest

from hamelin.utils.export_paths import default_export_path


def test_no_project_keeps_bare_filename():
    assert default_export_path(None, "tables", "Table1.csv") == "Table1.csv"
    assert default_export_path("/does/not/exist", "tables", "Table1.csv") == "Table1.csv"


def test_project_gets_results_subfolder_created_on_demand(tmp_path):
    out = default_export_path(tmp_path, "tables", "Table1.csv")
    assert Path(out) == tmp_path / "results" / "tables" / "Table1.csv"
    assert (tmp_path / "results" / "tables").is_dir()


def test_unknown_kind_rejected(tmp_path):
    with pytest.raises(ValueError):
        default_export_path(tmp_path, "misc", "x.csv")


def test_table1_export_dialog_opens_in_project(qtbot, tmp_path, monkeypatch):
    from hamelin.view.pages import table1_page

    captured = {}

    def fake_dialog(parent, caption, path, filt):
        captured["path"] = path
        return "", ""  # user cancels

    monkeypatch.setattr(table1_page.QFileDialog, "getSaveFileName", fake_dialog)
    page = table1_page.Table1Page()
    qtbot.addWidget(page)
    page._generator = object()  # any non-None generator reaches the dialog
    page.set_project_dir(tmp_path)
    page._export_table1()
    assert Path(captured["path"]) == tmp_path / "results" / "tables" / "Table1.csv"

    page.set_project_dir(None)
    page._export_table1()
    assert captured["path"] == "Table1.csv"

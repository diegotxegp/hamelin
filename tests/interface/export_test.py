"""Tests for utils/export.py - the PNG/PDF/CSV export helpers."""
from pathlib import Path

import pytest
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from hamelin.interface.utils import export as export_mod
from hamelin.interface.utils.export import (
    _render_image, _report_pdf, export_chart_and_data, export_csv,
)


def _tall_table(rows=50, cols=3):
    t = QTableWidget(rows, cols)
    for r in range(rows):
        for c in range(cols):
            t.setItem(r, c, QTableWidgetItem(f"r{r}c{c}"))
    t.resize(600, 1600)
    return t


def test_render_image_png_from_widget(qtbot, tmp_path):
    t = _tall_table()
    qtbot.addWidget(t)
    out = tmp_path / "grab.png"
    _render_image(t, out)
    assert out.stat().st_size > 500


def test_render_image_pdf_paginates_tall_widget(qtbot, tmp_path):
    t = _tall_table(rows=120)
    qtbot.addWidget(t)
    out = tmp_path / "grab.pdf"
    _render_image(t, out)
    data = out.read_bytes()
    assert data[:4] == b"%PDF"
    # a 120-row grab is well over one A4 page
    assert data.count(b"/Type /Page") >= 2 or data.count(b"/Type/Page") >= 2


def test_render_image_pdf_from_matplotlib_figure(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [2, 3, 1])
    out = tmp_path / "fig.pdf"
    _render_image(fig, out)
    assert out.read_bytes()[:4] == b"%PDF"


def test_report_pdf_writes_a_pdf_with_the_title(tmp_path):
    out = tmp_path / "report.pdf"
    _report_pdf(out, "Model report", ["field", "value"],
                [("Project", "P1"), ("Accuracy", 0.9), ("Note", None)])
    assert out.read_bytes()[:4] == b"%PDF"


def test_export_chart_and_data_writes_chosen_format_plus_csv(qtbot, tmp_path, monkeypatch):
    t = _tall_table()
    qtbot.addWidget(t)
    target = tmp_path / "out.pdf"
    monkeypatch.setattr(
        export_mod.QFileDialog, "getSaveFileName",
        staticmethod(lambda *a, **k: (str(target), "PDF Document (*.pdf)")),
    )
    monkeypatch.setattr(export_mod, "Toast", lambda *a, **k: type("T", (), {"show": lambda self: None})())

    export_chart_and_data(t, "x", t, ["a", "b", "c"], [(1, 2, 3), (4, 5, 6)])

    assert target.exists() and target.read_bytes()[:4] == b"%PDF"
    csv_path = target.with_suffix(".csv")
    assert csv_path.exists()
    assert "a,b,c" in csv_path.read_text()


def test_export_csv_pdf_branch(qtbot, tmp_path, monkeypatch):
    target = tmp_path / "rep.pdf"
    monkeypatch.setattr(
        export_mod.QFileDialog, "getSaveFileName",
        staticmethod(lambda *a, **k: (str(target), "PDF Document (*.pdf)")),
    )
    monkeypatch.setattr(export_mod, "Toast", lambda *a, **k: type("T", (), {"show": lambda self: None})())

    export_csv(None, "model_report", ["field", "value"],
               [("Model", "m1"), ("Accuracy", 0.91)], title="Model report - m1")

    assert target.read_bytes()[:4] == b"%PDF"


def test_export_csv_csv_branch(qtbot, tmp_path, monkeypatch):
    target = tmp_path / "rep.csv"
    monkeypatch.setattr(
        export_mod.QFileDialog, "getSaveFileName",
        staticmethod(lambda *a, **k: (str(target), "CSV File (*.csv)")),
    )
    monkeypatch.setattr(export_mod, "Toast", lambda *a, **k: type("T", (), {"show": lambda self: None})())

    export_csv(None, "model_report", ["field", "value"], [("Model", "m1")])

    assert "field,value" in target.read_text()
    assert "Model,m1" in target.read_text()

"""Evaluation page features carried over from the old dashboard: metrics
with confidence intervals, favourites, notes, comparison views, config diff,
deleting models, model-type content and the arrow-only cursor."""
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from PySide6.QtCore import Qt

from hamelin.analytics import eval_data as ed
from hamelin.core.model_history import ModelHistory, ModelTraining, models_dir


def _make_model(project: Path, name: str, acc: float, auc: float, lr: float = 0.001) -> ModelTraining:
    folder = models_dir(project) / name
    folder.mkdir(parents=True)
    (folder / "model_hyperparameters.json").write_text(json.dumps({
        "input_features": [{"name": "age", "type": "number"}, {"name": "sex", "type": "category"}],
        "output_features": [{"name": "y", "type": "binary"}],
    }))
    report = {
        "metrics": {"test": {"y": {"accuracy": {"best": acc, "last": acc}, "roc_auc": {"best": auc, "last": auc},
                                    "loss": {"best": 1 - acc, "last": 1 - acc}}}},
        "config": {"trainer": {"learning_rate": lr}, "output_features": [{"name": "y", "column": "y", "type": "binary"}]},
        "data_schema": {"input_features": [{"name": "age"}, {"name": "sex"}],
                        "output_features": [{"name": "y", "type": "binary"}]},
    }
    (folder / "training_report.json").write_text(json.dumps(report))
    rows = ["y_true,y_pred,y_score,y_prob_0,y_prob_1,sex"]
    for i in range(40):
        t_, p_ = i % 2, (i % 2) if i % 5 else 1 - i % 2
        rows.append(f"{t_},{p_},0.8,{0.2 if p_ else 0.8},{0.8 if p_ else 0.2},{'F' if i % 3 else 'M'}")
    (folder / "test_predictions.csv").write_text("\n".join(rows))
    rec = ModelTraining(target_variable="y", model_type="Ludwig/MLP", num_samples=100, num_features=2,
                        test_metrics={"accuracy": acc, "roc_auc": auc}, model_name=name,
                        checkpoint_path=str(folder), timestamp=datetime(2026, 1, 1))
    ModelHistory(project).add_training(rec)
    return rec


@pytest.fixture
def project(tmp_path):
    (tmp_path / "metadata.json").write_text(json.dumps({"name": "Demo", "primary_objective": "Predict y"}))
    _make_model(tmp_path, "m1", 0.80, 0.85)
    _make_model(tmp_path, "m2", 0.70, 0.75, lr=0.5)
    return tmp_path


def test_flat_metrics_from_report_and_fallback(project):
    rec = ModelHistory(project).list_trainings()[0]
    names, keys = ed.split_metrics(ed.flat_metrics(rec), "test")
    assert {"accuracy", "roc_auc", "loss"} <= set(names)
    # no report on disk -> rebuilt from the stored metrics
    (Path(rec.checkpoint_path) / "training_report.json").unlink()
    names, _ = ed.split_metrics(ed.flat_metrics(rec), "test")
    assert {"accuracy", "roc_auc"} <= set(names)


def test_favorites_and_notes_roundtrip(project):
    d = models_dir(project)
    assert ed.toggle_favorite(d, "m1") is True
    assert ed.load_favorites(d) == {"m1"}
    assert ed.toggle_favorite(d, "m1") is False
    rec = ModelHistory(project).get_training(next(r.model_id for r in ModelHistory(project).list_trainings()
                                                  if r.model_name == "m1"))
    assert ed.save_note(rec, "  hello  ") and ed.load_note(rec) == "hello"
    assert ed.save_note(rec, "") and ed.load_note(rec) == ""


def test_subgroup_table_and_roc(project):
    rec = ModelHistory(project).list_trainings()[0]
    df = pd.read_csv(Path(rec.checkpoint_path) / "test_predictions.csv")
    rows = ed.subgroup_table(df, "sex")
    assert {r["group"] for r in rows} == {"F", "M"} and all(r["small"] for r in rows)
    fpr, tpr, auc = ed.roc_points(df)
    assert 0 <= auc <= 1 and len(fpr) == len(tpr)


def test_comparison_ranks_and_lower_is_better(project):
    recs = ModelHistory(project).list_trainings()
    rows, names, keys = ed.build_comparison(recs, "test")
    assert {r["model"] for r in rows} == {"m1", "m2"}
    assert ed.is_lower_better("loss") and not ed.is_lower_better("accuracy")


def test_inspect_panel_tiles_confidence_interval_and_matrix(qtbot, project):
    from hamelin.view.widgets.eval_inspect_panel import ModelInspectPanel

    rec = ModelHistory(project).list_trainings()[0]
    panel = ModelInspectPanel()
    qtbot.addWidget(panel)
    panel.load(rec, project)
    assert panel.tiles_grid.count() == 3          # accuracy, loss, roc_auc
    assert panel._cm is not None and panel.cm_table.rowCount() == 2
    assert [panel.group_combo.itemText(i) for i in range(panel.group_combo.count())] == ["None", "sex"]
    before = panel._cm["matrix"]
    panel.threshold_spin.setValue(90)             # threshold re-classifies rows
    assert panel._cm["matrix"] != before
    panel.group_combo.setCurrentIndex(1)
    assert panel.subgroup_table.rowCount() == 2
    panel.notes.setPlainText("note")
    panel.flush_note()
    assert ed.load_note(rec) == "note"


def test_compare_panel_draws_every_view_and_diff(qtbot, project):
    from hamelin.view.widgets.eval_compare_panel import ModelComparePanel, _ConfigDiffDialog

    recs = ModelHistory(project).list_trainings()
    panel = ModelComparePanel()
    qtbot.addWidget(panel)
    panel.set_records(recs, project, models_dir(project))
    panel.select(["m1", "m2"])
    assert len(panel._selected()) == 2 and panel.diff_btn.isEnabled()
    for view in ("table", "graph", "heatmap", "radar"):
        panel._set_view(view)
    panel.ci_check.setChecked(True)
    panel._toggle_split()
    dlg = _ConfigDiffDialog(panel, project, *panel._selected())
    assert any(d["key"] == "trainer.learning_rate" for d in dlg._diffs)
    panel.select(["m1"])
    assert not panel.diff_btn.isEnabled()


def test_page_delete_removes_record_and_folder(qtbot, project):
    from hamelin.view.pages.evaluation_page import EvaluationPage

    page = EvaluationPage()
    qtbot.addWidget(page)
    page.set_project_dir(project)
    ed.toggle_favorite(models_dir(project), "m1")
    victims = [r for r in page._records if ed.model_label(r) not in page._favorites()]
    assert [r.model_name for r in victims] == ["m2"]
    page._delete(victims)
    assert not (models_dir(project) / "m2").exists()
    assert [r.model_name for r in ModelHistory(project).list_trainings()] == ["m1"]
    assert (models_dir(project) / "m1").exists()


def test_describe_architecture_reads_saved_config(tmp_path):
    import json
    from hamelin.analytics.architecture import describe_architecture

    cfg = {
        "combiner": {"type": "ft_transformer", "num_layers": 2, "num_heads": 8},
        "input_features": [{"type": "number", "encoder": {"type": "passthrough"}}],
        "output_features": [{"type": "binary", "decoder": {"type": "regressor"}}],
        "trainer": {"optimizer": {"type": "adam"}, "learning_rate": 0.001, "batch_size": 256, "epochs": 100},
    }
    (tmp_path / "model_hyperparameters.json").write_text(json.dumps(cfg))
    rows = dict(describe_architecture(tmp_path))
    assert "FT-Transformer" in rows["Combiner"]
    assert rows["Batch size"] == "256" and rows["Max. epochs"] == "100"
    assert "adam" in rows["Optimizer"]
    assert describe_architecture(tmp_path / "missing") == []


def test_arrow_cursor_filter_resets_pointing_hand(qtbot):
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import QApplication, QWidget
    from hamelin.view.widgets import ArrowCursorFilter

    app = QApplication.instance()
    flt = ArrowCursorFilter(app)
    w = QWidget()
    qtbot.addWidget(w)
    w.setCursor(Qt.CursorShape.PointingHandCursor)
    flt.eventFilter(w, QEvent(QEvent.Type.Enter))
    assert w.cursor().shape() == Qt.CursorShape.ArrowCursor
    w.setCursor(Qt.CursorShape.IBeamCursor)
    flt.eventFilter(w, QEvent(QEvent.Type.Enter))
    assert w.cursor().shape() == Qt.CursorShape.IBeamCursor


def test_theme_subscription_survives_deleted_widgets(qtbot):
    """A destroyed widget must not make later theme switches raise."""
    from qfluentwidgets import BodyLabel, qconfig
    from hamelin.utils.theme_colors import bind_style

    label = BodyLabel("x")
    bind_style(label, lambda c: f"color: {c.text_secondary};")
    import shiboken6
    shiboken6.delete(label)
    qconfig.themeChanged.emit(qconfig.theme)   # would raise RuntimeError before the fix
    qconfig.themeChanged.emit(qconfig.theme)


def test_local_time_converts_stored_utc(project):
    """ModelTraining stores naive UTC; the UI shows it in the user's zone."""
    from datetime import datetime, timezone

    rec = ModelHistory(project).list_trainings()[0]
    expected = rec.timestamp.replace(tzinfo=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    assert ed.local_time(rec) == expected


def test_patients_dialog_hides_probability_columns(qtbot):
    from PySide6.QtWidgets import QTableWidget
    from hamelin.view.widgets.eval_inspect_panel import _PatientsDialog

    rows = [{"age": 50, "y_prob_0": 0.4, "y_prob_1": 0.6, "_true_label": "1", "_predicted_label": "0", "_confidence": 0.55}]
    dlg = _PatientsDialog(None, "1", "0", rows)
    qtbot.addWidget(dlg)
    table = dlg.findChild(QTableWidget)
    headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
    assert headers == ["age", "True", "Predicted", "Confidence"]


def test_window_never_exceeds_the_screen(qtbot, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from hamelin.utils.config_manager import config
    from hamelin.view.main_window import MainWindow

    avail = QApplication.primaryScreen().availableGeometry()
    real_get = config.get
    monkeypatch.setattr(config, "get", lambda k, d=None: {"ui.window.width": avail.width() + 500,
                                                            "ui.window.height": avail.height() + 500}.get(k, real_get(k, d)))
    w = MainWindow()
    qtbot.addWidget(w)
    # leaves room for the OS title bar / borders, so strictly inside the screen
    # (unless the pages' own minimum size is larger than that margin)
    assert w.width() <= max(int(avail.width() * 0.94), w.minimumSizeHint().width())
    assert w.height() <= max(int(avail.height() * 0.90), w.minimumSizeHint().height())


def test_fast_bootstrap_matches_the_slow_reference_and_is_fast():
    import time

    import numpy as np
    from hamelin.interface.utils.bootstrap_ci import bootstrap_ci

    rng = np.random.default_rng(1)
    n = 154
    cls = pd.DataFrame({"y_true": rng.integers(0, 2, n)})
    cls["y_pred"] = np.where(rng.random(n) < 0.75, cls["y_true"], 1 - cls["y_true"])
    y = rng.normal(50, 10, n)
    reg = pd.DataFrame({"y_true": y, "y_pred": y + rng.normal(0, 4, n)})

    for df, metric in ((cls, "accuracy"), (reg, "r2"), (reg, "root_mean_squared_error"), (reg, "mean_absolute_error")):
        p_slow, lo_slow, hi_slow = bootstrap_ci(df, metric, n_bootstrap=400)
        t0 = time.perf_counter()
        p_fast, lo, hi = ed.bootstrap_ci_fast(df, metric)
        assert time.perf_counter() - t0 < 0.5
        assert p_fast == pytest.approx(p_slow)
        assert lo < p_fast < hi
        assert lo == pytest.approx(lo_slow, abs=0.05 * max(1, abs(p_fast)))
        assert hi == pytest.approx(hi_slow, abs=0.05 * max(1, abs(p_fast)))

    assert ed.bootstrap_ci_fast(cls, "roc_auc") == (None, None, None)          # unsupported metric
    assert ed.bootstrap_ci_fast(cls.head(5), "accuracy") == (None, None, None)  # too few rows


def test_data_preview_table_is_filled_correctly_and_fast(qtbot):
    import time

    import numpy as np
    from hamelin.view.pages.data_page import DataPage

    page = DataPage()
    qtbot.addWidget(page)
    df = pd.DataFrame(np.arange(4000 * 30).reshape(4000, 30)).astype(str)
    page.data_table.setRowCount(len(df))
    page.data_table.setColumnCount(df.shape[1])
    t0 = time.perf_counter()
    page._fill_preview_table(df)
    assert time.perf_counter() - t0 < 3.0          # was ~25 s with per-cell df.iloc
    assert page.data_table.item(0, 0).text() == "0"
    assert page.data_table.item(3999, 29).text() == str(4000 * 30 - 1)


def test_config_no_longer_carries_unused_model_keys():
    from hamelin.utils.config_manager import ConfigManager

    cfg = ConfigManager.__new__(ConfigManager)
    defaults = ConfigManager._get_defaults(cfg)
    assert "ui" in defaults and "model" not in defaults


def test_window_size_is_remembered_between_launches(qtbot):
    from hamelin.utils.config_manager import config
    from hamelin.view.main_window import MainWindow

    w = MainWindow()
    qtbot.addWidget(w)
    w.resize(1000, 720)
    width, height = w.width(), w.height()      # the page minimums may enlarge the request
    w.close()
    assert (config.get("ui.window.width"), config.get("ui.window.height")) == (width, height)
    assert config.get("ui.window.maximized") is False
    saved = config.config_file.read_text(encoding="utf-8")
    assert f"width: {width}" in saved and f"height: {height}" in saved       # written to disk
    assert config.config_file.parent != Path("workspace/config").resolve()  # never the real one


def test_transparent_container_keeps_a_tooltip_rule_after_the_transparent_one(qtbot):
    from PySide6.QtWidgets import QWidget
    from hamelin.view.widgets.theme_colors import apply_transparent_container

    w = QWidget()
    qtbot.addWidget(w)
    apply_transparent_container(w)
    sheet = w.styleSheet()
    assert "QToolTip" in sheet and sheet.index("QToolTip") > sheet.index("transparent")
    assert "background-color" in sheet[sheet.index("QToolTip"):]


def test_export_file_dialogs_use_the_top_level_window_as_parent(qtbot, monkeypatch, tmp_path):
    """A dialog parented to a widget inside a page inherits the page's
    transparent stylesheet and comes out see-through."""
    from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QWidget
    from hamelin.view.widgets import eval_export

    seen = []
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        staticmethod(lambda parent, *a, **k: (seen.append(parent) or ("", ""))))
    top = QWidget()
    qtbot.addWidget(top)
    inner = QWidget(top)
    QVBoxLayout(top).addWidget(inner)
    eval_export.export_report(inner, tmp_path, "x", ["a"], [[1]])
    eval_export.export_chart_and_data(inner, tmp_path, "x", inner, ["a"], [[1]])
    assert seen == [top, top]

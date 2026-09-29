"""Dataset change record, Training-page predictor/outcome sync and form persistence,
locked navigation entries, lazy help sections, deferred heavy imports."""
import json

import pandas as pd
import pytest

from hamelin.core import dataset_changes as dc
from hamelin.model.data_model import DataModel


def _model(tmp_path):
    csv = tmp_path / "study.csv"
    pd.DataFrame({"a": range(10), "b": list("xyxyxyxyxy"), "c": [1.0] * 10}).to_csv(csv, index=False)
    dm = DataModel()
    dm.load_from_file(csv)
    return dm


def test_changes_record_lists_every_change_and_never_touches_the_file(tmp_path):
    dm = _model(tmp_path)
    project = tmp_path / "proj"
    before = (tmp_path / "study.csv").read_bytes()

    dm.save_state(project)                                     # nothing changed yet
    dm.excluded_rows.update({0, 3})
    dm._change_reason = "duplicate rows (first occurrence kept)"
    dm.save_state(project)
    dm.excluded_columns.add("c")
    dm.set_column_type("b", "binary")
    dm.save_state(project)
    dm.excluded_rows.clear()
    dm.save_state(project)

    rec = json.loads(dc.changes_path(project, dm.filepath).read_text())
    assert rec["original"] == {"rows": 10, "columns": 3}
    assert rec["in_use"] == {"rows": 10, "columns": 2}
    assert rec["columns_removed"] == ["c"]
    assert rec["variable_types_overridden"] == {"b": "binary"}
    actions = [h["action"] for h in rec["history"]]
    assert actions == ["rows_removed", "columns_removed", "type_changed", "rows_restored"]
    assert rec["history"][0]["items"] == [1, 4] and "duplicate" in rec["history"][0]["detail"]
    assert (tmp_path / "study.csv").read_bytes() == before


def test_history_survives_reloading_the_dataset(tmp_path):
    dm = _model(tmp_path)
    project = tmp_path / "proj"
    dm.excluded_rows.add(2)
    dm.save_state(project)

    again = _model(tmp_path)
    again.load_state(project)
    again.excluded_columns.add("a")
    again.save_state(project)
    rec = dc.load_record(project, again.filepath)
    assert [h["action"] for h in rec["history"]] == ["rows_removed", "columns_removed"]


def test_record_is_copied_into_the_model_folder(tmp_path):
    dm = _model(tmp_path)
    project = tmp_path / "proj"
    dm.excluded_rows.add(1)
    dm.save_state(project)
    model_dir = project / "results" / "models" / "m1"
    dc.copy_to_model(project, dm.filepath, model_dir)
    assert json.loads((model_dir / dc.MODEL_COPY_NAME).read_text())["rows_removed"]["count"] == 1


@pytest.fixture
def page(qtbot):
    from hamelin.view.pages.training_page import TrainingPage
    p = TrainingPage()
    qtbot.addWidget(p)
    return p


def _dm(tmp_path):
    dm = _model(tmp_path)
    return dm


def test_outcome_is_removed_from_predictors_and_returns_when_changed(page, tmp_path):
    page.set_data_model(_dm(tmp_path))
    names = lambda: [page.features_list.item(i).text() for i in range(page.features_list.count())]
    page.primary_combo.setCurrentIndex(page.primary_combo.findText("b"))
    assert "b" not in names() and {"a", "c"} <= set(names())
    page.features_list.item(0).setSelected(True)
    kept = page.features_list.item(0).text()
    page.primary_combo.setCurrentIndex(page.primary_combo.findText("a"))
    assert "a" not in names() and "b" in names()
    assert kept == "a" or kept in [i.text() for i in page.features_list.selectedItems()]


def test_class_balance_is_a_plain_checkbox_that_toggles(page):
    from qfluentwidgets import CheckBox
    assert isinstance(page.class_balance_switch, CheckBox)
    page.class_balance_switch.setChecked(True)
    assert page._collect_config_fields().get("class_imbalance") is True


def test_model_configuration_is_remembered_per_project(page, tmp_path):
    page.time_budget.setValue(900)
    page.random_seed.setValue(7)
    page.early_stop_mode.setCurrentIndex(1)
    page.class_balance_switch.setChecked(True)
    saved = page._collect_form_state()
    page.time_budget.setValue(300)
    page.random_seed.setValue(1)
    page.early_stop_mode.setCurrentIndex(0)
    page.class_balance_switch.setChecked(False)
    page._restore_form_state(saved)
    assert page.time_budget.value() == 900 and page.random_seed.value() == 7
    assert page.early_stop_mode.currentIndex() == 1 and page.class_balance_switch.isChecked()


def test_prediction_and_forecasting_are_locked_in_the_nav(qtbot):
    from hamelin.view.main_window import MainWindow
    w = MainWindow()
    qtbot.addWidget(w)
    nav = w.navigationInterface
    assert not nav.widget(w.prediction_page.objectName()).isEnabled()
    assert not nav.widget(w.forecasting_page.objectName()).isEnabled()
    assert nav.widget(w.evaluation_page.objectName()).isEnabled()


def test_help_sections_build_their_content_only_when_opened(qtbot):
    from hamelin.view.pages.help_page import HelpPage
    h = HelpPage()
    qtbot.addWidget(h)
    card = h._section_cards[0]
    assert card._body_layout.count() == 0
    card.expand()
    assert card._body_layout.count() > 0


def test_heavy_libraries_are_not_imported_at_startup():
    import subprocess, sys
    code = ("import sys; from PySide6.QtWidgets import QApplication; a=QApplication([]);"
            "import hamelin.view.main_window;"
            "print([m for m in ('ludwig','torch','scipy.stats','sklearn') if m in sys.modules])")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         env={**__import__("os").environ, "QT_QPA_PLATFORM": "offscreen"}).stdout
    assert out.strip().splitlines()[-1] == "[]"


def test_time_limit_of_100_seconds_can_be_typed_and_applies_at_once(page, qtbot):
    from PySide6.QtCore import Qt
    seen = []
    page.time_budget.valueChanged.connect(seen.append)
    page.time_budget.lineEdit().selectAll()
    qtbot.keyClicks(page.time_budget.lineEdit(), "100")
    assert page.time_budget.value() == 100 and seen[-1] == 100      # no Enter needed
    assert page._collect_form_state()["time_budget"] == 100


def test_settings_apply_and_persist_at_once(qtbot):
    import pandas as pd
    from hamelin.utils.config_manager import config
    from hamelin.view.pages.settings_page import SettingsPage
    from hamelin.analytics.table1_generator import Table1Generator

    page = SettingsPage()
    qtbot.addWidget(page)
    page._decimals_spin.setValue(4)
    assert config.get("table1.decimal_places") == 4
    gen = Table1Generator(pd.DataFrame({"x": [1.0, 2.0, 3.0]}))
    assert gen._format_continuous(pd.Series([1.0, 2.0, 4.0]), True).startswith("2.3333 ±")
    page._decimals_spin.setValue(0)
    assert gen._format_continuous(pd.Series([1.0, 2.0, 4.0]), True).startswith("2 ±")

    page._log_level_combo.setCurrentText("WARNING")
    assert config.get("app.log_level") == "WARNING"
    page._log_level_combo.setCurrentText("INFO")

from hamelin.interface.widgets.visualise_comparison_table import VisualiseComparisonWidget
from hamelin.interface.utils.app_state import app_state


def test_table_has_star_and_model_columns(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)  # bypass the simple-mode priority gate
    widget.set_data(models, None)

    assert widget.table.horizontalHeaderItem(0).text() == "★"
    assert widget.table.horizontalHeaderItem(1).text() == "Model"
    assert widget.table.rowCount() == len(models)


def test_clicking_star_toggles_favorite_and_colors_star_and_name(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    was_favorite = favorites.is_favorite(widget.data[0]["model"])
    widget.on_cell_clicked(0, 0)

    assert favorites.is_favorite(widget.data[0]["model"]) is (not was_favorite)
    star_color = widget.table.item(0, 0).foreground().color().name()
    name_color = widget.table.item(0, 1).foreground().color().name()
    expected = "#e0dd6c" if not was_favorite else "#121010"
    assert star_color == expected
    assert name_color == expected

    # restore so this test doesn't leak state via favorites.json
    widget.on_cell_clicked(0, 0)
    assert favorites.is_favorite(widget.data[0]["model"]) is was_favorite


def test_clicking_a_non_star_column_does_not_toggle_favorite(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    widget.set_data(models, None)

    before = favorites.load_favorites()
    widget.on_cell_clicked(0, 1)  # the model-name column, not the star
    assert favorites.load_favorites() == before


def test_favorite_state_persists_after_rebuilding_the_table(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    widget.on_cell_clicked(0, 0)
    model_name = widget.data[0]["model"]
    is_fav_now = favorites.is_favorite(model_name)

    widget.update_ui()  # simulate a re-sort / rebuild

    row_idx = next(i for i, row in enumerate(widget.data) if row["model"] == model_name)
    expected_color = "#e0dd6c" if is_fav_now else "#121010"
    assert widget.table.item(row_idx, 0).foreground().color().name() == expected_color

    # restore
    widget.on_cell_clicked(row_idx, 0)


def test_clicking_a_metric_header_sorts_by_that_metric(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models or len(models) < 2:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    widget.on_header_clicked(2)  # first metric column

    # display_metrics_keys, not metrics_keys - column 2 maps to
    # display_metrics_keys[0] (identical to metrics_keys here since advanced
    # mode shows every metric unfiltered, but the column-index mapping goes
    # through the display list either way).
    assert widget.criterion == widget.display_metrics_keys[0]
    values = [row.get(widget.criterion) for row in widget.data]
    numeric = [v for v in values if isinstance(v, (int, float))]
    assert numeric == sorted(numeric, reverse=True)


def test_clicking_the_star_header_does_not_crash_or_sort(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    widget.set_data(models, None)
    criterion_before = widget.criterion

    widget.on_header_clicked(0)

    assert widget.criterion == criterion_before


def test_resize_positions_info_button_bottom_right(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.set_data(models, None)
    widget.resize(900, 700)

    pos = widget.info_btn.pos()
    assert pos.x() == widget.table_card.width() - widget.info_btn.width() - 15
    assert pos.y() == 60


def test_popup_glossary_reflects_shown_metrics(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    widget.set_data(models, None)

    widget.show_popup()

    assert widget.popup is not None


# favorites_only toggle

def test_favorites_only_hides_non_favorited_rows(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    was_favorite = favorites.is_favorite(models[0])
    if not was_favorite:
        favorites.toggle_favorite(models[0])

    widget.favorites_only_btn.setChecked(True)

    assert widget.table.rowCount() == 1
    assert widget.data[0]["model"] == models[0]

    if not was_favorite:
        favorites.toggle_favorite(models[0])  # restore


def test_favorites_only_with_no_favorites_shows_no_rows(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    for m in models:
        if favorites.is_favorite(m):
            favorites.toggle_favorite(m)

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    widget.favorites_only_btn.setChecked(True)

    assert widget.table.rowCount() == 0


def test_unchecking_favorites_only_restores_all_rows(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    widget.favorites_only_btn.setChecked(True)
    widget.favorites_only_btn.setChecked(False)

    assert widget.table.rowCount() == len(models)


# split toggle (test / train)

def test_split_toggle_defaults_to_test(qtbot):
    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)

    assert widget.split == "test"
    assert widget.split_toggle_btn.isChecked() is False


def test_toggling_split_switches_to_training_metrics(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", lambda models, split="test": (
        [{"model": m} for m in models],
        ["accuracy"],
        [f"{split}/accuracy/best"],
    ))

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(["model_a"], None)

    assert widget.criterion == "test/accuracy/best"

    widget.split_toggle_btn.setChecked(True)

    assert widget.split == "training"
    assert widget.criterion == "training/accuracy/best"
    assert "Train" in widget.split_toggle_btn.text()

    widget.split_toggle_btn.setChecked(False)

    assert widget.split == "test"
    assert widget.criterion == "test/accuracy/best"


def _fake_build_comparison_data(models, split="test"):
    return (
        [{"model": "model_a", "test/accuracy/best": 0.9,
          "test/precision/best": 0.8, "test/roc_auc/best": 0.85}],
        ["accuracy", "precision", "roc_auc"],
        ["test/accuracy/best", "test/precision/best", "test/roc_auc/best"],
    )


# simple-mode priority gate

def test_simple_mode_shows_priority_gate_instead_of_the_table(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)

    assert widget.priority_selector.isVisibleTo(widget) is True
    assert widget.table_card.isVisibleTo(widget) is False
    # nothing rendered yet - the gate hasn't been answered
    assert widget.table.columnCount() == 0


def test_advanced_mode_skips_the_gate(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(True)
    widget.set_data(["model_a"], None)

    assert widget.priority_selector.isVisibleTo(widget) is False
    assert widget.table_card.isVisibleTo(widget) is True
    assert widget.table.columnCount() == 5  # star, model, accuracy, precision, roc_auc


def test_choosing_a_priority_reveals_the_table_and_is_remembered(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)

    widget.priority_selector._cards["precision"].mousePressEvent(None)

    assert widget.priority_selector.isVisibleTo(widget) is False
    assert widget.table_card.isVisibleTo(widget) is True
    # precision (priority) + roc_auc (has a quality scale) survive; accuracy
    # (neither) is dropped - star + model + 2 metric columns.
    assert widget.table.columnCount() == 4
    assert widget.display_metric_names == ["precision", "roc_auc"]
    # export/glossary still see the full, unfiltered set.
    assert widget.metric_names == ["accuracy", "precision", "roc_auc"]

    # a later set_data() (e.g. a new comparison launched from the same
    # session) doesn't re-ask - the choice is remembered for the page's life.
    widget.set_data(["model_a"], None)
    assert widget.priority_selector.isVisibleTo(widget) is False
    assert widget.table_card.isVisibleTo(widget) is True


def test_choosing_precision_puts_it_first_and_sorts_by_it(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)
    widget.priority_selector._cards["precision"].mousePressEvent(None)

    assert widget.display_metric_names[0] == "precision"
    assert widget.criterion == "test/precision/best"


def test_toggling_to_advanced_mode_bypasses_an_unanswered_gate(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)
    assert widget.priority_selector.isVisibleTo(widget) is True

    app_state.set_advanced_mode(True)

    assert widget.priority_selector.isVisibleTo(widget) is False
    assert widget.table_card.isVisibleTo(widget) is True
    assert widget.table.columnCount() == 5

    # back to simple mode - no priority was ever chosen, so the gate returns.
    app_state.set_advanced_mode(False)
    assert widget.priority_selector.isVisibleTo(widget) is True
    assert widget.table_card.isVisibleTo(widget) is False


# CI toggle

def _fake_build_comparison_data_with_accuracy(models, split="test"):
    return (
        [{"model": m, "test/accuracy/best": 0.9} for m in models],
        ["accuracy"],
        ["test/accuracy/best"],
    )


def test_ci_hidden_by_default(qtbot, monkeypatch):
    import pandas as pd
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data_with_accuracy)
    monkeypatch.setattr(vct.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(vct.gmp, "load_test_predictions", lambda p: pd.DataFrame({
        "y_true": ["yes"] * 15 + ["no"] * 15, "y_pred": ["yes"] * 12 + ["no"] * 18,
    }))

    app_state.set_advanced_mode(True)
    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_a"], None)

    assert widget.ci_toggle_btn.isChecked() is False
    assert "[" not in widget.table.item(0, 2).text()


def test_ci_shown_when_toggled_on(qtbot, monkeypatch):
    import pandas as pd
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data_with_accuracy)
    monkeypatch.setattr(vct.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(vct.gmp, "load_test_predictions", lambda p: pd.DataFrame({
        "y_true": ["yes"] * 15 + ["no"] * 15, "y_pred": ["yes"] * 12 + ["no"] * 18,
    }))

    app_state.set_advanced_mode(True)
    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_a"], None)

    widget.ci_toggle_btn.setChecked(True)

    cell_text = widget.table.item(0, 2).text()
    assert "[" in cell_text and "]" in cell_text
    assert widget.table.item(0, 2).toolTip() != ""


def test_ci_toggled_on_but_no_saved_predictions_shows_plain_value(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_table as vct

    monkeypatch.setattr(vct, "build_comparison_data", _fake_build_comparison_data_with_accuracy)
    monkeypatch.setattr(vct.gmp, "model_path_from_name", lambda m: "fake/path")
    # No test_predictions.csv for this run - the common case for anything
    # trained before that file existed.
    monkeypatch.setattr(vct.gmp, "load_test_predictions", lambda p: None)

    app_state.set_advanced_mode(True)
    widget = VisualiseComparisonWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_a"], None)

    widget.ci_toggle_btn.setChecked(True)

    assert widget.table.item(0, 2).text() == "0.900"

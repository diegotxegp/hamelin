from hamelin.interface.widgets.one_model import VisualiseOneModel, metric_name


# Pure helpers

def test_metric_name_normalizes_acc_and_accuracy():
    assert metric_name("test/foo/acc/best") == "accuracy"
    assert metric_name("test/foo/accuracy/best") == "accuracy"


def test_metric_name_leaves_other_names_alone():
    assert metric_name("test/foo/loss/best") == "loss"


# Favorite toggle

def test_favorite_button_reflects_selected_model(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    models = gmp.get_model_names()
    if not models:
        return

    widget.set_data(models[0])
    assert widget.favorite_btn.text() == "☆"

    widget._toggle_favorite()
    assert widget.favorite_btn.text() == "★"

    widget._toggle_favorite()
    assert widget.favorite_btn.text() == "☆"


def test_favorite_button_hidden_state_with_no_model(qtbot):
    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget._update_favorite_button(False)
    assert widget.favorite_btn.text() == "☆"


# Cards grid - simple mode narrows it to priority metrics

def _card_tile(widget, upper_label):
    # startswith, not == : in advanced mode a card's label gets its jargon
    # abbreviation appended in parentheses (e.g. "OVERALL ACCURACY
    # (ACCURACY)") - see VisualiseOneModel._populate_metric_cards.
    grid = widget.cards_grid
    for i in range(grid.count()):
        tile = grid.itemAt(i).widget()
        name_lbl = tile.layout().itemAt(0).widget()
        if name_lbl.text().startswith(upper_label):
            return tile
    return None


def _tile_value_label(tile):
    value_row = tile.layout().itemAt(1).layout()
    return value_row.itemAt(0).widget()


def test_all_reported_metrics_get_a_card(qtbot, monkeypatch):
    # No narrowing here - every metric this model reported gets its own
    # tile, regardless of the app-wide "Advanced mode" setting (that
    # setting still affects other pages, just not the count of cards here).
    import hamelin.interface.widgets.one_model as one_model_mod
    from hamelin.interface.utils.app_state import app_state

    fake_metrics = {
        "test/accuracy/best": 0.9,
        "test/precision/best": 0.8,
        "test/recall/best": 0.7,
        "test/roc_auc/best": 0.85,
    }
    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: dict(fake_metrics))

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data("fake_model")
    assert widget.cards_grid.count() == 4

    app_state.set_advanced_mode(True)
    widget.update_graph()
    assert widget.cards_grid.count() == 4

    app_state.set_advanced_mode(False)

    app_state.set_advanced_mode(False)


# Cards grid - confidence interval, when the model has saved predictions

def test_cards_grid_shows_a_ci_when_predictions_are_saved(qtbot, monkeypatch):
    import pandas as pd
    import hamelin.interface.widgets.one_model as one_model_mod
    from hamelin.interface.utils.app_state import app_state

    fake_metrics = {"test/accuracy/best": 0.85}
    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: dict(fake_metrics))
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")

    predictions_df = pd.DataFrame({
        "y_true": ["yes"] * 15 + ["no"] * 15,
        "y_pred": ["yes"] * 12 + ["no"] * 3 + ["no"] * 12 + ["yes"] * 3,
    })
    monkeypatch.setattr(one_model_mod.gmp, "load_test_predictions", lambda p: predictions_df)

    app_state.set_advanced_mode(True)
    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")

    tile = _card_tile(widget, "OVERALL ACCURACY")
    assert tile is not None
    value_lbl = _tile_value_label(tile)
    assert "[" in value_lbl.text() and "]" in value_lbl.text()
    assert value_lbl.toolTip() != ""


def test_cards_grid_has_no_ci_when_no_predictions_saved(qtbot, monkeypatch):
    import hamelin.interface.widgets.one_model as one_model_mod
    from hamelin.interface.utils.app_state import app_state

    fake_metrics = {"test/accuracy/best": 0.85}
    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: dict(fake_metrics))
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    # No test_predictions.csv for this run - the common case for anything
    # trained before that file existed, or a non-Ludwig backend.
    monkeypatch.setattr(one_model_mod.gmp, "load_test_predictions", lambda p: None)

    app_state.set_advanced_mode(True)
    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")

    tile = _card_tile(widget, "OVERALL ACCURACY")
    assert tile is not None
    value_lbl = _tile_value_label(tile)
    assert value_lbl.text() == "0.8500"
    assert "[" not in value_lbl.text()


def test_cards_grid_has_one_tile_per_metric(qtbot, monkeypatch):
    import hamelin.interface.widgets.one_model as one_model_mod
    from hamelin.interface.utils.app_state import app_state

    fake_metrics = {"test/accuracy/best": 0.9, "test/roc_auc/best": 0.85}
    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: dict(fake_metrics))

    app_state.set_advanced_mode(True)
    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")

    assert widget.cards_grid.count() == 2


def test_cards_grid_empty_when_no_metrics(qtbot, monkeypatch):
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {})

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")

    assert widget.cards_grid.count() == 0
    assert widget.no_metrics_label.isHidden() is False


def test_export_is_csv_only_with_project_model_and_metrics(qtbot, monkeypatch):
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {"test/accuracy/best": 0.9})
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(one_model_mod.gmp, "detect_model_type_from_ludwig", lambda p: "MLP")
    monkeypatch.setattr(one_model_mod.gmp, "get_output_feature_info", lambda p: {"name": "Diabetes"})
    monkeypatch.setattr(one_model_mod.gmp, "get_input_feature_names", lambda p: ["Age", "Glucose"])
    monkeypatch.setattr(one_model_mod.gmp, "get_evaluated_size", lambda p: (19, True))
    monkeypatch.setattr(one_model_mod.gmp, "get_project_info", lambda: {
        "name": "Test3", "protocol_number": "a", "primary_objective": "Assess X",
    })

    captured = {}
    monkeypatch.setattr(
        one_model_mod, "export_csv",
        lambda parent, name, header, rows, title=None: captured.update(
            header=header, rows=dict(rows), title=title
        ),
    )

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")
    widget._on_export_clicked()

    assert captured["header"] == ["field", "value"]
    rows = captured["rows"]
    assert rows["Project name"] == "Test3"
    assert rows["Model name"] == "fake_model"
    assert rows["Model type"] == "MLP"
    assert rows["Target variable"] == "Diabetes"
    assert rows["Predictive variables"] == "Age, Glucose"
    assert rows["Evaluated on (patients)"] == 19
    assert rows["Overall Accuracy"] == 0.9


# Subgroup breakdown ("Break down by")

def test_subgroup_dropdown_hidden_when_no_candidate_columns(qtbot, monkeypatch):
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {"test/accuracy/best": 0.9})
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(one_model_mod.gmp, "get_output_feature_info", lambda p: {"type": "binary"})
    monkeypatch.setattr(one_model_mod.gmp, "get_subgroup_columns", lambda p: [])

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")

    assert widget.subgroup_row_widget.isHidden() is True


def test_subgroup_dropdown_hidden_for_regression_models(qtbot, monkeypatch):
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {"test/r2/best": 0.9})
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(one_model_mod.gmp, "get_output_feature_info", lambda p: {"type": "number"})
    # Even if a column would otherwise qualify, regression shouldn't offer it.
    monkeypatch.setattr(one_model_mod.gmp, "get_subgroup_columns", lambda p: ["sex"])

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")

    assert widget.subgroup_row_widget.isHidden() is True


def _setup_subgroup_widget(qtbot, monkeypatch):
    import pandas as pd
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {"test/accuracy/best": 0.8})
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(one_model_mod.gmp, "get_output_feature_info", lambda p: {"type": "binary"})
    monkeypatch.setattr(one_model_mod.gmp, "get_subgroup_columns", lambda p: ["sex"])

    predictions_df = pd.DataFrame({
        "sex": ["F", "F", "F", "M", "M"],
        "y_true": ["no", "no", "yes", "yes", "no"],
        "y_pred": ["no", "no", "no", "yes", "no"],
    })
    monkeypatch.setattr(one_model_mod.gmp, "load_test_predictions", lambda p: predictions_df)

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")
    return widget


def test_subgroup_dropdown_shown_and_defaults_to_cards(qtbot, monkeypatch):
    widget = _setup_subgroup_widget(qtbot, monkeypatch)

    assert widget.subgroup_row_widget.isHidden() is False
    assert widget.subgroup_dropdown.currentText() == "None"
    assert widget.cards_section.isHidden() is False
    assert widget.subgroup_section.isHidden() is True


def test_selecting_a_subgroup_shows_per_group_accuracy(qtbot, monkeypatch):
    widget = _setup_subgroup_widget(qtbot, monkeypatch)

    widget.subgroup_dropdown.selected = "sex"
    widget.subgroup_dropdown._update_label()
    widget._render_metrics()

    assert widget.cards_section.isHidden() is True
    assert widget.subgroup_section.isHidden() is False
    assert widget.subgroup_table.rowCount() == 2

    rows = {
        widget.subgroup_table.item(r, 0).text(): (
            widget.subgroup_table.item(r, 1).text(), widget.subgroup_table.item(r, 2).text(),
        )
        for r in range(widget.subgroup_table.rowCount())
    }
    # Both groups are below the small-group threshold (3 and 2 patients),
    # so both get the "⚠ " prefix right on their own row - see
    # test_small_subgroup_shows_a_warning for that behavior specifically.
    # F: 3 patients, 2/3 correct (no,no,yes -> no,no,no)
    assert rows["⚠ F"] == ("3", "0.6667")
    # M: 2 patients, 2/2 correct
    assert rows["⚠ M"] == ("2", "1.0000")


def test_small_subgroup_shows_a_warning(qtbot, monkeypatch):
    widget = _setup_subgroup_widget(qtbot, monkeypatch)

    widget.subgroup_dropdown.selected = "sex"
    widget.subgroup_dropdown._update_label()
    widget._render_metrics()

    # The generic caption explains what the symbol means, but doesn't name
    # groups itself - the "⚠" sits right on each affected row instead (see
    # test_selecting_a_subgroup_shows_per_group_accuracy).
    assert "Fewer than" in widget.subgroup_warning.text()
    assert widget.subgroup_warning.isHidden() is False

    for r in range(widget.subgroup_table.rowCount()):
        assert widget.subgroup_table.item(r, 0).text().startswith("⚠ ")
        assert widget.subgroup_table.item(r, 0).toolTip() != ""


def test_only_the_small_group_gets_marked(qtbot, monkeypatch):
    # A mix of one large and one small group - only the small one should
    # carry the "⚠" and the tooltip; the large one stays plain.
    import pandas as pd
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {"test/accuracy/best": 0.8})
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(one_model_mod.gmp, "get_output_feature_info", lambda p: {"type": "binary"})
    monkeypatch.setattr(one_model_mod.gmp, "get_subgroup_columns", lambda p: ["sex"])

    predictions_df = pd.DataFrame({
        "sex": ["F"] * 12 + ["M"] * 3,
        "y_true": ["no"] * 15,
        "y_pred": ["no"] * 15,
    })
    monkeypatch.setattr(one_model_mod.gmp, "load_test_predictions", lambda p: predictions_df)

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")
    widget.subgroup_dropdown.selected = "sex"
    widget.subgroup_dropdown._update_label()
    widget._render_metrics()

    texts = {widget.subgroup_table.item(r, 0).text() for r in range(widget.subgroup_table.rowCount())}
    assert texts == {"F", "⚠ M"}

    f_item = next(widget.subgroup_table.item(r, 0) for r in range(widget.subgroup_table.rowCount())
                  if widget.subgroup_table.item(r, 0).text() == "F")
    assert f_item.toolTip() == ""


def test_switching_back_to_none_restores_cards(qtbot, monkeypatch):
    widget = _setup_subgroup_widget(qtbot, monkeypatch)

    widget.subgroup_dropdown.selected = "sex"
    widget.subgroup_dropdown._update_label()
    widget._render_metrics()

    widget.subgroup_dropdown.selected = "None"
    widget.subgroup_dropdown._update_label()
    widget._render_metrics()

    assert widget.cards_section.isHidden() is False
    assert widget.subgroup_section.isHidden() is True


def test_subgroup_selection_preserved_across_model_refresh(qtbot, monkeypatch):
    widget = _setup_subgroup_widget(qtbot, monkeypatch)

    widget.subgroup_dropdown.selected = "sex"
    widget.subgroup_dropdown._update_label()
    widget._render_metrics()

    # A refresh that doesn't change which columns are available (e.g. an
    # advanced-mode toggle re-render) shouldn't silently drop the choice.
    widget.update_graph()

    assert widget.subgroup_dropdown.currentText() == "sex"
    assert widget.subgroup_section.isHidden() is False


# Run metadata line + notes field

def test_meta_line_always_shows_full_run_detail(qtbot, monkeypatch):
    # This page has no Advanced mode toggle of its own (unlike the
    # comparison views) - its whole point is one model's own numbers, so
    # the full technical detail (seed/epochs/Ludwig version) is always
    # shown, not gated behind the app-wide advanced_mode flag.
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {"test/accuracy/best": 0.9})
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(one_model_mod, "load_note", lambda m: "")
    monkeypatch.setattr(one_model_mod.gmp, "get_run_metadata", lambda p: {
        "generated_at": "2026-03-03T09:12:00", "dataset_name": "cohort_v2.csv",
        "random_seed": 42, "epochs_trained": 30, "ludwig_version": "0.17.5",
    })

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("fake_model")

    text = widget.meta_label.text()
    assert widget.meta_label.isHidden() is False
    assert "03 Mar 2026" in text
    assert "cohort_v2.csv" in text
    assert "seed 42" in text
    assert "30 epochs" in text
    assert "Ludwig 0.17.5" in text


def test_notes_field_loads_and_saves_per_model(qtbot, monkeypatch):
    import hamelin.interface.widgets.one_model as one_model_mod

    monkeypatch.setattr(one_model_mod.gmp, "get_model_names", lambda: ["m1", "m2"])
    monkeypatch.setattr(one_model_mod, "load_run_metrics", lambda m: {"test/accuracy/best": 0.9})
    monkeypatch.setattr(one_model_mod.gmp, "model_path_from_name", lambda m: f"path/{m}")
    monkeypatch.setattr(one_model_mod.gmp, "get_run_metadata", lambda p: {})

    store = {"m1": "existing note"}
    monkeypatch.setattr(one_model_mod, "load_note", lambda m: store.get(m, ""))
    monkeypatch.setattr(one_model_mod, "save_note", lambda m, t: store.__setitem__(m, t))

    widget = VisualiseOneModel()
    qtbot.addWidget(widget)
    widget.set_data("m1")
    assert widget.notes_edit.toPlainText() == "existing note"

    widget.notes_edit.setPlainText("m1 updated")
    widget._save_note()
    assert store["m1"] == "m1 updated"

    # switching model saves the outgoing one and loads the incoming one
    widget.model_selector.selected = "m2"
    widget.model_selector._update_label()
    widget.update_graph()
    assert widget.notes_edit.toPlainText() == ""

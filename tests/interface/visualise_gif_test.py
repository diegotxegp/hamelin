from hamelin.interface.widgets.visualise_gif import VisualiseGifWidget, infer_output_type


def test_no_model_selected_on_load_hides_details_card_and_favorite_button(qtbot):
    widget = VisualiseGifWidget()
    qtbot.addWidget(widget)

    # A card full of "—" placeholders isn't useful before a model is
    # actually picked - hidden until then, unlike the action buttons.
    assert widget.details_card.isHidden() is True
    assert widget.btn_info.isHidden() is False
    assert widget.btn_analyse_main.isHidden() is False
    assert widget.favorite_btn.isHidden() is True
    assert widget.current_model is None
    assert widget.model_type_badge.text() == "—"
    assert widget.output_type_badge.text() == "—"


def test_selecting_a_model_reveals_the_favorite_button(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    widget = VisualiseGifWidget()
    qtbot.addWidget(widget)
    models = gmp.get_model_names()
    if not models:
        return

    widget.model_selector.selected = models[0]
    widget.model_selector._update_label()
    widget.on_model_changed()

    assert widget.details_card.isHidden() is False
    assert widget.favorite_btn.isHidden() is False
    assert widget.btn_info.isHidden() is False
    assert widget.btn_analyse_main.isHidden() is False
    assert widget.current_model == models[0]
    assert widget.model_type_badge.text() != ""


def test_deselecting_hides_the_favorite_button_again(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    widget = VisualiseGifWidget()
    qtbot.addWidget(widget)
    models = gmp.get_model_names()
    if not models:
        return

    widget.model_selector.selected = models[0]
    widget.model_selector._update_label()
    widget.on_model_changed()

    widget.model_selector.selected = None
    widget.on_model_changed()

    assert widget.favorite_btn.isHidden() is True
    assert widget.details_card.isHidden() is True
    assert widget.current_model is None
    assert widget.model_type_badge.text() == "—"
    assert widget.output_type_badge.text() == "—"


def test_favorite_button_toggles_for_selected_model(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    widget = VisualiseGifWidget()
    qtbot.addWidget(widget)
    models = gmp.get_model_names()
    if not models:
        return

    widget.model_selector.selected = models[0]
    widget.model_selector._update_label()
    widget.on_model_changed()

    initial = widget.favorite_btn.text()
    widget._toggle_favorite()
    assert widget.favorite_btn.text() != initial
    widget._toggle_favorite()
    assert widget.favorite_btn.text() == initial


def test_infer_output_type_uses_ludwig_schema_when_available(monkeypatch):
    import hamelin.interface.widgets.visualise_gif as gif_mod

    monkeypatch.setattr(
        gif_mod.gmp, "get_output_feature_info",
        lambda path: {"type": "binary"},
    )
    assert infer_output_type("some/path") == "Classification"


def test_infer_output_type_falls_back_to_metric_heuristic(monkeypatch):
    import hamelin.interface.widgets.visualise_gif as gif_mod

    monkeypatch.setattr(gif_mod.gmp, "get_output_feature_info", lambda path: {})
    assert infer_output_type("some/path", {"test/x/accuracy/best": 0.9}) == "Classification (estimated)"
    assert infer_output_type("some/path", {"test/x/loss/best": 0.1}) == "Regression (estimated)"
    assert infer_output_type("some/path", {}) == "Not identified"


# Details card (project / target / predictive variables / evaluated size)

def test_details_card_shows_project_and_variables(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_gif as gif_mod

    monkeypatch.setattr(gif_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(gif_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(gif_mod.gmp, "detect_model_type_from_ludwig", lambda p: "MLP")
    monkeypatch.setattr(gif_mod.gmp, "get_output_feature_info", lambda p: {"name": "Diabetes", "type": "binary"})
    monkeypatch.setattr(gif_mod.gmp, "get_input_feature_names", lambda p: ["Age", "Glucose"])
    monkeypatch.setattr(gif_mod.gmp, "get_evaluated_size", lambda p: (19, True))
    monkeypatch.setattr(gif_mod.gmp, "get_project_info", lambda: {
        "name": "Test3", "protocol_number": "a", "primary_objective": "Assess X",
    })
    monkeypatch.setattr(gif_mod, "load_run_metrics", lambda m: {})

    widget = VisualiseGifWidget()
    qtbot.addWidget(widget)
    widget.init_models()
    widget.model_selector.selected = "fake_model"
    widget.model_selector._update_label()
    widget.on_model_changed()

    assert widget.project_label.text() == "Project: Test3 (protocol a)"
    assert widget.objective_label.text() == "Primary objective: Assess X"
    assert widget.target_label.text() == "Target variable: Diabetes"
    # No parenthetical count before the list - just the plain names.
    assert widget.features_label.text() == "Predictive variables: Age, Glucose"
    assert widget.eval_size_label.text() == "Evaluated on: 19 patients"


def test_details_card_hides_project_lines_when_no_project(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_gif as gif_mod

    monkeypatch.setattr(gif_mod.gmp, "get_model_names", lambda: ["fake_model"])
    monkeypatch.setattr(gif_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(gif_mod.gmp, "detect_model_type_from_ludwig", lambda p: "MLP")
    monkeypatch.setattr(gif_mod.gmp, "get_output_feature_info", lambda p: {})
    monkeypatch.setattr(gif_mod.gmp, "get_input_feature_names", lambda p: [])
    monkeypatch.setattr(gif_mod.gmp, "get_evaluated_size", lambda p: (None, False))
    monkeypatch.setattr(gif_mod.gmp, "get_project_info", lambda: {})
    monkeypatch.setattr(gif_mod, "load_run_metrics", lambda m: {})

    widget = VisualiseGifWidget()
    qtbot.addWidget(widget)
    widget.init_models()
    widget.model_selector.selected = "fake_model"
    widget.model_selector._update_label()
    widget.on_model_changed()

    assert widget.project_label.isHidden() is True
    assert widget.objective_label.isHidden() is True
    assert widget.target_label.text() == "Target variable: —"
    assert widget.features_label.text() == "Predictive variables: —"
    assert widget.eval_size_label.text() == "Evaluated on: unknown"


def test_no_export_button_on_this_page(qtbot):
    # The fuller export (project + model + metrics, CSV) now lives on the
    # Model Metrics page ("Analyse the Model's Results") instead - having
    # it here too was redundant.
    widget = VisualiseGifWidget()
    qtbot.addWidget(widget)
    assert not hasattr(widget, "export_btn")

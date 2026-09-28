import json
import math

from hamelin.interface.widgets.duplicate_model import (
    DuplicateModelWidget,
    SETTING_RANGES,
    SIMPLE_MODE_OPTIONS,
    SLIDER_RESOLUTION,
    _slider_to_value,
    _value_to_slider,
    _format_value,
    _find_metric,
    _diagnose_model,
    _set_nested,
)

SIMPLE_MODE_OPTIONS_BY_KEY = {o["key"]: o["changes"] for o in SIMPLE_MODE_OPTIONS}


# _slider_to_value / _value_to_slider

def test_int_slider_is_a_direct_passthrough():
    spec = SETTING_RANGES["trainer.epochs"]
    assert _slider_to_value(spec, 42) == 42
    assert _value_to_slider(spec, 42) == 42


def test_float_slider_roundtrips_across_its_range():
    spec = SETTING_RANGES["combiner.dropout"]
    for value in (0.0, 0.2, 0.45, 0.9):
        pos = _value_to_slider(spec, value)
        back = _slider_to_value(spec, pos)
        assert abs(back - value) < 1e-3


def test_log_slider_midpoint_is_geometric_mean_of_bounds():
    spec = SETTING_RANGES["trainer.learning_rate"]
    mid = _slider_to_value(spec, SLIDER_RESOLUTION // 2)
    assert abs(math.log10(mid) - math.log10(math.sqrt(spec["min"] * spec["max"]))) < 0.05


def test_log_slider_roundtrips():
    spec = SETTING_RANGES["trainer.learning_rate"]
    for value in (1e-5, 1e-3, 1e-1):
        pos = _value_to_slider(spec, value)
        back = _slider_to_value(spec, pos)
        assert abs(math.log10(back) - math.log10(value)) < 0.02


def test_value_to_slider_clamps_out_of_range_values():
    spec = SETTING_RANGES["trainer.epochs"]
    assert _value_to_slider(spec, -50) == spec["min"]
    assert _value_to_slider(spec, 99999) == spec["max"]


# _format_value

def test_format_value_int_has_no_decimals():
    spec = SETTING_RANGES["trainer.epochs"]
    assert _format_value(spec, 12.0) == "12"


def test_format_value_float_is_short():
    spec = SETTING_RANGES["combiner.dropout"]
    assert _format_value(spec, 0.123456) == "0.12346"


# _find_metric / _diagnose_model

def test_find_metric_matches_split_and_name():
    metrics = {"test/sentiment/accuracy/best": 0.9, "train/sentiment/accuracy/best": 0.95}
    assert _find_metric(metrics, "test", "accuracy") == 0.9
    assert _find_metric(metrics, "train", "accuracy") == 0.95


def test_find_metric_returns_none_when_absent():
    assert _find_metric({}, "test", "accuracy") is None


def test_diagnose_model_flags_overfitting(monkeypatch):
    import hamelin.interface.widgets.duplicate_model as dm

    monkeypatch.setattr(dm, "load_run_metrics", lambda model: {
        "train/x/accuracy/best": 0.95,
        "test/x/accuracy/best": 0.80,
    })

    suggestions = _diagnose_model("some_model")
    keys = [set(s["changes"]) for s in suggestions]
    assert {"combiner.dropout", "trainer.regularization_lambda"} in keys


def test_diagnose_model_flags_undertrained(monkeypatch):
    import hamelin.interface.widgets.duplicate_model as dm

    monkeypatch.setattr(dm, "load_run_metrics", lambda model: {
        "train/x/accuracy/best": 0.5,
        "test/x/accuracy/best": 0.5,
    })

    suggestions = _diagnose_model("some_model")
    keys = [set(s["changes"]) for s in suggestions]
    assert {"trainer.epochs", "trainer.early_stop"} in keys


def test_diagnose_model_no_suggestions_when_metrics_look_fine(monkeypatch):
    import hamelin.interface.widgets.duplicate_model as dm

    monkeypatch.setattr(dm, "load_run_metrics", lambda model: {
        "train/x/accuracy/best": 0.9,
        "test/x/accuracy/best": 0.88,
    })

    assert _diagnose_model("some_model") == []


def test_diagnose_model_silent_when_metrics_missing(monkeypatch):
    import hamelin.interface.widgets.duplicate_model as dm

    monkeypatch.setattr(dm, "load_run_metrics", lambda model: {})
    assert _diagnose_model("some_model") == []


# _set_nested

def test_set_nested_dict_path():
    config = {"trainer": {"epochs": 5}}
    _set_nested(config, "trainer.epochs", 50)
    assert config["trainer"]["epochs"] == 50


def test_set_nested_creates_new_leaf():
    config = {"combiner": {}}
    _set_nested(config, "combiner.dropout", 0.3)
    assert config["combiner"]["dropout"] == 0.3


def test_set_nested_through_list_index():
    config = {"input_features": [{"encoder": {"dropout": 0.1}}]}
    _set_nested(config, "input_features.0.encoder.dropout", 0.4)
    assert config["input_features"][0]["encoder"]["dropout"] == 0.4


# Widget behavior

def test_widget_populates_sliders_from_source_model(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)

    models = gmp.get_model_names()
    widget.model_dropdown.addItems(models)
    widget.model_dropdown.buttons[0].click()

    assert set(widget.fields.keys()) == set(SETTING_RANGES.keys())
    for key, slider in widget.fields.items():
        spec = SETTING_RANGES[key]
        if spec["kind"] == "int":
            assert slider.minimum() == spec["min"]
            assert slider.maximum() == spec["max"]
        else:
            assert slider.minimum() == 0
            assert slider.maximum() == SLIDER_RESOLUTION


def test_moving_slider_updates_value_label(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    slider = widget.fields["trainer.epochs"]
    slider.setValue(77)

    assert widget.value_labels["trainer.epochs"].text() == "77"


def _seed_run(tmp_path, run_name="experiment_run"):
    model_dir = tmp_path / run_name / "model"
    model_dir.mkdir(parents=True)
    (model_dir / "model_hyperparameters.json").write_text("{}")
    report = {
        "config": {
            "trainer": {
                "epochs": 50,
                "batch_size": 32,
                "learning_rate": 0.001,
                "early_stop": 5,
                "regularization_lambda": 0.0,
            },
            "combiner": {"dropout": 0.1},
        }
    }
    (tmp_path / run_name / "training_report.json").write_text(json.dumps(report))


def test_continue_emits_slider_values_with_correct_types(qtbot, tmp_path, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp

    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    payloads = []
    widget.open_training_requested.connect(payloads.append)

    widget.fields["trainer.epochs"].setValue(80)
    widget.new_name_edit.setText("my_dup_run")
    widget._on_continue_clicked()

    assert len(payloads) == 1
    data = payloads[0]
    assert data["based_on"] == widget.source_model
    assert data["new_run_name"] == "my_dup_run"
    assert data["config"]["trainer"]["epochs"] == 80
    assert isinstance(data["config"]["trainer"]["epochs"], int)
    assert isinstance(data["config"]["trainer"]["learning_rate"], float)
    # Nothing is written to disk - the run is only persisted once trained.
    assert not (tmp_path / "duplicated_configs").exists()


def test_continue_without_a_name_shows_error_and_does_not_emit(qtbot, tmp_path, monkeypatch):
    from hamelin.interface.utils.widgets import ErrorPopup
    import hamelin.interface.utils.get_model_paths as gmp

    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()
    widget.new_name_edit.setText("   ")

    payloads = []
    widget.open_training_requested.connect(payloads.append)

    widget._on_continue_clicked()

    assert any(isinstance(child, ErrorPopup) for child in widget.findChildren(ErrorPopup))
    assert payloads == []


def test_suggestion_apply_button_moves_the_right_slider(qtbot, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.widgets.duplicate_model as dm

    monkeypatch.setattr(dm, "load_run_metrics", lambda model: {
        "train/x/accuracy/best": 0.95,
        "test/x/accuracy/best": 0.80,
    })

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    assert widget.suggestions_box.isHidden() is False
    dropout_before = _slider_to_value(SETTING_RANGES["combiner.dropout"], widget.fields["combiner.dropout"].value())

    widget._apply_suggestion({"combiner.dropout": 0.15, "trainer.regularization_lambda": 0.02})

    dropout_after = _slider_to_value(SETTING_RANGES["combiner.dropout"], widget.fields["combiner.dropout"].value())
    assert dropout_after > dropout_before


def test_no_suggestions_hides_suggestions_box(qtbot, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.widgets.duplicate_model as dm

    monkeypatch.setattr(dm, "load_run_metrics", lambda model: {
        "train/x/accuracy/best": 0.9,
        "test/x/accuracy/best": 0.89,
    })

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    assert widget.suggestions_box.isVisible() is False


# simple mode: 3-option flow

def test_simple_mode_shows_option_flow_and_hides_sliders(qtbot, tmp_path, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    from hamelin.interface.utils.app_state import app_state

    app_state.set_advanced_mode(False)
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    assert not widget.simple_flow_card.isHidden()
    assert widget.form_card.isHidden()
    # Stays clickable regardless of selection state - _on_continue_clicked
    # itself is what validates and shows an error popup if nothing's picked.
    assert widget.continue_btn.isEnabled() is True


def test_simple_mode_keep_as_is_does_not_change_values(qtbot, tmp_path, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    from hamelin.interface.utils.app_state import app_state

    app_state.set_advanced_mode(False)
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    widget._on_simple_option_clicked("keep_as_is")

    for key, slider in widget.fields.items():
        value = _slider_to_value(SETTING_RANGES[key], slider.value())
        assert abs(value - widget._original_values[key]) < 1e-3
    assert widget.continue_btn.isEnabled() is True


def test_simple_mode_boost_recall_raises_epochs_and_lowers_dropout(qtbot, tmp_path, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    from hamelin.interface.utils.app_state import app_state

    app_state.set_advanced_mode(False)
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    widget._on_simple_option_clicked("boost_recall")

    epochs = _slider_to_value(SETTING_RANGES["trainer.epochs"], widget.fields["trainer.epochs"].value())
    dropout = _slider_to_value(SETTING_RANGES["combiner.dropout"], widget.fields["combiner.dropout"].value())
    assert epochs > widget._original_values["trainer.epochs"]
    assert dropout < widget._original_values["combiner.dropout"]


def test_simple_mode_switching_options_is_not_cumulative(qtbot, tmp_path, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    from hamelin.interface.utils.app_state import app_state

    app_state.set_advanced_mode(False)
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    widget._on_simple_option_clicked("boost_recall")
    widget._on_simple_option_clicked("boost_precision")

    expected = (
        widget._original_values["trainer.regularization_lambda"]
        + SIMPLE_MODE_OPTIONS_BY_KEY["boost_precision"]["trainer.regularization_lambda"]
    )
    actual = _slider_to_value(
        SETTING_RANGES["trainer.regularization_lambda"],
        widget.fields["trainer.regularization_lambda"].value(),
    )
    assert abs(actual - expected) < 1e-3


def test_simple_mode_continue_emits_the_same_payload_shape(qtbot, tmp_path, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    from hamelin.interface.utils.app_state import app_state

    app_state.set_advanced_mode(False)
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    payloads = []
    widget.open_training_requested.connect(payloads.append)

    widget._on_simple_option_clicked("boost_precision")
    widget.new_name_edit.setText("simple_flow_run")
    widget._on_continue_clicked()

    assert len(payloads) == 1
    data = payloads[0]
    assert data["based_on"] == widget.source_model
    assert data["new_run_name"] == "simple_flow_run"
    assert data["config"]["combiner"]["dropout"] > widget._original_values["combiner.dropout"]


def test_switching_to_advanced_mode_shows_sliders_with_simple_mode_edits_kept(qtbot, tmp_path, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    from hamelin.interface.utils.app_state import app_state

    app_state.set_advanced_mode(False)
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _seed_run(tmp_path)

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)
    widget.model_dropdown.addItems(gmp.get_model_names())
    widget.model_dropdown.buttons[0].click()

    widget._on_simple_option_clicked("boost_recall")
    app_state.set_advanced_mode(True)

    assert not widget.form_card.isHidden()
    assert widget.simple_flow_card.isHidden()
    epochs = _slider_to_value(SETTING_RANGES["trainer.epochs"], widget.fields["trainer.epochs"].value())
    assert epochs > widget._original_values["trainer.epochs"]


def test_continue_without_a_model_selected_shows_error_popup(qtbot):
    from hamelin.interface.utils.widgets import ErrorPopup

    widget = DuplicateModelWidget()
    qtbot.addWidget(widget)

    assert widget.continue_btn.isEnabled() is True

    widget._on_continue_clicked()

    assert any(isinstance(child, ErrorPopup) for child in widget.findChildren(ErrorPopup))

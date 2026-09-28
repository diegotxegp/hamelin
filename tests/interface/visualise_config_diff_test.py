from hamelin.interface.widgets.visualise_config_diff import (
    VisualiseConfigDiffWidget,
    humanize_key,
    friendly_label,
    setting_explanation,
)


# Pure helper functions

def test_humanize_key_simple_setting():
    assert humanize_key("trainer.some_setting") == "Some Setting"


def test_humanize_key_with_list_index():
    assert humanize_key("input_features.0") == "Input Features #1"


def test_friendly_label_known_setting():
    assert friendly_label("trainer.batch_size") == "Batch Size"


def test_friendly_label_two_part_key():
    assert friendly_label("optimizer.type") == "Optimizer"


def test_friendly_label_unknown_setting_falls_back_to_humanized_key():
    assert friendly_label("some.unmapped_setting") == "Unmapped Setting"


def test_setting_explanation_known_setting_is_specific():
    text = setting_explanation("trainer.learning_rate")
    assert "step" in text


def test_setting_explanation_unknown_setting_is_generic():
    text = setting_explanation("some.unmapped_setting")
    assert text == (
        "A more technical training setting - the exact value matters less than "
        "whether it's the same or different between the two runs."
    )


# Widget behavior

def _diff(key, value_a, value_b, only_in=None):
    return {"key": key, "value_a": value_a, "value_b": value_b, "only_in": only_in}


def test_widget_shows_empty_message_when_models_have_no_diffs(qtbot, monkeypatch):
    widget = VisualiseConfigDiffWidget()
    qtbot.addWidget(widget)

    import hamelin.interface.widgets.visualise_config_diff as vcd
    monkeypatch.setattr(vcd.gmp, "model_path_from_name", lambda name, *a, **k: f"/fake/{name}")
    monkeypatch.setattr(vcd.gmp, "diff_configs", lambda a, b, include_defaults=False: [])

    widget.set_data("run_a", "run_b")

    assert widget.empty_label.isHidden() is False
    assert "identical" in widget.empty_label.text()
    assert widget.table.isHidden() is True


def test_widget_shows_error_when_model_path_missing(qtbot, monkeypatch):
    widget = VisualiseConfigDiffWidget()
    qtbot.addWidget(widget)

    import hamelin.interface.widgets.visualise_config_diff as vcd
    monkeypatch.setattr(vcd.gmp, "model_path_from_name", lambda name, *a, **k: None)

    widget.set_data("run_a", "run_b")

    assert widget.empty_label.isHidden() is False
    assert "Could not load" in widget.empty_label.text()


def test_widget_populates_table_with_diffs(qtbot, monkeypatch):
    widget = VisualiseConfigDiffWidget()
    qtbot.addWidget(widget)

    import hamelin.interface.widgets.visualise_config_diff as vcd
    monkeypatch.setattr(vcd.gmp, "model_path_from_name", lambda name, *a, **k: f"/fake/{name}")
    monkeypatch.setattr(
        vcd.gmp, "diff_configs",
        lambda a, b, include_defaults=False: [
            _diff("trainer.batch_size", 32, 64),
            _diff("combiner.type", None, "concat", only_in="b"),
        ],
    )

    widget.set_data("run_a", "run_b")

    assert widget.table.rowCount() == 2
    assert widget.table.item(0, 0).text() == "Batch Size"
    assert widget.table.item(0, 1).text() == "32"
    assert widget.table.item(0, 2).text() == "64"
    assert widget.table.item(1, 2).text() == "concat"
    assert widget.table.item(1, 1).text() == "— (not set)"
    assert widget.empty_label.isVisible() is False


def test_toggle_defaults_flips_state_and_button_text(qtbot, monkeypatch):
    widget = VisualiseConfigDiffWidget()
    qtbot.addWidget(widget)

    import hamelin.interface.widgets.visualise_config_diff as vcd
    monkeypatch.setattr(vcd.gmp, "model_path_from_name", lambda name, *a, **k: f"/fake/{name}")
    monkeypatch.setattr(vcd.gmp, "diff_configs", lambda a, b, include_defaults=False: [])
    widget.set_data("run_a", "run_b")

    assert widget.include_defaults is False
    widget.on_toggle_defaults()
    assert widget.include_defaults is True
    assert widget.toggle_btn.text() == "Hide default settings"

    widget.on_toggle_defaults()
    assert widget.include_defaults is False
    assert widget.toggle_btn.text() == "Show all settings"


def test_popup_entries_list_each_setting_once(qtbot, monkeypatch):
    widget = VisualiseConfigDiffWidget()
    qtbot.addWidget(widget)

    import hamelin.interface.widgets.visualise_config_diff as vcd
    monkeypatch.setattr(vcd.gmp, "model_path_from_name", lambda name, *a, **k: f"/fake/{name}")
    monkeypatch.setattr(
        vcd.gmp, "diff_configs",
        lambda a, b, include_defaults=False: [
            _diff("trainer.batch_size", 32, 64),
            _diff("trainer.eval_batch_size", 32, 64),
        ],
    )
    widget.set_data("run_a", "run_b")

    entries = widget._build_settings_explanation_entries()
    labels = [e["label"] for e in entries]
    assert labels.count("Batch Size") == 1
    assert "Evaluation Batch Size" in labels


def test_popup_entries_empty_with_no_diffs_yet():
    widget = VisualiseConfigDiffWidget()
    entries = widget._build_settings_explanation_entries()
    assert entries == []

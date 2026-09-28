from hamelin.interface.utils.app_state import app_state
from hamelin.interface.widgets.comparison import ComparisonWindow


class _FakeMainWindow:
    def __init__(self):
        self.calls = []

    def launch_comparison(self, models, criterion, view_mode):
        self.calls.append((models, criterion, view_mode))


def _make_window(qtbot):
    window = ComparisonWindow()
    qtbot.addWidget(window)
    window.main_window = _FakeMainWindow()
    return window


def _has_error_popup(widget):
    from hamelin.interface.utils.widgets import ErrorPopup
    return any(isinstance(child, ErrorPopup) for child in widget.findChildren(ErrorPopup))


def test_launch_with_nothing_selected_shows_error_and_does_not_launch(qtbot):
    window = _make_window(qtbot)

    window.on_compare_clicked()

    assert window.main_window.calls == []
    assert _has_error_popup(window) is True


def test_launch_with_model_but_no_criterion_shows_error(qtbot):
    window = _make_window(qtbot)
    models = window._known_models
    if not models:
        return
    window.model_dropdown._toggle_item(models[0], True)

    window.on_compare_clicked()

    assert window.main_window.calls == []
    assert _has_error_popup(window) is True


def test_launch_with_model_and_criterion_but_no_view_mode_shows_error(qtbot):
    window = _make_window(qtbot)
    models = window._known_models
    if not models:
        return
    window.model_dropdown._toggle_item(models[0], True)
    if window.display_labels:
        window.criteria_dropdown.selected = window.display_labels[0]
        window.criteria_dropdown._update_label()

    window.on_compare_clicked()

    assert window.main_window.calls == []
    assert _has_error_popup(window) is True


def test_launch_with_everything_selected_calls_launch_comparison(qtbot):
    window = _make_window(qtbot)
    models = window._known_models
    if not models or not window.display_labels:
        return

    window.model_dropdown._toggle_item(models[0], True)
    window.criteria_dropdown.selected = window.display_labels[0]
    window.criteria_dropdown._update_label()
    window.view_dropdown.selected = "Table"
    window.view_dropdown._update_label()

    window.on_compare_clicked()

    assert len(window.main_window.calls) == 1
    launched_models, criterion, view_mode = window.main_window.calls[0]
    assert launched_models == [models[0]]
    assert criterion == window.metrics_keys[0]
    assert view_mode == "Table"


def test_radar_is_a_selectable_view_mode(qtbot):
    window = _make_window(qtbot)
    models = window._known_models
    if not models or not window.display_labels:
        return

    window.model_dropdown._toggle_item(models[0], True)
    window.criteria_dropdown.selected = window.display_labels[0]
    window.criteria_dropdown._update_label()
    window.view_dropdown.selected = "Radar"
    window.view_dropdown._update_label()

    window.on_compare_clicked()

    assert len(window.main_window.calls) == 1
    _, _, view_mode = window.main_window.calls[0]
    assert view_mode == "Radar"


def test_config_diff_button_enabled_only_with_exactly_two_models(qtbot):
    app_state.set_advanced_mode(True)

    window = _make_window(qtbot)
    models = window._known_models
    if len(models) < 2:
        return

    assert window.config_diff_btn.isEnabled() is False

    window.model_dropdown._toggle_item(models[0], True)
    assert window.config_diff_btn.isEnabled() is False

    window.model_dropdown._toggle_item(models[1], True)
    assert window.config_diff_btn.isEnabled() is True

    window.model_dropdown._toggle_item(models[1], False)
    assert window.config_diff_btn.isEnabled() is False


def test_config_diff_button_hidden_in_simple_mode(qtbot):
    app_state.set_advanced_mode(False)

    window = _make_window(qtbot)
    models = window._known_models
    if len(models) < 2:
        return

    assert window.config_diff_btn.isHidden()

    window.model_dropdown._toggle_item(models[0], True)
    window.model_dropdown._toggle_item(models[1], True)
    assert window.config_diff_btn.isHidden()
    assert window.config_diff_btn.isEnabled() is False


def test_config_diff_button_appears_when_switching_to_advanced_mode(qtbot):
    app_state.set_advanced_mode(False)

    window = _make_window(qtbot)
    models = window._known_models
    if len(models) < 2:
        return

    window.model_dropdown._toggle_item(models[0], True)
    window.model_dropdown._toggle_item(models[1], True)

    app_state.set_advanced_mode(True)

    assert not window.config_diff_btn.isHidden()
    assert window.config_diff_btn.isEnabled() is True

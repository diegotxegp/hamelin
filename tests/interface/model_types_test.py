from hamelin.interface.widgets.model_types import ModelTypeInfoWidget
from hamelin.interface.utils.widgets import ErrorPopup


def test_open_popup_with_nothing_selected_shows_error(qtbot):
    widget = ModelTypeInfoWidget()
    qtbot.addWidget(widget)

    widget.open_popup()

    assert any(isinstance(c, ErrorPopup) for c in widget.findChildren(ErrorPopup))


def test_open_popup_with_a_type_selected_opens_the_overlay(qtbot):
    widget = ModelTypeInfoWidget()
    qtbot.addWidget(widget)
    widget.dropdown.selected = "MLP"
    widget.dropdown._update_label()

    widget.open_popup()

    assert not any(isinstance(c, ErrorPopup) for c in widget.findChildren(ErrorPopup))


def test_layout_fits_within_a_reasonable_window_height(qtbot):
    widget = ModelTypeInfoWidget()
    qtbot.addWidget(widget)
    assert widget.minimumSizeHint().height() < 700

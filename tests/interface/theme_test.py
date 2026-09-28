from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtTest import QTest

from hamelin.interface.utils.widgets import RoundedButton, Popup, WidgetPopupOverlay, style_info_button, ErrorPopup, AdvancedModeToggle
from hamelin.interface.utils.colors import COLORS


def test_rounded_button_has_fixed_size(qtbot):
    btn = RoundedButton("Click me", 200, 60, 20)
    qtbot.addWidget(btn)
    assert btn.text() == "Click me"
    assert btn.width() == 200
    assert btn.height() == 60


def test_popup_close_button_closes_popup(qtbot):
    parent = QLabel()
    qtbot.addWidget(parent)
    popup = Popup(parent=parent, width=300, height=200)
    qtbot.addWidget(popup)
    popup.show()

    assert popup.isHidden() is False
    popup.close_btn.click()
    assert popup.isHidden() is True


def test_popup_close_button_stays_in_top_right_corner_on_resize(qtbot):
    popup = Popup(width=400, height=300)
    qtbot.addWidget(popup)
    popup.show()
    popup.resize(500, 350)

    expected_x = popup.width() - popup.close_btn.width() - popup._close_btn_margin
    assert popup.close_btn.x() == expected_x
    assert popup.close_btn.y() == popup._close_btn_margin


def test_widget_popup_overlay_close_button_closes_overlay(qtbot):
    content = QLabel("info")
    overlay = WidgetPopupOverlay(content)
    qtbot.addWidget(overlay)
    overlay.show()

    close_btn = next(b for b in overlay.findChildren(QPushButton) if b.text() == "✕")
    close_btn.click()

    assert overlay.isVisible() is False


def test_widget_popup_overlay_centers_over_parent(qtbot):
    parent = QLabel()
    parent.resize(1000, 800)
    qtbot.addWidget(parent)

    content = QLabel("info")
    overlay = WidgetPopupOverlay(content, parent=parent, width=400, height=300)
    qtbot.addWidget(overlay)

    assert overlay.width() == 400
    assert overlay.height() == 300
    assert overlay.x() == (1000 - 400) // 2
    assert overlay.y() == (800 - 300) // 2


def test_style_info_button_uses_given_background_and_default_text_color():
    btn = RoundedButton("!", 50, 50, 25)
    style_info_button(btn, COLORS["yellow"])
    style = btn.styleSheet()
    assert COLORS["yellow"] in style
    assert COLORS["black"] in style


def test_style_info_button_accepts_custom_text_color():
    btn = RoundedButton("!", 50, 50, 25)
    style_info_button(btn, COLORS["yellow"], text_color=COLORS["black"])
    assert COLORS["black"] in btn.styleSheet()


def test_error_popup_shows_the_given_message(qtbot):
    parent = QWidget()
    parent.resize(1000, 800)
    qtbot.addWidget(parent)

    popup = ErrorPopup(parent, "Please select at least a model.", duration_ms=5000)
    qtbot.addWidget(popup)

    label = next(c for c in popup.findChildren(QLabel) if "Please select" in c.text())
    assert label.text() == "Please select at least a model."


def test_error_popup_closes_itself_after_the_duration(qtbot):
    parent = QWidget()
    parent.resize(1000, 800)
    qtbot.addWidget(parent)

    popup = ErrorPopup(parent, "Please select a criterion.", duration_ms=50)
    qtbot.addWidget(popup)
    popup.show()

    assert popup.isHidden() is False
    QTest.qWait(200)
    assert popup.isHidden() is True


def test_error_popup_is_centered_horizontally_on_its_parent(qtbot):
    parent = QWidget()
    parent.resize(1000, 800)
    qtbot.addWidget(parent)

    popup = ErrorPopup(parent, "Please select a visualization mode.", duration_ms=5000)
    qtbot.addWidget(popup)

    expected_x = (parent.width() - popup.width()) // 2
    assert popup.x() == expected_x


# AdvancedModeToggle

def test_advanced_mode_toggle_is_unchecked_by_default(qtbot):
    toggle = AdvancedModeToggle()
    qtbot.addWidget(toggle)
    assert toggle.isChecked() is False


def test_advanced_mode_toggle_click_flips_checked_state(qtbot):
    toggle = AdvancedModeToggle()
    qtbot.addWidget(toggle)

    QTest.mouseClick(toggle.switch, Qt.LeftButton)

    assert toggle.isChecked() is True


def test_advanced_mode_toggle_set_checked_updates_state(qtbot):
    toggle = AdvancedModeToggle()
    qtbot.addWidget(toggle)

    toggle.setChecked(True)
    assert toggle.isChecked() is True

    toggle.setChecked(False)
    assert toggle.isChecked() is False


def test_advanced_mode_toggle_emits_toggled_signal(qtbot):
    toggle = AdvancedModeToggle()
    qtbot.addWidget(toggle)

    received = []
    toggle.toggled.connect(received.append)

    toggle.setChecked(True)

    assert received == [True]


def test_rounded_button_stylesheet_follows_theme(qtbot):
    from hamelin.interface.utils.theme_state import set_dark
    from hamelin.interface.utils.colors import LIGHT, DARK
    btn = RoundedButton("x", 100, 40, 10)
    qtbot.addWidget(btn)
    assert LIGHT.surface in btn.styleSheet()
    set_dark(True)
    assert DARK.surface in btn.styleSheet() and DARK.border in btn.styleSheet()


def test_rounded_button_accent_keeps_black_text_in_dark(qtbot):
    from hamelin.interface.utils.theme_state import set_dark
    btn = RoundedButton("x", 100, 40, 10)
    qtbot.addWidget(btn)
    btn.set_accent(COLORS["yellow"])
    set_dark(True)
    assert f"background: {COLORS['yellow']}; color: {COLORS['black']}" in btn.styleSheet()
    btn.set_accent(None)
    assert COLORS["yellow"] not in btn.styleSheet()


def test_comparison_graph_background_follows_theme(qtbot):
    from hamelin.interface.utils.theme_state import set_dark
    from hamelin.interface.widgets.visualise_comparison_graphs import VisualiseComparisonGraphsWidget
    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    set_dark(True)
    assert widget.graph.backgroundBrush().color().name().upper() == "#2A2A2A"
    set_dark(False)
    assert widget.graph.backgroundBrush().color().name().upper() == "#FFFFFF"

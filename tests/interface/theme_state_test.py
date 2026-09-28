from hamelin.interface.utils.colors import colors, themed, themed_add, LIGHT, DARK
from hamelin.interface.utils.theme_state import theme_state, set_dark


def test_defaults_to_light_and_set_dark_emits_once(qtbot):
    assert theme_state.dark is False
    assert colors() is LIGHT

    with qtbot.waitSignal(theme_state.themeChanged, timeout=500) as blocker:
        set_dark(True)
    assert blocker.args == [True]
    assert colors() is DARK

    with qtbot.assertNotEmitted(theme_state.themeChanged):
        set_dark(True)


def test_light_palette_keeps_original_constants():
    from hamelin.interface.utils.colors import BLACK, WHITE, GRAY, GRAY_PALE
    assert (LIGHT.text, LIGHT.surface, LIGHT.muted, LIGHT.page) == (BLACK, WHITE, GRAY, GRAY_PALE)


def test_themed_restyles_on_switch_and_replaces_previous_style(qtbot):
    from PySide6.QtWidgets import QLabel
    label = QLabel("x")
    qtbot.addWidget(label)
    themed(label, lambda c: f"color: {c.text};")
    assert LIGHT.text in label.styleSheet()

    set_dark(True)
    assert DARK.text in label.styleSheet()

    themed(label, "color: red;")
    set_dark(False)
    assert label.styleSheet() == "color: red;"


def test_themed_add_keeps_base_style_across_switch(qtbot):
    from PySide6.QtWidgets import QLabel
    label = QLabel("x")
    qtbot.addWidget(label)
    themed(label, lambda c: f"color: {c.text};")
    themed_add(label, "font-size: 9px;")
    set_dark(True)
    assert DARK.text in label.styleSheet() and "font-size: 9px;" in label.styleSheet()

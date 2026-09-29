"""
Theme Colors (view-layer re-export)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The real module lives at src/utils/theme_colors.py - see its docstring for
why: a couple of pure-matplotlib analytics modules need these colours too,
and importing anything under hamelin.view from there would pull in
src/view/__init__.py's eager `from .main_window import MainWindow` (which
imports every page/widget in the app), causing a circular import.

This re-export exists so view code can still do the more discoverable::
    from hamelin.view.widgets.theme_colors import colors, on_theme_changed
"""

from hamelin.utils.theme_colors import (
    ThemeColors,
    apply_scroll_area_theme,
    bind_style,
    colors,
    apply_tooltip_theme,
    apply_transparent_container,
    isDarkTheme,
    list_item_qss,
    on_theme_changed,
    qconfig,
    scroll_area_qss,
    scrollbar_qss,
    style_figure,
    table_header_qss,
    table_qss,
    tooltip_qss,
)

__all__ = [
    'ThemeColors',
    'apply_scroll_area_theme',
    'bind_style',
    'colors',
    'isDarkTheme',
    'list_item_qss',
    'on_theme_changed',
    'qconfig',
    'scroll_area_qss',
    'scrollbar_qss',
    'style_figure',
    'table_header_qss',
    'table_qss',
]

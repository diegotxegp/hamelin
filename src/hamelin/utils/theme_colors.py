"""
Theme Colors
~~~~~~~~~~~~

Shared light/dark colour values for the custom (non-qfluentwidgets) widgets
scattered across the app - tables, lists, scroll bars, plain QLabel/QCheckBox
text, matplotlib figures - none of which get theming for free the way
CardWidget/PushButton/ComboBox etc. do.

Historically these were hardcoded to light-only values because the signal
available for "is the app in dark mode" - either qfluentwidgets' own
isDarkTheme(), or reading the widget's inherited QPalette - was unreliable:
several custom containers (QScrollArea, QTableWidget, QListWidget) painted
an opaque *native* palette background that hid Hamelin's real, correctly
themed background underneath, so isDarkTheme() (which only reflects
Hamelin's own Settings > Theme choice) and the real rendered palette could
disagree. That root cause is now fixed everywhere - see table_theme.py's
docstring - so isDarkTheme() is trustworthy again, as long as every call
site pairs it with an explicit hardcoded value for both branches, never an
inherited/native palette.

Lives under src/utils rather than src/view/widgets (where view code actually
imports it from - see that module) because a few pure-matplotlib analytics
modules (forecasting_chart.py, results_visualizer.py) need these colours too,
and importing anything under hamelin.view pulls in src/view/__init__.py's eager
`from .main_window import MainWindow`, which imports every page and widget -
a real circular import for any analytics module those widgets themselves
import. src/utils has no such dependency back into hamelin.view.

Usage::
    from hamelin.view.widgets.theme_colors import colors, on_theme_changed
    # or, from analytics/other non-view code:
    from hamelin.utils.theme_colors import colors, on_theme_changed

    def _apply_theme():
        label.setStyleSheet(f"color: {colors().text_secondary};")
    on_theme_changed(_apply_theme)
"""

from __future__ import annotations

from dataclasses import dataclass

from qfluentwidgets import isDarkTheme, qconfig


@dataclass(frozen=True)
class ThemeColors:
    text_primary: str
    text_secondary: str
    card_background: str
    table_row: str
    table_row_alt: str
    table_gridline: str
    table_header_bg: str
    table_header_border: str
    list_item_bg: str
    list_item_alt_bg: str
    list_item_selected_bg: str
    border: str
    scrollbar_handle: str
    scrollbar_handle_hover: str
    chart_face: str


# Light values match what was hardcoded throughout the app before this
# module existed - light mode's appearance shouldn't shift.
_LIGHT = ThemeColors(
    text_primary="#1A1A1A",
    text_secondary="#808080",  # Qt's named "gray", used everywhere as `color: gray;`
    card_background="#FFFFFF",
    table_row="#FFFFFF",
    table_row_alt="#F7F7F7",
    table_gridline="#E0E0E0",
    table_header_bg="#F3F3F3",
    table_header_border="#D0D0D0",
    list_item_bg="#FFFFFF",
    list_item_alt_bg="#F7F7F7",
    list_item_selected_bg="#CCE4F7",
    border="#E0E0E0",
    scrollbar_handle="#BDBDBD",
    scrollbar_handle_hover="#9E9E9E",
    chart_face="#FAFAFA",
)

# Dark values calibrated against qfluentwidgets' own dark QSS resources
# (:/qfluentwidgets/qss/dark/*.qss) so custom widgets don't clash with the
# native ones sitting right next to them.
_DARK = ThemeColors(
    text_primary="#E8E8E8",
    text_secondary="#A0A0A0",
    card_background="#2B2B2B",
    table_row="#232323",
    table_row_alt="#2A2A2A",
    table_gridline="#3D3D3D",
    table_header_bg="#262626",
    table_header_border="#3D3D3D",
    list_item_bg="#232323",
    list_item_alt_bg="#2A2A2A",
    list_item_selected_bg="#0F3F66",
    border="#3D3D3D",
    scrollbar_handle="#5A5A5A",
    scrollbar_handle_hover="#787878",
    chart_face="#232323",
)


def colors() -> ThemeColors:
    """Return the colour set for the app's current theme."""
    return _DARK if isDarkTheme() else _LIGHT


def on_theme_changed(apply_fn) -> None:
    """Call *apply_fn* now, and again every time the app's theme changes.

    The subscription is dropped by itself once *apply_fn* fails because the
    widget it styles has been destroyed (dialogs, cards rebuilt on every
    selection, ...); otherwise every later theme switch would raise
    "Internal C++ object already deleted" for each dead widget.
    """
    def apply(*_args) -> None:
        try:
            apply_fn()
        except RuntimeError:  # wrapped C++ object already deleted
            try:
                qconfig.themeChanged.disconnect(apply)
            except (RuntimeError, TypeError):
                pass

    apply_fn()
    qconfig.themeChanged.connect(apply)


def bind_style(widget, style_fn) -> None:
    """Set *widget*'s stylesheet from `style_fn(colors())` now, and keep it
    in sync with theme changes. Shorthand for the common one-label,
    one-rule case, e.g.::

        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
    """
    on_theme_changed(lambda: widget.setStyleSheet(style_fn(colors())))


def scrollbar_qss() -> str:
    """Flat, rounded scroll bar QSS (SCROLLBAR_QSS from table_theme.py),
    themed to the current light/dark colours."""
    c = colors()
    return f"""
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {c.scrollbar_handle};
            border-radius: 5px;
            min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {c.scrollbar_handle_hover};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {c.scrollbar_handle};
            border-radius: 5px;
            min-width: 24px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {c.scrollbar_handle_hover};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}
    """


def tooltip_qss() -> str:
    """App-wide QToolTip rule, themed. QToolTip is never touched by
    qfluentwidgets or by any per-widget stylesheet in this app (every
    setToolTip() call just relies on Qt's native tooltip), so it falls
    back to the native platform palette - on a system whose native
    tooltip palette is dark-on-dark (or otherwise mismatched), that made
    every tooltip unreadable regardless of Hamelin's own light/dark
    setting. Meant to be set once, app-wide (QApplication.setStyleSheet),
    since qfluentwidgets styles its own widgets individually rather than
    through the application-level stylesheet - see StyleSheetBase.apply -
    so this won't clash with anything else."""
    c = colors()
    return f"""
        QToolTip {{
            background-color: {c.card_background};
            color: {c.text_primary};
            border: 1px solid {c.border};
            padding: 4px 8px;
            opacity: 255;
        }}
    """


def file_dialog_qss() -> str:
    """Theme for Qt's own (non-native) open/save dialogs, which otherwise
    stay in the platform's light style whatever the app theme is. Native
    dialogs (Windows, macOS) ignore this and follow the OS."""
    c = colors()
    return f"""
        QFileDialog, QFileDialog QWidget {{
            background-color: {c.card_background};
            color: {c.text_primary};
        }}
        QFileDialog QListView, QFileDialog QTreeView {{
            background-color: {c.table_row};
            alternate-background-color: {c.table_row_alt};
            border: 1px solid {c.border};
            selection-background-color: {c.list_item_selected_bg};
            selection-color: {c.text_primary};
        }}
        QFileDialog QHeaderView::section {{
            background-color: {c.table_header_bg};
            color: {c.text_primary};
            border: 1px solid {c.table_header_border};
            padding: 4px;
        }}
        QFileDialog QLineEdit, QFileDialog QComboBox {{
            background-color: {c.table_row};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 3px 6px;
        }}
        QFileDialog QComboBox QAbstractItemView {{
            background-color: {c.table_row};
            color: {c.text_primary};
            selection-background-color: {c.list_item_selected_bg};
        }}
        QFileDialog QPushButton {{
            background-color: {c.table_header_bg};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 4px 14px;
        }}
        QFileDialog QPushButton:hover {{ background-color: {c.list_item_selected_bg}; }}
        QFileDialog QToolButton {{ background-color: transparent; border: none; }}
        QFileDialog QToolButton:hover {{ background-color: {c.list_item_selected_bg}; }}
    """


def apply_tooltip_theme() -> None:
    """Style every tooltip for the current theme: the QToolTip rule above
    plus the QToolTip palette. The rule alone left the tip window's
    background unpainted (a see-through window: black on some desktops)
    under the dark theme while its text turned light, so the text could not
    be read; the palette gives the tip an opaque base colour of its own."""
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QApplication, QToolTip

    c = colors()
    app = QApplication.instance()
    if app is not None:
        app.setStyleSheet(tooltip_qss() + file_dialog_qss())
    palette = QToolTip.palette()
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(c.card_background))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(c.text_primary))
    palette.setColor(QPalette.ColorRole.Window, QColor(c.card_background))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(c.text_primary))
    QToolTip.setPalette(palette)


def apply_transparent_container(widget) -> None:
    """Let the app's themed background show through *widget* and everything
    inside it (the pages' scroll-area content), keeping tooltips readable.

    A bare ``background: transparent;`` on a container also reaches the
    tooltips of the widgets inside it, and a widget-level rule beats the
    application-level QToolTip rule, so every tooltip on the page came out
    see-through (light text on nothing, in the dark theme). The QToolTip rule
    is therefore repeated in the same sheet, after the transparent one so it
    wins. Re-applied on theme changes because tooltip_qss() is themed."""
    on_theme_changed(lambda: widget.setStyleSheet("QWidget { background: transparent; } " + tooltip_qss()))


def scroll_area_qss() -> str:
    """Full stylesheet for a page's outer, border/background-less QScrollArea."""
    return "QScrollArea{border: none; background: transparent}" + scrollbar_qss()


def apply_scroll_area_theme(scroll_area) -> None:
    """Style *scroll_area* with scroll_area_qss() now, and keep it in sync
    with theme changes for the rest of the app's lifetime."""
    on_theme_changed(lambda: scroll_area.setStyleSheet(scroll_area_qss()))


def table_qss() -> str:
    """Background/alternate-row/text/gridline rule for QTableWidget and
    QTableView, themed. Needed *in addition to* an explicit QPalette (see
    table_theme.py's style_table_widget): qfluentwidgets applies its own
    app-wide QSS giving every QTableView a transparent background (its
    dark-theme table_view.qss), and a Qt stylesheet rule from an ancestor
    beats a plain QPalette colour for any role that rule also sets - so
    without a rule here too, the table's Base role silently reverts to
    that transparent default the moment qfluentwidgets' own stylesheet is
    live, regardless of what colour style_table_widget() set on the
    palette."""
    c = colors()
    return (
        f"QTableWidget, QTableView {{ "
        f"background-color: {c.table_row}; "
        f"alternate-background-color: {c.table_row_alt}; "
        f"color: {c.text_primary}; "
        f"gridline-color: {c.table_gridline}; "
        f"}}"
    )


def table_header_qss() -> str:
    """QHeaderView::section rule used by table_theme.py for a table's
    column and row headers."""
    c = colors()
    return f"""
        QHeaderView::section {{
            background-color: {c.table_header_bg};
            color: {c.text_primary};
            border: none;
            border-bottom: 1px solid {c.table_header_border};
            padding: 4px;
        }}
    """


def list_item_qss(extra: str = "") -> str:
    """QListWidget::item background + alternating-row + selected-row rules, themed. *extra*
    is appended verbatim (e.g. an explicit item text colour)."""
    c = colors()
    return (
        f"QListWidget {{ background: {c.list_item_bg}; }}"
        f"QListWidget::item {{ background: {c.list_item_bg}; {extra} }}"
        f"QListWidget::item:alternate {{ background: {c.list_item_alt_bg}; }}"
        f"QListWidget::item:selected {{ background: {c.list_item_selected_bg}; {extra} }}"
    )


def style_figure(fig, *axes) -> None:
    """Apply the current theme's chart colours to a matplotlib Figure and
    any number of its Axes - face colour, tick/label/title colour, spine
    and grid colour. Safe to call on axes with ticks/spines hidden."""
    c = colors()
    fig.patch.set_facecolor(c.chart_face)
    for ax in axes:
        ax.set_facecolor(c.chart_face)
        ax.tick_params(colors=c.text_secondary)
        ax.xaxis.label.set_color(c.text_secondary)
        ax.yaxis.label.set_color(c.text_secondary)
        ax.title.set_color(c.text_primary)
        for spine in ax.spines.values():
            spine.set_color(c.table_gridline)
        legend = ax.get_legend()
        if legend is not None:
            legend.get_frame().set_facecolor(c.chart_face)
            legend.get_frame().set_edgecolor(c.table_gridline)
            for text in legend.get_texts():
                text.set_color(c.text_secondary)

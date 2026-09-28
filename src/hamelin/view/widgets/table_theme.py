"""
Table Theme Sync
~~~~~~~~~~~~~~~~

A plain QTableWidget doesn't inherit qfluentwidgets' theming the way
CardWidget/PushButton/etc. do - anything it doesn't style itself falls
back to Qt's palette, which is fine in principle, EXCEPT that the
default alternate-row/gridline/header colors barely contrast with each
other and font/padding aren't set at all - rows blur together.

This was first "fixed" by picking one of two hardcoded colour sets based
on qfluentwidgets' isDarkTheme() - the wrong signal, since it only
reflects Hamelin's own Settings > Theme choice (always "Light" unless
changed there), not what's actually rendered.

The next attempt used the Qt Style Sheets palette() function instead,
on the theory that it always resolves to whatever's really active and
would automatically match CardWidget's own background. In practice it
doesn't: this app's actual inherited QPalette can come back dark
regardless of Hamelin's light theme (independently of anything this app
controls), while CardWidget and everything else styled with a fixed
colour keep rendering light - so a table styled with palette() ends up
dark, sitting on an otherwise light page.

Setting colours via QPalette instead of a plain "QTableWidget { ... }"
stylesheet avoids that - background/alternate-row/text/gridline are set
here on the table's own QPalette, not a stylesheet, so items/headers
with their own explicit foreground (e.g. the gray secondary-info column
in DataPage's variables table) still override these defaults, same as
with a plain, unstyled table.

The QScrollArea/QTableWidget/QListWidget opaque-native-background bug
behind both of those failed attempts is now fixed app-wide (this table
included - see style_table_widget() below), which makes isDarkTheme()
trustworthy again. Colours themselves now live in theme_colors.py and
are re-applied on every qconfig.themeChanged, so light/dark switches
live without a restart.

The flat, rounded scroll bar look used everywhere in Hamelin that has
its own scrollable area (this table, a page's own QScrollArea, a
QListWidget, ...) instead of each one's native OS rendering now lives
in theme_colors.scrollbar_qss() - deliberately consistent app-wide
rather than left to whatever the underlying platform happens to draw
by default, and themed the same way as everything else here.

Usage::
    from hamelin.view.widgets.table_theme import style_table_widget
    style_table_widget(self.data_table)
"""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFrame, QTableWidget

from hamelin.view.widgets.theme_colors import colors, on_theme_changed, scrollbar_qss, table_header_qss, table_qss


def style_table_widget(table: QTableWidget) -> None:
    """Colour *table* via QPalette (background/alternate-row/text/
    gridline) AND a matching stylesheet rule (table_qss() - see its
    docstring for why the QPalette alone isn't enough once qfluentwidgets'
    own app-wide QSS is live), plus a stylesheet for its headers and its
    own scroll bar. Re-applied on every theme change so switching
    Settings > Theme updates the table live, no restart needed."""
    table.setFrameShape(QFrame.Shape.Box)
    table.setLineWidth(1)

    def _apply() -> None:
        c = colors()
        palette = table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(c.table_row))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(c.table_row_alt))
        palette.setColor(QPalette.ColorRole.Text, QColor(c.text_primary))
        palette.setColor(QPalette.ColorRole.Mid, QColor(c.table_gridline))  # gridlines
        table.setPalette(palette)
        table.setStyleSheet(table_qss() + scrollbar_qss())
        table.horizontalHeader().setStyleSheet(table_header_qss())
        # The row-number header - separate widget from the column one above,
        # so it needs the same rule again or it's left on its own unstyled
        # (dark) default instead of matching the rest of the table.
        table.verticalHeader().setStyleSheet(table_header_qss())

    on_theme_changed(_apply)

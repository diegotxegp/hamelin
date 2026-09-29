"""
Arrow Cursor Filter
~~~~~~~~~~~~~~~~~~~

App-wide event filter that keeps the basic arrow cursor everywhere.

Some widgets ask for a pointing-hand cursor on their own (qfluentwidgets'
HyperlinkButton and a few of its own controls, plus the "?" help buttons).
The app wants the plain arrow throughout, so instead of touching every
construction site this filter resets any pointing-hand cursor the moment a
widget is shown or hovered. Other cursors are left alone: text fields keep
their I-beam and resize grips keep their resize cursors.
"""

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QWidget


class ArrowCursorFilter(QObject):
    """Install on a QApplication with ``app.installEventFilter(...)``."""

    _EVENTS = (QEvent.Type.Show, QEvent.Type.Enter)

    def eventFilter(self, obj, event) -> bool:
        if (
            event.type() in self._EVENTS
            and isinstance(obj, QWidget)
            and obj.cursor().shape() == Qt.CursorShape.PointingHandCursor
        ):
            obj.setCursor(Qt.CursorShape.ArrowCursor)
        return False

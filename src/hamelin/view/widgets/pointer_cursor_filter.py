"""
Pointing-Hand Cursor Filter
~~~~~~~~~~~~~~~~~~~~~~~~~~~

App-wide event filter that gives every clickable control a pointing-hand
cursor on hover.

qfluentwidgets only does this itself for HyperlinkButton (see
qfluentwidgets/components/widgets/button.py) - PushButton,
PrimaryPushButton, ToolButton, ComboBox, SwitchButton and everything else
fall back to Qt's default arrow cursor, which made buttons across the app
feel inconsistent (some had a hand cursor, most didn't). Installed once on
the QApplication instead of touching every button construction site
individually across every page.

Matches the convention already used throughout the standalone "interface"
tool, where every clickable widget sets Qt.PointingHandCursor directly.
"""

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QAbstractButton, QComboBox

from qfluentwidgets import SwitchButton

_TARGET_TYPES = (QAbstractButton, QComboBox, SwitchButton)


class PointingHandCursorFilter(QObject):
    """Install on a QApplication with ``app.installEventFilter(...)``."""

    def eventFilter(self, obj, event) -> bool:
        if isinstance(obj, _TARGET_TYPES) and obj.isEnabled():
            if event.type() == QEvent.Type.Enter:
                obj.setCursor(Qt.CursorShape.PointingHandCursor)
            elif event.type() == QEvent.Type.Leave:
                obj.unsetCursor()
        return False

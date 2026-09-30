"""
Wheel Guard
~~~~~~~~~~~

App-wide event filter that stops the mouse wheel from changing values.

By default Qt lets the wheel step a spin box, flip a combo box to its next
entry or move a slider whenever the pointer happens to rest on it, so
scrolling a long page silently alters settings. With this filter those
widgets ignore the wheel and Qt passes it on to the page's scroll area, so
the page keeps scrolling normally.
"""

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractSpinBox, QComboBox, QSlider

# Not QAbstractSlider: QScrollBar is one, and scroll areas scroll through it.
_GUARDED = (QAbstractSpinBox, QComboBox, QSlider)


class WheelGuard(QObject):
    """Install on a QApplication with ``app.installEventFilter(...)``."""

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.Wheel and isinstance(obj, _GUARDED):
            # Returning True with the event *ignored* makes Qt stop handing
            # it to this widget and offer it to the parent instead, so the
            # enclosing scroll area scrolls as if the widget were not there.
            event.ignore()
            return True
        return False

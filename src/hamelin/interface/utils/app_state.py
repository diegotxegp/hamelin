"""App-wide UI state. Currently just the advanced/simple mode toggle - kept
as a tiny module-level singleton rather than threading a context object
through every page constructor, since pages are all built with no args."""

from PySide6.QtCore import QObject, Signal


class AppState(QObject):
    advancedModeChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self._advanced_mode = False

    @property
    def advanced_mode(self):
        return self._advanced_mode

    def set_advanced_mode(self, value):
        value = bool(value)
        if value == self._advanced_mode:
            return
        self._advanced_mode = value
        self.advancedModeChanged.emit(value)


app_state = AppState()

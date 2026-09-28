"""Light/dark state for the whole app. Deliberately free of any Hamelin or
qfluentwidgets import so the interface still runs standalone; a host app just
calls set_dark() (e.g. from its own theme-changed signal)."""

from PySide6.QtCore import QObject, Signal


class ThemeState(QObject):
    themeChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self._dark = False

    @property
    def dark(self):
        return self._dark

    def set_dark(self, value):
        value = bool(value)
        if value == self._dark:
            return
        self._dark = value
        self.themeChanged.emit(value)


theme_state = ThemeState()


def set_dark(value):
    theme_state.set_dark(value)

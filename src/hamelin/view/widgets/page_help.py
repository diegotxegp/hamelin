"""
Page Help Button
~~~~~~~~~~~~~~~~

A circular "?" button meant for a page's title row, opening a small popup
with a plain-language explanation of what that page lets a clinician do -
mirrors the "?" info buttons already used throughout the standalone
interface/ tool (see interface/utils/theme.py's style_info_button/Popup),
adapted for Hamelin:

- Styled from theme_colors.py rather than the Qt Style Sheets palette()
  function. palette() used to be the safer choice here, back when
  qfluentwidgets' isDarkTheme() didn't reliably match the real inherited
  palette in this app (see table_theme.py's docstring for that history) -
  but that root cause is fixed everywhere now (see theme_colors.py's own
  docstring), and palette() itself turned out to have the opposite
  problem: this widget's native/inherited palette doesn't actually track
  Hamelin's own light/dark Settings choice, it tracks the OS/Qt platform
  theme - on a system whose native palette defaults to dark, that made
  this popup black-on-black regardless of what Hamelin's own theme was
  set to.
- The popup is a Qt.Popup + FramelessWindowHint + NoDropShadowWindowHint
  window: Qt.Popup alone still gets the window manager's own
  decoration/border drawn around it (a visible "double frame" - the WM's
  square border behind this widget's own) - FramelessWindowHint stops the
  WM decorating it at all, so only this widget's own border shows. On some
  compositors FramelessWindowHint alone still leaves a faint drop-shadow
  rectangle around the frame (the same "double frame" look, one more
  layer down) - NoDropShadowWindowHint suppresses that too.
- Square corners (no border-radius), on purpose: a rounded version was
  tried too, which needs the window itself to be alpha-translucent so the
  four corner triangles outside the rounded rect are transparent instead
  of an opaque square block - but real desktop compositing here rendered
  that as genuinely see-through instead, with page content showing
  straight through the popup's middle. Square corners need no such
  translucency, so they sidestep that failure mode entirely.
- attach_help_popup() (below) opens on click by default - see its own
  docstring for when to use attach_help_popup_hover() instead, and why
  that one only shows after a couple of seconds of hovering rather than
  immediately.
- HelpPopup (below) is the one and only rich-text help surface in this
  app - see help_button.py's HelpButton, the smaller per-section "?" used
  everywhere else, which shows this same class instead of a native
  QToolTip. A native tooltip's look is ultimately up to the OS/platform
  theme (some Linux desktop/style integrations paint QToolTip natively
  and ignore the app's own QSS entirely, regardless of theme_colors.py's
  app-wide QToolTip rule), so it was never actually a reliable place to
  put anything but the shortest incidental hint - this widget, fully
  self-painted, isn't at the mercy of that.

Usage::
    from hamelin.view.widgets.page_help import PageHelpButton

    title_row.addWidget(TitleLabel(t("data.title")))
    title_row.addStretch()
    title_row.addWidget(PageHelpButton(t("data.help")))
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from hamelin.utils.theme_colors import colors, on_theme_changed
from hamelin.utils.usage_logger import usage_log, infer_page_name


def _position_popup(popup: QWidget, anchor: QWidget) -> None:
    """Anchor *popup* below *anchor*, flipping above it - or clamping
    sideways - instead of running off whatever screen *anchor* is on.
    popup's size must already be final (HelpPopup's SetFixedSize layout
    constraint guarantees that as soon as it's constructed, before the
    first show())."""
    screen = anchor.screen() if hasattr(anchor, "screen") else None
    screen = screen or QApplication.primaryScreen()
    bounds = screen.availableGeometry() if screen else None

    size = popup.sizeHint()
    below = anchor.mapToGlobal(anchor.rect().bottomLeft())
    x, y = below.x(), below.y()

    if bounds is not None:
        if y + size.height() > bounds.bottom():
            above_y = anchor.mapToGlobal(anchor.rect().topLeft()).y() - size.height()
            y = max(bounds.top(), above_y)
        x = min(x, bounds.right() - size.width())
        x = max(x, bounds.left())

    popup.move(x, y)


class HelpPopup(QFrame):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(
            parent,
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        c = colors()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {c.card_background};
                color: {c.text_primary};
                border: 2px solid {c.border};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        # A word-wrapped QLabel's heightForWidth isn't reliably picked up
        # by the popup's initial size otherwise - long text (e.g. the
        # Training page's) would get clipped instead of growing the popup.
        # SetFixedSize makes the whole frame always resize to exactly fit
        # its content.
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        label = QLabel(text)
        label.setWordWrap(True)
        # Fixes the label's width so wrapping - and therefore its wrapped
        # height - is deterministic; 380 total width minus the margins above.
        label.setFixedWidth(340)
        label.setStyleSheet(f"background: transparent; color: {c.text_primary}; font-size: 14px;")
        layout.addWidget(label)


class PageHelpButton(QPushButton):
    """Circular "?" button; click opens a plain-language popup anchored
    below it. `help_text` should already be translated (pass t("...") in,
    not a raw key) since this codebase's i18n has no live reload."""

    def __init__(self, help_text: str, parent: QWidget | None = None):
        super().__init__("?", parent)
        self.help_text = help_text
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        on_theme_changed(self._apply_theme)
        self.clicked.connect(self._show_popup)

    def _apply_theme(self):
        c = colors()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c.card_background};
                color: {c.text_primary};
                border: 2px solid {c.border};
                border-radius: 16px;
                font-size: 16px;
                font-weight: 700;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {c.list_item_alt_bg};
            }}
            QPushButton:pressed {{
                background-color: {c.list_item_selected_bg};
            }}
        """)

    def _show_popup(self):
        usage_log.event(infer_page_name(self), "click", "Help button (page)", self.help_text[:60])
        popup = HelpPopup(self.help_text, self)
        _position_popup(popup, self)
        popup.show()


def attach_help_popup(widget: QWidget, text: str) -> None:
    """Give *widget* a HelpPopup on click instead of a native QToolTip -
    see HelpPopup's own docstring for why setToolTip() isn't used for
    anything but the shortest incidental hint in this app. Drop-in
    replacement for widget.setToolTip(text); works on any QWidget
    (buttons, combo boxes, the rule-builder widgets, ...) that has a
    clicked signal or accepts a plain mouse click.

    Not for a widget where clicking already means something else - a
    QListWidget's own items, say, where every click to select/deselect
    a row would also pop this open. See attach_help_popup_hover() for
    those instead.
    """
    def _show(*_args):
        usage_log.event(infer_page_name(widget), "click", "Help button (attached)", text[:60])
        popup = HelpPopup(text, widget)
        _position_popup(popup, widget)
        popup.show()

    clicked = getattr(widget, "clicked", None)
    if clicked is not None:
        clicked.connect(_show)
        return

    # Widgets with no clicked signal of their own (QComboBox, the
    # rule-builder widgets...) - a raw mouse-press event filter instead.
    from PySide6.QtCore import QEvent, QObject

    class _ClickFilter(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.MouseButtonPress:
                _show()
            return False

    widget.installEventFilter(_ClickFilter(widget))


def attach_help_popup_hover(widget: QWidget, text: str, delay_ms: int = 2000) -> None:
    """Give *widget* a HelpPopup that appears after the mouse has sat over
    it for *delay_ms* (default 2s), and disappears again as soon as the
    mouse leaves - no click involved either way. For a widget like
    attach_help_popup() itself warns against: a QListWidget whose items
    are clicked to select/deselect them, where a click-triggered popup
    fires on every single one of those instead of just an incidental
    first click.

    The delay matters: an earlier version showed the popup on the very
    first mouseover (no delay) and hid it as soon as the mouse left
    either the widget or the popup - in practice that flickered open and
    closed from completely ordinary mouse movement (e.g. sweeping across
    the list on the way to click an item several rows down). Requiring a
    couple of seconds of the mouse genuinely sitting still means passing
    through on the way to click something else never triggers it.
    """
    from PySide6.QtCore import QEvent, QObject, QTimer

    class _HoverFilter(QObject):
        def __init__(self, widget):
            super().__init__(widget)
            self._widget = widget
            self._popup: HelpPopup | None = None
            self._open_timer = QTimer(self)
            self._open_timer.setSingleShot(True)
            self._open_timer.setInterval(delay_ms)
            self._open_timer.timeout.connect(self._show)

        def _show(self):
            if self._popup is not None:
                return
            usage_log.event(infer_page_name(self._widget), "hover", "Help popup (hover)", text[:60])
            popup = HelpPopup(text, self._widget)
            popup.destroyed.connect(self._forget)
            _position_popup(popup, self._widget)
            popup.show()
            self._popup = popup

        def _forget(self):
            self._popup = None

        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.Enter:
                self._open_timer.start()
            elif event.type() == QEvent.Type.Leave:
                self._open_timer.stop()
                if self._popup is not None:
                    self._popup.close()
            return False

    widget.installEventFilter(_HoverFilter(widget))

import re
import weakref
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QTimer, QByteArray
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QFontDatabase, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QFrame, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QComboBox, QAbstractButton
)
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon

from hamelin.interface.utils.colors import BLUE, YELLOW, WHITE, BLACK, GREEN, colors, restyle, themed
from hamelin.interface.utils.theme_state import theme_state

# Resolved from this file's own location rather than a "assets/x.svg"
# path relative to the process's current working directory - the app is
# also launched embedded inside another app (Hamelin), whose CWD isn't
# necessarily this project's root, so a CWD-relative path would silently
# fail to load there.
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
FONTS_DIR = Path(__file__).resolve().parent / "fonts"


def asset_icon(name):
    if not theme_state.dark:
        return QIcon(str(ASSETS_DIR / name))
    c = colors()
    svg = (ASSETS_DIR / name).read_text(encoding="utf-8")
    for original, tint in (("#3333B0", c.icon), ("#464D48", c.muted), ("#121010", c.text)):
        svg = re.sub(re.escape(original), tint, svg, flags=re.IGNORECASE)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(96, 96)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


# id(button) -> (weakref, icon file name), so icons re-tint on a theme switch
_asset_icons = {}


def set_asset_icon(button, name):
    key = id(button)
    if key not in _asset_icons:
        button.destroyed.connect(lambda *_, k=key: _asset_icons.pop(k, None))
    _asset_icons[key] = (weakref.ref(button), name)
    button.setIcon(asset_icon(name))


def _refresh_asset_icons(_dark=None):
    for key, (ref, name) in list(_asset_icons.items()):
        try:
            ref().setIcon(asset_icon(name))
        except (RuntimeError, AttributeError):
            _asset_icons.pop(key, None)


theme_state.themeChanged.connect(_refresh_asset_icons)


def load_app_fonts():
    for name in ("Inter-Regular.ttf", "Inter-Medium.ttf", "Inter-Bold.ttf"):
        QFontDatabase.addApplicationFont(str(FONTS_DIR / name))


class ClickableHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        self.setSectionsClickable(True)

        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.viewport():
            if event.type() == QEvent.MouseMove:
                logical = self.logicalIndexAt(event.pos())

                if logical >= 0:
                    self.viewport().setCursor(Qt.PointingHandCursor)
                else:
                    self.viewport().setCursor(Qt.ArrowCursor)

            elif event.type() == QEvent.Leave:
                self.viewport().setCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)


class BackgroundWidget(QWidget):
    """Flat page background - same light neutral (#F0F4F9) as Hamelin's
    own window background, instead of this app's old solid-blue-plus-two-
    decorative-circles look."""

    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(colors().page))


class RoundedButton(QPushButton):
    def __init__(self, text, w, h, radius):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(w, h)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._accent = None
        themed(self, lambda c, radius=radius: f"""
            QPushButton {{
                background: {c.surface};
                color: {c.text};
                border: 2px solid {c.border};
                border-radius: {radius}px;
                font-size: 32px;
                font-weight: 700;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background: {c.line};
                color: {WHITE};
            }}
        """ + (f"QPushButton {{ background: {self._accent}; color: {BLACK}; }}" if self._accent else ""))

    def set_accent(self, color):
        """Fill the button with an accent colour (or None to clear it),
        e.g. the yellow "favorited" state; text stays black on the accent."""
        self._accent = color
        restyle(self)


class DropdownCard(QPushButton):
    def __init__(self, text):
        super().__init__()

        self.setText(text)
        self.setMinimumHeight(96)
        self.setCursor(Qt.PointingHandCursor)
        theme_state.themeChanged.connect(self.update)
        themed(self, lambda c: f"""
        QPushButton {{
            background: {c.surface};
            border: 2px solid {c.border};
            border-radius: 16px;
            color: {c.text};
            font-size: 32px;
            font-weight: 400;
            text-align: left;
            padding-left: 28px;
            padding-right: 70px;
        }}
        QPushButton:hover {{
            background: {c.line};
            color: {WHITE};
        }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        pen_color = WHITE if self.underMouse() else colors().muted
        p.setPen(QPen(QColor(pen_color), 3))

        x = self.width() - 45
        y = self.height() // 2 - 8

        p.drawLine(x - 10, y, x, y + 10)
        p.drawLine(x + 10, y, x, y + 10)

class StyledComboBox(QComboBox):
    """
    Même style visuel que DropdownCard
    mais conserve le comportement d'un vrai QComboBox.
    """

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(96)
        self.setCursor(Qt.PointingHandCursor)
        theme_state.themeChanged.connect(self.update)
        themed(self, lambda c: f"""
        QComboBox {{
            background: {c.surface};
            border: 2px solid {c.border};
            border-radius: 16px;
            color: {c.text};
            font-size: 24px;
            padding-left: 28px;
            padding-right: 70px;
        }}

        QComboBox::drop-down {{
            border: none;
            width: 60px;
        }}

        QComboBox::down-arrow {{
            image: none;
        }}

        QComboBox QAbstractItemView {{
            background: {c.surface};
            color: {c.text};
            border: 2px solid {c.border};
            selection-background-color: {c.line};
            selection-color: {c.text};
        }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(QPen(QColor(colors().muted), 3))

        x = self.width() - 40
        y = self.height() // 2 - 8

        p.drawLine(x - 10, y, x, y + 10)
        p.drawLine(x + 10, y, x, y + 10)


class Popup(QFrame):
    def __init__(
        self,
        parent=None,
        width=500,
        height=250,
        x=100,
        y=100,
        background=None,
        radius=20,
    ):
        super().__init__(parent)

        self.setObjectName("Popup")

        self.setGeometry(x, y, width, height)

        # An accent `background` (the yellow help popups) becomes a plain dark
        # surface with an accent border in dark mode, so the text inside can
        # simply follow the theme's text colour.
        def popup_style(c):
            if background is None:
                fill, edge = c.surface, c.border_pure
            elif c.dark:
                fill, edge = c.surface, background
            else:
                fill, edge = background, c.border_pure
            return f"""
            QFrame#Popup {{
                background: {fill};
                border: 2px solid {edge};
                border-radius: {radius}px;
            }}
        """

        themed(self, popup_style)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 25, 25, 25)

        self.close_btn = RoundedButton("×", 44, 44, 22)

        themed(self.close_btn, f"""
            QPushButton {{
                font-size: 36px;
                font-weight: 700;
                background: {YELLOW};
                color: {BLACK};
                border: none;
                border-radius: 22px;
                padding: 0;
            }}

            QPushButton:hover {{
                background: #CC7000;
                color: {BLACK};
            }}
        """)

        self.close_btn.setParent(self)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.raise_()

        self._close_btn_margin = 8
        self._position_close_btn()


    def _position_close_btn(self):
        self.close_btn.move(
            self.width() - self.close_btn.width() - self._close_btn_margin,
            self._close_btn_margin
        )


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_close_btn()


class WidgetPopupOverlay(QWidget):
    """Frameless overlay that hosts another widget, centered over its parent
    with a close button. Used by the model-type explanation pages to show a
    CNN/MLP/LSTM diagram widget on top of whichever page opened it."""

    def __init__(self, content_widget: QWidget, parent=None, title="Info", width=1200, height=750):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_StyledBackground, True)

        themed(self, lambda c: f"""
            QWidget {{
                background: {c.surface};
                color: {c.text};
                border: 2px solid {c.border};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(34, 34)
        btn_close.setCursor(Qt.PointingHandCursor)
        themed(btn_close, lambda c: f"""
            QPushButton {{
                background: {c.surface};
                color: {c.text};
                font-size: 18px;
                font-weight: 700;
                border-radius: 17px;
                border: none;
            }}
            QPushButton:hover {{
                background: {c.line};
                color: {WHITE};
            }}
        """)
        btn_close.clicked.connect(self.close)

        header.addWidget(btn_close)
        root.addLayout(header)

        content_widget.setParent(self)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(content_widget, stretch=1)

        if parent:
            x = (parent.width() - width) // 2
            y = (parent.height() - height) // 2
            self.setGeometry(x, y, width, height)
            self.raise_()


def info_button_row(button):
    """Right-aligned row holding a page's (!) button, meant to sit just above
    the card it explains instead of floating over the card's content."""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch()
    layout.addWidget(button)
    return row


def style_info_button(button, background_color, text_color=None):
    """Shared visual style for the circular "!" info buttons used across the
    comparison views (table/heatmap/graphs/config-diff pages)."""
    text_color = text_color or BLACK
    themed(button, lambda c, background_color=background_color, text_color=text_color: f"""
        QPushButton {{
            font-size: 28px;
            font-weight: 700;
            background: {background_color};
            color: {text_color};
            border: none;
            border-radius: 25px;
            padding: 0;
        }}
    """)


def build_glossary_widget(entries, intro=None, empty_text="Nothing to explain yet.", footer_title=None, footer_lines=None):
    """Plain-text (no rich-text/HTML) glossary block: an optional intro line,
    then one bold label + description per entry, then an optional separated
    footer section (e.g. dataset sizes) below a thin divider. Shared by
    every popup that explains a list of metrics or settings, so they render
    consistently instead of one view bolting extra text onto the bottom on
    its own."""
    container = QWidget()
    container.setAttribute(Qt.WA_StyledBackground, True)
    themed(container, "background: transparent;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(14)

    if intro:
        intro_label = QLabel(intro)
        intro_label.setWordWrap(True)
        themed(intro_label, lambda c: f"color: {c.text}; font-size: 16px; font-weight: 700; background: transparent;")
        layout.addWidget(intro_label)

    if not entries and not footer_lines:
        empty_label = QLabel(empty_text)
        empty_label.setWordWrap(True)
        themed(empty_label, lambda c: f"color: {c.text}; font-size: 16px; background: transparent;")
        layout.addWidget(empty_label)
    else:
        for entry in entries:
            star = "⭐ " if entry.get("priority") else ""
            title = QLabel(f"{star}{entry['label']}")
            title.setWordWrap(True)
            themed(title, lambda c: f"color: {c.text}; font-size: 16px; font-weight: 700; background: transparent;")
            layout.addWidget(title)

            desc = QLabel(entry["text"])
            desc.setWordWrap(True)
            themed(desc, lambda c: f"color: {c.text}; font-size: 15px; background: transparent;")
            layout.addWidget(desc)

    if footer_lines:
        divider = QWidget()
        divider.setAttribute(Qt.WA_StyledBackground, True)
        divider.setFixedHeight(1)
        themed(divider, lambda c: f"background: {c.line};")
        layout.addSpacing(4)
        layout.addWidget(divider)

        if footer_title:
            footer_title_label = QLabel(footer_title)
            themed(footer_title_label, lambda c: f"color: {c.text}; font-size: 14px; font-weight: 700; background: transparent;")
            layout.addWidget(footer_title_label)

        for line in footer_lines:
            line_label = QLabel(line)
            line_label.setWordWrap(True)
            themed(line_label, lambda c: f"color: {c.muted}; font-size: 13px; background: transparent;")
            layout.addWidget(line_label)

    layout.addStretch()
    return container


class Toast(QFrame):
    """Small self-dismissing message - an icon + a colored accent border
    instead of a new color per meaning, that closes itself after a few
    seconds instead of needing a close click. Centered near the top of its
    parent so it doesn't sit on top of whatever the user was just
    interacting with. success=True reads as a green checkmark (e.g. "export
    finished"); success=False is the red-flag look ErrorPopup always used.

    Usage::
        Toast(self, "Exported chart.png and chart.csv").show()
        Toast(self, "Export failed: disk full", success=False).show()
    """

    def __init__(self, parent, message, success=True, duration_ms=3000, width=460):
        super().__init__(parent)
        self.setObjectName("Toast")

        accent = GREEN if success else YELLOW
        icon_char = "✓" if success else "⚠"

        themed(self, lambda c, accent=accent: f"""
            QFrame#Toast {{
                background: {c.toast_bg};
                border: 2px solid {accent};
                border-radius: 14px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(10)

        icon = QLabel(icon_char)
        themed(icon, lambda c, accent=accent: f"""
            color: {accent};
            font-size: 22px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        layout.addWidget(icon)

        text = QLabel(message)
        text.setWordWrap(True)
        themed(text, lambda c: f"""
            color: {c.toast_text};
            font-size: 16px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        layout.addWidget(text, stretch=1)

        self.setFixedWidth(width)
        self.adjustSize()

        if parent is not None:
            x = (parent.width() - self.width()) // 2
            self.move(max(x, 20), 30)

        QTimer.singleShot(duration_ms, self.close)


class ErrorPopup(Toast):
    """Toast for invalid/missing input - kept as its own name since "error"
    reads clearer at each call site than a success=False flag would.

    Usage::
        ErrorPopup(self, "Please select at least a model.").show()
    """

    def __init__(self, parent, message, duration_ms=3000, width=460):
        super().__init__(parent, message, success=False, duration_ms=duration_ms, width=width)


class _SwitchButton(QAbstractButton):
    """Painted on/off track+knob switch. No dedicated toggle widget existed
    in this codebase before - checkable QPushButtons/DropdownCards all read
    as buttons, not as a persistent on/off state, which is what a mode
    switch needs to communicate."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(52, 28)
        theme_state.themeChanged.connect(self.update)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        # "On" is BLACK, not BLUE, in light mode: several pages put this
        # switch on a blue top bar, where a blue track vanishes into the
        # background and only the white knob stays visible.
        c = colors()
        on = BLUE if c.dark else BLACK
        p.setBrush(QColor(on if self.isChecked() else c.line))
        p.drawRoundedRect(QRectF(self.rect()), self.height() / 2, self.height() / 2)

        margin = 3
        knob_d = self.height() - 2 * margin
        x = self.width() - margin - knob_d if self.isChecked() else margin
        p.setBrush(QColor(WHITE))
        p.drawEllipse(QRectF(x, margin, knob_d, knob_d))


class AdvancedModeToggle(QWidget):
    """Small labeled switch meant for a page's top bar. Wraps the painted
    switch (`self.switch`) with a label so pages don't each redo the label
    styling; `toggled` mirrors the switch's own signal."""

    def __init__(self, parent=None, text="Advanced mode", text_color=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        text_color = text_color or (lambda c: c.text)
        label = QLabel(text)
        themed(label, lambda c: f"""
            color: {text_color(c)};
            font-size: 14px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(label)

        self.switch = _SwitchButton()
        layout.addWidget(self.switch)

        self.toggled = self.switch.toggled

    def isChecked(self):
        return self.switch.isChecked()

    def setChecked(self, value):
        self.switch.setChecked(value)

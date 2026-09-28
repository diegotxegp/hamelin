# Shared palette for the whole app. Every page should import COLORS (or the
# aliases below) from here instead of redeclaring its own copy.
# Retinted to match Hamelin's Fluent Design palette (same accent blue and
# status colors as hamelin-v2/src/view), while keeping this app's own
# layout/shapes (thick borders, large radii) untouched - see widgets.py.
import weakref
from dataclasses import dataclass

from hamelin.interface.utils.theme_state import theme_state

COLORS = {
    "blue": "#0078D4",
    "yellow": "#E0DD6C",
    "white": "#FFFFFF",
    "black": "#121010",
    "gray": "#605E5C",
    "gray_light": "#C8C6C4",
    "gray_pale": "#F0F4F9",
    "green": "#107C10",
    # The circular (!) info buttons keep this app's original soft yellow,
    # same yellow as the accent above; kept as its own key for hover.
    "info_yellow": "#E0DD6C",
    "info_yellow_hover": "#CFC85A",
}

BLUE = COLORS["blue"]
YELLOW = COLORS["yellow"]
WHITE = COLORS["white"]
BLACK = COLORS["black"]
GRAY = COLORS["gray"]
GRAY_LIGHT = COLORS["gray_light"]
GRAY_PALE = COLORS["gray_pale"]
GREEN = COLORS["green"]
INFO_YELLOW = COLORS["info_yellow"]
INFO_YELLOW_HOVER = COLORS["info_yellow_hover"]


@dataclass(frozen=True)
class Palette:
    page: str
    surface: str
    surface_alt: str
    header_bg: str
    text: str
    muted: str
    subtle: str
    border: str
    line: str
    input_bg: str
    selected: str
    scrollbar: str
    chart_face: str
    chart_grid: str
    text_pure: str
    border_pure: str
    header_pure: str
    hover_tint: str
    accent_fill: str
    accent_edge: str
    accent_edge_pure: str
    primary_fill: str
    ring: str
    spoke: str
    rule: str
    label_text: str
    priority_text: str
    blue_text: str
    icon: str
    toast_bg: str
    toast_text: str
    dark: bool


# Light values equal the constants above so light mode is unchanged. Dark
# values follow Hamelin's src/utils/theme_colors.py.
LIGHT = Palette(
    page=GRAY_PALE, surface=WHITE, surface_alt="#F7F7F7", header_bg=BLACK, text=BLACK, muted=GRAY, subtle="#555555",
    border=BLACK, line=GRAY_LIGHT, input_bg=WHITE, selected="#CCE4F7",
    scrollbar="#C8C8C8", chart_face=WHITE, chart_grid="#D0D0D0", text_pure="black", border_pure="black", header_pure="black", hover_tint="rgba(0,0,0,0.05)",
    accent_fill=YELLOW, accent_edge=BLACK, accent_edge_pure="black", primary_fill=BLACK,
    ring="#BBBBBB", spoke="#AAAAAA", rule="#BDBDBD", label_text="#111111", priority_text="#155724",
    blue_text=BLUE, icon="#3333B0", toast_bg=BLACK, toast_text=WHITE, dark=False,
)
DARK = Palette(
    page="#1E1E1E", surface="#2A2A2A", surface_alt="#323232", header_bg="#151515", text="#E8E8E8", muted="#A0A0A0", subtle="#B0B0B0",
    border="#5C5C5C", line="#4A4A4A", input_bg="#232323", selected="#0F3F66",
    scrollbar="#5A5A5A", chart_face="#2A2A2A", chart_grid="#3D3D3D", text_pure="#E8E8E8", border_pure="#5C5C5C", header_pure="#151515", hover_tint="rgba(255,255,255,0.08)",
    accent_fill="#323232", accent_edge=YELLOW, accent_edge_pure=YELLOW, primary_fill=BLUE,
    ring="#555555", spoke="#6A6A6A", rule="#4A4A4A", label_text="#E8E8E8", priority_text="#7FD99A",
    blue_text="#4CC2FF", icon="#8C9EFF", toast_bg="#3A3A3A", toast_text="#F0F0F0", dark=True,
)


def colors():
    return DARK if theme_state.dark else LIGHT


# id(widget) -> (weakref, style); the id key (not the widget) keeps a style
# callable that closes over its own widget from pinning it in memory.
_themed = {}


def _restyle_all(_dark=None):
    palette = colors()
    for key, (ref, style) in list(_themed.items()):
        widget = ref()
        try:
            widget.setStyleSheet(style(palette))
        except (RuntimeError, AttributeError):
            _themed.pop(key, None)


def themed(widget, style):
    """Set widget's stylesheet now and re-apply it on every theme switch.
    `style` is a QSS string or a callable taking the current Palette; a later
    themed() call on the same widget replaces the earlier one."""
    key = id(widget)
    if callable(style):
        if key not in _themed:
            widget.destroyed.connect(lambda *_, k=key: _themed.pop(k, None))
        _themed[key] = (weakref.ref(widget), style)
        widget.setStyleSheet(style(colors()))
    else:
        _themed.pop(key, None)
        widget.setStyleSheet(style)


def on_theme_changed(fn):
    """Call fn(palette) now and after every theme switch."""
    fn(colors())
    theme_state.themeChanged.connect(lambda _dark: fn(colors()))


theme_state.themeChanged.connect(_restyle_all)


def restyle(widget):
    entry = _themed.get(id(widget))
    if entry:
        widget.setStyleSheet(entry[1](colors()))


def themed_add(widget, extra):
    """Append `extra` (QSS string or callable taking the Palette) to whatever
    themed() style the widget already has, keeping both live across theme
    switches."""
    entry = _themed.get(id(widget))
    base = entry[1] if entry else widget.styleSheet()
    themed(widget, lambda c: (base(c) if callable(base) else base) + (extra(c) if callable(extra) else extra))


def table_corner_qss(c):
    # Light mode keeps the platform's own corner cell; only dark needs it painted.
    return f"QTableCornerButton::section {{ background: {c.header_bg}; }}" if c.dark else ""

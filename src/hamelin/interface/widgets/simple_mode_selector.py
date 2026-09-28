from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from hamelin.interface.utils.colors import BLUE, themed
from hamelin.interface.utils.metric_labels import SIMPLE_MODE_PRIORITIES


class MetricPrioritySelector(QWidget):
    """Simple-mode gate shown before comparison results: instead of reading
    straight into a table/graph of every metric, the user first says what
    they actually care about (SIMPLE_MODE_PRIORITIES) and this emits
    prioritySelected(key) - the caller resolves that to an actual metric
    once it has data to match against (see pick_priority_metric).

    Cards stack vertically, not in a row - the option labels are full
    sentences, and stacking is what avoids any risk of them clipping or
    wrapping unpredictably in a horizontal layout."""

    prioritySelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(22)

        intro = QLabel("What matters most to you for this comparison?")
        intro.setAlignment(Qt.AlignCenter)
        intro.setWordWrap(True)
        themed(intro, lambda c: f"""
            color: {c.text};
            font-size: 24px;
            font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(intro)

        self._cards = {}
        for option in SIMPLE_MODE_PRIORITIES:
            card = self._build_card(option)
            self._cards[option["key"]] = card
            # stretch=1 on every card: once a caller gives this whole
            # widget real vertical room (see e.g.
            # visualise_comparison_table.py's own stretch=10), the cards
            # grow to fill it together instead of staying pill-sized with
            # the leftover room left empty below them.
            layout.addWidget(card, stretch=1)

        self._selected_key = None

    def _build_card(self, option):
        card = QWidget()
        card.setCursor(Qt.PointingHandCursor)
        # Forces Qt's stylesheet engine to own the whole box (background +
        # border) instead of falling through to a platform style's own
        # panel chrome underneath it, which on some styles doubles the
        # border - same fix as duplicate_model.py's option cards.
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(76)
        self._style_card(card, selected=False)

        row = QHBoxLayout(card)
        row.setContentsMargins(28, 20, 28, 20)

        label = QLabel(option["label"])
        label.setWordWrap(True)
        # card's own stylesheet (QWidget { border: Npx solid ...; ... })
        # cascades to descendant QWidgets that don't override border
        # themselves - without "border: none" here, this label inherited
        # that border and showed as a second frame drawn tightly around
        # the text, on top of the card's own full-width one.
        themed(label, lambda c: f"color: {c.text}; font-size: 19px; font-weight: 600; "
            "background: transparent; border: none;")
        row.addWidget(label)

        card.mousePressEvent = lambda event, key=option["key"]: self._on_card_clicked(key)
        return card

    def _style_card(self, card, selected):
        width = 3 if selected else 2
        themed(card, lambda c, selected=selected, width=width: f"""
            QWidget {{
                background: {c.page};
                border: {width}px solid {BLUE if selected else c.line};
                border-radius: 12px;
            }}
        """)

    def _on_card_clicked(self, key):
        self._selected_key = key
        for k, card in self._cards.items():
            self._style_card(card, selected=(k == key))
        self.prioritySelected.emit(key)

    def selected_key(self):
        return self._selected_key

    def reset(self):
        """Clear any prior selection and its highlight - used when a page
        wants to ask again (e.g. a fresh set_data() call with new models)."""
        self._selected_key = None
        for card in self._cards.values():
            self._style_card(card, selected=False)

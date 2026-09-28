"""Reusable dropdown widgets shared by most pages in the app.

SimpleDropdown (single choice) and CheckBoxDropdown (multi choice)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea, QLineEdit,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QColor

from hamelin.interface.utils.widgets import DropdownCard
from hamelin.interface.utils.colors import themed



class _PopupListFrame(QFrame):
    def __init__(self, on_hidden, parent=None):
        super().__init__(parent, Qt.Popup)
        self._on_hidden = on_hidden

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.setGraphicsEffect(shadow)

    def hideEvent(self, event):
        super().hideEvent(event)
        if self._on_hidden:
            self._on_hidden()


# MULTI SELECT DROPDOWN (CHECKBOX): scrollable

class CheckBoxDropdown(QWidget):
    selectionChanged = Signal()

    def __init__(self, title, items, favorite_check=None, annotate=None):
        super().__init__()
        self.main_window = None
        self.selected = set()
        self.title = title
        # Optional callable(item) -> bool, e.g. utils.favorites.is_favorite.
        # When set, items get a star prefix, purely cosmetic - self.selected
        # and get_selected() always stay the plain item values.
        self._favorite_check = favorite_check
        # Optional callable(item) -> str | None, e.g. a model's predicted
        # target column. When set, shown as a suffix on each row in the
        # popup list only - left out of the collapsed header/summary so it
        # doesn't turn into a wall of text once several items are selected.
        self._annotate = annotate

        # HEADER
        self.button = DropdownCard(title)
        self.button.clicked.connect(self._toggle_popup)

        # CONTAINER 
        self.container = _PopupListFrame(self._on_popup_hidden, self)
        self.container.setMinimumHeight(200)
        self.container.setMaximumHeight(360)
        self.container.setObjectName("popupListFrame")
        themed(self.container, lambda c: f"""
            QFrame#popupListFrame {{
                background: {c.surface};
                border-left: 2px solid {c.border};
                border-right: 2px solid {c.border};
                border-bottom: 2px solid {c.border};
                border-top: none;
                border-radius: 12px;
            }}
        """)

        # SEARCH BOX ( juseful when there are many items)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search models...")
        self.search.setVisible(len(items) > 8)
        themed(self.search, lambda c: f"""
            QLineEdit {{
                border: none;
                border-bottom: 2px solid {c.muted};
                color: {c.text};
                font-size: 18px;
                padding: 8px 10px;
                background: {c.surface};
            }}
        """)
        self.search.textChanged.connect(self._filter_items)

        # SCROLL AREA
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        themed(self.scroll, lambda c: f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                width: 10px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {c.scrollbar};
                border-radius: 5px;
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px;
            }}
        """)

        # CONTENT
        self.content = QWidget()
        themed(self.content, lambda c: f"background: {c.surface};")

        self.layout_content = QVBoxLayout(self.content)
        self.layout_content.setContentsMargins(10, 10, 10, 10)
        self.layout_content.setSpacing(6)

        self.scroll.setWidget(self.content)

        # ADD SCROLL TO CONTAINER
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.search)
        container_layout.addWidget(self.scroll)

        self.item_widgets = []
        self.no_results_label = QLabel("No matching models.")
        themed(self.no_results_label, lambda c: f"color: {c.muted}; font-size: 16px; padding: 6px;")
        self.no_results_label.setVisible(False)
        self.layout_content.addWidget(self.no_results_label)

        for item in items:
            self._add_item_widget(item)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(self.button)

        self._update_label()

    def _item_text(self, item):
        if self._favorite_check is None:
            return item
        return ("★ " if self._favorite_check(item) else "☆ ") + item

    def _row_text(self, item):
        text = self._item_text(item)
        if self._annotate is not None:
            note = self._annotate(item)
            if note:
                text = f"{text}  —  {note}"
        return text

    def _add_item_widget(self, item):
        w = QPushButton(self._row_text(item))
        w.setProperty("raw_value", item)
        w.setCheckable(True)

        themed(w, lambda c: f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {c.text};
                font-size: 20px;
                text-align: left;
                padding: 6px;
            }}
            QPushButton:checked {{
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {c.hover_tint};
            }}
        """)

        w.toggled.connect(lambda checked, x=item: self._toggle_item(x, checked))

        self.layout_content.addWidget(w)
        self.item_widgets.append(w)

    def set_items(self, items):
        for w in self.item_widgets:
            w.deleteLater()
        self.item_widgets = []
        self.selected = set()

        self.search.setText("")
        self.search.setVisible(len(items) > 8)
        self.no_results_label.setVisible(False)

        for item in items:
            self._add_item_widget(item)

        self._update_label()
        self.selectionChanged.emit()

    def _toggle_popup(self):
        if self.container.isVisible():
            self.container.hide()
        else:
            self._show_popup()

    def _show_popup(self):
        self.refresh_favorites()
        width = max(self.button.width(), 320)
        self.container.setFixedWidth(width)
        pos = self.button.mapToGlobal(QPoint(0, self.button.height() + 4))
        self.container.move(pos)
        self.container.show()
        self.container.raise_()

    def refresh_favorites(self):
        """Re-check favorite status for every item and the header summary -
        call after a favorite may have changed elsewhere (also done
        automatically whenever the popup opens)."""
        for w in self.item_widgets:
            w.setText(self._row_text(w.property("raw_value")))
        if self._favorite_check is not None:
            self._update_label()

    def _on_popup_hidden(self):
        pass

    def _filter_items(self, text):
        text = text.strip().lower()
        any_visible = False
        for w in self.item_widgets:
            visible = text in w.text().lower()
            w.setVisible(visible)
            any_visible = any_visible or visible
        self.no_results_label.setVisible(bool(text) and not any_visible)

    def _toggle_item(self, item, checked):
        if checked:
            self.selected.add(item)
        else:
            self.selected.discard(item)
        self._update_label()
        self.selectionChanged.emit()

    def _update_label(self):
        if not self.selected:
            self.button.setText(self.title)
        else:
            shown = list(self.selected)[:2]
            self.button.setText(
                ", ".join(self._item_text(s) for s in shown) +
                ("..." if len(self.selected) > 2 else "")
            )

    def get_selected(self):
        return list(self.selected)


# SINGLE SELECT DROPDOWN (SCROLLABLE)

class SimpleDropdown(QWidget):
    currentIndexChanged = Signal()

    def __init__(self, title, items, favorite_check=None, annotate=None):
        super().__init__()
        self.selected = None
        self.title = title
        # Optional callable(item) -> bool, e.g. utils.favorites.is_favorite.
        # When set, items get a star prefix, purely cosmetic - self.selected
        # and get_selected()/currentText() always stay the plain item value.
        self._favorite_check = favorite_check
        # Optional callable(item) -> str | None, e.g. a model's predicted
        # target column. When set, shown as a suffix on each row in the
        # popup list only - left out of the collapsed header so it doesn't
        # get cluttered once something is selected.
        self._annotate = annotate

        # HEADER
        self.button = DropdownCard(title)
        self.button.clicked.connect(self._toggle_popup)

        # CONTAINER 
        self.container = _PopupListFrame(self._on_popup_hidden, self)
        self.container.setMinimumHeight(200)
        self.container.setMaximumHeight(360)
        self.container.setObjectName("popupListFrame")
        themed(self.container, lambda c: f"""
            QFrame#popupListFrame {{
                background: {c.surface};
                border-left: 2px solid {c.border};
                border-right: 2px solid {c.border};
                border-bottom: 2px solid {c.border};
                border-top: none;
                border-radius: 12px;
            }}
        """)

        # SEARCH BOX (useful when there are many items)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.setVisible(len(items) > 8)
        themed(self.search, lambda c: f"""
            QLineEdit {{
                border: none;
                border-bottom: 2px solid {c.muted};
                color: {c.text};
                font-size: 18px;
                padding: 8px 10px;
                background: {c.surface};
            }}
        """)
        self.search.textChanged.connect(self._filter_items)

        # SCROLL AREA
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        themed(self.scroll, lambda c: f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                width: 10px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {c.scrollbar};
                border-radius: 5px;
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px;
            }}
        """)

        # CONTENT
        self.content = QWidget()
        themed(self.content, lambda c: f"background: {c.surface};")

        self.layout_content = QVBoxLayout(self.content)
        self.layout_content.setContentsMargins(10, 10, 10, 10)
        self.layout_content.setSpacing(6)

        self.scroll.setWidget(self.content)

        # ADD SCROLL TO CONTAINER
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.search)
        container_layout.addWidget(self.scroll)

        # BUTTONS
        self.buttons = []
        self.no_results_label = QLabel("No matching items.")
        themed(self.no_results_label, lambda c: f"color: {c.muted}; font-size: 16px; padding: 6px;")
        self.no_results_label.setVisible(False)
        self.layout_content.addWidget(self.no_results_label)

        for item in items:
            self._add_item_button(item)

        # MAIN LAYOUT
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(self.button)

        self._update_label()

    def _toggle_popup(self):
        if self.container.isVisible():
            self.container.hide()
        else:
            self._show_popup()

    def _show_popup(self):
        self.refresh_favorites()
        width = max(self.button.width(), 320)
        self.container.setFixedWidth(width)
        pos = self.button.mapToGlobal(QPoint(0, self.button.height() + 4))
        self.container.move(pos)
        self.container.show()
        self.container.raise_()

    def _on_popup_hidden(self):
        pass

    def _select(self, value):
        self.selected = value
        self._update_label()

        self.container.hide()

        self.currentIndexChanged.emit()

    def _item_text(self, item):
        if self._favorite_check is None:
            return item
        return ("★ " if self._favorite_check(item) else "☆ ") + item

    def _row_text(self, item):
        text = self._item_text(item)
        if self._annotate is not None:
            note = self._annotate(item)
            if note:
                text = f"{text}  —  {note}"
        return text

    def _update_label(self):
        self.button.setText(self._item_text(self.selected) if self.selected else self.title)

    def refresh_favorites(self):
        """Re-check favorite status for every item and the closed-button
        label - call after a favorite may have changed elsewhere (also
        done automatically whenever the popup opens)."""
        for b in self.buttons:
            b.setText(self._row_text(b.property("raw_value")))
        if self._favorite_check is not None:
            self._update_label()

    def get_selected(self):
        return self.selected

    def clear(self):
        for b in self.buttons:
            b.deleteLater()

        self.buttons.clear()
        self.selected = None

        self.search.setText("")
        self.search.setVisible(False)
        self.no_results_label.setVisible(False)

    def _filter_items(self, text):
        text = text.strip().lower()
        any_visible = False
        for b in self.buttons:
            visible = text in b.text().lower()
            b.setVisible(visible)
            any_visible = any_visible or visible
        self.no_results_label.setVisible(bool(text) and not any_visible)

    def _add_item_button(self, item):
        b = QPushButton(self._row_text(item))
        b.setProperty("raw_value", item)

        themed(b, lambda c: f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {c.text};
                font-size: 20px;
                text-align: left;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {c.hover_tint};
            }}
        """)

        b.clicked.connect(lambda _, x=item: self._select(x))

        self.layout_content.addWidget(b)
        self.buttons.append(b)

    def addItems(self, items):
        for item in items:
            self._add_item_button(item)
        self.search.setVisible(len(self.buttons) > 8)

    def currentText(self):
        return self.selected

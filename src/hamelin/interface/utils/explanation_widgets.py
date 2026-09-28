"""Shared building blocks for the model-type explanation pages (CNN/MLP/LSTM
visualisation widgets): a titled paragraph card and a page header. Kept in
one place so the three pages can't quietly drift out of sync in styling."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

from hamelin.interface.utils.colors import BLUE, themed


def make_section(title, body, accent=BLUE):
    """A small styled block: a colored title + its text, used to vary the
    layout instead of one long uniform paragraph."""
    wrapper = QFrame()
    wrapper.setObjectName("sectionCard")
    # Scoped to #sectionCard: QLabel is a QFrame subclass in Qt, so a bare
    # "QFrame { ... }" selector here would also match the title/body labels
    # added below and paint a second background behind them.
    themed(wrapper, lambda c: f"""
        QFrame#sectionCard {{
            background: {c.surface};
            border-radius: 8px;
        }}
    """)
    lay = QVBoxLayout(wrapper)
    # Bigger than the original 14/10/14/12, 4 - these cards were the main
    # reason a whole explanation page could end with a big empty gap below
    # them: sized to their text at 13-15px, they left most of a tall window
    # unused instead of the content actually filling it.
    lay.setContentsMargins(22, 18, 22, 20)
    lay.setSpacing(8)

    t = QLabel(title)
    t.setWordWrap(True)
    themed(t, lambda c: f"font-size: 18px; font-weight: 700; color: {c.blue_text};")

    b = QLabel(body)
    b.setWordWrap(True)
    themed(b, lambda c: f"font-size: 16px; color: {c.text}; line-height: 150%;")

    lay.addWidget(t)
    lay.addWidget(b)
    return wrapper


def make_header(title, subtitle):
    header = QVBoxLayout()
    header.setSpacing(2)

    t = QLabel(title)
    t.setWordWrap(True)
    themed(t, lambda c: f"font-size: 26px; font-weight: 800; color: {c.blue_text};")

    s = QLabel(subtitle)
    s.setWordWrap(True)
    themed(s, lambda c: f"font-size: 15px; color: {c.muted}; font-style: italic;")

    header.addWidget(t)
    header.addWidget(s)
    return header

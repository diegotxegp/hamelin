"""
Training Summary Dialog
~~~~~~~~~~~~~~~~~~~~~~~

"Review before training": a read-only list of everything the run about to
start will use - the data, the outcome and predictors, and every model
setting - each marked as a default, the user's own choice, or detected from
the data, with a one-line explanation. The user confirms or goes back.
Shown by the Training page just before the worker starts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, PrimaryPushButton, PushButton, StrongBodyLabel, TitleLabel

from hamelin.i18n import t
from hamelin.view.widgets.theme_colors import bind_style

# Where a value comes from.
DEFAULT, CHOSEN, DETECTED = "default", "chosen", "detected"
_ORIGIN_COLOURS = {DEFAULT: "#808080", CHOSEN: "#0078D4", DETECTED: "#107C10"}
_ORIGIN_KEYS = {
    DEFAULT: "training.summary.origin.default",
    CHOSEN: "training.summary.origin.chosen",
    DETECTED: "training.summary.origin.detected",
}


@dataclass
class SummaryRow:
    label: str
    value: str
    origin: str | None = None      # DEFAULT / CHOSEN / DETECTED, or None for plain facts
    hint: str = ""                 # one-line explanation


@dataclass
class SummarySection:
    title: str
    rows: list[SummaryRow] = field(default_factory=list)


def _row_widget(row: SummaryRow) -> QWidget:
    box = QWidget()
    lay = QHBoxLayout(box)
    lay.setContentsMargins(0, 4, 0, 4)
    lay.setSpacing(12)

    left = QVBoxLayout()
    left.setSpacing(2)
    label = StrongBodyLabel(row.label)
    label.setWordWrap(True)
    left.addWidget(label)
    if row.hint:
        hint = BodyLabel(row.hint)
        hint.setWordWrap(True)
        bind_style(hint, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        left.addWidget(hint)
    lay.addLayout(left, 5)

    value = BodyLabel(row.value)
    value.setWordWrap(True)
    value.setTextInteractionFlags(Qt.TextSelectableByMouse)
    lay.addWidget(value, 4)

    pill = BodyLabel(t(_ORIGIN_KEYS[row.origin]) if row.origin else "")
    pill.setAlignment(Qt.AlignRight | Qt.AlignTop)
    if row.origin:
        pill.setStyleSheet(f"color: {_ORIGIN_COLOURS[row.origin]}; font-weight: 600;")
    pill.setMinimumWidth(110)
    lay.addWidget(pill, 0)
    return box


def confirm_training(parent, sections: list[SummarySection], warnings: list[str],
                     notes: list[str]) -> bool:
    """Show the summary; True if the user chose to start training."""
    dlg = QDialog(parent)
    dlg.setWindowTitle(t("training.summary.title"))
    dlg.resize(820, 680)
    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(24, 20, 24, 20)
    outer.setSpacing(12)

    outer.addWidget(TitleLabel(t("training.summary.title")))
    intro = BodyLabel(t("training.summary.intro"))
    intro.setWordWrap(True)
    bind_style(intro, lambda c: f"color: {c.text_secondary};")
    outer.addWidget(intro)

    legend = BodyLabel(
        "  ".join(f'<span style="color:{_ORIGIN_COLOURS[o]}"><b>●</b></span> {t(k)}'
                  for o, k in _ORIGIN_KEYS.items()))
    legend.setTextFormat(Qt.RichText)
    outer.addWidget(legend)

    body = QWidget()
    body.setObjectName("summaryBody")
    body.setStyleSheet("#summaryBody { background: transparent; }")
    body_lay = QVBoxLayout(body)
    body_lay.setContentsMargins(0, 0, 8, 0)
    body_lay.setSpacing(4)
    for section in sections:
        title = StrongBodyLabel(section.title)
        title.setStyleSheet("font-size: 15px; padding-top: 10px;")
        body_lay.addWidget(title)
        for row in section.rows:
            body_lay.addWidget(_row_widget(row))
    for text in warnings:
        warn = BodyLabel("⚠ " + text)
        warn.setWordWrap(True)
        warn.setStyleSheet("color: #D13438; padding-top: 8px;")
        body_lay.addWidget(warn)
    for text in notes:
        note = BodyLabel(text)
        note.setWordWrap(True)
        bind_style(note, lambda c: f"color: {c.text_secondary}; padding-top: 6px;")
        body_lay.addWidget(note)
    body_lay.addStretch()

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.NoFrame)
    scroll.setStyleSheet("QScrollArea { background: transparent; }")
    scroll.viewport().setStyleSheet("background: transparent;")
    scroll.setWidget(body)
    outer.addWidget(scroll, 1)

    buttons = QHBoxLayout()
    buttons.addStretch()
    back = PushButton(t("training.summary.back"))
    back.clicked.connect(dlg.reject)
    buttons.addWidget(back)
    start = PrimaryPushButton(t("training.summary.start"))
    start.clicked.connect(dlg.accept)
    start.setDefault(True)
    buttons.addWidget(start)
    outer.addLayout(buttons)

    bind_style(dlg, lambda c: f"QDialog {{ background: {c.card_background}; }}")
    return dlg.exec() == QDialog.Accepted

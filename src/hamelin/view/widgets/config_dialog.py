"""
Config Dialog
~~~~~~~~~~~~~

Read-only viewer for a Ludwig config: either a dict (e.g. the partial
config a training run is about to use) or the ``model_hyperparameters.json``
of a saved model. Shared by the Training page ("Preview Config") and the
Evaluation page ("View Config").
"""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QTextEdit
from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, FluentIcon

from hamelin.utils.logger import log
from hamelin.view.widgets.theme_colors import bind_style
from hamelin.i18n import t

CONFIG_FILENAME = "model_hyperparameters.json"


def load_model_config(checkpoint_path: str | Path) -> dict | None:
    """Read the Ludwig config saved with a model, or None if unavailable."""
    if not checkpoint_path:
        return None
    for candidate in (Path(checkpoint_path) / CONFIG_FILENAME,
                      Path(checkpoint_path) / "model" / CONFIG_FILENAME):
        if candidate.is_file():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                log.warning(f"Could not read model config {candidate}: {exc}")
                return None
    return None


def show_config_dialog(parent, title: str, config: dict | str | Path, note: str = "") -> bool:
    """Show *config* (a dict, or a checkpoint folder holding a saved model)
    in a read-only, scrollable dialog. Returns False, showing nothing, if a
    checkpoint folder has no readable config."""
    if not isinstance(config, dict):
        config = load_model_config(config)
        if config is None:
            return False

    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.resize(720, 560)
    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)

    if note:
        lbl = BodyLabel(note)
        lbl.setWordWrap(True)
        bind_style(lbl, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(lbl)

    text = json.dumps(config, indent=2, ensure_ascii=False, default=str)
    view = QTextEdit()
    view.setReadOnly(True)
    view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    view.setStyleSheet("font-family: monospace;")
    view.setPlainText(text)
    bind_style(dlg, lambda c: f"QDialog {{ background: {c.card_background}; }}"
                              f"QTextEdit {{ background: {c.table_row}; color: {c.text_primary};"
                              f" border: 1px solid {c.border}; border-radius: 6px; }}")
    layout.addWidget(view, 1)

    buttons = QHBoxLayout()
    buttons.addStretch()
    copy_btn = PushButton(t("config.btn.copy"))
    copy_btn.setIcon(FluentIcon.COPY)
    copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text))
    buttons.addWidget(copy_btn)
    close_btn = PrimaryPushButton(t("config.btn.close"))
    close_btn.clicked.connect(dlg.accept)
    buttons.addWidget(close_btn)
    layout.addLayout(buttons)

    dlg.exec()
    return True

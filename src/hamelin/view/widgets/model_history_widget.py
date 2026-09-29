"""
Model History Widget — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Collapsible widget showing the full training history for a project:
- Summary header (total runs, best accuracy)
- Comparison table (collapsed by default, expandable)

Sprint 3 Q3 answered: Option B — collapsed by default.

Author: GitHub Copilot AI
Date: February 23, 2026
Sprint: 3, Day 25
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
    QAbstractItemView, QSizePolicy,
)
from qfluentwidgets import (
    CardWidget, StrongBodyLabel, BodyLabel, PushButton,
    FluentIcon, InfoBar, InfoBarPosition,
)

from hamelin.analytics.history_visualizer import HistoryVisualizer
from hamelin.core.model_history import ModelHistory
from hamelin.utils.logger import log
from hamelin.i18n import t
from hamelin.view.widgets.table_theme import style_table_widget


class ModelHistoryWidget(QWidget):
    """
    Collapsible training history widget.

    Shows a summary header (best accuracy, total runs) and a comparison
    table that is collapsed by default. The user can expand it with the
    "Show history" button.

    Usage::

        widget = ModelHistoryWidget(parent=self)
        widget.load(project_dir)
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._viz: Optional[HistoryVisualizer] = None
        self._table_visible = False
        self._init_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, project_dir) -> None:
        """
        Load (or reload) the training history for *project_dir*.

        Args:
            project_dir: ``Path`` to the project root directory.
        """
        try:
            history = ModelHistory(project_dir)
            self._viz = HistoryVisualizer(history)
            self._refresh()
            log.debug(f"ModelHistoryWidget: loaded {len(history)} records")
        except Exception as exc:
            log.warning(f"ModelHistoryWidget.load error: {exc}")
            self._show_error(str(exc))

    def clear(self) -> None:
        """Reset the widget to its empty state."""
        self._viz = None
        self._refresh()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        self._card = CardWidget(self)
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(10)

        # ---- Summary row ----
        summary_row = QHBoxLayout()

        self._lbl_total = BodyLabel(t("common.txt.no_training_runs_yet"))
        self._lbl_best = BodyLabel("")
        self._lbl_best.setStyleSheet("color: #0078d4; font-weight: 600;")

        self._btn_toggle = PushButton(FluentIcon.DOWN, "Show history")
        self._btn_toggle.setFixedWidth(150)
        self._btn_toggle.clicked.connect(self._toggle_table)

        summary_row.addWidget(StrongBodyLabel(t("common.txt.training_history")))
        summary_row.addSpacing(16)
        summary_row.addWidget(self._lbl_total)
        summary_row.addSpacing(16)
        summary_row.addWidget(self._lbl_best)
        summary_row.addStretch()
        summary_row.addWidget(self._btn_toggle)
        card_layout.addLayout(summary_row)

        # ---- Comparison table (hidden by default) ----
        self._table_container = QWidget(self._card)
        table_layout = QVBoxLayout(self._table_container)
        table_layout.setContentsMargins(0, 8, 0, 0)
        table_layout.setSpacing(0)

        self._table = QTableView(self._table_container)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._table.setMaximumHeight(300)
        # A plain QTableView, like QTableWidget, falls back to Qt's
        # inherited (theme-blind) palette if left unstyled - reuse the
        # same explicit QPalette theming table_theme.py already gives
        # every other table in the app.
        style_table_widget(self._table)

        table_layout.addWidget(self._table)
        self._table_container.setVisible(False)
        card_layout.addWidget(self._table_container)

        outer.addWidget(self._card)

    # ------------------------------------------------------------------
    # Refresh logic
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        if self._viz is None:
            self._lbl_total.setText(t("common.txt.no_training_runs_yet"))
            self._lbl_best.setText("")
            self._btn_toggle.setEnabled(False)
            self._table.setModel(None)
            return

        stats = self._viz.summary_stats("accuracy")
        count = stats["count"]

        if count == 0:
            self._lbl_total.setText(t("common.txt.no_training_runs_yet"))
            self._lbl_best.setText("")
            self._btn_toggle.setEnabled(False)
            self._table.setModel(None)
            return

        self._btn_toggle.setEnabled(True)
        self._lbl_total.setText(t("common.txt.0_run_1").format(count, 's' if count != 1 else ''))

        best = stats["best"]
        if best is not None:
            self._lbl_best.setText(t("common.txt.best_accuracy_0_1").format(best))
        else:
            self._lbl_best.setText("")

        self._populate_table()

    def _populate_table(self) -> None:
        if self._viz is None:
            return

        df = self._viz.comparison_table()
        if df.empty:
            self._table.setModel(None)
            return

        # Format timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")

        # Format model_id to short 8-char prefix
        if "model_id" in df.columns:
            df["model_id"] = df["model_id"].str[:8]

        # Round floats
        float_cols = df.select_dtypes("float64").columns
        df[float_cols] = df[float_cols].round(4)

        model = QStandardItemModel(len(df), len(df.columns))
        model.setHorizontalHeaderLabels(list(df.columns))

        for row_idx, row in df.iterrows():
            for col_idx, val in enumerate(row):
                text = "" if val is None or (isinstance(val, float) and val != val) else str(val)
                item = QStandardItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row_idx, col_idx, item)

        self._table.setModel(model)

    # ------------------------------------------------------------------
    # Toggle table visibility
    # ------------------------------------------------------------------

    def _toggle_table(self) -> None:
        self._table_visible = not self._table_visible
        self._table_container.setVisible(self._table_visible)
        if self._table_visible:
            self._btn_toggle.setIcon(FluentIcon.UP)
            self._btn_toggle.setText(t("common.txt.hide_history"))
        else:
            self._btn_toggle.setIcon(FluentIcon.DOWN)
            self._btn_toggle.setText(t("common.txt.show_history"))

    def _show_error(self, message: str) -> None:
        self._lbl_total.setText(t("common.txt.error_0").format(message))
        self._lbl_best.setText("")
        self._btn_toggle.setEnabled(False)

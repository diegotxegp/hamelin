"""
Prediction Page
~~~~~~~~~~~~~~~

Run a trained model against new data that has no outcome column.

    1. Pick a model - one trained in the active project, or any external
       folder holding a saved Ludwig model (model_hyperparameters.json).
    2. Load the new dataset (same formats as the Data page).
    3. The dataset's columns are checked against the model's input features.
    4. Predict (background thread), preview the result and export it.
"""

from __future__ import annotations

import os
from pathlib import Path
from hamelin.utils.paths import workspace_dir

import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog,
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget, PushButton,
    PrimaryPushButton, ComboBox, LineEdit, FluentIcon, InfoBar,
    InfoBarPosition, IndeterminateProgressBar,
)

from hamelin.analytics.predictor import PredictWorker, required_input_columns, resolve_model_dir
from hamelin.core.model_history import ModelHistory
from hamelin.model.data_model import DataModel
from hamelin.utils.logger import log
from hamelin.utils.export_paths import default_export_path
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets import HelpButton, PageHelpButton, style_table_widget
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style, on_theme_changed, apply_transparent_container
from hamelin.i18n import t

_DATASETS_DIR = workspace_dir() / "data"
_MAX_PREVIEW_ROWS = 500
_BROWSE = "__browse__"


class PredictionPage(QWidget):
    """Predict on new, unlabeled data with a trained model."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PredictionPage")
        self._project_dir: Path | None = None
        self._df: pd.DataFrame | None = None
        self._result: pd.DataFrame | None = None
        self._worker: PredictWorker | None = None
        self._missing: list[str] = []
        self._prev_index = 0
        log.debug("Initializing Prediction Page")
        self._init_ui()
        self._populate_models()

    # ── Public API (called by MainWindow) ──────────────────────────────
    def set_project_dir(self, project_dir) -> None:
        self._project_dir = Path(project_dir) if project_dir else None
        self._populate_models()

    def showEvent(self, event):
        super().showEvent(event)
        self._populate_models()  # picks up models trained since the last visit

    # ── UI construction ────────────────────────────────────────────────
    def _card(self, title: str, help_text: str):
        card = CardWidget()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)
        head = QHBoxLayout()
        head.addWidget(StrongBodyLabel(title))
        head.addWidget(HelpButton(help_text))
        head.addStretch()
        lay.addLayout(head)
        return card, lay

    def _init_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        container = QWidget()
        scroll.setWidget(container)
        apply_scroll_area_theme(scroll)
        apply_transparent_container(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_row = QHBoxLayout()
        title = TitleLabel(t("prediction.title"))
        title.setAlignment(Qt.AlignLeft)
        title_row.addWidget(title)
        title_row.addWidget(PageHelpButton(t("prediction.help"), self))
        title_row.addStretch()
        layout.addLayout(title_row)
        subtitle = StrongBodyLabel(t("prediction.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        # ── 1. Model ───────────────────────────────────────────────────
        card, lay = self._card(t("prediction.section.model"), t("prediction.help.model"))
        self.model_combo = ComboBox()
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        lay.addWidget(self.model_combo)
        self.model_info = BodyLabel("")
        self.model_info.setWordWrap(True)
        bind_style(self.model_info, lambda c: f"color: {c.text_secondary};")
        lay.addWidget(self.model_info)
        layout.addWidget(card)

        # ── 2. Data ────────────────────────────────────────────────────
        card, lay = self._card(t("prediction.section.data"), t("prediction.help.data"))
        row = QHBoxLayout()
        self.file_edit = LineEdit()
        self.file_edit.setReadOnly(True)
        self.file_edit.setPlaceholderText(t("prediction.data.placeholder"))
        row.addWidget(self.file_edit, 1)
        self.browse_btn = PushButton(t("prediction.btn.browse"))
        self.browse_btn.setIcon(FluentIcon.FOLDER)
        self.browse_btn.clicked.connect(self._browse_data)
        row.addWidget(self.browse_btn)
        lay.addLayout(row)
        self.data_info = BodyLabel("")
        self.data_info.setWordWrap(True)
        lay.addWidget(self.data_info)
        layout.addWidget(card)

        # ── 3. Run ─────────────────────────────────────────────────────
        card, lay = self._card(t("prediction.section.run"), t("prediction.help.run"))
        row = QHBoxLayout()
        self.run_btn = PrimaryPushButton(t("prediction.btn.run"))
        self.run_btn.setIcon(FluentIcon.PLAY)
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        row.addWidget(self.run_btn)
        self.export_btn = PushButton(t("prediction.btn.export"))
        self.export_btn.setIcon(FluentIcon.SAVE)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._export)
        row.addWidget(self.export_btn)
        row.addStretch()
        lay.addLayout(row)
        self.spinner = IndeterminateProgressBar(self)
        self.spinner.setVisible(False)
        lay.addWidget(self.spinner)
        self.status_lbl = BodyLabel("")
        self.status_lbl.setWordWrap(True)
        lay.addWidget(self.status_lbl)
        layout.addWidget(card)

        # ── 4. Results ─────────────────────────────────────────────────
        self.results_card, lay = self._card(t("prediction.section.results"), t("prediction.help.results"))
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(320)
        style_table_widget(self.table)
        lay.addWidget(self.table)
        self.results_card.setVisible(False)
        layout.addWidget(self.results_card)

        layout.addStretch()
        on_theme_changed(self._apply_status_colors)

    def _apply_status_colors(self) -> None:
        # Neutral text follows the theme; ok/error keep fixed semantic colors.
        self._set_label(self.data_info, self.data_info.text(), getattr(self, "_data_state", "neutral"))
        self._set_label(self.status_lbl, self.status_lbl.text(), getattr(self, "_status_state", "neutral"))

    @staticmethod
    def _set_label(label: BodyLabel, text: str, state: str) -> None:
        from hamelin.view.widgets.theme_colors import colors
        color = {"ok": "#2E9E5B", "error": "#D13438"}.get(state, colors().text_secondary)
        label.setText(text)
        label.setStyleSheet(f"color: {color};")

    def _set_data_msg(self, text: str, state: str = "neutral") -> None:
        self._data_state = state
        self._set_label(self.data_info, text, state)

    def _set_status(self, text: str, state: str = "neutral") -> None:
        self._status_state = state
        self._set_label(self.status_lbl, text, state)

    # ── Model selection ────────────────────────────────────────────────
    def _populate_models(self) -> None:
        """Rebuild the combo: this project's trained models, any external
        model already picked this session, then 'Browse external model…'."""
        current = self.model_combo.currentData()
        if current == _BROWSE:
            current = None
        externals = [
            (self.model_combo.itemText(i), self.model_combo.itemData(i))
            for i in range(self.model_combo.count())
            if str(self.model_combo.itemData(i) or "").startswith("ext:")
        ]
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        if self._project_dir is not None:
            try:
                for rec in ModelHistory(self._project_dir).list_trainings():
                    if rec.checkpoint_path and resolve_model_dir(rec.checkpoint_path):
                        self.model_combo.addItem(
                            f"{rec.model_name or rec.model_id[:8]}  ({rec.target_variable})",
                            userData=f"proj:{rec.checkpoint_path}",
                        )
            except Exception as exc:  # noqa: BLE001
                log.warning(f"PredictionPage: cannot list models: {exc}")
        for text, data in externals:
            self.model_combo.addItem(text, userData=data)
        self.model_combo.addItem(t("prediction.model.browse"), userData=_BROWSE)
        idx = self.model_combo.findData(current) if current else -1
        self.model_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._prev_index = self.model_combo.currentIndex()
        if self.model_combo.itemData(self._prev_index) == _BROWSE:
            self._prev_index = -1  # nothing but "Browse…": no model selected
        self.model_combo.blockSignals(False)
        self._on_model_changed(self.model_combo.currentIndex(), from_populate=True)

    def _on_model_changed(self, index: int, from_populate: bool = False) -> None:
        data = self.model_combo.itemData(index)
        if data == _BROWSE and not from_populate:
            self._browse_external_model()
            return
        if data != _BROWSE:
            self._prev_index = index
        if not from_populate:
            usage_log.event("Prediction", "select", "Model", self.model_combo.itemText(index))
        self._result = None
        self.results_card.setVisible(False)
        self.export_btn.setEnabled(False)
        self._set_status("")
        self._refresh_model_info()
        self._validate()

    def _browse_external_model(self) -> None:
        usage_log.event("Prediction", "click", "Browse external model")
        start = str(self._project_dir) if self._project_dir else str(Path.home())
        folder = QFileDialog.getExistingDirectory(self.window(), t("prediction.model.dialog"), start)
        resolved = resolve_model_dir(folder) if folder else None
        self.model_combo.blockSignals(True)
        if not folder:
            self.model_combo.setCurrentIndex(self._prev_index)
        elif resolved is None:
            self.model_combo.setCurrentIndex(self._prev_index)
            InfoBar.error(
                title=t("prediction.model.invalid.title"), content=t("prediction.model.invalid.body"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=6000, parent=self,
            )
        else:
            key = f"ext:{resolved}"
            idx = self.model_combo.findData(key)
            if idx < 0:
                idx = self.model_combo.count() - 1  # just before "Browse…"
                self.model_combo.insertItem(idx, f"{Path(folder).name}  (external)", userData=key)
            self.model_combo.setCurrentIndex(idx)
            usage_log.event("Prediction", "select", "External model", folder)
        self.model_combo.blockSignals(False)
        self._on_model_changed(self.model_combo.currentIndex(), from_populate=True)

    def _current_model_dir(self) -> Path | None:
        data = self.model_combo.currentData()
        if not data or data == _BROWSE:
            return None
        return resolve_model_dir(str(data).split(":", 1)[1])

    def _refresh_model_info(self) -> None:
        model_dir = self._current_model_dir()
        if model_dir is None:
            self.model_info.setText(t("prediction.model.none"))
            return
        cols = required_input_columns(model_dir)
        self.model_info.setText(
            t("prediction.model.info").format(n=len(cols), cols=", ".join(cols[:12]) + ("…" if len(cols) > 12 else ""))
        )

    # ── Data ───────────────────────────────────────────────────────────
    def _browse_data(self) -> None:
        usage_log.event("Prediction", "click", "Browse data button")
        _DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        path, _ = QFileDialog.getOpenFileName(
            self.window(), t("data.dialog.select"), str(_DATASETS_DIR), t("data.dialog.filters")
        )
        if not path:
            return
        self.file_edit.setText(path)
        usage_log.event("Prediction", "select", "File path", path)
        try:
            dm = DataModel()
            dm.load_from_file(path, auto_detect_types=False)
            self._df = dm.df
        except Exception as exc:  # noqa: BLE001
            self._df = None
            self._set_data_msg(str(exc), "error")
            self.run_btn.setEnabled(False)
            log.error(f"PredictionPage: cannot load {path}: {exc}")
            return
        self._result = None
        self.results_card.setVisible(False)
        self.export_btn.setEnabled(False)
        self._set_status("")
        self._validate()

    def _validate(self) -> None:
        """Check the loaded dataset's columns against the model's inputs."""
        self._missing = []
        model_dir = self._current_model_dir()
        if self._df is None:
            self.run_btn.setEnabled(False)
            if not self.file_edit.text():
                self._set_data_msg("")
            return
        rows, cols = self._df.shape
        if model_dir is None:
            self._set_data_msg(t("prediction.data.loaded").format(rows=rows, cols=cols))
            self.run_btn.setEnabled(False)
            return
        required = required_input_columns(model_dir)
        self._missing = [c for c in required if c not in self._df.columns]
        if self._missing:
            self._set_data_msg(
                t("prediction.data.missing").format(cols=", ".join(self._missing)), "error"
            )
        else:
            self._set_data_msg(t("prediction.data.ok").format(rows=rows, cols=cols), "ok")
        self.run_btn.setEnabled(not self._missing and rows > 0)

    # ── Run ────────────────────────────────────────────────────────────
    def _run(self) -> None:
        model_dir = self._current_model_dir()
        if model_dir is None or self._df is None or self._missing:
            return
        if self._worker is not None and self._worker.isRunning():
            return
        usage_log.event("Prediction", "click", "Run prediction button", f"{len(self._df)} rows")
        self.run_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.spinner.setVisible(True)
        self.spinner.start()
        self._set_status(t("prediction.status.running"))
        self._worker = PredictWorker(model_dir, self._df, parent=self)
        self._worker.prediction_ready.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _stop_spinner(self) -> None:
        self.spinner.stop()
        self.spinner.setVisible(False)
        self.run_btn.setEnabled(not self._missing and self._df is not None)

    def _on_done(self, result: pd.DataFrame) -> None:
        self._stop_spinner()
        self._result = result
        self._show_result(result)
        self.export_btn.setEnabled(True)
        self._set_status(t("prediction.status.done").format(n=len(result)), "ok")
        usage_log.event("Prediction", "created", "Predictions", f"{len(result)} rows")

    def _on_error(self, message: str) -> None:
        self._stop_spinner()
        self._set_status(t("prediction.status.error").format(msg=message), "error")
        InfoBar.error(
            title=t("prediction.error.title"), content=message,
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=8000, parent=self,
        )

    def _show_result(self, df: pd.DataFrame) -> None:
        shown = df.head(_MAX_PREVIEW_ROWS)
        self.table.setColumnCount(len(shown.columns))
        self.table.setRowCount(len(shown))
        self.table.setHorizontalHeaderLabels([str(c) for c in shown.columns])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        for r, values in enumerate(shown.itertuples(index=False)):
            for c, v in enumerate(values):
                text = f"{v:.4f}" if isinstance(v, float) else str(v)
                self.table.setItem(r, c, QTableWidgetItem(text))
        self.results_card.setVisible(True)

    # ── Export ─────────────────────────────────────────────────────────
    def _export(self) -> None:
        usage_log.event("Prediction", "click", "Export Predictions button")
        if self._result is None:
            return
        path, selected = QFileDialog.getSaveFileName(
            self.window(), t("prediction.export.dialog"),
            default_export_path(self._project_dir, "predictions", "predictions.csv"),
            "CSV files (*.csv);;Excel files (*.xlsx);;All files (*.*)",
        )
        if not path:
            return
        try:
            if path.lower().endswith(".xlsx") or (not os.path.splitext(path)[1] and "xlsx" in selected):
                if not path.lower().endswith(".xlsx"):
                    path += ".xlsx"
                self._result.to_excel(path, index=False)
            else:
                self._result.to_csv(path, index=False)
            InfoBar.success(
                title=t("prediction.export.done"), content=os.path.basename(path),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            usage_log.event("Prediction", "exported", "Predictions", os.path.basename(path))
        except Exception as exc:  # noqa: BLE001
            InfoBar.error(
                title=t("prediction.export.error"), content=str(exc),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=5000, parent=self,
            )
            log.error(f"Prediction export failed: {exc}")

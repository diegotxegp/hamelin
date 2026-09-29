"""
Evaluation Page
~~~~~~~~~~~~~~~

Everything about the models trained in the active project, in two tabs:

    Models        list (with favourites), and for the selected model: metrics
                  with confidence intervals, subgroup break-down, confusion
                  matrix (threshold, patient drill-down), ROC, notes, report;
                  view its config, duplicate and retrain, delete.
    Compare       ranked table / bars / heat map / radar over 2+ models and a
                  settings diff between two.

The panels live in hamelin.view.widgets.eval_*_panel; the data logic is in
hamelin.analytics.eval_data.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QHBoxLayout, QScrollArea,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from qfluentwidgets import (
    BodyLabel, CardWidget, FluentIcon, InfoBar, InfoBarPosition, MessageBox,
    Pivot, PushButton, StrongBodyLabel, TitleLabel,
)

from hamelin.analytics import eval_data as ed
from hamelin.core.model_history import ModelHistory, ModelTraining, models_dir
from hamelin.i18n import t
from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets import HelpButton, PageHelpButton, style_table_widget
from hamelin.view.widgets.config_dialog import load_model_config, show_config_dialog
from hamelin.view.widgets.eval_compare_panel import CurrentPageStack, ModelComparePanel
from hamelin.view.widgets.eval_inspect_panel import ModelInspectPanel
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style, apply_transparent_container

# Preferred "headline" metric per run, first one present wins.
_KEY_METRICS = ("roc_auc", "auc", "accuracy", "r2", "root_mean_squared_error", "mean_absolute_error")
_TABS = ("models", "compare")


def key_metric(rec: ModelTraining) -> tuple[str, float] | None:
    """(name, value) of the most representative test metric of *rec*."""
    metrics = rec.test_metrics or {}
    for name in _KEY_METRICS:
        v = metrics.get(name)
        if isinstance(v, (int, float)):
            return name, float(v)
    for name, v in metrics.items():
        if isinstance(v, (int, float)) and name != "loss":
            return name, float(v)
    return None


class EvaluationPage(QWidget):
    """Evaluate the trained models of the active project.

    Signals
    -------
    duplicate_requested(dict):
        ``{"based_on", "new_run_name", "config"}`` - MainWindow forwards it
        to TrainingPage.prefill_from_config().
    """

    duplicate_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EvaluationPage")
        self._project_dir: Path | None = None
        self._records: list[ModelTraining] = []
        self._inspected: ModelTraining | None = None
        log.debug("Initializing Evaluation Page")
        self._init_ui()

    # ── Public API (called by MainWindow) ──────────────────────────────
    def set_project_dir(self, project_dir) -> None:
        self.inspect_panel.flush_note()
        self._project_dir = Path(project_dir) if project_dir else None
        self._inspected = None
        self.refresh()

    def refresh(self) -> None:
        """Reload the model list from the project's ModelHistory."""
        self._records = []
        if self._project_dir is not None:
            try:
                self._records = ModelHistory(self._project_dir).list_trainings()
            except Exception as exc:  # noqa: BLE001
                log.warning(f"EvaluationPage: cannot load model history: {exc}")
        self._fill_table()
        self.compare_panel.set_records(self._records, self._project_dir, self._models_dir())

    def showEvent(self, event):
        super().showEvent(event)
        # Cheap, and picks up models trained/deleted since the last visit.
        selected = [r.model_id for r in self._selected_records()]
        self.refresh()
        if selected:
            self._select_ids(selected)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.inspect_panel.flush_note()

    def _models_dir(self) -> Path | None:
        return models_dir(self._project_dir) if self._project_dir else None

    # ── UI construction ────────────────────────────────────────────────
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
        title = TitleLabel(t("eval.title"))
        title.setAlignment(Qt.AlignLeft)
        title_row.addWidget(title)
        title_row.addWidget(PageHelpButton(t("eval.help"), self))
        title_row.addStretch()
        layout.addLayout(title_row)

        subtitle = StrongBodyLabel(t("eval.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(subtitle)

        self.pivot = Pivot()
        for key in _TABS:
            self.pivot.addItem(routeKey=key, text=t(f"eval.tab.{key}"),
                               onClick=lambda _=False, k=key: self._set_tab(k))
        self.pivot.setCurrentItem("models")
        layout.addWidget(self.pivot, 0, Qt.AlignLeft)

        self.stack = CurrentPageStack()
        layout.addWidget(self.stack)
        layout.addStretch()

        # ── Tab 1: models ──────────────────────────────────────────────
        models_tab = QWidget()
        ml = QVBoxLayout(models_tab)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(20)

        list_card = CardWidget()
        ll = QVBoxLayout(list_card)
        ll.setContentsMargins(20, 20, 20, 20)
        ll.setSpacing(12)
        head = QHBoxLayout()
        head.addWidget(StrongBodyLabel(t("eval.section.models")))
        head.addWidget(HelpButton(t("eval.help.models")))
        head.addStretch()
        ll.addLayout(head)

        self._empty_lbl = BodyLabel(t("eval.empty"))
        bind_style(self._empty_lbl, lambda c: f"color: {c.text_secondary};")
        self._empty_lbl.setWordWrap(True)
        ll.addWidget(self._empty_lbl)

        self._table = QTableWidget()
        headers = ["★", t("eval.col.name"), t("eval.col.target"), t("eval.col.type"),
                   t("eval.col.metric"), t("eval.col.date")]
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 44)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        style_table_widget(self._table)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        self._table.cellClicked.connect(self._on_cell_clicked)
        ll.addWidget(self._table)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns2 = QHBoxLayout()
        btns2.setSpacing(10)
        self._config_btn = PushButton(t("eval.btn.config"), self)
        self._config_btn.setIcon(FluentIcon.DOCUMENT)
        self._config_btn.clicked.connect(self._on_view_config)
        btns.addWidget(self._config_btn)
        self._dup_btn = PushButton(t("eval.btn.duplicate"), self)
        self._dup_btn.setIcon(FluentIcon.COPY)
        self._dup_btn.clicked.connect(self._on_duplicate)
        btns.addWidget(self._dup_btn)
        self._compare_btn = PushButton(t("eval.btn.compare_selected"), self)
        self._compare_btn.setIcon(FluentIcon.SYNC)
        self._compare_btn.clicked.connect(self._on_compare_selected)
        btns.addWidget(self._compare_btn)
        self._delete_btn = PushButton(t("eval.btn.delete"), self)
        self._delete_btn.setIcon(FluentIcon.DELETE)
        self._delete_btn.clicked.connect(self._on_delete_selected)
        btns2.addWidget(self._delete_btn)
        self._delete_others_btn = PushButton(t("eval.btn.delete_others"), self)
        self._delete_others_btn.clicked.connect(self._on_delete_non_favorites)
        btns2.addWidget(self._delete_others_btn)
        self._folder_btn = PushButton(t("eval.btn.folder"), self)
        self._folder_btn.setIcon(FluentIcon.FOLDER)
        self._folder_btn.clicked.connect(self._on_open_folder)
        btns2.addWidget(self._folder_btn)
        btns2.addStretch()
        btns.addStretch()
        self._selection_lbl = BodyLabel("")
        bind_style(self._selection_lbl, lambda c: f"color: {c.text_secondary};")
        btns2.addWidget(self._selection_lbl)
        ll.addLayout(btns)
        ll.addLayout(btns2)
        ml.addWidget(list_card)

        self.inspect_panel = ModelInspectPanel()
        ml.addWidget(self.inspect_panel)
        ml.addStretch()   # spare height goes here, not into the cards
        self.stack.addWidget(models_tab)

        # ── Tab 2: compare ─────────────────────────
        self.compare_panel = ModelComparePanel()
        self.compare_panel.favorites_changed.connect(self._fill_table_keep_selection)
        self.stack.addWidget(self.compare_panel)

        self._on_selection_changed()

    def _set_tab(self, key: str) -> None:
        self.stack.setCurrentIndex(_TABS.index(key))
        self.pivot.setCurrentItem(key)
        usage_log.event("Evaluation", "click", "Tab", key)

    # ── Table ──────────────────────────────────────────────────────────
    def _favorites(self) -> set[str]:
        d = self._models_dir()
        return ed.load_favorites(d) if d else set()

    def _fill_table(self) -> None:
        favs = self._favorites()
        self._table.blockSignals(True)
        self._table.setRowCount(len(self._records))
        for row, rec in enumerate(self._records):
            km = key_metric(rec)
            label = ed.model_label(rec)
            cells = [
                "★" if label in favs else "☆", label, rec.target_variable, rec.model_type,
                f"{km[0]}: {km[1]:.3f}" if km else "—", ed.local_time(rec),
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if col == 0:
                    item.setTextAlignment(Qt.AlignCenter)
                self._table.setItem(row, col, item)
        self._table.blockSignals(False)
        has = bool(self._records)
        self._empty_lbl.setVisible(not has)
        self._table.setVisible(has)
        self._table.setFixedHeight(min(340, 44 + 30 * max(len(self._records), 1)))
        self._on_selection_changed()

    def _fill_table_keep_selection(self) -> None:
        ids = [r.model_id for r in self._selected_records()]
        self._fill_table()
        self._select_ids(ids)

    def _selected_records(self) -> list[ModelTraining]:
        rows = sorted({i.row() for i in self._table.selectionModel().selectedRows()})
        return [self._records[r] for r in rows if r < len(self._records)]

    def _select_ids(self, ids: list[str]) -> None:
        for row, rec in enumerate(self._records):
            if rec.model_id in ids:
                self._table.selectRow(row)

    def _on_cell_clicked(self, row: int, col: int) -> None:
        if col != 0 or row >= len(self._records) or self._models_dir() is None:
            return
        label = ed.model_label(self._records[row])
        now = ed.toggle_favorite(self._models_dir(), label)
        usage_log.event("Evaluation", "click", "Favorite star", f"{label} -> {now}")
        self._table.item(row, 0).setText("★" if now else "☆")
        self.compare_panel.set_records(self._records, self._project_dir, self._models_dir())

    def _on_selection_changed(self) -> None:
        sel = self._selected_records()
        n = len(sel)
        self._config_btn.setEnabled(n == 1)
        self._dup_btn.setEnabled(n == 1)
        self._compare_btn.setEnabled(n >= 2)
        self._delete_btn.setEnabled(n >= 1)
        self._delete_others_btn.setEnabled(bool(self._records))
        self._folder_btn.setEnabled(self._project_dir is not None)
        self._selection_lbl.setText(t("eval.selected").format(n=n) if n else t("eval.hint"))
        self.inspect_panel.setVisible(n == 1)
        if n == 1:
            self._inspect(sel[0])
        else:
            self.inspect_panel.flush_note()
            self._inspected = None

    # ── Inspect ────────────────────────────────────────────────────────
    def _inspect(self, rec: ModelTraining) -> None:
        if self._inspected is not None and self._inspected.model_id == rec.model_id:
            return
        self._inspected = rec
        usage_log.event("Evaluation", "select", "Model", ed.model_label(rec))
        self.inspect_panel.load(rec, self._project_dir)

    # ── Actions ────────────────────────────────────────────────────────
    def _single_selection(self) -> ModelTraining | None:
        sel = self._selected_records()
        return sel[0] if len(sel) == 1 else None

    def _warn_missing_config(self) -> None:
        InfoBar.warning(
            title=t("eval.config.missing.title"), content=t("eval.config.missing.body"),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self,
        )

    def _on_view_config(self) -> None:
        rec = self._single_selection()
        if rec is None:
            return
        usage_log.event("Evaluation", "click", "View Config button", rec.model_name)
        title = f"{t('eval.config.title')} - {ed.model_label(rec)}"
        source = rec.checkpoint_path if load_model_config(rec.checkpoint_path) else rec.hyperparameters
        if not source or not show_config_dialog(self, title, source):
            self._warn_missing_config()

    def _on_duplicate(self) -> None:
        rec = self._single_selection()
        if rec is None:
            return
        usage_log.event("Evaluation", "click", "Duplicate and Retrain button", rec.model_name)
        config = None
        if rec.checkpoint_path:
            from hamelin.interface.utils.get_model_paths import get_model_config
            config = get_model_config(rec.checkpoint_path) or load_model_config(rec.checkpoint_path)
        config = config or rec.hyperparameters
        if not config or not config.get("output_features"):
            self._warn_missing_config()
            return
        name = ed.model_label(rec)
        self.duplicate_requested.emit({
            "based_on": name,
            "new_run_name": f"{name}_copy",
            "config": config,
        })

    def _on_compare_selected(self) -> None:
        self.compare_panel.select([ed.model_label(r) for r in self._selected_records()])
        self._set_tab("compare")

    def _on_open_folder(self) -> None:
        d = self._models_dir()
        if d is None:
            return
        d.mkdir(parents=True, exist_ok=True)
        usage_log.event("Evaluation", "click", "Open models folder")
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(d)))

    def _confirm(self, title: str, body: str) -> bool:
        return bool(MessageBox(title, body, self.window()).exec())

    def _on_delete_selected(self) -> None:
        sel = self._selected_records()
        if not sel:
            return
        names = ", ".join(ed.model_label(r) for r in sel)
        if self._confirm(t("eval.delete.title"), t("eval.delete.body").format(names=names)):
            self._delete(sel)

    def _on_delete_non_favorites(self) -> None:
        favs = self._favorites()
        victims = [r for r in self._records if ed.model_label(r) not in favs]
        if not victims:
            InfoBar.info(title=t("eval.delete.none"), content="", orient=Qt.Horizontal, isClosable=True,
                         position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        if self._confirm(t("eval.delete.title"), t("eval.delete.others_body").format(n=len(victims))):
            self._delete(victims)

    def _delete(self, recs: list[ModelTraining]) -> None:
        """Remove models from the history and their folders from disk (only
        folders inside the project's results/models/)."""
        self.inspect_panel.flush_note()
        history = ModelHistory(self._project_dir)
        root = self._models_dir()
        for rec in recs:
            usage_log.event("Evaluation", "deleted", "Model", ed.model_label(rec))
            folder = ed.model_folder(rec)
            history.delete_training(rec.model_id)
            if folder is not None and root is not None and root.resolve() in folder.resolve().parents:
                shutil.rmtree(folder, ignore_errors=True)
        self._inspected = None
        self.refresh()

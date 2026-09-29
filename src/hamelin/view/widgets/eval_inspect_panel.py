"""
Model inspection panel
~~~~~~~~~~~~~~~~~~~~~~

Everything the Evaluation page shows about ONE trained model:

    - provenance line (trained when, dataset, seed, ...) and a details card
      (algorithm family, outcome, project objective, predictors, test size)
    - summary KPI cards + plain-language reading (same widget as right after
      training)
    - every test metric as a tile, with a 95 % bootstrap confidence interval
      where one can be computed, or a break-down by a patient attribute
    - interactive confusion matrix (counts / %, decision threshold for binary
      models, click a cell to list the patients behind it) and ROC curve
    - free-text notes (saved next to the model) and an exportable report
"""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QGridLayout, QHBoxLayout, QHeaderView,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from qfluentwidgets import (
    BodyLabel, CardWidget, ComboBox, FluentIcon, PlainTextEdit, PushButton,
    SpinBox, StrongBodyLabel, InfoBar, InfoBarPosition,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from hamelin.analytics import eval_data as ed
from hamelin.analytics.architecture import describe_architecture
from hamelin.analytics.automl.base import AutoMLResult
from hamelin.core.model_history import ModelTraining
from hamelin.i18n import t
from hamelin.interface.utils import get_model_paths as gmp
from hamelin.interface.utils import print_confusion_matrix as pcm
from hamelin.interface.utils.bootstrap_ci import is_supported as ci_supported
from hamelin.interface.utils.metric_labels import get_metric_info, get_metric_quality
from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets.eval_export import export_chart_and_data, export_report
from hamelin.view.widgets.kpi_card_widget import KPICardWidget
from hamelin.view.widgets.model_results_widget import ModelResultsWidget
from hamelin.view.widgets.table_theme import style_table_widget
from hamelin.view.widgets.theme_colors import bind_style, colors, isDarkTheme, on_theme_changed, style_figure

_CONFUSION_TYPES = {"binary", "category", "set"}
_CLASSIFICATION_TYPES = _CONFUSION_TYPES
_TILES_PER_ROW = 4
_FEATURES_SHOWN = 8
_CORRECT = QColor(96, 158, 224)
_INCORRECT = QColor(226, 124, 118)


def _blend(base: QColor, top: QColor, amount: float) -> QColor:
    return QColor(*(round(b + (t_ - b) * amount) for b, t_ in zip(base.getRgb()[:3], top.getRgb()[:3])))


def _section_title(text: str, help_text: str = "") -> QWidget:
    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(StrongBodyLabel(text))
    if help_text:
        from hamelin.view.widgets import HelpButton
        lay.addWidget(HelpButton(help_text))
    lay.addStretch()
    return row


class _PatientsDialog(QDialog):
    """The patients behind one confusion-matrix cell."""

    def __init__(self, parent, true_label, pred_label, rows):
        super().__init__(parent)
        outcome = t("eval.cm.correct") if true_label == pred_label else t("eval.cm.misclassified")
        self.setWindowTitle(t("eval.cm.patients"))
        self.resize(900, 520)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        head = StrongBodyLabel(
            f"{t('eval.cm.true')}: {true_label}  →  {t('eval.cm.predicted')}: {pred_label}   "
            f"({len(rows)} {t('eval.cm.cases')}, {outcome})"
        )
        head.setWordWrap(True)
        lay.addWidget(head)
        bind_style(self, lambda c: f"QDialog {{ background: {c.card_background}; }}")
        if not rows:
            lay.addWidget(BodyLabel(t("eval.cm.none")))
        else:
            # The per-class probability columns are noise here (the confidence
            # column already carries the winning one).
            inputs = [k for k in rows[0] if not k.startswith("_") and not str(k).startswith("y_prob_")]
            cols = inputs + ["_true_label", "_predicted_label"]
            if "_confidence" in rows[0]:
                cols.append("_confidence")
            names = {"_true_label": t("eval.cm.true"), "_predicted_label": t("eval.cm.predicted"),
                     "_confidence": t("eval.cm.confidence")}
            table = QTableWidget(len(rows), len(cols))
            table.setHorizontalHeaderLabels([names.get(c, str(c)) for c in cols])
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setAlternatingRowColors(True)
            style_table_widget(table)
            for r, rec in enumerate(rows):
                for c, key in enumerate(cols):
                    v = rec.get(key, "")
                    if key == "_confidence":
                        text = f"{v * 100:.1f}%"
                    elif isinstance(v, float):
                        text = f"{v:.4g}"
                    else:
                        text = str(v)
                    item = QTableWidgetItem(text)
                    if key == "_confidence" and v < 0.6:
                        item.setForeground(_INCORRECT)
                    table.setItem(r, c, item)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            lay.addWidget(table, 1)
        close = PushButton(t("config.btn.close"))
        close.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(close)
        lay.addLayout(row)


class ModelInspectPanel(QWidget):
    """Details of one model. Call :meth:`load` with a record."""


    def __init__(self, parent=None):
        super().__init__(parent)
        self._rec: ModelTraining | None = None
        self._project_dir: Path | None = None
        self._pred_df: pd.DataFrame | None = None
        self._flat: dict = {}
        self._tiles_labels: list[str] = []
        self._raw: dict[str, float] = {}
        self._cm = None
        self._show_pct = False
        self._threshold = 0.5
        self._note_rec: ModelTraining | None = None
        self._groups: list[str] = []
        self._out_type = None
        self._build()
        on_theme_changed(self._render_plots)

    # ── UI ─────────────────────────────────────────────────────────────
    def _card(self) -> tuple[CardWidget, QVBoxLayout]:
        card = CardWidget()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)
        return card, lay

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # ── Details + summary ─────────────────────────────────────────
        card, lay = self._card()
        lay.addWidget(_section_title(t("eval.section.inspect"), t("eval.help.inspect")))
        self.meta_lbl = BodyLabel("")
        self.meta_lbl.setWordWrap(True)
        bind_style(self.meta_lbl, lambda c: f"color: {c.text_secondary};")
        lay.addWidget(self.meta_lbl)

        self.details_lbl = BodyLabel("")
        self.details_lbl.setWordWrap(True)
        self.details_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(self.details_lbl)

        self.results = ModelResultsWidget(self)
        lay.addWidget(self.results)
        root.addWidget(card)

        # ── Metrics (tiles / subgroup) ────────────────────────────────
        card, lay = self._card()
        head = QHBoxLayout()
        head.addWidget(_section_title(t("eval.section.metrics"), t("eval.help.metrics")))
        head.addStretch()
        self.group_lbl = BodyLabel(t("eval.breakdown"))
        head.addWidget(self.group_lbl)
        self.group_combo = ComboBox()
        self.group_combo.setMinimumWidth(180)
        self.group_combo.currentIndexChanged.connect(self._render_metrics)
        head.addWidget(self.group_combo)
        lay.addLayout(head)

        self.no_metrics_lbl = BodyLabel(t("eval.no_metrics"))
        lay.addWidget(self.no_metrics_lbl)
        self.tiles_widget = QWidget()
        self.tiles_grid = QGridLayout(self.tiles_widget)
        self.tiles_grid.setContentsMargins(0, 0, 0, 0)
        self.tiles_grid.setSpacing(12)
        self.tiles_grid.setColumnStretch(_TILES_PER_ROW, 1)
        lay.addWidget(self.tiles_widget)

        self.subgroup_warn = BodyLabel("")
        self.subgroup_warn.setWordWrap(True)
        self.subgroup_warn.setStyleSheet("color: #D13438;")
        lay.addWidget(self.subgroup_warn)
        self.subgroup_table = QTableWidget()
        self.subgroup_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.subgroup_table.setAlternatingRowColors(True)
        self.subgroup_table.verticalHeader().setVisible(False)
        self.subgroup_table.setMinimumHeight(200)
        style_table_widget(self.subgroup_table)
        lay.addWidget(self.subgroup_table)

        self.ci_note = BodyLabel(t("eval.ci_note"))
        self.ci_note.setWordWrap(True)
        bind_style(self.ci_note, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        lay.addWidget(self.ci_note)
        root.addWidget(card)

        # ── Confusion matrix + ROC ────────────────────────────────────
        self.cm_card, lay = self._card()
        head = QHBoxLayout()
        head.addWidget(_section_title(t("eval.section.cm"), t("eval.help.cm")))
        head.addStretch()
        self.threshold_lbl = BodyLabel(t("eval.cm.threshold"))
        head.addWidget(self.threshold_lbl)
        self.threshold_spin = SpinBox()
        self.threshold_spin.setRange(1, 99)
        self.threshold_spin.setValue(50)
        self.threshold_spin.setSuffix(" %")
        self.threshold_spin.setSymbolVisible(False)
        self.threshold_spin.valueChanged.connect(self._on_threshold)
        head.addWidget(self.threshold_spin)
        self.pct_btn = PushButton(t("eval.cm.show_pct"))
        self.pct_btn.clicked.connect(self._toggle_pct)
        head.addWidget(self.pct_btn)
        self.cm_export_btn = PushButton(t("eval.btn.export"))
        self.cm_export_btn.setIcon(FluentIcon.SAVE)
        self.cm_export_btn.clicked.connect(self._export_cm)
        head.addWidget(self.cm_export_btn)
        lay.addLayout(head)

        self.cm_info = BodyLabel("")
        self.cm_info.setWordWrap(True)
        bind_style(self.cm_info, lambda c: f"color: {c.text_secondary};")
        lay.addWidget(self.cm_info)

        plots = QHBoxLayout()
        plots.setSpacing(16)
        self.cm_table = QTableWidget()
        self.cm_table.setMinimumHeight(300)
        self.cm_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.cm_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cm_table.cellClicked.connect(self._on_cell)
        style_table_widget(self.cm_table)
        plots.addWidget(self.cm_table, 1)
        self.roc_canvas = FigureCanvasQTAgg(Figure(figsize=(4.4, 3.8)))
        self.roc_canvas.setMinimumHeight(300)
        plots.addWidget(self.roc_canvas, 1)
        lay.addLayout(plots)

        self.cm_hint = BodyLabel(t("eval.cm.hint"))
        bind_style(self.cm_hint, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        lay.addWidget(self.cm_hint)
        self.cm_none = BodyLabel(t("eval.no_predictions"))
        self.cm_none.setWordWrap(True)
        lay.addWidget(self.cm_none)
        root.addWidget(self.cm_card)

        # ── Notes + report ────────────────────────────────────────────
        card, lay = self._card()
        lay.addWidget(_section_title(t("eval.section.notes"), t("eval.help.notes")))
        self.notes = PlainTextEdit()
        self.notes.setPlaceholderText(t("eval.notes.placeholder"))
        self.notes.setFixedHeight(90)
        lay.addWidget(self.notes)
        row = QHBoxLayout()
        self.report_btn = PushButton(t("eval.btn.report"))
        self.report_btn.setIcon(FluentIcon.SAVE)
        self.report_btn.clicked.connect(self._export_report)
        row.addWidget(self.report_btn)
        row.addStretch()
        lay.addLayout(row)
        root.addWidget(card)

    # ── Public ─────────────────────────────────────────────────────────
    def load(self, rec: ModelTraining, project_dir: Path | None) -> None:
        self.flush_note()
        self._rec = rec
        self._project_dir = project_dir
        folder = ed.model_folder(rec)
        path = str(folder) if folder else ""
        self._flat = ed.flat_metrics(rec)
        self._pred_df = gmp.load_test_predictions(path) if path else None

        self._render_meta(path)
        self.results.load(AutoMLResult(
            model_type=rec.model_type, hyperparameters=rec.hyperparameters,
            train_metrics=rec.train_metrics, val_metrics=rec.val_metrics,
            test_metrics=rec.test_metrics, training_time_seconds=rec.training_time_seconds,
            num_trials=rec.num_trials,
            extra={"test_predictions": self._pred_df} if self._pred_df is not None else {},
        ))
        out_type = gmp.get_output_feature_info(path).get("type") if path else None
        self._out_type = out_type
        groups = gmp.get_subgroup_columns(path) if path and out_type in _CLASSIFICATION_TYPES else []
        self._groups = groups
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        self.group_combo.addItem(t("eval.breakdown.none"))
        for g in groups:
            self.group_combo.addItem(g)
        self.group_combo.blockSignals(False)
        self.group_lbl.setVisible(bool(groups))
        self.group_combo.setVisible(bool(groups))
        self._render_metrics()
        self._threshold = 0.5
        self.threshold_spin.blockSignals(True)
        self.threshold_spin.setValue(50)
        self.threshold_spin.blockSignals(False)
        self._render_cm(path)
        self._note_rec = rec
        self.notes.setPlainText(ed.load_note(rec))

    def flush_note(self) -> None:
        """Save the note of the model shown so far (called on switching)."""
        if self._note_rec is not None:
            ed.save_note(self._note_rec, self.notes.toPlainText())

    # ── Details ────────────────────────────────────────────────────────
    def _render_meta(self, path: str) -> None:
        rec = self._rec
        meta = gmp.get_run_metadata(path) if path else {}
        parts = [f"{t('eval.meta.trained')} {ed.local_time(rec)}"]
        if meta.get("dataset_name"):
            parts.append(f"{t('eval.meta.dataset')}: {meta['dataset_name']}")
        if meta.get("random_seed") is not None:
            parts.append(f"{t('eval.meta.seed')} {meta['random_seed']}")
        if meta.get("ludwig_version"):
            parts.append(f"Ludwig {meta['ludwig_version']}")
        parts.append(f"{rec.training_time_seconds:.0f} s")
        self.meta_lbl.setText("   ·   ".join(parts))

        info = gmp.get_output_feature_info(path) if path else {}
        kind = gmp.OUTPUT_TYPE_LABELS.get(info.get("type"), info.get("type") or "—")
        features = gmp.get_input_feature_names(path) if path else []
        shown = ", ".join(features[:_FEATURES_SHOWN])
        if len(features) > _FEATURES_SHOWN:
            shown += f", … (+{len(features) - _FEATURES_SHOWN})"
        size, exact = gmp.get_evaluated_size(path) if path else (None, False)
        proj = ed.project_info(self._project_dir)
        lines = [
            f"<b>{t('eval.det.type')}:</b> {rec.model_type}",
            f"<b>{t('eval.det.predicts')}:</b> {info.get('name') or rec.target_variable} — {kind}",
            f"<b>{t('eval.det.features')} ({len(features)}):</b> {shown or '—'}",
        ]
        if size is not None:
            lines.append(
                f"<b>{t('eval.det.evaluated')}:</b> {size} {t('eval.samples')}"
                + ("" if exact else f" ({t('eval.det.approx')})")
            )
        for label, value in describe_architecture(path) if path else []:
            lines.append(f"<b>{html.escape(label)}:</b> {html.escape(value)}")
        if proj.get("name"):
            lines.insert(0, f"<b>{t('eval.det.project')}:</b> {proj['name']}"
                            + (f" — {proj['primary_objective']}" if proj.get("primary_objective") else ""))
        self.details_lbl.setText("<br>".join(lines))

    # ── Metrics tiles / subgroup ───────────────────────────────────────
    def _clear_tiles(self) -> None:
        while self.tiles_grid.count():
            w = self.tiles_grid.takeAt(0).widget()
            if w is not None:
                w.deleteLater()

    def _render_metrics(self) -> None:
        names, keys = ed.split_metrics(self._flat, "test")
        self._raw = {n: float(self._flat[k]) for n, k in zip(names, keys)}
        self._tiles_labels = sorted(self._raw)
        has = bool(self._tiles_labels)
        self.no_metrics_lbl.setVisible(not has)
        idx = self.group_combo.currentIndex()
        group = self.group_combo.currentText() if idx > 0 and self._groups else ""
        by_group = bool(group) and self._pred_df is not None
        self.tiles_widget.setVisible(has and not by_group)
        self.subgroup_table.setVisible(by_group)
        self.subgroup_warn.setVisible(False)
        self.ci_note.setVisible(has and not by_group and self._pred_df is not None)
        if by_group:
            self._fill_subgroup(group)
            return
        self._clear_tiles()
        for i, name in enumerate(self._tiles_labels):
            value = self._raw[name]
            info = get_metric_info(name)
            label = info["label"] + (f" ({info['jargon']})" if info.get("jargon") else "")
            card = KPICardWidget(label, f"{value:.4f}")
            card.setFixedSize(250, 140)
            card._label_lbl.setWordWrap(True)
            band, warn = get_metric_quality(name, value)
            card.set_status({"excellent": "good", "good": "good", "moderate": "info"}.get(band, "warning" if warn else "default"))
            is_auc = name.lower().replace("_", "") in ("rocauc", "auc", "rocaucscore")
            if self._pred_df is not None and (is_auc or ci_supported(name)) and len(self._pred_df) > 0:
                _, lo, hi = (ed.bootstrap_auc_ci(self._pred_df) if is_auc
                             else ed.bootstrap_ci_fast(self._pred_df, name))
                if lo is not None:
                    card.update_value(f"{value:.4f}", f"95% CI [{lo:.3f}–{hi:.3f}]")
            card.setToolTip(info.get("short", ""))
            r, c = divmod(i, _TILES_PER_ROW)
            self.tiles_grid.addWidget(card, r, c, Qt.AlignLeft)

    def _fill_subgroup(self, column: str) -> None:
        rows = ed.subgroup_table(self._pred_df, column)
        tbl = self.subgroup_table
        tbl.clear()
        tbl.setColumnCount(3)
        tbl.setRowCount(len(rows))
        tbl.setHorizontalHeaderLabels([t("eval.sub.group"), "N", t("eval.sub.accuracy")])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        small = False
        for r, row in enumerate(rows):
            small = small or row["small"]
            g = QTableWidgetItem(f"⚠ {row['group']}" if row["small"] else str(row["group"]))
            if row["small"]:
                g.setToolTip(t("eval.sub.small").format(n=ed.SMALL_SUBGROUP_N))
            tbl.setItem(r, 0, g)
            tbl.setItem(r, 1, QTableWidgetItem(str(row["n"])))
            acc = row["accuracy"]
            tbl.setItem(r, 2, QTableWidgetItem(f"{acc:.4f}" if acc is not None else "N/A"))
        self.subgroup_warn.setText("⚠ " + t("eval.sub.small").format(n=ed.SMALL_SUBGROUP_N))
        self.subgroup_warn.setVisible(small)

    # ── Confusion matrix / ROC ─────────────────────────────────────────
    def _render_cm(self, path: str) -> None:
        self._cm = None
        supported = self._out_type in _CONFUSION_TYPES or self._out_type is None
        threshold_ok = bool(path) and pcm.supports_threshold_adjustment(path)
        self.threshold_lbl.setVisible(threshold_ok)
        self.threshold_spin.setVisible(threshold_ok)
        result = None
        if path and supported and self._pred_df is not None:
            try:
                result = pcm.compute_confusion_matrix(
                    path, None, threshold=self._threshold if threshold_ok else None)
            except Exception as exc:  # noqa: BLE001
                log.warning(f"Confusion matrix unavailable: {exc}")
        show = result is not None
        for w in (self.cm_table, self.roc_canvas, self.cm_hint, self.cm_info, self.pct_btn, self.cm_export_btn):
            w.setVisible(show)
        self.cm_none.setVisible(not show)
        self.cm_none.setText(t("eval.cm.regression") if not supported else t("eval.no_predictions"))
        if not show:
            return
        self._cm = result
        n = sum(sum(r) for r in result["matrix"])
        self.cm_info.setText(f"{n} {t('eval.samples')}")
        self._fill_cm()
        self._render_plots()

    def _fill_cm(self) -> None:
        labels, matrix = self._cm["labels"], self._cm["matrix"]
        tbl = self.cm_table
        tbl.setRowCount(len(labels))
        tbl.setColumnCount(len(labels))
        tbl.setHorizontalHeaderLabels([str(x) for x in labels])
        tbl.setVerticalHeaderLabels([str(x) for x in labels])
        dark = isDarkTheme()
        surface = QColor(colors().table_row)
        for i, row in enumerate(matrix):
            total = sum(row)
            for j, v in enumerate(row):
                ratio = v / total if total else 0
                item = QTableWidgetItem(f"{ratio * 100:.1f}%" if self._show_pct else str(v))
                base = _CORRECT if i == j else _INCORRECT
                if ratio == 0:
                    color = surface
                elif dark:
                    color = _blend(surface, base, 0.3 + 0.6 * ratio)
                else:
                    color = base.lighter(int(185 - ratio * 55))
                item.setBackground(color)
                item.setForeground(QColor("#F0F0F0" if dark else "#000000"))
                item.setTextAlignment(Qt.AlignCenter)
                f = item.font()
                f.setBold(i == j)
                f.setPointSize(14)
                item.setFont(f)
                tbl.setItem(i, j, item)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _render_plots(self) -> None:
        if self._cm is None or self._pred_df is None:
            return
        c = colors()
        fig = self.roc_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        pts = ed.roc_points(self._pred_df)
        if pts is None:
            ax.text(0.5, 0.5, t("eval.plot.na"), ha="center", va="center", color=c.text_secondary)
            ax.set_axis_off()
        else:
            fpr, tpr, auc = pts
            ax.plot(fpr, tpr, color="#0078D4", lw=2, label=f"AUC = {auc:.3f}")
            ax.plot([0, 1], [0, 1], "--", color=c.text_secondary, lw=1)
            ax.set_xlabel(t("eval.plot.fpr"))
            ax.set_ylabel(t("eval.plot.tpr"))
            ax.set_title(t("eval.plot.roc"))
            ax.legend(loc="lower right")
        style_figure(fig, ax)
        fig.tight_layout()
        self.roc_canvas.draw_idle()
        self._fill_cm()

    def _on_threshold(self, value: int) -> None:
        self._threshold = value / 100.0
        folder = ed.model_folder(self._rec) if self._rec else None
        if folder:
            self._render_cm(str(folder))

    def _toggle_pct(self) -> None:
        self._show_pct = not self._show_pct
        self.pct_btn.setText(t("eval.cm.show_counts") if self._show_pct else t("eval.cm.show_pct"))
        if self._cm is not None:
            self._fill_cm()

    def _on_cell(self, row: int, col: int) -> None:
        if self._cm is None:
            return
        labels = [str(x) for x in self._cm["labels"]]
        if not (0 <= row < len(labels) and 0 <= col < len(labels)):
            return
        rows = [r for r in self._cm["rows"]
                if str(r.get("_true_label")) == labels[row] and str(r.get("_predicted_label")) == labels[col]]
        usage_log.event("Evaluation", "click", "Confusion matrix cell", f"{labels[row]}->{labels[col]}")
        _PatientsDialog(self, labels[row], labels[col], rows).exec()

    # ── Exports ────────────────────────────────────────────────────────
    def _export_cm(self) -> None:
        if self._cm is None or self._rec is None:
            return
        labels = [str(x) for x in self._cm["labels"]]
        header = ["true \\ predicted"] + labels
        rows = [[labels[i]] + list(r) for i, r in enumerate(self._cm["matrix"])]
        usage_log.event("Evaluation", "click", "Export confusion matrix")
        export_chart_and_data(self, self._project_dir, f"confusion_matrix_{ed.model_label(self._rec)}",
                              self.cm_table, header, rows)

    def _export_report(self) -> None:
        rec = self._rec
        if rec is None:
            return
        folder = ed.model_folder(rec)
        path = str(folder) if folder else ""
        proj = ed.project_info(self._project_dir)
        meta = gmp.get_run_metadata(path) if path else {}
        info = gmp.get_output_feature_info(path) if path else {}
        features = gmp.get_input_feature_names(path) if path else []
        size, exact = gmp.get_evaluated_size(path) if path else (None, False)
        rows = [
            ("Project name", proj.get("name")), ("Protocol number", proj.get("protocol_number")),
            ("Institution", proj.get("institution")),
            ("Principal investigator", proj.get("principal_investigator")),
            ("Study type", proj.get("study_type")), ("Primary objective", proj.get("primary_objective")),
            ("Secondary objectives", "; ".join(proj.get("secondary_objectives") or []) or None),
            ("Model name", ed.model_label(rec)), ("Model type", rec.model_type),
            ("Trained", ed.local_time(rec)), ("Dataset", meta.get("dataset_name")),
            ("Target variable", info.get("name") or rec.target_variable),
            ("Predictive variables", ", ".join(features) or None),
            ("Number of predictive variables", len(features) or None),
            ("Evaluated on (patients)", size),
            ("Evaluation set is exact held-out test set", exact if size is not None else None),
        ]
        for name in self._tiles_labels:
            rows.append((get_metric_info(name)["label"], self._raw.get(name)))
        note = self.notes.toPlainText().strip()
        if note:
            rows.append(("Notes", note))
        usage_log.event("Evaluation", "click", "Export model report", ed.model_label(rec))
        export_report(self, self._project_dir, ed.model_label(rec), ["field", "value"], rows,
                      title=f"Model report — {ed.model_label(rec)}")

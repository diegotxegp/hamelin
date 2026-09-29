"""
Model comparison panel
~~~~~~~~~~~~~~~~~~~~~~

Pick two or more trained models and compare them as a ranked table, a bar
chart, a heat map or a radar chart, on their test (or training) metrics.
Also: favourites-only filter, 95 % confidence intervals in the table, a
"what matters most" shortcut, all-metrics / key-metrics switch, a settings
diff for exactly two models, and export of whatever view is on screen.
"""

from __future__ import annotations

import statistics
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QHBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from qfluentwidgets import (
    BodyLabel, CardWidget, CheckBox, ComboBox, FluentIcon, Pivot, PushButton,
    StrongBodyLabel, SwitchButton,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from hamelin.analytics import eval_data as ed
from hamelin.analytics.setting_labels import friendly_label, setting_explanation
from hamelin.core.model_history import ModelTraining
from hamelin.i18n import t
from hamelin.interface.utils import get_model_paths as gmp
from hamelin.interface.utils.bootstrap_ci import is_supported as ci_supported
from hamelin.interface.utils.metric_labels import (
    SIMPLE_MODE_PRIORITIES, filter_priority_metric_pairs, get_metric_info, pick_priority_metric,
)
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets import HelpButton
from hamelin.view.widgets.eval_export import export_chart_and_data
from hamelin.view.widgets.table_theme import style_table_widget
from hamelin.view.widgets.theme_colors import bind_style, colors, on_theme_changed, style_figure

_GREEN = "#2E9E5B"
_BLUE = "#2E6BFF"
_YELLOW = "#E0A800"
_VIEWS = ("table", "graph", "heatmap", "radar")


def _robust_bounds(values):
    s = sorted(values)
    return s[int(0.05 * (len(s) - 1))], s[int(0.95 * (len(s) - 1))]


def _normalize(v, lo, hi):
    return 0.5 if hi == lo else max(0.0, min(1.0, (v - lo) / (hi - lo)))


class CurrentPageStack(QWidget):
    """Like QStackedWidget, but only the page being shown takes up room.

    QStackedWidget reserves the size of its largest page for all of them, so
    a short page (a two-row table) sat in the empty height kept for a tall
    one (a chart). Here the other pages are simply hidden.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pages: list[QWidget] = []
        self._current = -1
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

    def addWidget(self, page: QWidget) -> int:
        self._pages.append(page)
        self.layout().addWidget(page)
        page.setVisible(False)
        if self._current < 0:
            self.setCurrentIndex(0)
        return len(self._pages) - 1

    def setCurrentIndex(self, index: int) -> None:
        self._current = index
        for i, page in enumerate(self._pages):
            page.setVisible(i == index)
        self.updateGeometry()

    def currentIndex(self) -> int:
        return self._current

    def currentWidget(self):
        return self._pages[self._current] if 0 <= self._current < len(self._pages) else None

    def count(self) -> int:
        return len(self._pages)


class _ConfigDiffDialog(QDialog):
    """Settings that differ between two models."""

    def __init__(self, parent, project_dir, rec_a: ModelTraining, rec_b: ModelTraining):
        super().__init__(parent)
        self._project_dir = project_dir
        self._a, self._b = rec_a, rec_b
        self._defaults = False
        self._diffs: list[dict] = []
        self.setWindowTitle(t("eval.diff.title"))
        self.resize(900, 560)
        bind_style(self, lambda c: f"QDialog {{ background: {c.card_background}; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)
        self.subtitle = StrongBodyLabel(f"{ed.model_label(rec_a)}   vs.   {ed.model_label(rec_b)}")
        lay.addWidget(self.subtitle)
        self.empty = BodyLabel("")
        lay.addWidget(self.empty)
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        style_table_widget(self.table)
        lay.addWidget(self.table, 1)
        row = QHBoxLayout()
        self.toggle = PushButton(t("eval.diff.show_all"))
        self.toggle.clicked.connect(self._toggle)
        row.addWidget(self.toggle)
        self.export = PushButton(t("eval.btn.export"))
        self.export.setIcon(FluentIcon.SAVE)
        self.export.clicked.connect(self._export)
        row.addWidget(self.export)
        row.addStretch()
        close = PushButton(t("config.btn.close"))
        close.clicked.connect(self.accept)
        row.addWidget(close)
        lay.addLayout(row)
        self._fill()

    def _toggle(self) -> None:
        self._defaults = not self._defaults
        self.toggle.setText(t("eval.diff.hide_defaults") if self._defaults else t("eval.diff.show_all"))
        self._fill()

    def _fill(self) -> None:
        fa, fb = ed.model_folder(self._a), ed.model_folder(self._b)
        if fa is None or fb is None:
            self._diffs = []
            self.table.hide()
            self.empty.setText(t("eval.diff.unavailable"))
            return
        self._diffs = gmp.diff_configs(str(fa), str(fb), include_defaults=self._defaults)
        if not self._diffs:
            self.table.hide()
            self.empty.setText(t("eval.diff.identical"))
            return
        self.empty.setText("")
        self.table.show()
        self.table.setColumnCount(3)
        self.table.setRowCount(len(self._diffs))
        self.table.setHorizontalHeaderLabels(
            [t("eval.diff.setting"), ed.model_label(self._a), ed.model_label(self._b)])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for r, d in enumerate(self._diffs):
            key = QTableWidgetItem(friendly_label(d["key"]))
            key.setToolTip(f"{d['key']}\n\n{setting_explanation(d['key'])}")
            self.table.setItem(r, 0, key)
            self.table.setItem(r, 1, QTableWidgetItem(
                t("eval.diff.not_set") if d["only_in"] == "b" else str(d["value_a"])))
            self.table.setItem(r, 2, QTableWidgetItem(
                t("eval.diff.not_set") if d["only_in"] == "a" else str(d["value_b"])))

    def _export(self) -> None:
        if not self._diffs:
            return
        rows = [(friendly_label(d["key"]), "" if d["only_in"] == "b" else d["value_a"],
                 "" if d["only_in"] == "a" else d["value_b"]) for d in self._diffs]
        export_chart_and_data(
            self, self._project_dir, f"config_diff_{ed.model_label(self._a)}_{ed.model_label(self._b)}",
            self.table, [t("eval.diff.setting"), ed.model_label(self._a), ed.model_label(self._b)], rows)


class ModelComparePanel(QWidget):
    """Compare the trained models of the active project."""

    favorites_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recs: list[ModelTraining] = []
        self._project_dir: Path | None = None
        self._models_dir: Path | None = None
        self._split = "test"
        self._view = "table"
        self._criterion = ""
        self._show_ci = False
        self._rows: list[dict] = []
        self._names: list[str] = []
        self._keys: list[str] = []
        self._by_label: dict[str, ModelTraining] = {}
        self._table_names: list[str] = []
        self._table_keys: list[str] = []
        self._table_rows: list[dict] = []
        self._build()
        on_theme_changed(self._refresh_theme)

    # ── UI ─────────────────────────────────────────────────────────────
    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # selection + controls
        card = CardWidget()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)
        head = QHBoxLayout()
        head.addWidget(StrongBodyLabel(t("eval.section.compare")))
        head.addWidget(HelpButton(t("eval.help.compare")))
        head.addStretch()
        lay.addLayout(head)

        self.empty_lbl = BodyLabel(t("eval.empty"))
        lay.addWidget(self.empty_lbl)
        self.model_list = QWidget()
        self._list_layout = QVBoxLayout(self.model_list)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._checks: list[tuple[str, CheckBox]] = []
        lay.addWidget(self.model_list)
        self.sel_lbl = BodyLabel("")
        bind_style(self.sel_lbl, lambda c: f"color: {c.text_secondary};")
        lay.addWidget(self.sel_lbl)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.fav_check = CheckBox(t("eval.cmp.favorites_only"))
        self.fav_check.stateChanged.connect(self._fill_list)
        row.addWidget(self.fav_check)
        self.split_btn = PushButton(t("eval.cmp.test_metrics"))
        self.split_btn.clicked.connect(self._toggle_split)
        row.addWidget(self.split_btn)
        self.all_check = CheckBox(t("eval.cmp.all_metrics"))
        self.all_check.setChecked(True)
        self.all_check.stateChanged.connect(self._refresh)
        row.addWidget(self.all_check)
        self.ci_check = CheckBox(t("eval.cmp.ci"))
        self.ci_check.stateChanged.connect(self._on_ci)
        row.addWidget(self.ci_check)
        row.addStretch()
        self.diff_btn = PushButton(t("eval.btn.diff"))
        self.diff_btn.setIcon(FluentIcon.SYNC)
        self.diff_btn.clicked.connect(self._open_diff)
        row.addWidget(self.diff_btn)
        self.export_btn = PushButton(t("eval.btn.export"))
        self.export_btn.setIcon(FluentIcon.SAVE)
        self.export_btn.clicked.connect(self._export)
        row.addWidget(self.export_btn)
        lay.addLayout(row)

        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(BodyLabel(t("eval.cmp.metric")))
        self.metric_combo = ComboBox()
        self.metric_combo.setMinimumWidth(260)
        self.metric_combo.currentIndexChanged.connect(self._on_metric)
        row.addWidget(self.metric_combo)
        row.addWidget(BodyLabel(t("eval.cmp.focus")))
        self.focus_combo = ComboBox()
        self.focus_combo.addItem(t("eval.cmp.focus.none"))
        for opt in SIMPLE_MODE_PRIORITIES:
            self.focus_combo.addItem(opt["label"], userData=opt["key"])
        self.focus_combo.currentIndexChanged.connect(self._on_focus)
        row.addWidget(self.focus_combo)
        row.addStretch()
        lay.addLayout(row)
        root.addWidget(card)

        # views
        self.view_card = CardWidget()
        vl = QVBoxLayout(self.view_card)
        vl.setContentsMargins(20, 20, 20, 20)
        vl.setSpacing(12)
        self.pivot = Pivot()
        for key in _VIEWS:
            self.pivot.addItem(routeKey=key, text=t(f"eval.cmp.view.{key}"),
                               onClick=lambda _=False, k=key: self._set_view(k))
        self.pivot.setCurrentItem("table")
        vl.addWidget(self.pivot, 0, Qt.AlignLeft)

        self.radar_row = QWidget()
        rr = QHBoxLayout(self.radar_row)
        rr.setContentsMargins(0, 0, 0, 0)
        rr.addWidget(BodyLabel(t("eval.cmp.radar_model")))
        self.radar_combo = ComboBox()
        self.radar_combo.setMinimumWidth(240)
        self.radar_combo.currentIndexChanged.connect(self._draw_radar)
        rr.addWidget(self.radar_combo)
        rr.addStretch()
        vl.addWidget(self.radar_row)

        self.title_lbl = StrongBodyLabel("")
        vl.addWidget(self.title_lbl)
        self.stack = CurrentPageStack()
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().sectionClicked.connect(self._on_header)
        self.table.cellClicked.connect(self._on_cell)
        style_table_widget(self.table)
        self.stack.addWidget(self.table)
        self.canvases: dict[str, FigureCanvasQTAgg] = {}
        for key in ("graph", "heatmap", "radar"):
            canvas = FigureCanvasQTAgg(Figure(figsize=(7, 4.6)))
            canvas.setFixedHeight(460)
            self.canvases[key] = canvas
            self.stack.addWidget(canvas)
        vl.addWidget(self.stack)

        self.note_lbl = BodyLabel("")
        self.note_lbl.setWordWrap(True)
        bind_style(self.note_lbl, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        vl.addWidget(self.note_lbl)
        self.size_lbl = BodyLabel("")
        self.size_lbl.setWordWrap(True)
        bind_style(self.size_lbl, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        vl.addWidget(self.size_lbl)
        root.addWidget(self.view_card)
        root.addStretch()
        self.radar_row.setVisible(False)
        self._update_state()

    # ── Public ─────────────────────────────────────────────────────────
    def set_records(self, recs: list[ModelTraining], project_dir, models_dir) -> None:
        checked = {label for label, box in self._checks if box.isChecked()}
        self._recs = list(recs)
        self._project_dir = Path(project_dir) if project_dir else None
        self._models_dir = Path(models_dir) if models_dir else None
        self._fill_list(preselect=checked if checked else None)

    def select(self, labels: list[str]) -> None:
        """Tick exactly these models (by label)."""
        for label, box in self._checks:
            box.blockSignals(True)
            box.setChecked(label in labels)
            box.blockSignals(False)
        self._on_selection()

    # ── Selection ──────────────────────────────────────────────────────
    def _is_fav(self, rec: ModelTraining) -> bool:
        return self._models_dir is not None and ed.model_label(rec) in ed.load_favorites(self._models_dir)

    def _fill_list(self, *_args, preselect=None) -> None:
        favs = ed.load_favorites(self._models_dir) if self._models_dir else set()
        while self._list_layout.count():
            w = self._list_layout.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        self._checks = []
        self._by_label = {}
        for rec in self._recs:
            label = ed.model_label(rec)
            if self.fav_check.isChecked() and label not in favs:
                continue
            self._by_label[label] = rec
            box = CheckBox(f"{'★' if label in favs else '☆'} {label}   —   {rec.target_variable}")
            box.setChecked(bool(preselect and label in preselect))
            box.stateChanged.connect(self._on_selection)
            self._list_layout.addWidget(box)
            self._checks.append((label, box))
        self._on_selection()

    def _selected(self) -> list[ModelTraining]:
        return [self._by_label[label] for label, box in self._checks if box.isChecked()]

    def _on_selection(self, *_args) -> None:
        self._refresh()

    def _update_state(self) -> None:
        n = len(self._selected())
        self.empty_lbl.setVisible(not self._recs)
        self.model_list.setVisible(bool(self._recs))
        self.sel_lbl.setText(t("eval.selected").format(n=n) if n else t("eval.cmp.pick"))
        self.diff_btn.setEnabled(n == 2)
        self.diff_btn.setToolTip("" if n == 2 else t("eval.diff.needs_two"))
        self.view_card.setVisible(n >= 1)
        self.export_btn.setEnabled(n >= 1)

    # ── Controls ───────────────────────────────────────────────────────
    def _toggle_split(self) -> None:
        self._split = "training" if self._split == "test" else "test"
        self.split_btn.setText(t("eval.cmp.train_metrics") if self._split == "training"
                               else t("eval.cmp.test_metrics"))
        self.split_btn.setToolTip(ed.SPLIT_EXPLANATIONS[self._split])
        self._refresh()

    def _on_ci(self) -> None:
        self._show_ci = self.ci_check.isChecked()
        if self._view == "table":
            self._draw_table()

    def _on_metric(self, index: int) -> None:
        if 0 <= index < len(self._keys) and self.metric_combo.signalsBlocked() is False:
            self._criterion = self._keys[index]
            self._draw_current()

    def _on_focus(self, index: int) -> None:
        key = self.focus_combo.itemData(index)
        if key:
            picked = pick_priority_metric(self._names, key)
            if picked and picked in self._names:
                self.metric_combo.setCurrentIndex(self._names.index(picked))

    def _set_view(self, key: str) -> None:
        self._view = key
        self.stack.setCurrentIndex(_VIEWS.index(key))
        self.radar_row.setVisible(key == "radar")
        self._draw_current()

    # ── Data + drawing ─────────────────────────────────────────────────
    def _refresh(self, *_args) -> None:
        self._update_state()
        recs = self._selected()
        if not recs:
            return
        self._rows, self._names, self._keys = ed.build_comparison(recs, self._split)
        prev = self._criterion
        self.metric_combo.blockSignals(True)
        self.metric_combo.clear()
        for n in self._names:
            self.metric_combo.addItem(get_metric_info(n)["label"])
        if self._keys:
            if prev in self._keys:
                idx = self._keys.index(prev)
            else:
                idx = 0
            self.metric_combo.setCurrentIndex(idx)
            self._criterion = self._keys[idx]
        self.metric_combo.blockSignals(False)

        self.radar_combo.blockSignals(True)
        cur = self.radar_combo.currentText()
        self.radar_combo.clear()
        for r in self._rows:
            self.radar_combo.addItem(r["model"])
        if cur and cur in [r["model"] for r in self._rows]:
            self.radar_combo.setCurrentText(cur)
        self.radar_combo.blockSignals(False)

        self.note_lbl.setText(ed.checkpoint_disclosure(self._keys))
        lines = []
        for rec in recs:
            f = ed.model_folder(rec)
            size, exact = gmp.get_evaluated_size(str(f)) if f else (None, False)
            label = ed.model_label(rec)
            lines.append(f"{label}: " + (t("eval.cmp.size_unknown") if size is None else
                         f"{size} {t('eval.samples')}" + ("" if exact else f" ({t('eval.det.approx')})")))
        self.size_lbl.setText(t("eval.cmp.sizes") + "  " + "   ·   ".join(lines))
        self._draw_current()

    def _display_metrics(self):
        if self.all_check.isChecked():
            return list(self._names), list(self._keys)
        return filter_priority_metric_pairs(self._names, self._keys)

    def _draw_current(self) -> None:
        if not self._rows or not self._keys:
            return
        crit_name = self._criterion.split("/")[-2] if self._criterion else ""
        self.title_lbl.setText(t("eval.cmp.ranking").format(m=get_metric_info(crit_name)["label"]) if crit_name else "")
        self.title_lbl.setVisible(self._view != "radar")
        {"table": self._draw_table, "graph": self._draw_graph,
         "heatmap": self._draw_heatmap, "radar": self._draw_radar}[self._view]()

    def _sorted_rows(self) -> list[dict]:
        crit = self._criterion
        low = ed.is_lower_better(crit.split("/")[-2]) if crit else False

        def keyf(row):
            v = row.get(crit)
            return (v if isinstance(v, (int, float)) else (float("inf") if low else float("-inf")))
        return sorted(self._rows, key=keyf, reverse=not low)

    def _draw_table(self) -> None:
        names, keys = self._display_metrics()
        rows = self._sorted_rows()
        favs = ed.load_favorites(self._models_dir) if self._models_dir else set()
        headers = ["★", t("eval.col.name")] + [get_metric_info(n)["label"] for n in names]
        tbl = self.table
        tbl.clear()
        tbl.setColumnCount(len(headers))
        tbl.setRowCount(len(rows))
        tbl.setHorizontalHeaderLabels(headers)
        # Long plain-language metric names: size columns to their header text
        # (the table scrolls sideways if needed) instead of eliding them.
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        tbl.setColumnWidth(0, 44)
        tbl.setFixedHeight(min(420, 44 + 32 * max(len(rows), 1)))
        by_label = {ed.model_label(r): r for r in self._selected()}
        best = {}
        for j, (n, k) in enumerate(zip(names, keys)):
            vals = [r.get(k) for r in rows if isinstance(r.get(k), (int, float))]
            if vals:
                best[k] = min(vals) if ed.is_lower_better(n) else max(vals)
        for i, row in enumerate(rows):
            fav = row["model"] in favs
            star = QTableWidgetItem("★" if fav else "☆")
            star.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 0, star)
            tbl.setItem(i, 1, QTableWidgetItem(row["model"]))
            for c in (0, 1):
                tbl.item(i, c).setForeground(QColor(_YELLOW) if fav else QColor(colors().text_primary))
            rec = by_label.get(row["model"])
            preds = None
            if self._show_ci and rec is not None:
                f = ed.model_folder(rec)
                preds = gmp.load_test_predictions(str(f)) if f else None
            for j, (n, k) in enumerate(zip(names, keys), start=2):
                v = row.get(k)
                text = f"{v:.3f}" if isinstance(v, (int, float)) else "N/A"
                tip = ""
                if preds is not None and len(preds) and ci_supported(n) and self._split == "test":
                    _, lo, hi = ed.bootstrap_ci_fast(preds, n)
                    if lo is not None:
                        text += f"  [{lo:.3f}–{hi:.3f}]"
                        tip = t("eval.ci_note")
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if tip:
                    item.setToolTip(tip)
                if isinstance(v, (int, float)) and best.get(k) == v and len(rows) > 1:
                    f_ = item.font()
                    f_.setBold(True)
                    item.setFont(f_)
                tbl.setItem(i, j, item)
        self._table_names, self._table_keys, self._table_rows = names, keys, rows

    def _on_header(self, col: int) -> None:
        idx = col - 2
        if 0 <= idx < len(self._table_keys):
            self._criterion = self._table_keys[idx]
            if self._criterion in self._keys:
                self.metric_combo.blockSignals(True)
                self.metric_combo.setCurrentIndex(self._keys.index(self._criterion))
                self.metric_combo.blockSignals(False)
            self._draw_current()

    def _on_cell(self, row: int, col: int) -> None:
        if col != 0 or self._models_dir is None or row >= len(self._table_rows):
            return
        toggled = ed.toggle_favorite(self._models_dir, self._table_rows[row]["model"])
        usage_log.event("Evaluation", "click", "Favorite star", f"{self._table_rows[row]['model']} -> {toggled}")
        self._fill_list(preselect={ed.model_label(r) for r in self._selected()})
        self.favorites_changed.emit()

    def _fig(self, key: str):
        fig = self.canvases[key].figure
        fig.clear()
        return fig, self.canvases[key]

    def _draw_graph(self) -> None:
        fig, canvas = self._fig("graph")
        ax = fig.add_subplot(111)
        c = colors()
        if not self._criterion:
            return
        name = self._criterion.split("/")[-2]
        rows = [r for r in self._sorted_rows() if isinstance(r.get(self._criterion), (int, float))]
        vals = [r[self._criterion] for r in rows]
        if vals:
            best = vals.index(min(vals) if ed.is_lower_better(name) else max(vals))
            favs = ed.load_favorites(self._models_dir) if self._models_dir else set()
            ax.bar(range(len(vals)), vals, color=[_GREEN if i == best else c.text_secondary for i in range(len(vals))],
                   width=0.7)
            ax.set_xticks(range(len(vals)),
                          [("★ " if r["model"] in favs else "") + r["model"] for r in rows], rotation=20, ha="right")
            for i, v in enumerate(vals):
                ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", color=c.text_primary, fontsize=9)
            ax.set_ylabel(get_metric_info(name)["label"])
            arrow = "↓" if ed.is_lower_better(name) else "↑"
            ax.set_title(f"{get_metric_info(name)['label']} {arrow}")
        style_figure(fig, ax)
        fig.tight_layout()
        canvas.draw_idle()

    def _draw_heatmap(self) -> None:
        import matplotlib
        from matplotlib import patheffects

        fig, canvas = self._fig("heatmap")
        ax = fig.add_subplot(111)
        names, keys = self._display_metrics()
        rows = self._sorted_rows()
        if not names or not rows:
            canvas.draw_idle()
            return
        matrix = np.full((len(rows), len(keys)), np.nan)
        for i, r in enumerate(rows):
            for j, k in enumerate(keys):
                v = r.get(k)
                if isinstance(v, (int, float)):
                    matrix[i, j] = v
        norm = np.full_like(matrix, np.nan)
        for j in range(matrix.shape[1]):
            col = matrix[:, j]
            ok = ~np.isnan(col)
            if not ok.any():
                continue
            lo, hi = np.nanmin(col), np.nanmax(col)
            if np.isclose(hi, lo):
                norm[ok, j] = 0.5
            else:
                cn = (col - lo) / (hi - lo)
                norm[:, j] = 1 - cn if ed.is_lower_better(names[j]) else cn
        cmap = matplotlib.colormaps["viridis"].copy()
        cmap.set_bad("#f2f2f2")
        im = ax.imshow(np.ma.masked_invalid(norm), aspect="auto", cmap=cmap, interpolation="nearest")
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if not np.isnan(matrix[i, j]):
                    txt = ax.text(j, i, f"{matrix[i, j]:.3g}", ha="center", va="center",
                                  color="white", fontsize=10, fontweight="bold")
                    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground="black")])
        favs = ed.load_favorites(self._models_dir) if self._models_dir else set()
        ax.set_yticks(range(len(rows)), [("★ " if r["model"] in favs else "") + r["model"] for r in rows])
        ax.set_xticks(range(len(names)),
                      [f"{get_metric_info(n)['label']} {'↓' if ed.is_lower_better(n) else '↑'}" for n in names],
                      rotation=45, ha="right")
        ax.set_title(t("eval.cmp.heatmap_title"))
        cbar = fig.colorbar(im, ax=ax, fraction=0.05)
        cbar.set_label(t("eval.cmp.heatmap_bar"))
        style_figure(fig, ax)
        cc = colors()
        cbar.ax.tick_params(colors=cc.text_secondary)
        cbar.set_label(t("eval.cmp.heatmap_bar"), color=cc.text_secondary)
        fig.tight_layout()
        canvas.draw_idle()

    def _draw_radar(self, *_args) -> None:
        fig, canvas = self._fig("radar")
        c = colors()
        rows = self._rows
        focus = self.radar_combo.currentText() or (rows[0]["model"] if rows else "")
        values: dict[str, list[float]] = {}
        own: dict[str, float] = {}
        for r in rows:
            for k, v in r.items():
                if k.startswith(f"{self._split}/") and isinstance(v, (int, float)):
                    name = k.split("/")[-2]
                    if r["model"] == focus:
                        own.setdefault(name, float(v))
                    values.setdefault(name, []).append(float(v))
        labels = sorted(values)
        if len(labels) < 3:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, t("eval.cmp.radar_min"), ha="center", va="center", color=c.text_secondary)
            ax.set_axis_off()
            style_figure(fig, ax)
            canvas.draw_idle()
            return
        model_vals, mean_vals = [], []
        for name in labels:
            vs = values[name]
            mean_v = statistics.mean(vs)
            mv = own.get(name, mean_v)
            sign = -1 if ed.is_lower_better(name) else 1
            lo, hi = _robust_bounds([sign * x for x in vs])
            model_vals.append(_normalize(sign * mv, lo, hi))
            mean_vals.append(_normalize(sign * mean_v, lo, hi))
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        ax = fig.add_subplot(111, projection="polar")
        for vals, color, ls, lab in ((mean_vals, c.text_secondary, "--", t("eval.cmp.mean")),
                                     (model_vals, _BLUE, "-", focus)):
            ax.plot(angles + angles[:1], vals + vals[:1], color=color, linestyle=ls, linewidth=2, label=lab)
            ax.fill(angles + angles[:1], vals + vals[:1], color=color, alpha=0.15)
        ax.set_xticks(angles, [get_metric_info(n)["label"] for n in labels], fontsize=8)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0], [""] * 4)
        ax.set_ylim(0, 1)
        ax.set_title(t("eval.cmp.radar_title"), pad=24)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False)
        style_figure(fig, ax)
        ax.set_facecolor(c.chart_face)
        ax.grid(color=c.table_gridline)
        fig.tight_layout()
        canvas.draw_idle()

    def _refresh_theme(self) -> None:
        if getattr(self, "_rows", None):
            self._draw_current()

    # ── Diff / export ──────────────────────────────────────────────────
    def _open_diff(self) -> None:
        sel = self._selected()
        if len(sel) != 2:
            return
        usage_log.event("Evaluation", "click", "Compare settings", f"{ed.model_label(sel[0])} vs {ed.model_label(sel[1])}")
        _ConfigDiffDialog(self, self._project_dir, sel[0], sel[1]).exec()

    def _export(self) -> None:
        if not self._rows:
            return
        header = ["model"] + self._names
        rows = [[r["model"]] + [r.get(k) for k in self._keys] for r in self._sorted_rows()]
        source = self.table if self._view == "table" else self.canvases[self._view].figure
        usage_log.event("Evaluation", "click", "Export comparison", self._view)
        export_chart_and_data(self, self._project_dir, f"model_comparison_{self._view}", source, header, rows)

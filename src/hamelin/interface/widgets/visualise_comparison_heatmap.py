from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtWidgets import (
    QWidget, QLabel,
    QVBoxLayout, QHBoxLayout,
    QSizePolicy,
)
from PySide6.QtGui import QFont
from hamelin.interface.utils.widgets import info_button_row, RoundedButton, Popup, ErrorPopup, style_info_button, set_asset_icon, build_glossary_widget, AdvancedModeToggle
from hamelin.interface.utils.colors import YELLOW, BLACK, GRAY_LIGHT, colors, themed, themed_add
from hamelin.interface.utils.metrix_extractor import build_comparison_data, is_lower_better, SPLIT_LABELS, SPLIT_EXPLANATIONS
from hamelin.interface.utils.metric_labels import get_metric_info, filter_priority_metric_pairs, pick_priority_metric
from hamelin.interface.utils.favorites import is_favorite, toggle_favorite
from hamelin.interface.utils.export import make_export_button, export_chart_and_data
from hamelin.interface.utils.app_state import app_state
from hamelin.interface.widgets.simple_mode_selector import MetricPrioritySelector
import hamelin.interface.utils.get_model_paths as gmp

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import patheffects
import numpy as np
from hamelin.interface.utils.theme_state import theme_state


class VisualiseComparisonHeatmap(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.models = []
        self._all_models = []
        self.criterion = None

        self.metrics_keys = []
        self.metric_names = []
        self.display_metrics_keys = []
        self.display_metric_names = []
        self.data = []
        self.popup = None
        self.favorites_only = False
        self.split = "test"
        self._chosen_priority_key = None
        app_state.advancedModeChanged.connect(self._on_advanced_mode_changed)

        # ROOT LAYOUT
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(40, 40, 40, 60)
        self.root.setSpacing(20)

        top = QHBoxLayout()

        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        self.btn_back = RoundedButton("  Back", 220, 80, 40)
        set_asset_icon(self.btn_home, "home.svg")
        self.btn_home.setIconSize(QSize(32, 32))
        set_asset_icon(self.btn_back, "back.svg")
        self.btn_back.setIconSize(QSize(32, 32))

        top.addWidget(self.btn_home)
        top.addStretch()

        self.advanced_toggle = AdvancedModeToggle()
        self.advanced_toggle.setChecked(app_state.advanced_mode)
        self.advanced_toggle.toggled.connect(app_state.set_advanced_mode)
        top.addWidget(self.advanced_toggle)

        top.addWidget(self.btn_back)

        self.root.addLayout(top)

        # TITLE
        self.title = QLabel("Comparison Heatmap")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        themed(self.title, lambda c: f"""
            background: {c.surface};
            color: {c.text_pure};
            border: 2px solid {c.border_pure};
            padding: 15px 25px;
            font-size: 42px;
            font-weight: 700;
            border-radius: 10px;
        """)

        self.favorites_only_btn = RoundedButton("☆ Favorites only", 240, 60, 30)
        self.favorites_only_btn.setCheckable(True)
        themed_add(self.favorites_only_btn, lambda c: f"""
            QPushButton {{ font-size: 16px; }}
            QPushButton:checked {{ background: {YELLOW}; color: {BLACK}; }}
        """)
        self.favorites_only_btn.toggled.connect(self._on_favorites_only_toggled)

        self.split_toggle_btn = RoundedButton(f"{SPLIT_LABELS['test']} metrics", 200, 60, 30)
        self.split_toggle_btn.setCheckable(True)
        themed_add(self.split_toggle_btn, lambda c: f"""
            QPushButton {{ font-size: 16px; }}
            QPushButton:checked {{ background: {YELLOW}; color: {BLACK}; }}
        """)
        self.split_toggle_btn.setToolTip(SPLIT_EXPLANATIONS["test"])
        self.split_toggle_btn.toggled.connect(self._on_split_toggled)

        self.export_btn = make_export_button()
        self.export_btn.clicked.connect(self._on_export_clicked)

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        self.root.addLayout(title_layout)

        # Action row, centered on its own line below the title rather than
        # crammed onto the same row - see visualise_comparison_table.py's
        # matching comment for why.
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        actions_layout.addWidget(self.favorites_only_btn)
        actions_layout.addSpacing(10)
        actions_layout.addWidget(self.split_toggle_btn)
        actions_layout.addSpacing(10)
        actions_layout.addWidget(self.export_btn)
        actions_layout.addStretch()
        self.root.addLayout(actions_layout)

        # PRIORITY GATE (simple mode) - shown above the heatmap until the
        # user says what they care about; see update_ui().
        self.priority_selector = MetricPrioritySelector()
        self.priority_selector.setVisible(False)
        self.priority_selector.prioritySelected.connect(self._on_priority_selected)
        # Same stretch weight as heatmap_card below - see the matching
        # comment in visualise_comparison_table.py.
        self.root.addWidget(self.priority_selector, stretch=10)

        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event', self._on_heatmap_clicked)
        theme_state.themeChanged.connect(self._on_theme_changed)
        self.ax = None

        self.heatmap_card = QWidget()
        card_layout = QVBoxLayout(self.heatmap_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(self.canvas)

        # Info button
        self.info_btn = RoundedButton("!", 50, 50, 25)
        self.info_btn.clicked.connect(self.show_popup)
        style_info_button(self.info_btn, GRAY_LIGHT)

        self.info_row = info_button_row(self.info_btn)
        self.root.addWidget(self.info_row)
        self.root.addWidget(self.heatmap_card, stretch=10)

        self.root.addStretch(2)


    def set_data(self, models, criterion, view_mode=None):
        self._all_models = models
        self.criterion = criterion
        self.update_ui()

    def _on_favorites_only_toggled(self, checked):
        self.favorites_only = checked
        self.favorites_only_btn.setText("★ Favorites only" if checked else "☆ Favorites only")
        self.update_ui()

    def _on_split_toggled(self, checked):
        self.split = "training" if checked else "test"
        self.split_toggle_btn.setText(f"{SPLIT_LABELS[self.split]} metrics")
        self.split_toggle_btn.setToolTip(SPLIT_EXPLANATIONS[self.split])
        self.update_ui()

    def update_ui(self):
        if not self._all_models:
            return

        # Simple mode gate: wait for the user to say what they care about
        # (see widgets/simple_mode_selector.py) before showing any results -
        # once chosen, it's remembered for the rest of this page's lifetime,
        # so this only blocks the very first render in simple mode.
        if not app_state.advanced_mode and self._chosen_priority_key is None:
            self.priority_selector.setVisible(True)
            self.heatmap_card.setVisible(False)
            self.info_row.setVisible(False)
            return

        self.priority_selector.setVisible(False)
        self.heatmap_card.setVisible(True)
        self.info_row.setVisible(True)

        # self.models is the currently-displayed (possibly favorites-only)
        # subset - everything below keys off it, self._all_models keeps the
        # full set around so toggling favorites_only back off restores it.
        self.models = [m for m in self._all_models if not self.favorites_only or is_favorite(m)]

        if not self.models:
            self.fig.clear()
            self.canvas.draw_idle()
            return

        self.data, self.metric_names, self.metrics_keys = build_comparison_data(self.models, split=self.split)

        if not self.metrics_keys:
            return

        if not app_state.advanced_mode and self._chosen_priority_key:
            resolved = pick_priority_metric(self.metric_names, self._chosen_priority_key)
            if resolved:
                self.criterion = self.metrics_keys[self.metric_names.index(resolved)]

        # Simple mode shows only the priority metrics as columns instead of
        # every metric across the group, with the chosen-priority one first
        # - export/glossary still use the full self.metric_names/
        # self.metrics_keys above, unaffected.
        if app_state.advanced_mode:
            self.display_metric_names, self.display_metrics_keys = self.metric_names, self.metrics_keys
        else:
            self.display_metric_names, self.display_metrics_keys = filter_priority_metric_pairs(
                self.metric_names, self.metrics_keys
            )
            if self._chosen_priority_key:
                resolved = pick_priority_metric(self.display_metric_names, self._chosen_priority_key)
                if resolved and resolved != self.display_metric_names[0]:
                    idx = self.display_metric_names.index(resolved)
                    self.display_metric_names.insert(0, self.display_metric_names.pop(idx))
                    self.display_metrics_keys.insert(0, self.display_metrics_keys.pop(idx))

        # MATRIX
        matrix = np.full((len(self.models), len(self.display_metrics_keys)), np.nan)

        for i, row in enumerate(self.data):
            for j, key in enumerate(self.display_metrics_keys):
                val = row.get(key, np.nan)
                if isinstance(val, (int, float)):
                    matrix[i, j] = val


        col_min = np.nanmin(matrix, axis=0)
        col_max = np.nanmax(matrix, axis=0)

        norm = np.full_like(matrix, np.nan, dtype=float)

        for j in range(matrix.shape[1]):
            col = matrix[:, j]
            if np.all(np.isnan(col)):
                continue

            cmin = col_min[j]
            cmax = col_max[j]

            if np.isclose(cmax, cmin) or np.isnan(cmin) or np.isnan(cmax):
                mask = ~np.isnan(col)
                norm[mask, j] = 0.5
            else:
                denom = cmax - cmin
                col_norm = (col - cmin) / denom
                if is_lower_better(self.display_metric_names[j]):
                    col_norm = 1.0 - col_norm
                norm[:, j] = col_norm

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        self.ax = ax

        masked = np.ma.masked_invalid(norm)

        try:
            cmap = matplotlib.colormaps['viridis']
        except AttributeError:
            cmap = matplotlib.cm.get_cmap('viridis')
        try:
            cmap.set_bad(color='#f2f2f2')
        except Exception:
            pass

        c = ax.imshow(masked, aspect='auto', cmap=cmap, interpolation='nearest')

        # Cell values on top of the color - the colors show relative
        # ranking at a glance, but the raw numbers are what someone
        # actually wants to quote. White with a black outline stays
        # readable regardless of how dark or light the cell's color is,
        # so it doesn't need a per-cell contrast calculation.
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix[i, j]
                if np.isnan(value):
                    continue
                label = ax.text(
                    j, i, f"{value:.3g}",
                    ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold",
                )
                label.set_path_effects([patheffects.withStroke(linewidth=2, foreground="black")])

        ax.set_yticks(np.arange(len(self.models)))
        # Row labels double as favorite toggles: click a model's name to
        # star/unstar it, see _on_heatmap_clicked.
        ax.set_yticklabels([
            ("★ " if is_favorite(m) else "☆ ") + m.split('/')[-1] for m in self.models
        ])
        for label, m in zip(ax.get_yticklabels(), self.models):
            label.set_color(YELLOW if is_favorite(m) else colors().text)
        ax.set_xticks(np.arange(len(self.display_metric_names)))
        xlabels = [
            f"{get_metric_info(name)['label']} {'↓' if is_lower_better(name) else '↑'}"
            for name in self.display_metric_names
        ]
        ax.set_xticklabels(xlabels, rotation=45, ha='right')

        ax.set_title("Models vs Metrics heatmap")
        cbar = self.fig.colorbar(c, ax=ax, orientation='vertical', fraction=0.05)
        cbar.set_label("brighter = better (per column, direction-adjusted)")
        self._style_figure(ax, cbar)

        self.canvas.draw_idle()

        if self.criterion:
            self.title.setText(f"Ranking by {get_metric_info(self.criterion.split('/')[-2])['label']}")

    def _style_figure(self, ax, cbar):
        c = colors()
        self.fig.patch.set_facecolor(c.chart_face)
        ax.set_facecolor(c.chart_face)
        # y tick labels are coloured one by one (favorites in yellow), so
        # only their tick marks are set here.
        ax.tick_params(axis="x", colors=c.text_pure)
        ax.tick_params(axis="y", color=c.text_pure)
        ax.title.set_color(c.text_pure)
        cbar.ax.tick_params(colors=c.text_pure)
        cbar.set_label(cbar.ax.yaxis.label.get_text(), color=c.text_pure)
        for spine in list(ax.spines.values()) + list(cbar.ax.spines.values()):
            spine.set_edgecolor(c.text_pure)

    def _on_theme_changed(self, _dark):
        self.update_ui()

    def _on_advanced_mode_changed(self, value):
        # Re-render so switching mode while a comparison is already showing
        # takes effect immediately, instead of only on the next set_data().
        self.advanced_toggle.setChecked(value)
        self.update_ui()

    def _on_priority_selected(self, key):
        self._chosen_priority_key = key
        self.update_ui()

    def _on_export_clicked(self):
        if not self.data:
            ErrorPopup(self, "Select some models to compare first.").show()
            return

        header = ["model"] + self.metric_names
        rows = [
            [row["model"]] + [row.get(key) for key in self.metrics_keys]
            for row in self.data
        ]
        export_chart_and_data(self, "model_comparison_heatmap", self.fig, header, rows)

    def _on_heatmap_clicked(self, event):
        if self.ax is None:
            return

        for i, label in enumerate(self.ax.get_yticklabels()):
            contains, _ = label.contains(event)
            if contains and i < len(self.models):
                toggle_favorite(self.models[i])
                self.update_ui()
                return

    def show_popup(self):
        width, height = 700, 350
        self.popup = Popup(
            parent=self,
            x=max((self.width() - width) // 2, 20),
            y=max((self.height() - height) // 2, 20),
            width=width,
            height=height,
            background=YELLOW,
        )
        self.popup.installEventFilter(self)
        self.popup.show()

        size_lines, size_caveat = (
            gmp.dataset_size_lines([row["model"] for row in self.data]) if self.data else ([], None)
        )

        content = build_glossary_widget(
            [],
            intro=(
                SPLIT_EXPLANATIONS[self.split] + " "
                "This heatmap shows models (rows) against metrics (columns). "
                "Values are column-normalized so higher colors indicate better relative performance."
            ),
            footer_title="Dataset sizes" if size_lines else None,
            footer_lines=size_lines + [size_caveat] if size_lines else None,
        )

        self.popup.layout.addSpacing(20)
        self.popup.layout.addWidget(content)

        self.popup.close_btn.raise_()

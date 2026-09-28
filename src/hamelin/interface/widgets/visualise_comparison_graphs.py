from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea
from PySide6.QtGui import QFont
import pyqtgraph as pg

from hamelin.interface.widgets.dropdowns import SimpleDropdown
from hamelin.interface.widgets.simple_mode_selector import MetricPrioritySelector
from hamelin.interface.utils.widgets import info_button_row, Popup, RoundedButton, ErrorPopup, style_info_button, build_glossary_widget, set_asset_icon, AdvancedModeToggle
from hamelin.interface.utils.colors import COLORS, BLACK, GREEN, INFO_YELLOW, colors, themed, themed_add
from hamelin.interface.utils.metrix_extractor import build_comparison_data, is_lower_better, SPLIT_LABELS, SPLIT_EXPLANATIONS
from hamelin.interface.utils.metric_labels import get_metric_info, get_metric_glossary_entries, pick_priority_metric
from hamelin.interface.utils.favorites import is_favorite, toggle_favorite
from hamelin.interface.utils.export import make_export_button, export_chart_and_data
from hamelin.interface.utils.app_state import app_state
import hamelin.interface.utils.get_model_paths as gmp
from hamelin.interface.utils.theme_state import theme_state
from hamelin.interface.utils.plot_theme import style_plot


class _FavoriteAxisItem(pg.AxisItem):
    """Bottom axis for the bar chart whose tick labels double as favorite
    toggles (see _on_graph_clicked). pyqtgraph draws every tick label with
    one shared pen, so per-label color needs overriding drawPicture -
    everything here is copied from AxisItem.drawPicture except the text
    loop, which colors a label yellow when its text starts with the star
    prefix set in update_graph()."""

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        p.setRenderHint(p.RenderHint.Antialiasing, False)
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)

        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)

        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)

        if self.style['tickFont'] is not None:
            p.setFont(self.style['tickFont'])

        default_pen = self.textPen()
        favorite_pen = pg.mkPen(COLORS['yellow'])
        bounding = self.boundingRect().toAlignedRect()
        p.setClipRect(bounding)
        for rect, flags, text in textSpecs:
            p.setPen(favorite_pen if text.startswith('★') else default_pen)
            p.drawText(rect, int(flags), text)


# MAIN WIDGET

class VisualiseComparisonGraphsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.models = []
        self.metric_names = []
        self.metrics_keys = []
        self.metric_labels = []
        self.data = []
        self.initial_criterion = None
        self.popup = None
        self._plotted_models = []
        self.favorites_only = False
        self.split = "test"
        self._selected_metric_name = None
        self._chosen_priority_key = None
        app_state.advancedModeChanged.connect(self._on_advanced_mode_changed)

        # ROOT
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(30, 15, 30, 20)
        self.root.setSpacing(20)

        # TOP
        top = QHBoxLayout()

        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        self.btn_back = RoundedButton("  Back", 220, 80, 40)
        self.btn_home.setIconSize(QSize(32, 32))
        set_asset_icon(self.btn_home, "home.svg")
        set_asset_icon(self.btn_back, "back.svg")
        self.btn_home.setIconSize(QSize(32, 32))
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
        self.title = QLabel("Comparison of Models")
        self.title.setAlignment(Qt.AlignCenter)
        themed(self.title, lambda c: f"""
            background: {c.surface};
            color: {c.text};
            border: 2px solid {c.border};
            padding: 14px 20px;
            font-size: 40px;
            font-weight: 700;
            border-radius: 10px;
        """)

        self.favorites_only_btn = RoundedButton("☆ Favorites only", 240, 60, 30)
        self.favorites_only_btn.setCheckable(True)
        themed_add(self.favorites_only_btn, lambda c: f"""
            QPushButton {{ font-size: 16px; }}
            QPushButton:checked {{ background: {COLORS['yellow']}; color: {BLACK}; }}
        """)
        self.favorites_only_btn.toggled.connect(self._on_favorites_only_toggled)

        self.split_toggle_btn = RoundedButton(f"{SPLIT_LABELS['test']} metrics", 200, 60, 30)
        self.split_toggle_btn.setCheckable(True)
        themed_add(self.split_toggle_btn, lambda c: f"""
            QPushButton {{ font-size: 16px; }}
            QPushButton:checked {{ background: {COLORS['yellow']}; color: {BLACK}; }}
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

        # PRIORITY GATE (simple mode) - shown above the metric picker/graph
        # until the user says what they care about; see update_ui().
        self.priority_selector = MetricPrioritySelector()
        self.priority_selector.setVisible(False)
        self.priority_selector.prioritySelected.connect(self._on_priority_selected)
        # Same stretch weight as graph_card below - see the matching
        # comment in visualise_comparison_table.py.
        self.root.addWidget(self.priority_selector, stretch=5)

        # DROPDOWN
        self.metric_selector = SimpleDropdown("Select Metric", [])
        self.metric_selector.currentIndexChanged.connect(self.update_graph)
        self.root.addWidget(self.metric_selector)

        # GRAPH
        self.graph = pg.PlotWidget(axisItems={'bottom': _FavoriteAxisItem(orientation='bottom')})

        # CLEAN SETUP
        self.graph.setMinimumHeight(450)

        self.graph.setFrameShape(QFrame.Shape.NoFrame)
        themed(self.graph, "border: none; background: transparent;")

        self.graph.getPlotItem().layout.setContentsMargins(60, 20, 20, 60)
        self.graph.setLabel("left", "Value")
        self.graph.scene().sigMouseClicked.connect(self._on_graph_clicked)
        style_plot(self.graph)
        theme_state.themeChanged.connect(self._on_theme_changed)

        # CARD 
        self.graph_card = QWidget()
        self.graph_card.setAttribute(Qt.WA_StyledBackground, True)

        themed(self.graph_card, lambda c: f"""
            QWidget {{
                background: {c.surface};
                border-radius: 20px;
                border: 2px solid {c.border_pure};
            }}
        """)

        self.info_btn = RoundedButton("!", 50, 50, 25)
        self.info_btn.clicked.connect(self.show_popup)

        style_info_button(self.info_btn, COLORS['gray_light'])

        card_layout = QVBoxLayout(self.graph_card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.addWidget(self.graph)


        self.info_row = info_button_row(self.info_btn)
        self.root.addWidget(self.info_row)
        self.root.addWidget(self.graph_card, stretch=5)
        self.root.addStretch(1)

    # DATA

    def set_data(self, models, criterion=None, view_mode=None):
        self.models = models
        self.initial_criterion = criterion
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
        if not self.models:
            return

        # Simple mode gate: wait for the user to say what they care about
        # (see widgets/simple_mode_selector.py) before showing any results -
        # once chosen, it's remembered for the rest of this page's lifetime,
        # so this only blocks the very first render in simple mode.
        if not app_state.advanced_mode and self._chosen_priority_key is None:
            self.priority_selector.setVisible(True)
            self.metric_selector.setVisible(False)
            self.graph_card.setVisible(False)
            self.info_row.setVisible(False)
            return

        self.priority_selector.setVisible(False)
        self.metric_selector.setVisible(True)
        self.graph_card.setVisible(True)
        self.info_row.setVisible(True)

        models_to_show = [m for m in self.models if not self.favorites_only or is_favorite(m)]

        if not models_to_show:
            self.graph.clear()
            self._plotted_models = []
            return

        self.data, self.metric_names, self.metrics_keys = build_comparison_data(models_to_show, split=self.split)
        self.metric_labels = [get_metric_info(n)["label"] for n in self.metric_names]

        self.metric_selector.clear()
        self.metric_selector.addItems(self.metric_labels)

        # Prefer re-selecting whichever metric FAMILY was already chosen
        # (survives a test/train split switch, since "accuracy" exists on
        # both even though the full key's prefix changes from "test/..."
        # to "training/..."). Otherwise, in simple mode, prefer whatever
        # answers the chosen priority; falls back to the initial launch
        # criterion, then to just the first metric so the graph is never
        # left on a stale/empty selection.
        target_name = self._selected_metric_name
        if target_name not in self.metric_names and not app_state.advanced_mode and self._chosen_priority_key:
            target_name = pick_priority_metric(self.metric_names, self._chosen_priority_key)
        if target_name not in self.metric_names and self.initial_criterion in self.metrics_keys:
            target_name = self.metric_names[self.metrics_keys.index(self.initial_criterion)]

        if target_name in self.metric_names:
            idx = self.metric_names.index(target_name)
        elif self.metric_names:
            idx = 0
        else:
            idx = None

        if idx is not None:
            self.metric_selector.selected = self.metric_labels[idx]
            self.metric_selector._update_label()

        self.update_graph()


    def _on_theme_changed(self, _dark):
        style_plot(self.graph)
        self.update_graph()

    def _on_advanced_mode_changed(self, value):
        # Re-render so switching mode while a comparison is already showing
        # takes effect immediately, instead of only on the next set_data().
        self.advanced_toggle.setChecked(value)
        self.update_ui()

    def _on_priority_selected(self, key):
        self._chosen_priority_key = key
        self.update_ui()

    # GRAPH

    def update_graph(self):
        self.graph.clear()

        label = self.metric_selector.currentText()
        if not label or label not in self.metric_labels:
            return

        idx = self.metric_labels.index(label)
        metric_name = self.metric_names[idx]
        self._selected_metric_name = metric_name
        metric_key = self.metrics_keys[idx]

        models, values = [], []

        for row in self.data:
            v = row.get(metric_key)
            if isinstance(v, (int, float)):
                models.append(row["model"])
                values.append(v)

        if not values:
            return

        self._plotted_models = models

        if is_lower_better(metric_name):
            best_idx = values.index(min(values))
        else:
            best_idx = values.index(max(values))

        # AXIS - model names double as favorite toggles: click a label
        # (below the bars) to star/unstar that model, see _on_graph_clicked.
        axis = self.graph.getAxis("bottom")
        axis.setTicks([[
            (i, ("★ " if is_favorite(m) else "☆ ") + m) for i, m in enumerate(models)
        ]])
        axis.setStyle(tickTextOffset=20, tickFont=QFont("Arial", 16))

        # BARS
        for i, v in enumerate(values):
            color = GREEN if i == best_idx else colors().muted

            bar = pg.BarGraphItem(
                x=[i],
                height=[v],
                width=0.75,
                brush=pg.mkBrush(color),
                pen=pg.mkPen(None)
            )
            self.graph.addItem(bar)

        self.graph.getViewBox().setDefaultPadding(0.1)

    def _on_export_clicked(self):
        if not self.data:
            ErrorPopup(self, "Select some models to compare first.").show()
            return

        header = ["model"] + self.metric_names
        rows = [
            [row["model"]] + [row.get(key) for key in self.metrics_keys]
            for row in self.data
        ]
        export_chart_and_data(self, "model_comparison_graph", self.graph_card, header, rows)

    def _on_graph_clicked(self, event):
        # Only the axis label strip toggles a favorite, not the bars
        # themselves - a click only counts if it lands below the plot's
        # data area (where pyqtgraph draws the bottom-axis tick labels).
        if not self._plotted_models:
            return

        vb = self.graph.getViewBox()
        scene_pos = event.scenePos()
        plot_rect = vb.mapRectToScene(vb.boundingRect())

        if scene_pos.y() <= plot_rect.bottom():
            return

        x = vb.mapSceneToView(scene_pos).x()
        idx = round(x)
        if idx < 0 or idx >= len(self._plotted_models) or abs(x - idx) > 0.4:
            return

        toggle_favorite(self._plotted_models[idx])
        self.update_graph()

    # POPUP / INFO BUTTON

    def show_popup(self):
        width, height = 700, 460
        self.popup = Popup(
            parent=self,
            x=max((self.width() - width) // 2, 20),
            y=max((self.height() - height) // 2, 20),
            width=width,
            height=height,
            background=COLORS['yellow'],
        )
        self.popup.installEventFilter(self)
        self.popup.show()

        self._fill_popup_content()

        style_info_button(self.info_btn, INFO_YELLOW, text_color=COLORS['black'])

    def eventFilter(self, obj, event):
        if self.popup is not None and obj is self.popup and event.type() == QEvent.Hide:
            style_info_button(self.info_btn, COLORS['gray_light'])
        return super().eventFilter(obj, event)

    def _fill_popup_content(self):
        entries = get_metric_glossary_entries(self.metric_names)

        size_lines, size_caveat = (
            gmp.dataset_size_lines([row["model"] for row in self.data]) if self.data else ([], None)
        )

        content = build_glossary_widget(
            entries,
            intro=(
                SPLIT_EXPLANATIONS[self.split] + " "
                "Each bar represents one model, and the green bar shows the "
                "best result for the metric selected in the menu."
            ),
            empty_text="Select some models to compare first.",
            footer_title="Dataset sizes" if size_lines else None,
            footer_lines=size_lines + [size_caveat] if size_lines else None,
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        themed(scroll, "QScrollArea { background: transparent; }")
        scroll.setWidget(content)

        self.popup.layout.addSpacing(20)
        self.popup.layout.addWidget(scroll)

        self.popup.close_btn.raise_()
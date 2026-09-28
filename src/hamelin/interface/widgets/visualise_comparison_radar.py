from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea
from PySide6.QtGui import QColor, QPainterPath, QPen
import pyqtgraph as pg

from hamelin.interface.widgets.dropdowns import SimpleDropdown, CheckBoxDropdown
from hamelin.interface.utils.widgets import info_button_row, Popup, RoundedButton, style_info_button, build_glossary_widget, set_asset_icon, AdvancedModeToggle, ErrorPopup
from hamelin.interface.utils.colors import COLORS, INFO_YELLOW, colors, themed
from hamelin.interface.utils.theme_state import theme_state
from hamelin.interface.utils.plot_theme import style_plot
from hamelin.interface.utils.export import make_export_button, export_chart_and_data
from hamelin.interface.utils.metrix_extractor import load_run_metrics, is_lower_better, get_target_column
from hamelin.interface.utils.metric_labels import get_metric_info, get_metric_glossary_entries
from hamelin.interface.utils.favorites import is_favorite
from hamelin.interface.utils.app_state import app_state
from hamelin.interface.utils.radar import robust_bounds, normalize, point_on_circle, RadarItem
import hamelin.interface.utils.get_model_paths as gmp

import statistics

BLUE_C = "#2E6BFF"


def metric_name(key):
    # Mirrors widgets.one_model.metric_name - kept as its own tiny copy
    # here rather than importing across widget modules for one two-line
    # helper.
    name = key.split("/")[-2].lower()
    return "accuracy" if name in ("acc", "accuracy") else name


class VisualiseComparisonRadarWidget(QWidget):
    """One model's metrics plotted against the average of a chosen group of
    other models, on a radar chart - the exact same model-vs-average radar
    one_model.py used to show for a single model, just living on its own
    page now (reachable from the landing page directly, or as a "Radar"
    option from the Comparison Dashboard's own model picker) since a
    comparison tool belongs with the other comparison tools rather than
    bolted onto the single-model page."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initial_model = None
        self.initial_compare_models = []
        self.last_labels = []
        self.last_model_raw = {}
        self.last_mean_raw = {}
        self.favorites_only = False
        self.split = "test"
        self.axis_popups = []
        app_state.advancedModeChanged.connect(self._on_advanced_mode_changed)

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(30, 15, 30, 20)
        self.root.setSpacing(20)

        # TOP
        top = QHBoxLayout()
        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        self.btn_back = RoundedButton("  Back", 220, 80, 40)
        set_asset_icon(self.btn_home, "home.svg")
        self.btn_home.setIconSize(QSize(32, 32))
        set_asset_icon(self.btn_back, "back.svg")
        self.btn_back.setIconSize(QSize(32, 32))
        top.addWidget(self.btn_home)
        top.addStretch()

        self.export_btn = make_export_button()
        self.export_btn.clicked.connect(self._on_export_clicked)
        top.addWidget(self.export_btn)
        top.addSpacing(10)

        self.advanced_toggle = AdvancedModeToggle()
        self.advanced_toggle.setChecked(app_state.advanced_mode)
        self.advanced_toggle.toggled.connect(app_state.set_advanced_mode)
        top.addWidget(self.advanced_toggle)

        top.addWidget(self.btn_back)
        self.root.addLayout(top)

        # TITLE
        self.title = QLabel("Model Comparison - Radar")
        self.title.setAlignment(Qt.AlignCenter)
        themed(self.title, lambda c: f"""
            background: {c.surface};
            color: {c.text};
            border: 2px solid {c.border};
            padding: 14px 20px;
            font-size: 36px;
            font-weight: 700;
            border-radius: 10px;
        """)

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        self.root.addLayout(title_layout)

        # This page is reachable directly from the landing page (not just
        # via the Comparison Dashboard's own model picker), so it needs its
        # own model selection: one model (plotted solid blue) and a
        # multi-select of whichever others its average is computed from
        # (plotted dashed gray) - exactly the "Select Model" / "Include in
        # average" pair one_model.py's own radar used to have. Each
        # dropdown's own placeholder text ("Select Model" / "Include in
        # comparison") is what shows until something's picked - same as
        # every other dropdown in the app - so no separate label needed
        # here.
        selector_row = QHBoxLayout()
        self.model_selector = SimpleDropdown(
            "Select Model", [], favorite_check=is_favorite, annotate=self._annotate_model
        )
        self.model_selector.currentIndexChanged.connect(self.update_graph)
        selector_row.addWidget(self.model_selector, stretch=1)
        self.root.addLayout(selector_row)

        compare_row = QHBoxLayout()
        self.compare_dropdown = CheckBoxDropdown(
            "Include in comparison", [], favorite_check=is_favorite, annotate=self._annotate_model
        )
        self.compare_dropdown.selectionChanged.connect(self.update_graph)
        compare_row.addWidget(self.compare_dropdown, stretch=1)
        self.root.addLayout(compare_row)

        self.empty_hint = QLabel(
            "Not enough data to draw a radar - select a model with test "
            "metrics."
        )
        self.empty_hint.setAlignment(Qt.AlignCenter)
        self.empty_hint.setWordWrap(True)
        themed(self.empty_hint, f"color: {COLORS['white']}; font-size: 18px;")
        self.empty_hint.setVisible(False)
        self.root.addWidget(self.empty_hint)

        # GRAPH
        self.graph = pg.PlotWidget()
        self.graph.setMinimumHeight(350)
        self.graph.getViewBox().setAspectLocked(True)
        style_plot(self.graph)
        theme_state.themeChanged.connect(self._on_theme_changed)
        self.graph.setFrameShape(QFrame.Shape.NoFrame)
        themed(self.graph, "border: none;")
        self.graph.getPlotItem().hideAxis("bottom")
        self.graph.getPlotItem().hideAxis("left")

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

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        themed(separator, lambda c: f"color: {c.rule};")
        card_layout.addWidget(separator)

        # LEGEND - fixed, two entries: the selected model (solid blue) and
        # the average of whatever's checked in "Include in comparison"
        # (dashed gray).
        legend_layout = QHBoxLayout()
        legend_layout.setContentsMargins(10, 8, 10, 0)
        legend_layout.setSpacing(10)

        # setFrameShape(NoFrame) explicitly on both - a QFrame's stylesheet
        # can override its background/border but Qt still paints its own
        # native frame underneath unless the frame shape itself is turned
        # off, which showed up as an unwanted box around each swatch.
        blue_line = QFrame()
        blue_line.setFrameShape(QFrame.NoFrame)
        blue_line.setFixedSize(35, 4)
        themed(blue_line, f"""
            background: {BLUE_C};
            border: none;
            border-radius: 2px;
        """)
        blue_label = QLabel("Selected model")
        # graph_card's own stylesheet (QWidget { border: 2px solid black;
        # background: white; ... }) cascades to every descendant QWidget
        # that doesn't override border/background itself - without these,
        # this QLabel inherits that border and shows as a boxed frame.
        themed(blue_label, lambda c: f"color: {c.text_pure}; font-size: 16px; border: none; background: transparent;")

        gray_line = QFrame()
        gray_line.setFrameShape(QFrame.NoFrame)
        gray_line.setFixedSize(35, 4)
        themed(gray_line, lambda c: f"""
            background: transparent;
            border: none;
            border-top: 3px dashed {c.muted};
        """)
        gray_label = QLabel("Average of included models")
        themed(gray_label, lambda c: f"color: {c.text_pure}; font-size: 16px; border: none; background: transparent;")

        legend_layout.addStretch()
        legend_layout.addWidget(blue_line)
        legend_layout.addWidget(blue_label)
        legend_layout.addSpacing(25)
        legend_layout.addWidget(gray_line)
        legend_layout.addWidget(gray_label)
        legend_layout.addStretch()
        card_layout.addLayout(legend_layout)


        self.info_row = info_button_row(self.info_btn)
        self.root.addWidget(self.info_row)
        self.root.addWidget(self.graph_card, stretch=5)
        self.root.addStretch(1)

    # DATA

    def set_data(self, models, criterion=None, view_mode=None):
        # Called either from the landing page (models=[] - this page reads
        # every available model itself) or from the Comparison Dashboard's
        # own model picker ("Radar" view mode - models is whatever was
        # checked there: the first becomes the selected model, the rest
        # seed "Include in comparison"). Either way this only seeds the two
        # selectors below with sensible defaults; update_ui() re-reads the
        # full model list live so it's never stale.
        self.initial_model = models[0] if models else None
        self.initial_compare_models = list(models) if models else []
        self.update_ui()

    @staticmethod
    def _annotate_model(model_name):
        # Shown next to each model in both dropdowns so it's harder to mix
        # models that don't even predict the same thing without noticing.
        target = get_target_column(model_name)
        return f"Predicts: {target}" if target else None

    def _on_advanced_mode_changed(self, value):
        self.advanced_toggle.setChecked(value)

    def update_ui(self):
        """Refreshes both selectors from the live model list and re-applies
        whatever set_data() seeded them with - called on every entry into
        this page (including the landing page's direct button) so it never
        shows a stale model list."""
        all_models = gmp.get_model_names()

        self.model_selector.clear()
        self.model_selector.addItems(all_models)
        primary = self.initial_model if self.initial_model in all_models else (all_models[0] if all_models else None)
        if primary:
            self.model_selector.selected = primary
            self.model_selector._update_label()

        self.compare_dropdown.set_items(all_models)
        # Defaults to every model, matching one_model.py's old "Include in
        # average" default, unless a specific set was passed via set_data().
        preselect = set(self.initial_compare_models) if self.initial_compare_models else set(all_models)
        for w in self.compare_dropdown.item_widgets:
            w.setChecked(w.property("raw_value") in preselect)

        self.update_graph()

    # GRAPH

    def clear_axis_popups(self):
        for p in self.axis_popups:
            p.close()
        self.axis_popups = []

    def show_axis_value(self, label, model_v, mean_v, x, y):
        self.clear_axis_popups()
        popup = Popup(
            parent=self,
            width=260,
            height=140,
            x=int(self.width() / 2 + x),
            y=int(self.height() / 2 + y),
            background="#FFF7C2",
        )
        # Transparent to mouse events so hover/leave detection on the point
        # underneath keeps working even while the mouse drifts onto the
        # tooltip itself - see one_model.py's original version of this.
        popup.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        title = QLabel(label)
        title.setAlignment(Qt.AlignLeft)
        themed(title, lambda c: f"font-size: 16px; font-weight: 700; color: {c.text_pure};")
        popup.layout.addWidget(title)

        values = QLabel(f"Model: {model_v:.4f}\nAverage: {mean_v:.4f}")
        values.setAlignment(Qt.AlignLeft)
        themed(values, lambda c: f"font-size: 16px; color: {c.text_pure};")
        popup.layout.addWidget(values)

        popup.show()
        self.axis_popups.append(popup)

    def _on_axis_hovered(self, plot, points, ev=None):
        # `points` can be a numpy array depending on pyqtgraph version,
        # where bool(array) raises for more than one element - check
        # length instead of truthiness.
        if len(points) == 0:
            self.clear_axis_popups()
            return

        p = points[0]
        data = p.data()
        if not data:
            return

        label = data.get("label")
        model_v = data.get("model")
        mean_v = data.get("mean")
        pos = p.pos()
        self.show_axis_value(label, model_v, mean_v, pos.x(), pos.y())

    def update_graph(self):
        self.graph.clear()
        self.clear_axis_popups()

        model = self.model_selector.currentText()
        if not model:
            self.last_labels = []
            self.empty_hint.setVisible(True)
            self.graph_card.setVisible(False)
            self.info_row.setVisible(False)
            return

        compare_models = self.compare_dropdown.get_selected()
        compare_models = [m for m in compare_models if not self.favorites_only or is_favorite(m)]
        all_models = compare_models or [model]

        current_metrics = load_run_metrics(model) or {}

        metric_values = {}
        for m in all_models:
            metrics = current_metrics if m == model else (load_run_metrics(m) or {})
            for k, v in metrics.items():
                if not k.startswith(f"{self.split}/") or not isinstance(v, (int, float)):
                    continue
                name = metric_name(k)
                metric_values.setdefault(name, []).append(float(v))

        if not metric_values:
            self.last_labels = []
            self.empty_hint.setVisible(True)
            self.graph_card.setVisible(False)
            self.info_row.setVisible(False)
            return

        self.empty_hint.setVisible(False)
        self.graph_card.setVisible(True)
        self.info_row.setVisible(True)

        labels = sorted(metric_values.keys())

        current_by_metric = {}
        for k, v in current_metrics.items():
            if k.startswith(f"{self.split}/") and isinstance(v, (int, float)):
                current_by_metric.setdefault(metric_name(k), float(v))

        # What THIS model actually reported, vs `labels` which is the union
        # across every model in the comparison set (used only to size/shape
        # the radar - a metric this model never computed still gets an axis
        # if another included model has it, just overlapping the average).
        own_labels = [m for m in labels if m in current_by_metric]
        self.last_labels = own_labels

        model_values = []
        mean_values = []
        model_raw = {}
        mean_raw = {}

        for metric in labels:
            values = metric_values[metric]
            mean_v = statistics.mean(values)
            model_v = current_by_metric.get(metric, mean_v)

            model_raw[metric] = model_v
            mean_raw[metric] = mean_v

            # For placement on the radar only: lower is better for "loss"
            # style metrics, so the sign is flipped purely for normalizing
            # position - a point further from the center always means
            # "better", regardless of metric type.
            sign = -1 if is_lower_better(metric) else 1

            p5, p95 = robust_bounds([sign * x for x in values])
            model_values.append(normalize(sign * model_v, p5, p95))
            mean_values.append(normalize(sign * mean_v, p5, p95))

        self.last_model_raw = model_raw
        self.last_mean_raw = mean_raw

        n = len(labels)
        radius = 220
        pal = colors()

        # RINGS
        for lvl in [0.25, 0.5, 0.75, 1.0]:
            path = QPainterPath()
            for i in range(n):
                x, y = point_on_circle(i, n, radius, lvl)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            item = pg.Qt.QtWidgets.QGraphicsPathItem(path)
            item.setPen(QPen(QColor(pal.ring), 1))
            self.graph.addItem(item)

        # SPOKES + AXIS LABELS + HOVER POINTS
        spots = []
        for i, label in enumerate(labels):
            x, y = point_on_circle(i, n, radius)
            self.graph.plot([0, x], [0, y], pen=pg.mkPen(pal.spoke))

            info = get_metric_info(label)
            display_text = info["label"]
            if info["priority"]:
                display_text = f"★ {display_text}"
            txt_color = pal.priority_text if info["priority"] else pal.label_text

            # Anchor each label on the edge closest to the plot center, so
            # the text always grows outward instead of overlapping the
            # chart on the left/bottom sides.
            dx, dy = x / radius, y / radius
            anchor = (0.5 * (1 - dx), 0.5 * (1 + dy))
            txt = pg.TextItem(display_text, color=txt_color, anchor=anchor)
            txt.setPos(1.25 * x, 1.25 * y)
            self.graph.addItem(txt)

            spots.append({
                "pos": (x, y),
                "data": {
                    "label": info["label"],
                    "model": model_raw.get(label, 0.0),
                    "mean": mean_raw.get(label, 0.0),
                },
            })

        if spots:
            sp = pg.ScatterPlotItem(hoverable=True)
            sp.addPoints([
                {
                    "pos": s["pos"],
                    "data": s["data"],
                    "symbol": "o",
                    "size": 20,
                    "pen": None,
                    "brush": QColor(0, 0, 0, 0),
                }
                for s in spots
            ])
            sp.setCursor(Qt.PointingHandCursor)
            sp.sigHovered.connect(self._on_axis_hovered)
            self.graph.addItem(sp)

        model_item = RadarItem(model_values, labels, radius, BLUE_C)
        mean_item = RadarItem(mean_values, labels, radius, pal.muted, dashed=True)

        self.graph.addItem(mean_item)
        self.graph.addItem(model_item)

        self.graph.setXRange(-radius * 1.4, radius * 1.4)
        self.graph.setYRange(-radius * 1.4, radius * 1.4)

    def _on_theme_changed(self, _dark):
        style_plot(self.graph)
        self.update_graph()


    # EXPORT

    def _on_export_clicked(self):
        if not self.last_labels or not self.last_model_raw:
            ErrorPopup(self, "Draw a radar first (pick a model with test metrics).").show()
            return

        model = self.model_selector.currentText() or "model"
        header = ["metric", model, "average of compared models"]
        rows = [
            (get_metric_info(metric)["label"],
             self.last_model_raw.get(metric),
             self.last_mean_raw.get(metric))
            for metric in sorted(self.last_model_raw)
        ]
        export_chart_and_data(
            self, f"{model.replace('/', '_')}_radar", self.graph_card, header, rows,
        )

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
        if getattr(self, "popup", None) is not None and obj is self.popup and event.type() == QEvent.Hide:
            style_info_button(self.info_btn, COLORS['gray_light'])
        return super().eventFilter(obj, event)

    def _fill_popup_content(self):
        entries = get_metric_glossary_entries(self.last_labels or [])
        content = build_glossary_widget(
            entries,
            intro="Metrics shown:",
            empty_text="Select a model to see explanations.",
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        themed(scroll, "QScrollArea { background: transparent; }")
        scroll.setWidget(content)

        self.popup.layout.addSpacing(20)
        self.popup.layout.addWidget(scroll)
        self.popup.close_btn.raise_()

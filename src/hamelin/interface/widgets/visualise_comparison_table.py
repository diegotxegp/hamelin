from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtWidgets import (
    QWidget, QLabel,
    QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractScrollArea,
    QSizePolicy, QScrollArea,
)
from PySide6.QtGui import QFont, QColor
from hamelin.interface.utils.widgets import info_button_row, RoundedButton, ClickableHeader, Popup, ErrorPopup, style_info_button, build_glossary_widget, set_asset_icon, AdvancedModeToggle
from hamelin.interface.utils.colors import COLORS, INFO_YELLOW, colors, themed, themed_add, table_corner_qss
from hamelin.interface.utils.metrix_extractor import build_comparison_data, SPLIT_LABELS, SPLIT_EXPLANATIONS
from hamelin.interface.utils.metric_labels import get_metric_info, get_metric_glossary_entries, filter_priority_metric_pairs, pick_priority_metric
from hamelin.interface.utils.favorites import is_favorite, toggle_favorite
from hamelin.interface.utils.export import make_export_button, export_chart_and_data
from hamelin.interface.utils.app_state import app_state
from hamelin.interface.utils.bootstrap_ci import bootstrap_ci, is_supported as ci_is_supported
from hamelin.interface.widgets.simple_mode_selector import MetricPrioritySelector
import hamelin.interface.utils.get_model_paths as gmp
from hamelin.interface.utils.theme_state import theme_state


# MAIN WIDGET

class VisualiseComparisonWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.models = []
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
        # Off by default - a bootstrap CI means loading + resampling every
        # shown model's test_predictions.csv, worth skipping unless asked
        # for rather than paying that cost on every render.
        self.show_ci = False
        app_state.advancedModeChanged.connect(self._on_advanced_mode_changed)
        theme_state.themeChanged.connect(self._restyle_favorites)

        # ROOT LAYOUT

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(40, 40, 40, 60)
        self.root.setSpacing(35)

        # TOP BAR

        top = QHBoxLayout()

        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        self.btn_back = RoundedButton("  Back", 220, 80, 40)
        set_asset_icon(self.btn_home, "home.svg")
        self.btn_home.setIconSize(QSize(32, 32))
        set_asset_icon(self.btn_back, "back.svg")
        self.btn_back.setIconSize(QSize(32, 32))

        self.btn_home.setCursor(Qt.PointingHandCursor)
        self.btn_back.setCursor(Qt.PointingHandCursor)

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
        self.title.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        themed(self.title, lambda c: f"""
            background: {c.surface};
            color: {c.text};
            border: 2px solid {c.border};
            padding: 15px 25px;
            font-size: 42px;
            font-weight: 700;
            border-radius: 10px;
        """)

        self.favorites_only_btn = RoundedButton("☆ Favorites only", 240, 60, 30)
        self.favorites_only_btn.setCheckable(True)
        themed_add(self.favorites_only_btn, lambda c: f"""
            QPushButton {{ font-size: 16px; }}
            QPushButton:checked {{ background: {COLORS['yellow']}; color: {COLORS['black']}; }}
        """)
        self.favorites_only_btn.toggled.connect(self._on_favorites_only_toggled)

        self.split_toggle_btn = RoundedButton(f"{SPLIT_LABELS['test']} metrics", 200, 60, 30)
        self.split_toggle_btn.setCheckable(True)
        themed_add(self.split_toggle_btn, lambda c: f"""
            QPushButton {{ font-size: 16px; }}
            QPushButton:checked {{ background: {COLORS['yellow']}; color: {COLORS['black']}; }}
        """)
        self.split_toggle_btn.setToolTip(SPLIT_EXPLANATIONS["test"])
        self.split_toggle_btn.toggled.connect(self._on_split_toggled)

        self.ci_toggle_btn = RoundedButton("Show CI", 160, 60, 30)
        self.ci_toggle_btn.setCheckable(True)
        themed_add(self.ci_toggle_btn, lambda c: f"""
            QPushButton {{ font-size: 16px; }}
            QPushButton:checked {{ background: {COLORS['yellow']}; color: {COLORS['black']}; }}
        """)
        self.ci_toggle_btn.setToolTip(
            "Show a 95% confidence interval next to each value (only for "
            "models with saved test predictions, and only for metrics it "
            "can be computed for - Accuracy, R², RMSE, MAE)."
        )
        self.ci_toggle_btn.toggled.connect(self._on_ci_toggled)

        self.export_btn = make_export_button()
        self.export_btn.clicked.connect(self._on_export_clicked)

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        self.root.addLayout(title_layout)

        # Action row, centered on its own line below the title rather than
        # crammed onto the same row - with the title's own stretch on both
        # sides, a long enough action cluster made the title read as
        # off-center (dragged toward the left by everything after it).
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        actions_layout.addWidget(self.favorites_only_btn)
        actions_layout.addSpacing(10)
        actions_layout.addWidget(self.split_toggle_btn)
        actions_layout.addSpacing(10)
        actions_layout.addWidget(self.ci_toggle_btn)
        actions_layout.addSpacing(10)
        actions_layout.addWidget(self.export_btn)
        actions_layout.addStretch()
        self.root.addLayout(actions_layout)

        # PRIORITY GATE (simple mode) - shown above the table until the user
        # says what they care about; see update_ui() for the gating logic.
        self.priority_selector = MetricPrioritySelector()
        self.priority_selector.setVisible(False)
        self.priority_selector.prioritySelected.connect(self._on_priority_selected)
        # Same stretch weight as table_card below - whichever of the two is
        # actually visible gets the space the other would have, instead of
        # the priority gate sitting cramped at the top with empty page
        # underneath it.
        self.root.addWidget(self.priority_selector, stretch=10)

        # TABLE CARD

        self.table_card = QWidget()
        table_card_layout = QVBoxLayout(self.table_card)
        table_card_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setSelectionMode(QTableWidget.NoSelection)

        themed(self.table, lambda c: f"""
            QTableWidget {{
                background: {c.surface};
                color: {c.text};
                border: 2px solid {c.border};
                gridline-color: {c.border};
                font-size: 15px;
            }}

            QHeaderView::section {{
                background: {c.header_bg};
                color: {COLORS['white']};
                padding: 8px;
                font-weight: bold;
            }}
            {table_corner_qss(c)}
        """)

        # Header custom
        header = ClickableHeader(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(header)

        header.setSectionResizeMode(QHeaderView.Stretch)

        header_font = QFont("Instrument Sans", 14, QFont.Bold)
        self.table.horizontalHeader().setFont(header_font)

        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.table.cellClicked.connect(self.on_cell_clicked)

        table_card_layout.addWidget(self.table)

        # INFO BUTTON
        self.info_btn = RoundedButton("!", 50, 50, 25)
        self.info_btn.clicked.connect(self.show_popup)
        style_info_button(self.info_btn, COLORS['gray_light'])

        self.info_row = info_button_row(self.info_btn)
        self.root.addWidget(self.info_row)
        self.root.addWidget(self.table_card, stretch=10)
        self.root.addStretch(2)

    # DATA ENTRY

    def set_data(self, models, criterion, view_mode=None):
        self.models = models
        self.criterion = criterion
        self.update_ui()

    # BUILD DATA

    def _on_favorites_only_toggled(self, checked):
        self.favorites_only = checked
        self.favorites_only_btn.setText("★ Favorites only" if checked else "☆ Favorites only")
        self.update_ui()

    def _on_split_toggled(self, checked):
        self.split = "training" if checked else "test"
        self.split_toggle_btn.setText(f"{SPLIT_LABELS[self.split]} metrics")
        self.split_toggle_btn.setToolTip(SPLIT_EXPLANATIONS[self.split])
        self.update_ui()

    def _on_ci_toggled(self, checked):
        self.show_ci = checked
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
            self.table_card.setVisible(False)
            self.info_row.setVisible(False)
            return

        self.priority_selector.setVisible(False)
        self.table_card.setVisible(True)
        self.info_row.setVisible(True)

        models_to_show = [m for m in self.models if not self.favorites_only or is_favorite(m)]

        if not models_to_show:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        self.data, self.metric_names, self.metrics_keys = build_comparison_data(models_to_show, split=self.split)

        if not self.metrics_keys:
            return

        # In simple mode, rank by whatever metric answers the chosen
        # priority instead of the alphabetically-first one, when this
        # comparison set actually reports something for it.
        if not app_state.advanced_mode and self._chosen_priority_key:
            resolved = pick_priority_metric(self.metric_names, self._chosen_priority_key)
            if resolved:
                self.criterion = self.metrics_keys[self.metric_names.index(resolved)]

        if self.criterion not in self.metrics_keys:
            self.criterion = self.metrics_keys[0]

        self.sort_by(self.criterion)

        # TABLE BUILD

        # Simple mode shows only the priority metrics as columns instead of
        # every metric across the group - export/glossary still use the
        # full self.metric_names/self.metrics_keys below, unaffected.
        if app_state.advanced_mode:
            self.display_metric_names, self.display_metrics_keys = self.metric_names, self.metrics_keys
        else:
            self.display_metric_names, self.display_metrics_keys = filter_priority_metric_pairs(
                self.metric_names, self.metrics_keys
            )
            # ...and puts the chosen-priority metric first among them, if it
            # survived the filter (it always should - see filter_priority_metrics).
            if self._chosen_priority_key:
                resolved = pick_priority_metric(self.display_metric_names, self._chosen_priority_key)
                if resolved and resolved != self.display_metric_names[0]:
                    idx = self.display_metric_names.index(resolved)
                    self.display_metric_names.insert(0, self.display_metric_names.pop(idx))
                    self.display_metrics_keys.insert(0, self.display_metrics_keys.pop(idx))

        headers = ["★", "Model"] + [get_metric_info(n)["label"] for n in self.display_metric_names]

        self.table.setColumnCount(len(headers))
        self.table.setRowCount(len(self.data))
        self.table.setHorizontalHeaderLabels(headers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 60)

        # Loaded once per model here rather than once per cell - every CI-
        # supported metric column for the same model reuses the same
        # test_predictions.csv instead of re-reading it from disk each time.
        predictions_cache = {}
        if self.show_ci:
            for row in self.data:
                model_path = gmp.model_path_from_name(row["model"])
                predictions_cache[row["model"]] = gmp.load_test_predictions(model_path) if model_path else None

        for row_idx, row in enumerate(self.data):

            is_fav = is_favorite(row["model"])

            star_item = QTableWidgetItem("★" if is_fav else "☆")
            star_item.setFont(QFont("Instrument Sans", 17))
            star_item.setTextAlignment(Qt.AlignCenter)
            star_item.setFlags(star_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 0, star_item)

            item = QTableWidgetItem(row["model"])
            item.setFont(QFont("Instrument Sans", 16, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item)

            for col_idx, (metric_name, key) in enumerate(
                zip(self.display_metric_names, self.display_metrics_keys), start=2
            ):

                value = row.get(key, None)
                text = f"{value:.3f}" if isinstance(value, (int, float)) else "N/A"

                tooltip = None
                if self.show_ci and ci_is_supported(metric_name):
                    predictions_df = predictions_cache.get(row["model"])
                    if predictions_df is not None and len(predictions_df) > 0:
                        _, ci_low, ci_high = bootstrap_ci(predictions_df, metric_name)
                        if ci_low is not None:
                            text += f"  [{ci_low:.3f}–{ci_high:.3f}]"
                            tooltip = (
                                "95% confidence interval: if this model were "
                                "re-evaluated on a different sample of similar "
                                "patients, the true value would typically fall "
                                "in this range."
                            )

                item = QTableWidgetItem(text)
                item.setFont(QFont("Instrument Sans", 16))
                item.setTextAlignment(Qt.AlignCenter)
                if tooltip:
                    item.setToolTip(tooltip)

                self.table.setItem(row_idx, col_idx, item)

            self._style_favorite(row_idx, is_fav)

        self.title.setText(f"Ranking by {get_metric_info(self.criterion.split('/')[-2])['label']}")

    def _style_favorite(self, row_idx, is_fav):
        color = QColor(COLORS['yellow']) if is_fav else QColor(colors().text)
        for col_idx in (0, 1):
            item = self.table.item(row_idx, col_idx)
            if item:
                item.setForeground(color)

    def _restyle_favorites(self):
        for row_idx in range(self.table.rowCount()):
            name_item = self.table.item(row_idx, 1)
            if name_item:
                self._style_favorite(row_idx, is_favorite(name_item.text()))

    # EXPORT

    def _on_export_clicked(self):
        if not self.data:
            ErrorPopup(self, "Select some models to compare first.").show()
            return

        header = ["model"] + self.metric_names
        rows = [
            [row["model"]] + [row.get(key) for key in self.metrics_keys]
            for row in self.data
        ]
        export_chart_and_data(self, "model_comparison_table", self.table, header, rows)

    # SORT

    def sort_by(self, metric):
        self.data.sort(
            key=lambda x: x.get(metric) if isinstance(x.get(metric), (int, float)) else float("-inf"),
            reverse=True
        )

    # HEADER CLICK

    def on_header_clicked(self, column):

        idx = column - 2
        if idx < 0 or idx >= len(self.display_metrics_keys):
            return

        metric = self.display_metrics_keys[idx]
        self.criterion = metric
        self.sort_by(metric)
        self.update_ui()

    def _on_advanced_mode_changed(self, value):
        # Re-render so switching mode while a comparison is already showing
        # takes effect immediately, instead of only on the next set_data().
        self.advanced_toggle.setChecked(value)
        self.update_ui()

    def _on_priority_selected(self, key):
        self._chosen_priority_key = key
        self.update_ui()

    def on_cell_clicked(self, row, column):
        if column != 0:
            return

        model = self.data[row]["model"]
        is_fav = toggle_favorite(model)

        item = self.table.item(row, 0)
        if item:
            item.setText("★" if is_fav else "☆")

        self._style_favorite(row, is_fav)

    # RESIZE 


    # POPUP / INFO BUTTON

    def show_popup(self):
        width, height = 700, 360
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
                "The best model for the selected metric is highlighted, and "
                "columns are sortable by clicking their header."
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
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QSpinBox, QAbstractSpinBox
)
from PySide6.QtCore import Qt, QSize, QEvent
from PySide6 import QtGui, QtCore

from hamelin.interface.utils.widgets import RoundedButton, BackgroundWidget, Popup, Toast, ErrorPopup, set_asset_icon, load_app_fonts
from hamelin.interface.utils.colors import COLORS, colors, themed, themed_add
from hamelin.interface.utils.theme_state import theme_state
from hamelin.interface.utils.export import make_export_button, export_chart_and_data
from hamelin.interface.utils.favorites import is_favorite
import hamelin.interface.utils.get_model_paths as gmp
import hamelin.interface.utils.print_confusion_matrix as pcm
from hamelin.interface.widgets.dropdowns import SimpleDropdown

models = gmp.get_model_names()

# Soft blue = correct, soft red = incorrect - kept light so the .lighter()
# shading in _render_table stays readable at every ratio. Blue/red rather
# than green/red so the pair stays distinguishable for colorblind viewers.
CORRECT_COLOR = QtGui.QColor(96, 158, 224)     # soft blue
INCORRECT_COLOR = QtGui.QColor(226, 124, 118)  # soft red
EMPTY_COLOR = QtGui.QColor(255, 255, 255)


def _blend(base, top, amount):
    return QtGui.QColor(
        *(round(b + (t - b) * amount) for b, t in zip(base.getRgb()[:3], top.getRgb()[:3]))
    )

# Display names for the error browser's non-dataset columns.
COLUMN_LABELS = {
    "_true_label": "True Label",
    "_predicted_label": "Predicted Label",
    "_confidence": "Confidence",
}

# A confusion matrix only means something when rows/columns are discrete
# classes - the same allowlist one_model.py's _CLASSIFICATION_TYPES uses for
# its own classifier-only "Break down by" control. Regression ("number"/
# "vector") predictions are near-unique floats, so building one from them
# produces a huge, meaningless grid instead of raising - see
# update_confusion_matrix().
_CONFUSION_MATRIX_TYPES = {"binary", "category", "set"}


# CONFUSION MATRIX WIDGET

class ConfusionMatrixWidget(BackgroundWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        load_app_fonts()
        self.setFont(QtGui.QFont("Inter", 11))

        self.show_percentage = False
        self.popup = None
        self.error_popup = None
        self.last_labels = []
        self.last_rows = []
        self.last_matrix = None
        self._known_models = models
        self._last_model_path = None
        self.threshold_value = 0.5

        self.initUI()
        theme_state.themeChanged.connect(self._on_theme_changed)

    def initUI(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # TOP BAR

        top = QHBoxLayout()

        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        set_asset_icon(self.btn_home, "home.svg")
        self.btn_home.setIconSize(QSize(32, 32))

        top.addWidget(self.btn_home)
        top.addStretch()

        self.info_btn = RoundedButton("?", 58, 58, 29)
        self._set_info_btn_style(COLORS["gray"])
        self.info_btn.clicked.connect(self.show_help_popup)

        self.export_btn = make_export_button()
        self.export_btn.clicked.connect(self._on_export_clicked)
        top.addWidget(self.export_btn)
        top.addSpacing(10)
        top.addWidget(self.info_btn)

        layout.addLayout(top)

        # ================= TITLE =================

        self.label = QLabel("Confusion Matrix")
        self.label.setAlignment(Qt.AlignCenter)
        themed(self.label, lambda c: f"""
            background:{c.surface};
            color:{c.text};
            border: 2px solid {c.border};
            padding:14px 20px;
            font-size:40px;
            font-weight:700;
            border-radius:10px;
        """)

        title = QHBoxLayout()
        title.addStretch()
        title.addWidget(self.label)
        title.addStretch()

        layout.addLayout(title)

        # MODEL SELECTOR

        self.models_dropdown = SimpleDropdown("Select Model", models, favorite_check=is_favorite)
        

        layout.addWidget(self.models_dropdown)

        self.empty_hint = QLabel(
            "No models found in ./results. Train a Ludwig model into "
            "that folder, then reopen this page."
        )
        self.empty_hint.setAlignment(Qt.AlignCenter)
        self.empty_hint.setWordWrap(True)
        themed(self.empty_hint, lambda c: f"color:{c.muted}; font-size:18px;")
        self.empty_hint.setVisible(not models)
        layout.addWidget(self.empty_hint)

        # INFO ROW 
        # Hidden until a model is actually picked -

        self.info_row_widget = QWidget()
        self.info_row_widget.setAttribute(Qt.WA_StyledBackground, True)
        themed(self.info_row_widget, "QWidget { background: transparent; }")
        info_row = QHBoxLayout(self.info_row_widget)
        info_row.setContentsMargins(0, 0, 0, 0)
        info_row.setSpacing(16)

        self.info_card = QWidget()
        self.info_card.setObjectName("infoCard")
        self.info_card.setAttribute(Qt.WA_StyledBackground, True)
        themed(self.info_card, lambda c: f"""
            QWidget#infoCard {{
                background: {c.accent_fill};
                border: 2px solid {c.accent_edge};
                border-radius: 22px;
            }}
        """)
        info_card_layout = QVBoxLayout(self.info_card)
        info_card_layout.setContentsMargins(20, 14, 20, 14)

        self.info_label = QLabel("")
        themed(self.info_label, lambda c: f"color:{c.text}; font-size:16px; font-weight:600; background:transparent;")
        self.info_label.setWordWrap(True)
        info_card_layout.addWidget(self.info_label)

        info_row.addWidget(self.info_card, stretch=1)

        self.toggle_btn = RoundedButton("Show %", 180, 56, 28)
        themed_add(self.toggle_btn, "QPushButton{font-size:20px;}")
        self.toggle_btn.clicked.connect(self.on_toggle_display)
        info_row.addWidget(self.toggle_btn)

        self.info_row_widget.setVisible(False)
        layout.addWidget(self.info_row_widget)

        # CONDITION OF INTEREST + DECISION THRESHOLD - one row, floating
        # directly on the page background (no card behind it) like the top
        # bar's own buttons, instead of a separate light rectangle.
        #
        row = QHBoxLayout()
        row.setSpacing(10)

        # Decision threshold - only shown for a genuinely binary run with
        # saved per-class probabilities (see
        # pcm.supports_threshold_adjustment). Recomputes the matrix from
        # those saved probabilities at whatever cutoff is set, instead of
        # Ludwig's own fixed 50% default. Its own sub-widget so it can be
        # hidden independently of the rest of the page.
        self.threshold_group = QWidget()
        self.threshold_group.setAttribute(Qt.WA_StyledBackground, True)
        themed(self.threshold_group, "QWidget { background: transparent; }")
        threshold_row = QHBoxLayout(self.threshold_group)
        threshold_row.setContentsMargins(0, 0, 0, 0)
        threshold_row.setSpacing(10)

        threshold_prefix = QLabel("Decision threshold:")
        themed(threshold_prefix, lambda c: f"color:{c.text}; font-weight:600; background: transparent;")
        threshold_row.addWidget(threshold_prefix)

        # A typed integer instead of a slider - easier to set an exact
        # value, and reads as a plain input field rather than a control
        # that needs to be dragged. No up/down step buttons: NoButtons
        # drops the little unstyled arrow block Qt draws next to the field
        # by default, which didn't pick up this box's border/radius.
        self.threshold_input = QSpinBox()
        self.threshold_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.threshold_input.setRange(1, 99)
        self.threshold_input.setValue(50)
        self.threshold_input.setSuffix("%")
        self.threshold_input.setAlignment(Qt.AlignCenter)
        self.threshold_input.setCursor(Qt.PointingHandCursor)
        themed(self.threshold_input, lambda c: f"""
            QSpinBox {{
                background: {c.surface};
                color: {c.text};
                border: 2px solid {c.border};
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 15px;
                font-weight: 700;
                min-width: 70px;
            }}
        """)
        self.threshold_input.valueChanged.connect(self._on_threshold_changed)
        threshold_row.addWidget(self.threshold_input)

        row.addWidget(self.threshold_group)
        row.addStretch()

        self.condition_row_widget = QWidget()
        self.condition_row_widget.setAttribute(Qt.WA_StyledBackground, True)
        themed(self.condition_row_widget, "QWidget { background: transparent; }")
        condition_col = QVBoxLayout(self.condition_row_widget)
        condition_col.setContentsMargins(0, 8, 0, 8)
        condition_col.setSpacing(4)
        condition_col.addLayout(row)
        self.condition_row_widget.setVisible(False)
        layout.addWidget(self.condition_row_widget)

        # TABLE

        self.table = QTableWidget()
        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.table.setCursor(Qt.PointingHandCursor)
        # A selected cell would otherwise repaint in the system highlight
        # colour (orange under Hamelin) over its blue/red shading.
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.cellClicked.connect(self.on_cell_clicked)

        layout.addWidget(self.table)

        self.no_data_hint = QLabel(
            "No confusion matrix available for this model - it was saved "
            "without test predictions and its original dataset can't be "
            "found either."
        )
        self.no_data_hint.setAlignment(Qt.AlignCenter)
        self.no_data_hint.setWordWrap(True)
        themed(self.no_data_hint, lambda c: f"color:{c.muted}; font-size:18px;")
        self.no_data_hint.hide()
        layout.addWidget(self.no_data_hint)

        self.hint_label = QLabel("Click a cell to see the actual patients behind that number.")
        self.hint_label.setAlignment(Qt.AlignCenter)
        # Explicit transparent: this label sits directly on the page's own
        # light background (see the QWidget{background:gray_pale} default
        # lower down), same treatment as empty_hint / no_data_hint above.
        themed(self.hint_label, lambda c: f"color:{c.muted}; font-size:14px; font-style:italic; background: transparent;")
        self.hint_label.hide()
        layout.addWidget(self.hint_label)

        themed(self, lambda c: f"""

            QWidget {{
                background-color:{c.page};
                color:{c.text};
                font-family:'Inter';
            }}


            QTableWidget {{
                background-color:{c.surface};
                color:{c.text};
                gridline-color:{c.muted};
                border:2px solid {c.border};
                border-radius:10px;
                font-size:16px;
            }}


            QHeaderView::section {{
                background-color:{c.header_bg};
                color:{COLORS['white']};
                padding:6px;
                border:1px solid {c.muted};
                font-weight:600;
            }}


            QTableCornerButton::section {{
                background-color:{c.header_bg};
                border:1px solid {c.muted};
            }}

        """)

        self.models_dropdown.currentIndexChanged.connect(
            self.update_confusion_matrix
        )

        layout.addSpacing(10)

    def _set_info_btn_style(self, background_color):
        themed(self.info_btn, lambda c, background_color=background_color: f"""
            QPushButton {{
                font-size: 30px;
                font-weight: 700;
                background: {background_color};
                color: {COLORS['white']};
                border: none;
                border-radius: 29px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: #106EBE;
            }}
        """)

    # INFO POPUP

    def show_help_popup(self):
        if self.popup is not None:
            self.popup.close()

        self.popup = Popup(
            parent=self,
            width=760,
            height=340,
            x=(self.width() - 760) // 2 if self.width() > 760 else 20,
            y=(self.height() - 340) // 2 if self.height() > 340 else 20,
            background=COLORS["yellow"],
        )
        self.popup.installEventFilter(self)

        text = QLabel(
            "Each row is the true outcome, each column is what the model "
            "predicted. The diagonal (blue) is where the model got it "
            "right; everything off the diagonal (amber) is a mistake.\n\n"
            "Use \"Show %\" to switch between raw counts and the "
            "percentage of each row. The decision threshold is how "
            "confident the model must be before choosing an outcome - "
            "changing it moves patients from one predicted column to the "
            "other.\n\n"
            "The matrix is computed on the exact patients this model was "
            "evaluated on, shown above the table.\n\n"
            "Click any cell to see the actual patients behind that number, "
            "including how confident the model was for each one - "
            "confidence below 60% is highlighted, whether the prediction "
            "was right or wrong."
        )
        text.setWordWrap(True)
        themed(text, lambda c: f"""
            QLabel {{
                color: {c.text};
                font-size: 18px;
                font-weight: 500;
                background: transparent;
            }}
        """)

        self.popup.layout.addSpacing(40)
        self.popup.layout.addWidget(text)
        self.popup.close_btn.raise_()

        self.popup.show()

    def eventFilter(self, obj, event):
        if self.popup is not None and obj is self.popup and event.type() == QEvent.Hide:
            self._set_info_btn_style(COLORS["gray"])
        return super().eventFilter(obj, event)

    # REFRESH MODEL LIST

    def showEvent(self, event):
        super().showEvent(event)
        current_models = gmp.get_model_names()
        if current_models == self._known_models:
            self.models_dropdown.refresh_favorites()
            return
        self._known_models = current_models

        previous_selection = self.models_dropdown.get_selected()
        self.empty_hint.setVisible(not current_models)
        self.models_dropdown.clear()
        self.models_dropdown.addItems(current_models)

        if previous_selection in current_models:
            self.models_dropdown.selected = previous_selection
            self.models_dropdown._update_label()

    # TOGGLE COUNTS / PERCENTAGE

    def _on_theme_changed(self, _dark):
        if self.last_matrix is not None:
            self._render_table(self.last_labels, self.last_matrix)

    def on_toggle_display(self):
        self.show_percentage = not self.show_percentage
        self.toggle_btn.setText("Show Counts" if self.show_percentage else "Show %")
        if self.last_matrix is not None:
            self._render_table(self.last_labels, self.last_matrix)

    # DECISION THRESHOLD

    def _on_threshold_changed(self, value):
        self.threshold_value = value / 100.0
        self.update_confusion_matrix()

    # UPDATE MATRIX

    def update_confusion_matrix(self):

        model_name = self.models_dropdown.get_selected()

        if not model_name:
            return

        model_path = gmp.model_path_from_name(model_name)

        if not model_path:
            return

        is_new_selection = model_path != self._last_model_path

        # Reset to the default 50% on a genuinely new model selection - a
        # threshold chosen for the previous model carries no meaning for
        # this one. Left untouched when this call is the input itself
        # triggering a re-render for the same model.
        if is_new_selection:
            self._last_model_path = model_path
            self.threshold_input.blockSignals(True)
            self.threshold_input.setValue(50)
            self.threshold_input.blockSignals(False)
            self.threshold_value = 0.5

        # A confusion matrix only means something for discrete classes -
        # for a regression model, "predicted" is a near-unique float, so
        # sklearn's confusion_matrix() would still happily build one, just
        # as a huge grid that's essentially all zeros (see
        # _CONFUSION_MATRIX_TYPES). Catch it here instead of letting that
        # reach the table. Only the table itself is cleared - unlike the
        # no-predictions-available path below, the rest of the page (info
        # row, threshold group, title) is left exactly as laid out; toggling
        # those on top of collapsing the (large) table was enough to shift
        # the whole page's proportions, since this widget is scaled to fit
        # its host window. ErrorPopup (same "invalid action" component every
        # other page uses - landing_page.py, one_model.py, comparison.py,
        # etc.) floats via Toast's own positioning rather than a layout
        # slot, so it can't touch the rest of the page either.
        output_type = gmp.get_output_feature_info(model_path).get("type")
        if output_type and output_type not in _CONFUSION_MATRIX_TYPES:
            self.last_matrix = None
            self.last_labels = []
            self.last_rows = []
            self.clear_matrix()
            if is_new_selection:
                ErrorPopup(
                    self,
                    "This model predicts a continuous number (regression) - "
                    "a confusion matrix only applies to classification models.",
                ).show()
            return
        self.no_data_hint.setText(
            "No confusion matrix available for this model - it was saved "
            "without test predictions and its original dataset can't be "
            "found either."
        )

        threshold_supported = pcm.supports_threshold_adjustment(model_path)
        self.threshold_group.setVisible(threshold_supported)

        # get_model_dataset() reads description.json, which Ludwig only
        # writes as part of its own train()/auto_train() run output - not
        # written by LudwigModel.save() (results/models/), so this comes
        # back None for most models now. That alone used to stop this
        # whole page short - compute_confusion_matrix() only actually needs
        # it as a fallback when test_predictions.csv wasn't saved, so it's
        # still worth calling even when this is None.
        dataset_path = gmp.get_model_dataset(model_path)

        try:
            result = pcm.compute_confusion_matrix(
                model_path, dataset_path,
                threshold=self.threshold_value if threshold_supported else None,
            )
        except Exception:
            self.info_row_widget.setVisible(False)
            self.hint_label.hide()
            self.condition_row_widget.setVisible(False)
            self.threshold_group.setVisible(False)
            self.table.setVisible(False)
            self.no_data_hint.show()
            return

        self.no_data_hint.hide()
        self.table.setVisible(True)
        self.info_row_widget.setVisible(True)
        self.hint_label.show()
        self.condition_row_widget.setVisible(True)

        labels = result["labels"]
        matrix = result["matrix"]
        rows = result.get("rows", [])
        total_n = sum(sum(row) for row in matrix)

        self.last_labels = labels
        self.last_rows = rows
        self.last_matrix = matrix

        meta = gmp.get_run_metadata(model_path)
        dataset_name = meta.get("dataset_name") or "unknown dataset"
        # Plain-language stats, not "N = ..." / "X epochs" - this line has no
        # info button of its own to explain shorthand, unlike the metrics in
        # metric_labels.py (see that module's own no-jargon policy).
        self.info_label.setText(
            f"Dataset: {dataset_name}  |  {total_n} patients  |  "
            f"Ludwig {meta.get('ludwig_version') or '?'}  |  "
            f"trained through the data {meta.get('epochs_trained') or '?'} times"
        )

        self._render_table(labels, matrix)

    def _render_table(self, labels, matrix):
        self.table.setRowCount(len(labels))
        self.table.setColumnCount(len(labels))

        self.table.setVerticalHeaderLabels(labels)
        self.table.setHorizontalHeaderLabels(labels)

        font = QtGui.QFont(self.table.font())
        pal = colors()
        dark = pal.dark

        for i, row in enumerate(matrix):

            row_sum = sum(row)

            for j, value in enumerate(row):

                ratio = value / row_sum if row_sum else 0

                if self.show_percentage:
                    text = f"{ratio * 100:.1f}%"
                else:
                    text = str(value)

                item = QTableWidgetItem(text)

                base = CORRECT_COLOR if i == j else INCORRECT_COLOR
                if dark:
                    color = _blend(QtGui.QColor(pal.surface), base, 0.3 + 0.6 * ratio) if ratio else QtGui.QColor(pal.surface)
                elif ratio == 0:
                    color = EMPTY_COLOR
                else:
                    color = base.lighter(int(185 - ratio * 55))

                item.setBackground(color)

                cell_font = QtGui.QFont(font)
                cell_font.setBold(i == j)
                item.setFont(cell_font)

                foreground = QtGui.QColor(pal.text if dark else "black")
                item.setForeground(foreground)
                item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(i, j, item)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.adjust_font_sizes()


    def on_cell_clicked(self, row, col):
        if not (0 <= row < len(self.last_labels)) or not (0 <= col < len(self.last_labels)):
            return

        true_label = self.last_labels[row]
        pred_label = self.last_labels[col]

        matches = [
            r for r in self.last_rows
            if str(r.get("_true_label")) == true_label and str(r.get("_predicted_label")) == pred_label
        ]

        self.show_error_browser(true_label, pred_label, matches)

    def show_error_browser(self, true_label, pred_label, matches):
        if self.error_popup is not None:
            self.error_popup.close()

        width, height = 900, 560
        self.error_popup = Popup(
            parent=self,
            width=width,
            height=height,
            x=max((self.width() - width) // 2, 20),
            y=max((self.height() - height) // 2, 20),
        )
        self.error_popup.installEventFilter(self)

        outcome = "correct" if true_label == pred_label else "misclassified"
        header = QLabel(
            f"True: {true_label}  →  Predicted: {pred_label}   "
            f"({len(matches)} {'case' if len(matches) == 1 else 'cases'}, {outcome})"
        )
        header.setWordWrap(True)
        themed(header, lambda c: f"color:{c.text}; font-size:18px; font-weight:700; background:transparent;")

        self.error_popup.layout.addSpacing(30)
        self.error_popup.layout.addWidget(header)

        if not matches:
            empty = QLabel("No patients in this category.")
            themed(empty, lambda c: f"color:{c.muted}; font-size:16px; background:transparent;")
            self.error_popup.layout.addWidget(empty)
        else:
            input_cols = [k for k in matches[0].keys() if not k.startswith("_")][:-1]
            columns = input_cols + ["_true_label", "_predicted_label"]
            if "_confidence" in matches[0]:
                columns.append("_confidence")

            table = QTableWidget()
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setColumnCount(len(columns))
            table.setRowCount(len(matches))
            headers = [COLUMN_LABELS.get(c, c.replace("_", " ").title()) for c in columns]
            table.setHorizontalHeaderLabels(headers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            themed(table, lambda c: f"""
                QTableWidget {{
                    background:{c.surface};
                    color:{c.text};
                    gridline-color:{c.muted};
                    font-size:14px;
                }}
                QHeaderView::section {{
                    background:{c.header_bg};
                    color:{COLORS['white']};
                    padding:4px;
                    font-weight:600;
                }}
            """)

            for r, record in enumerate(matches):
                for c, key in enumerate(columns):
                    if key == "_confidence":
                        text = f"{record[key] * 100:.1f}%"
                    else:
                        text = str(record.get(key, ""))
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    if key == "_confidence" and record[key] < 0.6:
                        item.setForeground(INCORRECT_COLOR.lighter(160) if colors().dark else INCORRECT_COLOR)
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    table.setItem(r, c, item)

            self.error_popup.layout.addWidget(table, stretch=1)

        self.error_popup.close_btn.raise_()
        self.error_popup.show()

    # ADAPT FONT SIZE TABLE

    def adjust_font_sizes(self):

        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):

                item = self.table.item(i, j)

                if item:

                    font = item.font()

                    size = int(
                        min(
                            self.table.columnWidth(j),
                            self.table.rowHeight(i)
                        ) * 0.35
                    )

                    font.setPointSize(
                        max(size, 8)
                    )

                    item.setFont(font)

    # EXPORT

    def _on_export_clicked(self):
        if self.last_matrix is None or not self.last_labels:
            Toast(self, "Select a model to see its confusion matrix first.", success=False).show()
            return

        model_name = self.models_dropdown.get_selected() or "confusion_matrix"
        # CSV mirrors the on-screen grid: one row per true label, one column
        # per predicted label, plus a leading "True \\ Predicted" corner.
        header = ["True \\ Predicted"] + list(self.last_labels)
        rows = [
            [self.last_labels[i]] + list(self.last_matrix[i])
            for i in range(len(self.last_labels))
        ]
        export_chart_and_data(
            self, f"{model_name.replace('/', '_')}_confusion_matrix",
            self.table, header, rows,
        )

    # OPTIONAL RESET

    def clear_matrix(self):

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtWidgets import (
    QWidget, QLabel,
    QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractScrollArea,
    QSizePolicy, QScrollArea,
)
from PySide6.QtGui import QFont, QColor

from hamelin.interface.utils.widgets import info_button_row, RoundedButton, Popup, ErrorPopup, style_info_button, build_glossary_widget, set_asset_icon
from hamelin.interface.utils.colors import YELLOW, WHITE, BLACK, GRAY_LIGHT, INFO_YELLOW, colors, themed, themed_add, table_corner_qss
from hamelin.interface.utils.theme_state import theme_state
from hamelin.interface.utils.export import make_export_button, export_chart_and_data
import hamelin.interface.utils.get_model_paths as gmp


# Plain-language name + explanation for the config settings clinicians are
# most likely to see differ between two runs. Looked up by the setting's
# last one or two path segments (e.g. "trainer.batch_size" -> "batch_size"),
# so it still matches regardless of which section of the config it's under.
SETTING_INFO = {
    "batch_size": ("Batch Size", "How many examples the model looks at together before updating what it has learned. Smaller values update more often but can be noisier; larger values are steadier but need more memory."),
    "eval_batch_size": ("Evaluation Batch Size", "Like Batch Size, but only used while measuring performance, not while learning - so it doesn't affect training itself."),
    "effective_batch_size": ("Effective Batch Size", "The real batch size actually used once other settings are taken into account."),
    "epochs": ("Epoch Size", "How many times the model goes through the entire training dataset. More epochs means more learning, but too many can cause it to memorize instead of generalize."),
    "learning_rate": ("Learning Rate", "How big a step the model takes each time it updates what it has learned. Too high and it can overshoot; too low and training is very slow."),
    "dropout": ("Dropout", "Randomly ignores part of the model during training so it doesn't rely too heavily on any single detail. Helps prevent overfitting."),
    "early_stop": ("Early Stop Patience", "How many rounds without improvement the model tolerates before training is stopped early, to avoid wasting time once it has stopped getting better."),
    "validation_metric": ("Validation Metric", "The measurement used to decide whether the model is improving during training (e.g. accuracy or loss)."),
    "validation_field": ("Validation Field", "Which output the model is checked against to measure its progress during training."),
    "regularization_lambda": ("Regularization Strength", "How strongly the model is discouraged from becoming overly complex, which helps it generalize instead of memorizing the training data."),
    "regularization_type": ("Regularization Type", "The mathematical method used to discourage the model from becoming overly complex."),
    "weight_decay": ("Weight Decay", "A gentle penalty applied during training to keep the model's internal values small, which helps prevent overfitting."),
    "activation": ("Activation Function", "The mathematical function that decides how a layer's output responds to its input. Different choices change how the model learns patterns."),
    "num_fc_layers": ("Number of Layers", "How many extra processing layers the model uses in this part of the network."),
    "output_size": ("Output Size", "The number of values this part of the model produces to pass on to the next step."),
    "embedding_size": ("Embedding Size", "The size of the internal representation the model uses to capture the meaning of each input (like a word)."),
    "num_filters": ("Number of Filters", "How many different patterns this part of the model looks for at once."),
    "filter_size": ("Filter Size", "How large a chunk of the input the model looks at in one go when searching for patterns."),
    "pool_function": ("Pooling Method", "How the model condenses information after scanning for patterns (e.g. taking the maximum or average)."),
    "max_sequence_length": ("Max Sequence Length", "The longest input the model will read; anything beyond this length gets cut off."),
    "most_common": ("Vocabulary Size", "How many of the most frequent values (e.g. words) the model keeps track of; anything rarer gets grouped together."),
    "lowercase": ("Lowercase Text", "Whether text is converted to lowercase before the model reads it, so it doesn't treat \"Cat\" and \"cat\" as different things."),
    "tokenizer": ("Tokenizer", "The method used to split text into smaller pieces the model can understand."),
    "missing_value_strategy": ("Missing Value Strategy", "What the model does when a piece of data is missing (e.g. fill it in, or drop that row)."),
    "should_shuffle": ("Shuffle Data", "Whether the training data is mixed up in a random order before each epoch, which usually helps the model learn better."),
    "use_mixed_precision": ("Mixed Precision", "Whether the model uses a faster, lower-precision number format during training to speed things up."),
    "num_classes": ("Number of Classes", "How many different categories the model is choosing between."),
    "top_k": ("Top K", "How many of the model's best guesses are considered correct when measuring accuracy."),
    "reduce_input": ("Input Reduction", "How the model combines multiple pieces of input into a single summary before using them."),
    "reduce_output": ("Output Reduction", "How the model combines its internal results into the final output."),
    "learning_rate_scaling": ("Learning Rate Scaling", "How the Learning Rate is automatically adjusted based on the batch size."),
    "decay_rate": ("Decay Rate", "How quickly the Learning Rate shrinks over time during training."),
    "warmup_fraction": ("Warmup Fraction", "The portion of training spent gradually ramping the Learning Rate up from a small value, to stabilize early training."),
    "clipnorm": ("Gradient Clip (Norm)", "A safety limit that stops the model's updates from becoming too large all at once, which helps keep training stable."),
    "clipvalue": ("Gradient Clip (Value)", "A safety limit on the size of any single update during training, to keep learning stable."),
    "clipglobalnorm": ("Gradient Clip (Global Norm)", "A safety limit on the overall size of all updates combined during training, to keep learning stable."),
    "optimizer.type": ("Optimizer", "The algorithm the model uses to update itself as it learns from its mistakes."),
    "combiner.type": ("Combiner Type", "The method used to merge information from all inputs before making a prediction."),
    "split.type": ("Data Split Method", "How the dataset is divided into training, validation, and test portions."),
    "learning_rate_scheduler.decay": ("Learning Rate Schedule", "The pattern used to gradually change the Learning Rate over the course of training."),
}

_GENERIC_EXPLANATION = (
    "A more technical training setting - the exact value matters less than "
    "whether it's the same or different between the two runs."
)


def humanize_key(key):
    """Fallback display name for any setting not in SETTING_INFO: turns
    "trainer.some_setting" into "Some Setting", using the parent segment
    instead of a bare list index (".0") so it stays readable."""
    parts = key.split(".")
    last = parts[-1]
    index = None
    if last.isdigit() and len(parts) >= 2:
        index = int(last) + 1
        last = parts[-2]

    label = " ".join(w.capitalize() for w in last.replace("_", " ").split())
    return f"{label} #{index}" if index is not None else label


def _lookup_setting(key):
    parts = key.split(".")
    two = ".".join(parts[-2:]) if len(parts) >= 2 else None
    return SETTING_INFO.get(two) or SETTING_INFO.get(parts[-1])


def friendly_label(key):
    info = _lookup_setting(key)
    return info[0] if info else humanize_key(key)


def setting_explanation(key):
    info = _lookup_setting(key)
    return info[1] if info else _GENERIC_EXPLANATION


# MAIN WIDGET

class VisualiseConfigDiffWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model_a = None
        self.model_b = None
        self.include_defaults = False
        self.popup = None
        self.last_diffs = []

        # ROOT LAYOUT

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(40, 40, 40, 60)
        self.root.setSpacing(25)

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

        self.export_btn = make_export_button()
        self.export_btn.clicked.connect(self._on_export_clicked)

        top.addWidget(self.btn_home)
        top.addStretch()
        top.addWidget(self.export_btn)
        top.addSpacing(10)
        top.addWidget(self.btn_back)

        self.root.addLayout(top)

        # TITLE

        self.title = QLabel("Compare Settings")
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

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        self.root.addLayout(title_layout)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        themed(self.subtitle, lambda c: f"""
            background: {YELLOW};
            color: {BLACK};
            padding: 8px 60px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 10px;
        """)

        subtitle_layout = QHBoxLayout()
        subtitle_layout.addStretch()
        subtitle_layout.addWidget(self.subtitle)
        subtitle_layout.addStretch()
        self.root.addLayout(subtitle_layout)

        # TOGGLE 

        toggle_row = QHBoxLayout()
        toggle_row.addStretch()

        self.toggle_btn = RoundedButton("Show all settings", 280, 60, 30)
        themed_add(self.toggle_btn, "QPushButton{font-size:18px;}")
        self.toggle_btn.clicked.connect(self.on_toggle_defaults)
        toggle_row.addWidget(self.toggle_btn)

        self.root.addLayout(toggle_row)

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
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        themed(self.table, lambda c: f"""
            QTableWidget {{
                background: {c.surface};
                color: {c.text};
                border: 2px solid {c.border};
                gridline-color: {c.border};
                font-size: 16px;
            }}

            QHeaderView::section {{
                background: {c.header_bg};
                color: {WHITE};
                padding: 8px;
                font-weight: bold;
            }}
            {table_corner_qss(c)}
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        theme_state.themeChanged.connect(self._restyle_key_column)

        table_card_layout.addWidget(self.table)

        # INFO BUTTON
        self.info_btn = RoundedButton("!", 50, 50, 25)
        self.info_btn.clicked.connect(self.show_popup)
        style_info_button(self.info_btn, GRAY_LIGHT)

        self.info_row = info_button_row(self.info_btn)
        self.root.addWidget(self.info_row)
        self.root.addWidget(self.table_card, stretch=10)

        # EMPTY / STATUS LABEL

        self.empty_label = QLabel("")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        themed(self.empty_label, f"color: {WHITE}; font-size: 20px; font-weight: 600;")
        self.empty_label.hide()
        self.root.addWidget(self.empty_label)

    # DATA ENTRY

    def set_data(self, model_a, model_b):
        self.model_a = model_a
        self.model_b = model_b
        self.update_ui()

    def _on_export_clicked(self):
        if not self.last_diffs:
            ErrorPopup(self, "Pick two models with differing settings first.").show()
            return

        header = ["Setting", self.model_a or "A", self.model_b or "B"]
        rows = [
            (friendly_label(d["key"]),
             "" if d["value_a"] is None and d["only_in"] == "b" else d["value_a"],
             "" if d["value_b"] is None and d["only_in"] == "a" else d["value_b"])
            for d in self.last_diffs
        ]
        name = f"config_diff_{(self.model_a or 'a')}_{(self.model_b or 'b')}".replace("/", "_")
        export_chart_and_data(self, name, self.table, header, rows)

    def on_toggle_defaults(self):
        self.include_defaults = not self.include_defaults
        self.toggle_btn.setText(
            "Hide default settings" if self.include_defaults else "Show all settings"
        )
        self.update_ui()

    # BUILD TABLE

    def update_ui(self):
        if not self.model_a or not self.model_b:
            return

        self.subtitle.setText(f"{self.model_a}   vs.   {self.model_b}")

        path_a = gmp.model_path_from_name(self.model_a)
        path_b = gmp.model_path_from_name(self.model_b)

        if not path_a or not path_b:
            self._show_empty("Could not load one of the selected models.")
            return

        diffs = gmp.diff_configs(path_a, path_b, include_defaults=self.include_defaults)
        self.last_diffs = diffs

        if not diffs:
            self._show_empty(
                "These two runs have identical settings."
            )
            return

        self.empty_label.hide()
        self.table.show()

        headers = ["Setting", self.model_a, self.model_b]
        self.table.setColumnCount(3)
        self.table.setRowCount(len(diffs))
        self.table.setHorizontalHeaderLabels(headers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 180)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        for row_idx, d in enumerate(diffs):
            key_item = QTableWidgetItem(friendly_label(d["key"]))
            key_item.setToolTip(d["key"])
            key_item.setFont(QFont("Instrument Sans", 14, QFont.Bold))
            key_item.setTextAlignment(Qt.AlignCenter)
            key_item.setBackground(QColor(colors().header_bg))
            key_item.setForeground(QColor(WHITE))
            self.table.setItem(row_idx, 0, key_item)

            a_text = self._format_value(d["value_a"], d["only_in"] == "b")
            b_text = self._format_value(d["value_b"], d["only_in"] == "a")

            a_item = QTableWidgetItem(a_text)
            a_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, a_item)

            b_item = QTableWidgetItem(b_text)
            b_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, b_item)

    def _restyle_key_column(self):
        for row_idx in range(self.table.rowCount()):
            item = self.table.item(row_idx, 0)
            if item:
                item.setBackground(QColor(colors().header_bg))

    def _format_value(self, value, absent):
        if absent:
            return "— (not set)"
        return str(value)

    def _show_empty(self, text):
        self.last_diffs = []
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.table.hide()
        self.empty_label.setText(text)
        self.empty_label.show()


    # POPUP / INFO BUTTON

    def _build_settings_explanation_entries(self):
        seen = set()
        entries = []
        for d in self.last_diffs:
            label = friendly_label(d["key"])
            if label in seen:
                continue
            seen.add(label)
            entries.append({"label": label, "text": setting_explanation(d["key"]), "priority": False})
        return entries

    def show_popup(self):
        if self.popup is not None:
            self.popup.close()

        self.popup = Popup(
            parent=self,
            x=max((self.width() - 700) // 2, 20),
            y=max((self.height() - 460) // 2, 20),
            width=700,
            height=460,
            background=YELLOW,
        )
        self.popup.installEventFilter(self)

        entries = self._build_settings_explanation_entries()
        content = build_glossary_widget(
            entries,
            intro="Here's a quick explanation of the settings shown in the table:",
            empty_text="No settings to explain yet, select two models to compare.",
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        themed(scroll, "QScrollArea { background: transparent; }")
        scroll.setWidget(content)

        self.popup.layout.addSpacing(20)
        self.popup.layout.addWidget(scroll)
        self.popup.close_btn.raise_()
        self.popup.show()

        style_info_button(self.info_btn, INFO_YELLOW, text_color=BLACK)

    def eventFilter(self, obj, event):
        if self.popup is not None and obj is self.popup and event.type() == QEvent.Hide:
            style_info_button(self.info_btn, GRAY_LIGHT)
        return super().eventFilter(obj, event)

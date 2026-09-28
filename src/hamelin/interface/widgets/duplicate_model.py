from PySide6.QtCore import QSize, Qt, QEvent, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout,
    QSizePolicy, QSlider,
)
import math

from hamelin.interface.utils.widgets import RoundedButton, Popup, ErrorPopup, AdvancedModeToggle, set_asset_icon
from hamelin.interface.utils.colors import BLACK, BLUE, YELLOW, WHITE, GRAY_LIGHT, INFO_YELLOW, themed, themed_add
from hamelin.interface.utils.app_state import app_state
from hamelin.interface.widgets.dropdowns import SimpleDropdown
from hamelin.interface.widgets.visualise_config_diff import friendly_label, setting_explanation
from hamelin.interface.utils.metrix_extractor import load_run_metrics
from hamelin.interface.utils.favorites import is_favorite
import hamelin.interface.utils.get_model_paths as gmp


# Curated, trainer-level knobs a clinician-facing "duplicate with different
# params" flow makes sense for. Kept narrow and flat (no per-feature/encoder
# settings) so it stays a handful of fields instead of the ~50 keys a full
# config exposes, and so the same setting name can't appear twice for
# different features with no way to tell which is which.
EDITABLE_SETTINGS = [
    "trainer.epochs",
    "trainer.batch_size",
    "trainer.learning_rate",
    "trainer.early_stop",
    "trainer.regularization_lambda",
    "combiner.dropout",
]

# Practical "when would I actually touch this" guidance, on top of
# setting_explanation()'s plain-language definition of what the setting is.
# Aimed at someone deciding how to retrain based on how the original run
# behaved, not at explaining Ludwig's config format.
TUNING_ADVICE = {
    "trainer.epochs": (
        "Raise this if test performance was still improving when training "
        "stopped. Lower it if the model kept training well after it had "
        "already plateaued."
    ),
    "trainer.batch_size": (
        "Lower this on a small dataset, it usually generalizes a bit better. "
        "Raise it mainly if training felt unstable or very slow."
    ),
    "trainer.learning_rate": (
        "Lower this if training looked unstable (loss jumping around). "
        "Raise it only if training seemed painfully slow to improve at all."
    ),
    "trainer.early_stop": (
        "Raise this if training stopped too early while metrics were still "
        "improving. Lower it to avoid wasting time once it plateaus quickly."
    ),
    "trainer.regularization_lambda": (
        "Raise this if test performance was clearly worse than training "
        "performance (the model was memorizing instead of learning)."
    ),
    "combiner.dropout": (
        "Raise this for the same overfitting symptom as above (good on "
        "training data, worse on test). Lower it if the model underfit both."
    ),
}


# Bounded range for each editable setting's slider, so a beginner can't
# type in a wild/invalid value by accident - "kind" picks how the slider's
# raw integer position maps to the actual value:
#   "int"   - slider bounds are the value bounds directly, 1 step = 1 unit.
#   "float" - slider runs 0..SLIDER_RESOLUTION, mapped linearly onto range.
#   "log"   - same, but mapped on a log10 scale (for learning rate, which
#             matters in orders of magnitude, not linear steps).
SLIDER_RESOLUTION = 1000

SETTING_RANGES = {
    "trainer.epochs": {"kind": "int", "min": 1, "max": 200},
    "trainer.batch_size": {"kind": "int", "min": 1, "max": 256},
    "trainer.learning_rate": {"kind": "log", "min": 1e-5, "max": 1e-1},
    "trainer.early_stop": {"kind": "int", "min": 1, "max": 50},
    "trainer.regularization_lambda": {"kind": "float", "min": 0.0, "max": 1.0},
    "combiner.dropout": {"kind": "float", "min": 0.0, "max": 0.9},
}

# Simple-mode "what do you want to try?" options, translated into deltas on
# the same EDITABLE_SETTINGS applied via _apply_suggestion. Scaled to match
# the deltas _diagnose_model already uses for its suggestion cards (dropout
# +-0.15, regularization_lambda +-0.02/0.03, epochs +-10/15, early_stop
# +-3/5) - a first-pass heuristic, not a clinically validated mapping.
SIMPLE_MODE_OPTIONS = [
    {
        "key": "boost_recall",
        "label": "Improve case detection",
        "changes": {
            "trainer.epochs": 15,
            "trainer.early_stop": 5,
            "trainer.regularization_lambda": -0.02,
            "combiner.dropout": -0.1,
        },
    },
    {
        "key": "boost_precision",
        "label": "Reduce false alarms",
        "changes": {
            "trainer.regularization_lambda": 0.03,
            "combiner.dropout": 0.15,
        },
    },
    {
        "key": "keep_as_is",
        "label": "Keep the same settings",
        "changes": {},
    },
]


def _slider_to_value(spec, pos):
    if spec["kind"] == "int":
        return pos
    t = pos / SLIDER_RESOLUTION
    if spec["kind"] == "log":
        lo, hi = math.log10(spec["min"]), math.log10(spec["max"])
        return 10 ** (lo + t * (hi - lo))
    return spec["min"] + t * (spec["max"] - spec["min"])


def _value_to_slider(spec, value):
    value = max(spec["min"], min(spec["max"], value))
    if spec["kind"] == "int":
        return round(value)
    if spec["kind"] == "log":
        lo, hi = math.log10(spec["min"]), math.log10(spec["max"])
        t = (math.log10(value) - lo) / (hi - lo)
    else:
        t = (value - spec["min"]) / (spec["max"] - spec["min"])
    return round(t * SLIDER_RESOLUTION)


def _format_value(spec, value):
    if spec["kind"] == "int":
        return str(int(round(value)))
    return f"{value:.5g}"


def _find_metric(metrics, split, metric_name):
    """First numeric value found for e.g. split='test', metric_name='accuracy'
    among flat keys like 'test/sentiment/accuracy/best'."""
    for key, value in metrics.items():
        parts = key.split("/")
        if len(parts) >= 3 and parts[0] == split and parts[-2] == metric_name and isinstance(value, (int, float)):
            return value
    return None


def _diagnose_model(model):
    """Best-effort, heuristic read of the source model's train vs test
    accuracy to suggest which knob is actually worth touching, instead of
    leaving a beginner to guess. Silently returns nothing if the run
    doesn't have both splits recorded - a missing nudge, not a wrong one."""
    metrics = load_run_metrics(model) or {}
    train_acc = _find_metric(metrics, "train", "accuracy")
    test_acc = _find_metric(metrics, "test", "accuracy")

    suggestions = []

    if train_acc is not None and test_acc is not None and (train_acc - test_acc) > 0.08:
        suggestions.append({
            "text": (
                "Training accuracy is a lot higher than test accuracy - "
                "this model may have overfit (memorized the training data "
                "instead of learning general patterns). Recommended: raise "
                "dropout and regularization."
            ),
            "button": "Apply recommended changes",
            "changes": {"combiner.dropout": 0.15, "trainer.regularization_lambda": 0.02},
        })

    if test_acc is not None and test_acc < 0.65:
        suggestions.append({
            "text": (
                "Test accuracy is pretty low - this model may not have had "
                "enough training. Recommended: raise the training epochs and "
                "early-stop patience."
            ),
            "button": "Apply recommended changes",
            "changes": {"trainer.epochs": 10, "trainer.early_stop": 3},
        })

    return suggestions


def _set_nested(config, dotted_key, value):
    parts = dotted_key.split(".")
    node = config
    for p in parts[:-1]:
        node = node[int(p)] if p.isdigit() and isinstance(node, list) else node[p]
    last = parts[-1]
    if last.isdigit() and isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value


class DuplicateModelWidget(QWidget):

    # Handed to a training page when the user confirms a duplicate:
    # {"based_on", "new_run_name", "config"}. Nothing is written to disk -
    # the new run is only persisted if/when the user actually trains it,
    # same as any other model.
    open_training_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.source_model = None
        self.source_config = None
        self.fields = {}
        self.value_labels = {}
        self.info_buttons = {}
        self._popup = None
        self._active_info_btn = None
        self._available_settings = []
        self._original_values = {}
        self._simple_selected_key = None

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(40, 40, 40, 40)
        self.root.setSpacing(20)

        # TOP BAR
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
        app_state.advancedModeChanged.connect(self._on_advanced_mode_changed)
        top.addWidget(self.advanced_toggle)

        top.addWidget(self.btn_back)
        self.root.addLayout(top)

        # TITLE
        self.title = QLabel("Duplicate a Model")
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

        # CONTENT (capped width so it doesn't stretch edge to edge on wide windows)
        content_wrapper = QWidget()
        content_wrapper.setMaximumWidth(1100)
        content_wrapper.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # SOURCE MODEL PICKER
        self.model_dropdown = SimpleDropdown("Select a model to duplicate", [], favorite_check=is_favorite)
        self.model_dropdown.currentIndexChanged.connect(self._on_model_selected)
        content_layout.addWidget(self.model_dropdown)

        # SUGGESTIONS (shown only when the source model's train/test metrics
        # hint at something worth tweaking - see _diagnose_model)
        self.suggestions_box = QWidget()
        self.suggestions_layout = QVBoxLayout(self.suggestions_box)
        self.suggestions_layout.setContentsMargins(0, 0, 0, 0)
        self.suggestions_layout.setSpacing(8)
        self.suggestions_box.hide()
        content_layout.addWidget(self.suggestions_box)

        # EDITABLE SETTINGS
        self.form_card = QWidget()
        self.form_card.setAttribute(Qt.WA_StyledBackground, True)
        themed(self.form_card, lambda c: f"""
            QWidget {{
                background: {c.surface};
                border-radius: 16px;
            }}
        """)
        self.form_layout = QVBoxLayout(self.form_card)
        self.form_layout.setContentsMargins(24, 20, 24, 20)
        self.form_layout.setSpacing(16)

        self.empty_label = QLabel("Select a model above to see its editable settings.")
        themed(self.empty_label, lambda c: f"color: {c.muted}; font-size: 16px;")
        self.form_layout.addWidget(self.empty_label)

        content_layout.addWidget(self.form_card, stretch=1)

        # SIMPLE MODE
        self.simple_flow_card = QWidget()
        self.simple_flow_card.setAttribute(Qt.WA_StyledBackground, True)
        themed(self.simple_flow_card, lambda c: f"""
            QWidget {{
                background: {c.surface};
                border-radius: 16px;
            }}
        """)
        simple_layout = QVBoxLayout(self.simple_flow_card)
        simple_layout.setContentsMargins(24, 20, 24, 20)
        simple_layout.setSpacing(16)

        question_label = QLabel("What would you like to try?")
        themed(question_label, lambda c: f"color: {c.text}; font-size: 18px; font-weight: 700;")
        simple_layout.addWidget(question_label)

        self._simple_option_cards = {}
        for option in SIMPLE_MODE_OPTIONS:
            card = self._build_simple_option_card(option)
            self._simple_option_cards[option["key"]] = card
            simple_layout.addWidget(card)

        content_layout.addWidget(self.simple_flow_card, stretch=1)

        # NEW RUN NAME
        name_row = QHBoxLayout()
        name_label = QLabel("New model name:")
        themed(name_label, f"color: {WHITE}; font-size: 18px; font-weight: 600;")
        self.new_name_edit = QLineEdit()
        themed(self.new_name_edit, lambda c: f"""
            QLineEdit {{
                background: {c.surface};
                color: {c.text};
                border: 2px solid {c.border};
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 16px;
            }}
        """)
        name_row.addWidget(name_label)
        name_row.addWidget(self.new_name_edit, stretch=1)
        content_layout.addLayout(name_row)

        content_row = QHBoxLayout()
        content_row.addStretch()
        content_row.addWidget(content_wrapper, stretch=1)
        content_row.addStretch()
        self.root.addLayout(content_row, stretch=1)

        # CONTINUE TO TRAINING
        continue_row = QHBoxLayout()
        continue_row.addStretch()
        self.continue_btn = RoundedButton("Continue to Training", 360, 72, 36)
        self.continue_btn.clicked.connect(self._on_continue_clicked)
        continue_row.addWidget(self.continue_btn)
        continue_row.addStretch()
        self.root.addLayout(continue_row)

        self._apply_mode_visibility()

    def showEvent(self, event):
        super().showEvent(event)
        self.model_dropdown.clear()
        self.model_dropdown.addItems(gmp.get_model_names())

    def _on_model_selected(self):
        model = self.model_dropdown.currentText()
        if not model:
            self.suggestions_box.hide()
            return

        self.source_model = model
        path = gmp.model_path_from_name(model)
        self.source_config = gmp.get_model_config(path) if path else {}
        flat = gmp.flatten_config(self.source_config)

        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.fields = {}
        self.value_labels = {}
        self.info_buttons = {}
        self._active_info_btn = None

        available = [k for k in EDITABLE_SETTINGS if k in flat]

        if not available:
            self.empty_label = QLabel("No editable settings found for this model.")
            themed(self.empty_label, lambda c: f"color: {c.muted}; font-size: 16px;")
            self.form_layout.addWidget(self.empty_label)
        else:
            for key in available:
                self.form_layout.addWidget(self._build_setting_row(key, flat[key]))

        self._populate_suggestions(model, available)

        self.new_name_edit.setText(f"{model}_copy")
        self._available_settings = available
        self._original_values = {k: flat[k] for k in available}
        self._reset_simple_flow()
        self._apply_mode_visibility()

    # SIMPLE / ADVANCED MODE

    def _apply_mode_visibility(self):
        advanced = app_state.advanced_mode
        self.form_card.setVisible(advanced)
        self.simple_flow_card.setVisible(not advanced)

    def _on_advanced_mode_changed(self, value):
        self.advanced_toggle.setChecked(value)
        self._apply_mode_visibility()

    # SIMPLE MODE FLOW

    def _build_simple_option_card(self, option):
        card = QWidget()
        card.setCursor(Qt.PointingHandCursor)
        # Without this, some platform styles (GTK-integrated ones in
        # particular) paint their own native panel/frame chrome underneath
        # the QSS border below, on top of it, showing up as a doubled
        # border - this forces Qt's stylesheet engine to own the whole box
        # (background + border) instead of falling through to that.
        card.setAttribute(Qt.WA_StyledBackground, True)
        self._style_simple_card(card, selected=False)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)

        label = QLabel(option["label"])
        label.setWordWrap(True)
        # card's own stylesheet (QWidget { border: Npx solid ...; ... })
        # cascades to descendant QWidgets that don't override border
        # themselves - without this, this label inherited that border and
        # showed as a second frame drawn tightly around the text.
        themed(label, lambda c: f"color: {c.text}; font-size: 15px; font-weight: 600; background: transparent; border: none;")
        layout.addWidget(label)

        card.mousePressEvent = lambda event, key=option["key"]: self._on_simple_option_clicked(key)
        return card

    def _style_simple_card(self, card, selected):
        # 2px even when unselected, not 1px - a hairline border is the most
        # likely to visually "double" under fractional display scaling
        # (Qt has to round 1 logical px onto a non-integer count of
        # physical pixels); a thicker line is far less prone to that.
        width = 3 if selected else 2
        themed(card, lambda c, selected=selected, width=width: f"""
            QWidget {{
                background: {c.page};
                border: {width}px solid {BLUE if selected else c.line};
                border-radius: 10px;
            }}
        """)

    def _on_simple_option_clicked(self, key):
        self._simple_selected_key = key
        for k, card in self._simple_option_cards.items():
            self._style_simple_card(card, selected=(k == key))

        option = next(o for o in SIMPLE_MODE_OPTIONS if o["key"] == key)
        self._reset_fields_to_original()
        self._apply_suggestion(option["changes"])

        self._apply_mode_visibility()

    def _reset_fields_to_original(self):
        for key, slider in self.fields.items():
            if key in self._original_values:
                spec = SETTING_RANGES[key]
                slider.setValue(_value_to_slider(spec, self._original_values[key]))

    def _reset_simple_flow(self):
        self._simple_selected_key = None
        for card in self._simple_option_cards.values():
            self._style_simple_card(card, selected=False)

    def _populate_suggestions(self, model, available_keys):
        while self.suggestions_layout.count():
            item = self.suggestions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        suggestions = [
            s for s in _diagnose_model(model)
            if set(s["changes"]) & set(available_keys)
        ]
        self.suggestions_box.setVisible(bool(suggestions))

        for s in suggestions:
            card = QWidget()
            card.setAttribute(Qt.WA_StyledBackground, True)
            themed(card, f"QWidget {{ background: {YELLOW}; border-radius: 10px; }}")
            row = QHBoxLayout(card)
            row.setContentsMargins(14, 10, 14, 10)
            row.setSpacing(12)

            text = QLabel(s["text"])
            text.setWordWrap(True)
            themed(text, f"color: {BLACK}; font-size: 14px; background: transparent;")
            row.addWidget(text, stretch=1)

            apply_btn = RoundedButton(s["button"], 280, 44, 22)
            themed_add(apply_btn, lambda c, apply_btn=apply_btn: "QPushButton{font-size:13px;}")
            apply_btn.clicked.connect(lambda _checked=False, changes=s["changes"]: self._apply_suggestion(changes))
            row.addWidget(apply_btn)

            self.suggestions_layout.addWidget(card)

    def _apply_suggestion(self, changes):
        for key, delta in changes.items():
            slider = self.fields.get(key)
            if slider is None:
                continue
            spec = SETTING_RANGES[key]
            current = _slider_to_value(spec, slider.value())
            slider.setValue(_value_to_slider(spec, current + delta))

    def _build_setting_row(self, key, current_value):
        spec = SETTING_RANGES[key]

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        label = QLabel(friendly_label(key))
        themed(label, lambda c: f"color: {c.text}; font-size: 16px; font-weight: 600;")
        label.setMinimumWidth(200)

        slider = QSlider(Qt.Horizontal)
        if spec["kind"] == "int":
            slider.setMinimum(spec["min"])
            slider.setMaximum(spec["max"])
        else:
            slider.setMinimum(0)
            slider.setMaximum(SLIDER_RESOLUTION)
        slider.setValue(_value_to_slider(spec, current_value))
        themed(slider, lambda c: f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {c.line};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {BLUE};
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
        """)

        value_label = QLabel(_format_value(spec, current_value))
        value_label.setMinimumWidth(70)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        themed(value_label, lambda c: f"color: {c.text}; font-size: 15px; font-weight: 600;")

        def _on_changed(pos, spec=spec, value_label=value_label):
            value_label.setText(_format_value(spec, _slider_to_value(spec, pos)))

        slider.valueChanged.connect(_on_changed)

        self.fields[key] = slider
        self.value_labels[key] = value_label

        info_btn = RoundedButton("!", 38, 38, 19)
        self._style_info_btn(info_btn, GRAY_LIGHT)
        info_btn.setToolTip(f"Why would I change {friendly_label(key)}?")
        info_btn.clicked.connect(lambda _checked=False, k=key: self._show_setting_popup(k))
        self.info_buttons[key] = info_btn

        row_layout.addWidget(label)
        row_layout.addWidget(slider, stretch=1)
        row_layout.addWidget(value_label)
        row_layout.addWidget(info_btn)

        return row

    def _style_info_btn(self, btn, background_color):
        themed(btn, lambda c, background_color=background_color: f"""
            QPushButton {{
                font-size: 18px;
                font-weight: 700;
                background: {background_color};
                color: {BLACK};
                border: none;
                border-radius: 19px;
                padding: 0;
            }}
        """)

    def _show_setting_popup(self, key):
        if self._popup is not None:
            self._popup.close()
        if self._active_info_btn is not None:
            self._style_info_btn(self._active_info_btn, GRAY_LIGHT)
            self._active_info_btn = None

        width, height = 560, 260
        self._popup = Popup(
            parent=self,
            x=max((self.width() - width) // 2, 20),
            y=max((self.height() - height) // 2, 20),
            width=width,
            height=height,
            background=YELLOW,
        )
        self._popup.installEventFilter(self)

        advice = TUNING_ADVICE.get(key, "")

        title = QLabel(friendly_label(key))
        title.setWordWrap(True)
        themed(title, lambda c: f"color: {c.text}; font-size: 15px; font-weight: 700; background: transparent;")

        explanation = QLabel(setting_explanation(key))
        explanation.setWordWrap(True)
        themed(explanation, lambda c: f"color: {c.text}; font-size: 15px; background: transparent;")

        advice_label = QLabel(f"When to change it: {advice}")
        advice_label.setWordWrap(True)
        themed(advice_label, lambda c: f"color: {c.text}; font-size: 15px; font-style: italic; background: transparent;")

        self._popup.layout.addSpacing(20)
        self._popup.layout.addWidget(title)
        self._popup.layout.addWidget(explanation)
        self._popup.layout.addWidget(advice_label)
        self._popup.close_btn.raise_()
        self._popup.show()

        self._active_info_btn = self.info_buttons.get(key)
        if self._active_info_btn is not None:
            self._style_info_btn(self._active_info_btn, INFO_YELLOW)

    def eventFilter(self, obj, event):
        if self._popup is not None and obj is self._popup and event.type() == QEvent.Hide:
            if self._active_info_btn is not None:
                self._style_info_btn(self._active_info_btn, GRAY_LIGHT)
                self._active_info_btn = None
        return super().eventFilter(obj, event)

    def _on_continue_clicked(self):
        if not self.source_model:
            ErrorPopup(self, "Please select a model first.").show()
            return

        new_name = self.new_name_edit.text().strip()
        if not new_name:
            ErrorPopup(self, "Give the new run a name first.").show()
            return

        import copy
        new_config = copy.deepcopy(self.source_config)

        for key, slider in self.fields.items():
            spec = SETTING_RANGES[key]
            value = _slider_to_value(spec, slider.value())
            if spec["kind"] == "int":
                value = int(round(value))
            _set_nested(new_config, key, value)

        self.open_training_requested.emit({
            "based_on": self.source_model,
            "new_run_name": new_name,
            "config": new_config,
        })

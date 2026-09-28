"""
Model Training Page
~~~~~~~~~~~~~~~~~~~

AutoML model configuration and training interface.
"""

import json
import re
import time
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea,
    QListWidget, QTextEdit, QCheckBox, QButtonGroup, QFileDialog
)
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget,
    PushButton, ComboBox, SpinBox, DoubleSpinBox, LineEdit,
    FluentIcon, ProgressBar, IndeterminateProgressBar, SwitchButton, RadioButton,
    InfoBar, InfoBarPosition
)

from hamelin.analytics.automl.base import AutoMLResult
from hamelin.analytics.ludwig_trainer import LudwigTrainerWorker
from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets import HelpButton, ModelHistoryWidget, ModelResultsWidget, PageHelpButton, TrainingTimelineWidget, attach_help_popup, attach_help_popup_hover
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style, colors, isDarkTheme, list_item_qss, on_theme_changed, scrollbar_qss
from hamelin.view.widgets.rule_builder import RuleBuilder
from hamelin.i18n import t


# ---------------------------------------------------------------------------
# Status colour mapping — used by _set_status()
# ---------------------------------------------------------------------------
# Saturated colours read fine on both a light and dark background as-is;
# only the two grey states are swapped for the theme's own muted text
# colour (see _status_style()) for the same contrast the rest of the
# app's secondary text gets.
_STATUS_STYLES: dict[str, str] = {
    "no_data":   "color: #808080;",   # grey  — no dataset loaded
    "ready":     "color: #0078D4;",   # blue  — ready to start
    "training":  "color: #FF8C00;",   # orange — training in progress
    "done":      "color: #107C10;",   # green — completed successfully
    "error":     "color: #D13438;",   # red   — failed
    "cancelled": "color: #808080;",   # grey  — stopped by user
}
_GREY_STATES = {"no_data", "cancelled"}


def _status_style(state: str) -> str:
    if state in _GREY_STATES:
        return f"color: {colors().text_secondary};"
    return _STATUS_STYLES.get(state, _STATUS_STYLES["no_data"])


# ---------------------------------------------------------------------------
# Model-configuration dropdowns: (i18n label key, stable value) pairs, in
# display order. The stable value is what reaches the Ludwig backend; the
# visible label is translated and must never be read back for logic - use
# the combo's currentIndex() against these lists instead.
# ---------------------------------------------------------------------------
_PROBLEM_TYPES = [
    ("training.problemtype.classification.binary", "binary"),
    ("training.problemtype.classification.multi", "category"),
    ("training.problemtype.regression", "number"),
]

# Minimum gap enforced between one Ludwig run ending and the next one
# starting - see _last_training_end_ts's docstring in __init__ for why.
_MIN_RESTART_GAP_S = 3.0
# Valid validation_metric values per Ludwig output-feature type (Ludwig
# docs: configuration/features/{binary,category,number}_features.md,
# "Metrics" section of each). Picking a metric outside its type's list
# makes every training/hyperopt trial fail identically - "f1" was dropped
# entirely since it isn't a documented Ludwig metric for any output type.
_METRICS_BY_TYPE = {
    "binary": [
        ("training.metric.auc", "roc_auc"),
        ("training.metric.accuracy", "accuracy"),
        ("training.metric.precision", "precision"),
        ("training.metric.recall", "recall"),
    ],
    "category": [
        ("training.metric.accuracy", "accuracy"),
    ],
    "number": [
        ("training.metric.rmse", "root_mean_squared_error"),
        ("training.metric.mae", "mean_absolute_error"),
    ],
}
_SEARCH_STRATEGIES = [
    ("training.strategy.none", "none"),
    ("training.strategy.random", "random"),
    ("training.strategy.bayesian", "bayesian"),
    ("training.strategy.exhaustive", "exhaustive"),
]


class TrainingPage(QWidget):
    """
    Model training and configuration page.
    
    Sections:
    1. Variable Selection (target + features)
    2. Study Criteria (inclusion/exclusion)
    3. Model Configuration (type, metrics, CV)
    4. Hyperparameter Optimization
    5. Training Control & Results
    """

    # Emitted after a successful training run (AutoMLResult payload).
    training_finished = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TrainingPage")
        self._data_model = None
        self._project_dir = None          # set by MainWindow via set_project_dir()
        self._trainer_worker = None       # active LudwigTrainerWorker or None
        self._last_result: AutoMLResult | None = None  # last finished training result
        # Set right after a Ludwig run ends (success, error or cancel) - see
        # _start_training()'s guard just below _MIN_RESTART_GAP_S's
        # definition for why: Ray's shutdown at the end of one run and its
        # re-init at the start of the next have been observed to race,
        # crashing the whole app outright ("Can't find actor ... it's from
        # a different cluster", then a native abort Python can't catch) if
        # the next run starts within a second or two of the last one
        # finishing - most likely a user clicking Start again right as the
        # button re-enables, before Ray's background processes from the
        # just-finished run have actually torn down.
        self._last_training_end_ts: float = 0.0
        # Fixed Ludwig config staged by prefill_from_config() (the "duplicate
        # a model" flow). While set, the next "Start training" trains with it
        # directly instead of letting AutoML pick the architecture.
        self._pending_config: dict | None = None
        # Target / predictors that staged config wants selected. Kept apart
        # so set_data_model() can re-apply them after it rebuilds the pickers
        # - the dataset is usually loaded *after* the duplicate hand-off,
        # which would otherwise wipe the selection.
        self._pending_target: str = ""
        self._pending_features: list[str] = []
        log.debug("Initializing Training Page")
        self._init_ui()

    def _add_form_row(self, form: QFormLayout, label_text: str, widget) -> None:
        label = BodyLabel(label_text)
        bind_style(label, lambda c: f"color: {c.text_primary};")
        form.addRow(label, widget)

    def _init_ui(self):
        """Initialize user interface"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Scroll content
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title
        title_row = QHBoxLayout()
        title = TitleLabel(t("training.title"))
        title.setAlignment(Qt.AlignLeft)
        title_row.addWidget(title)
        title_row.addWidget(PageHelpButton(t("training.help"), self))
        title_row.addStretch()
        main_layout.addLayout(title_row)

        # Subtitle
        subtitle = StrongBodyLabel(t("training.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        main_layout.addWidget(subtitle)

        # Persistent notice shown while a "duplicate a model" config is
        # staged: makes it obvious the next run bypasses AutoML, and lets
        # the user drop back to a normal run.
        self._pending_banner = QWidget()
        self._pending_banner.setObjectName("pendingConfigBanner")
        bind_style(
            self._pending_banner,
            lambda c: (
                "#pendingConfigBanner { "
                f"background: {'#4D3B14' if isDarkTheme() else '#FFF4E5'}; "
                f"border: 1px solid {'#8A6D2F' if isDarkTheme() else '#F0C27B'};"
                " border-radius: 8px; }"
            ),
        )
        banner_row = QHBoxLayout(self._pending_banner)
        banner_row.setContentsMargins(14, 10, 14, 10)
        banner_row.setSpacing(12)
        self._pending_banner_label = BodyLabel(t("training.duplicate.banner"))
        self._pending_banner_label.setWordWrap(True)
        banner_row.addWidget(self._pending_banner_label, 1)
        self._pending_banner_cancel = PushButton(t("training.duplicate.banner.cancel"))
        self._pending_banner_cancel.clicked.connect(self._on_cancel_pending_clicked)
        banner_row.addWidget(self._pending_banner_cancel)
        self._pending_banner.setVisible(False)
        main_layout.addWidget(self._pending_banner)

        # 1. Variable Selection Card
        
        variables_card = CardWidget()
        variables_layout = QVBoxLayout(variables_card)
        variables_layout.setContentsMargins(20, 20, 20, 20)
        variables_layout.setSpacing(15)
        
        # Section header with help
        title_row = QHBoxLayout()
        variables_title = StrongBodyLabel(t("training.section.variables"))
        title_row.addWidget(variables_title)
        help_btn = HelpButton(t("help.training.variables"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        variables_layout.addLayout(title_row)
        
        # Primary variable (outcome)
        primary_form = QFormLayout()
        primary_form.setSpacing(10)
        
        self.primary_combo = ComboBox()
        self.primary_combo.setPlaceholderText(t("training.placeholder.outcome"))
        self._add_form_row(primary_form, t("training.label.outcome.full"), self.primary_combo)
        
        variables_layout.addLayout(primary_form)
        
        # Feature variables
        features_label = BodyLabel(t("training.label.predictors"))
        variables_layout.addWidget(features_label)
        
        self.features_list = QListWidget()
        self.features_list.setMaximumHeight(150)
        self.features_list.setSelectionMode(QListWidget.MultiSelection)
        # Hover, not click (attach_help_popup_hover, not attach_help_popup) -
        # clicking an item in this list is how you select/deselect it, so a
        # click-triggered popup fired on every single one of those instead
        # of just an incidental first click.
        attach_help_popup_hover(
            self.features_list,
            "Select predictor variables (features). Use 'Select all' as a shortcut, then deselect irrelevant fields."
        )
        variables_layout.addWidget(self.features_list)

        select_all_predictors_btn = PushButton(t("training.btn.select_all_predictors"), self)
        select_all_predictors_btn.clicked.connect(self._select_all_predictors)
        variables_layout.addWidget(select_all_predictors_btn)

        # Secondary outcomes (optional) — show presets / mapping
        secondary_label = BodyLabel(t("training.label.secondary_outcomes"))
        variables_layout.addWidget(secondary_label)

        self.secondary_list = QListWidget()
        self.secondary_list.setMaximumHeight(120)
        self.secondary_list.setSelectionMode(QListWidget.MultiSelection)
        variables_layout.addWidget(self.secondary_list)

        # Explicit, readable item text colour - a plain QListWidget has no
        # qfluentwidgets theming of its own and falls back to Qt's
        # inherited palette, which can leave item text invisible against
        # its own row. Alternating row shades match style_table_widget's
        # zebra striping for visual consistency with every table in the
        # app, and the scroll bar matches every other scrollable area.
        self.features_list.setAlternatingRowColors(True)
        self.secondary_list.setAlternatingRowColors(True)

        def _apply_list_theme() -> None:
            qss = list_item_qss(f"color: {colors().text_primary};") + scrollbar_qss()
            self.features_list.setStyleSheet(qss)
            self.secondary_list.setStyleSheet(qss)

        on_theme_changed(_apply_list_theme)

        main_layout.addWidget(variables_card)
        
        # Study Criteria Card
        criteria_card = CardWidget()
        criteria_layout = QVBoxLayout(criteria_card)
        criteria_layout.setContentsMargins(20, 20, 20, 20)
        criteria_layout.setSpacing(15)
        
        # Section header with help
        title_row = QHBoxLayout()
        criteria_title = StrongBodyLabel(t("training.section.criteria"))
        title_row.addWidget(criteria_title)
        help_btn = HelpButton(t("help.training.criteria"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        criteria_layout.addLayout(title_row)
        
        # Inclusion criteria
        inclusion_label = BodyLabel(t("training.label.inclusion"))
        criteria_layout.addWidget(inclusion_label)
        
        # Inclusion rule builder (visual)
        self.inclusion_builder = RuleBuilder(columns=[], parent=self)
        attach_help_popup(
            self.inclusion_builder,
            "Add inclusion rules visually (column + operator + value).\n"
            "Click Preview to see matches and sample rows."
        )
        criteria_layout.addWidget(self.inclusion_builder)
        
        # Exclusion criteria
        exclusion_label = BodyLabel(t("training.label.exclusion"))
        criteria_layout.addWidget(exclusion_label)
        
        # Exclusion rule builder (visual)
        self.exclusion_builder = RuleBuilder(columns=[], parent=self)
        attach_help_popup(
            self.exclusion_builder,
            "Add exclusion rules visually (column + operator + value).\n"
            "Click Preview to see remaining matches and sample rows."
        )
        criteria_layout.addWidget(self.exclusion_builder)

        # Controls: Save/Reset preset and mapping options
        controls_row = QHBoxLayout()
        self.save_preset_btn = PushButton(t("training.btn.save_preset") if hasattr(t,'training') else "Save preset", self)
        self.save_preset_btn.clicked.connect(self._on_save_preset)
        controls_row.addWidget(self.save_preset_btn)

        self.reset_preset_btn = PushButton(t("training.btn.reset_preset") if hasattr(t,'training') else "Reset preset", self)
        self.reset_preset_btn.clicked.connect(self._on_reset_preset)
        controls_row.addWidget(self.reset_preset_btn)

        controls_row.addStretch()
        criteria_layout.addLayout(controls_row)

        # Patient count
        patient_count_label = BodyLabel(t("training.label.patients.count"))
        bind_style(patient_count_label, lambda c: f"color: {c.text_secondary};")
        criteria_layout.addWidget(patient_count_label)

        # Connect preview actions: when dataset available, preview builders
        self.inclusion_builder.preview_btn.clicked.connect(lambda: self._preview_rules(mode='include'))
        self.exclusion_builder.preview_btn.clicked.connect(lambda: self._preview_rules(mode='exclude'))
        
        main_layout.addWidget(criteria_card)
        
        # 3. Model Configuration Card — merged with what used to be a
        # separate "Advanced Configuration" card (see _toggle_hyperopt).
        # Only Prediction type and Time budget stay always visible: they're
        # the two settings a non-technical user can reason about directly
        # ("what am I predicting" / "how long can this take"). Everything
        # else - metric choice, CV folds, holdout %, random seed, class
        # imbalance handling, feature engineering, search strategy,
        # iteration/trial counts - is genuinely more ML-technical, so it
        # all lives behind one real collapsible "Advanced" toggle instead
        # of being split across a non-collapsible "Advanced Options" label
        # and a separately-collapsible "Advanced Configuration" card,
        # which looked like two different things but only one of them
        # actually collapsed.
        model_card = CardWidget()
        model_layout = QVBoxLayout(model_card)
        model_layout.setContentsMargins(20, 20, 20, 20)
        model_layout.setSpacing(15)

        # Section header with help + the single "Advanced" toggle
        title_row = QHBoxLayout()
        model_title = StrongBodyLabel(t("training.section.config"))
        title_row.addWidget(model_title)
        help_btn = HelpButton(t("help.training.config"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        self._hyperopt_toggle_btn = PushButton(t("training.btn.show.options"), self)
        self._hyperopt_toggle_btn.clicked.connect(self._toggle_hyperopt)
        title_row.addWidget(self._hyperopt_toggle_btn)
        model_layout.addLayout(title_row)

        # Always visible
        basic_form = QFormLayout()
        basic_form.setSpacing(12)

        # Model name - required (see _start_training's validation below).
        # What the checkpoint folder gets named (see _sanitize_model_name),
        # so it's what shows up wherever a model gets picked by name later
        # (Dashboard history, the "interface" comparison tool) instead of
        # an opaque auto-generated ID.
        self.model_name_edit = LineEdit()
        self._add_form_row(basic_form, t("training.label.modelname"), self.model_name_edit)

        # Problem type
        self.problem_type_combo = ComboBox()
        self.problem_type_combo.addItems([t(label) for label, _ in _PROBLEM_TYPES])
        self._add_form_row(basic_form, t("training.label.predictiontype"), self.problem_type_combo)

        # Evaluation metric - options depend on the selected problem type
        # (see _METRICS_BY_TYPE's docstring), refreshed by
        # _on_problem_type_changed() below.
        self.metric_combo = ComboBox()
        self._current_metrics: list[tuple[str, str]] = []
        self._add_form_row(basic_form, t("training.label.evaluationmetric"), self.metric_combo)

        model_layout.addLayout(basic_form)

        # Collapsible "Advanced" content (hidden by default)
        self._hyperopt_content = QWidget()
        hyperopt_content_layout = QVBoxLayout(self._hyperopt_content)
        hyperopt_content_layout.setContentsMargins(0, 10, 0, 0)
        hyperopt_content_layout.setSpacing(12)

        advanced_form = QFormLayout()
        advanced_form.setSpacing(12)

        # Time budget
        self.time_budget = SpinBox()
        self.time_budget.setRange(5, 1440)
        self.time_budget.setValue(60)
        self.time_budget.setSuffix(" minutes")
        self._add_form_row(advanced_form, t("training.label.timebudget"), self.time_budget)

        # Test split
        self.test_split = DoubleSpinBox()
        self.test_split.setRange(0.1, 0.5)
        self.test_split.setValue(0.2)
        self.test_split.setSingleStep(0.05)
        self.test_split.setSuffix(" (20%)")
        self._add_form_row(advanced_form, t("training.label.testsplit"), self.test_split)

        # Random seed
        self.random_seed = SpinBox()
        self.random_seed.setRange(0, 999999)
        self.random_seed.setValue(42)
        self._add_form_row(advanced_form, t("training.label.randomseed"), self.random_seed)

        # Optimization strategy
        self.hyperopt_strategy = ComboBox()
        self.hyperopt_strategy.addItems([t(label) for label, _ in _SEARCH_STRATEGIES])
        self._add_form_row(advanced_form, t("training.label.strategy"), self.hyperopt_strategy)

        # Number of trials
        self.hyperopt_trials = SpinBox()
        self.hyperopt_trials.setRange(10, 500)
        self.hyperopt_trials.setValue(50)
        self._add_form_row(advanced_form, t("training.label.maxiterations"), self.hyperopt_trials)

        # Parallelization
        self.parallel_trials = SpinBox()
        self.parallel_trials.setRange(1, 16)
        self.parallel_trials.setValue(4)
        self._add_form_row(advanced_form, t("training.label.paralleltrials"), self.parallel_trials)

        hyperopt_content_layout.addLayout(advanced_form)

        # Switches — each gets its own static label. SwitchButton's own
        # .setText() only sets what's currently displayed; the widget
        # overwrites it with "On"/"Off" the moment it's toggled (see
        # SwitchButton._updateText, wired to the indicator's toggled
        # signal), so it can't carry a permanent category name by itself.
        balance_row = QHBoxLayout()
        balance_row.addWidget(BodyLabel(t("training.label.imbalance")))
        self.class_balance_switch = SwitchButton()
        balance_row.addWidget(self.class_balance_switch)
        balance_row.addStretch()
        hyperopt_content_layout.addLayout(balance_row)

        # Evaluation metric options and class-imbalance handling both
        # depend on the problem type (Ludwig docs: oversample_minority is
        # only supported for binary output features - configuration/
        # preprocessing.md, "Data Balancing").
        self.problem_type_combo.currentIndexChanged.connect(self._on_problem_type_changed)
        self._on_problem_type_changed()

        features_row = QHBoxLayout()
        features_row.addWidget(BodyLabel(t("training.label.meanimpute")))
        self.mean_impute_switch = SwitchButton()
        features_row.addWidget(self.mean_impute_switch)
        features_row.addStretch()
        hyperopt_content_layout.addLayout(features_row)

        self._hyperopt_content.setVisible(False)
        model_layout.addWidget(self._hyperopt_content)

        self.model_card = model_card
        main_layout.addWidget(model_card)
        # Step 4 header
        step4_label = BodyLabel("Step 4 — Model configuration: choose problem type, metrics and CV")
        bind_style(step4_label, lambda c: f"font-weight:600; color: {c.text_primary};")
        attach_help_popup(step4_label, "Adjust model settings. Defaults come from presets but are editable by the clinician or data scientist.")
        self._step4_label = step4_label
        main_layout.addWidget(step4_label)
        
        # 5. Training Control Card
        training_card = CardWidget()
        training_layout = QVBoxLayout(training_card)
        training_layout.setContentsMargins(20, 20, 20, 20)
        training_layout.setSpacing(15)
        
        # Section header with help
        title_row = QHBoxLayout()
        training_title = StrongBodyLabel(t("training.section.control"))
        title_row.addWidget(training_title)
        help_btn = HelpButton(t("help.training.control"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        training_layout.addLayout(title_row)
        
        # Training buttons
        control_buttons = QHBoxLayout()
        control_buttons.setSpacing(10)
        
        self.start_training_btn = PushButton(t("training.btn.start"), self)
        self.start_training_btn.setIcon(FluentIcon.PLAY)
        self.start_training_btn.setEnabled(False)  # enabled once data is loaded
        self.start_training_btn.clicked.connect(self._start_training)
        control_buttons.addWidget(self.start_training_btn)
        
        self.stop_training_btn = PushButton(t("training.btn.stop"), self)
        self.stop_training_btn.setIcon(FluentIcon.CLOSE)
        self.stop_training_btn.setEnabled(False)
        self.stop_training_btn.clicked.connect(self._stop_training)
        control_buttons.addWidget(self.stop_training_btn)

        self.import_config_btn = PushButton(t("training.btn.import_config"), self)
        self.import_config_btn.setIcon(FluentIcon.FOLDER)
        attach_help_popup(
            self.import_config_btn,
            "Train using a fixed Ludwig config from a JSON file instead of "
            "letting AutoML pick the architecture - e.g. a config exported "
            "by the 'duplicate this model with different hyperparameters' tool."
        )
        self.import_config_btn.clicked.connect(self._on_import_config_clicked)
        control_buttons.addWidget(self.import_config_btn)

        control_buttons.addStretch()
        
        training_layout.addLayout(control_buttons)
        
        # Progress indicators: determinate bar (idle/done) + indeterminate (running)
        self.training_progress = ProgressBar()
        self.training_progress.setValue(0)
        self.training_progress.setTextVisible(True)
        training_layout.addWidget(self.training_progress)

        self._training_spinner = IndeterminateProgressBar(self)
        self._training_spinner.setVisible(False)
        self._training_spinner.stop()
        training_layout.addWidget(self._training_spinner)

        # Status label
        self.status_label = BodyLabel(t("training.status.nodata"))
        self._status_state = "no_data"
        on_theme_changed(lambda: self.status_label.setStyleSheet(_status_style(self._status_state)))
        training_layout.addWidget(self.status_label)

        # Model results widget (KPI cards + charts + interpretation)
        self._results_widget = ModelResultsWidget(self)
        training_layout.addWidget(self._results_widget)

        # Training history widgets (Sprint 3)
        self._history_widget = ModelHistoryWidget(self)
        training_layout.addWidget(self._history_widget)

        self._timeline_widget = TrainingTimelineWidget(metric="accuracy", parent=self)
        training_layout.addWidget(self._timeline_widget)

        # Export model button
        export_model_btn = PushButton(t("training.btn.export"), self)
        export_model_btn.setIcon(FluentIcon.SAVE)
        export_model_btn.clicked.connect(self._export_model)
        training_layout.addWidget(export_model_btn)
        
        main_layout.addWidget(training_card)
        
        # Set scroll content
        scroll.setWidget(content)
        # Make the scroll area transparent so the app's real (theme-aware)
        # background shows through instead of QScrollArea's own opaque,
        # theme-blind palette background.
        apply_scroll_area_theme(scroll)
        content.setStyleSheet("background: transparent;")

        # Page layout
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
        log.debug("Training Page initialized successfully")

    def _on_problem_type_changed(self) -> None:
        """Refresh the Evaluation Metric options and the Class Imbalance
        switch for the newly selected problem type - both are type-specific
        in Ludwig, not universal (see _METRICS_BY_TYPE and the
        class_balance_switch guard below)."""
        problem_type = _PROBLEM_TYPES[self.problem_type_combo.currentIndex()][1]

        self._current_metrics = _METRICS_BY_TYPE[problem_type]
        self.metric_combo.blockSignals(True)
        self.metric_combo.clear()
        self.metric_combo.addItems([t(label) for label, _ in self._current_metrics])
        self.metric_combo.blockSignals(False)

        # Ludwig docs (configuration/preprocessing.md, "Data Balancing"):
        # dataset balancing is only supported for binary output features.
        is_binary = problem_type == "binary"
        self.class_balance_switch.setEnabled(is_binary)
        if not is_binary:
            self.class_balance_switch.setChecked(False)
            self.class_balance_switch.setToolTip(
                "Class balancing is only supported for binary outcomes in Ludwig."
            )
        else:
            self.class_balance_switch.setToolTip("")

    def hideEvent(self, event):
        super().hideEvent(event)
        # Left the page from inside the app (not a window minimise, which is
        # spontaneous): a staged "duplicate a model" config shouldn't linger
        # and hijack an unrelated later run.
        if not event.spontaneous() and self._pending_config is not None:
            self._clear_pending_config()

    def _on_cancel_pending_clicked(self) -> None:
        usage_log.event("Training", "click", "Cancel Duplicated Config button")
        self._clear_pending_config()

    def _select_all_predictors(self) -> None:
        usage_log.event("Training", "click", "Select All Predictors button")
        for i in range(self.features_list.count()):
            self.features_list.item(i).setSelected(True)

    def set_data_model(self, dm) -> None:
        """Receive a loaded DataModel and populate variable selectors."""
        self._data_model = dm
        if dm is None or dm.df is None:
            self.primary_combo.clear()
            self.features_list.clear()
            self.start_training_btn.setEnabled(False)
            self._set_status("no_data", t("training.status.nodata"))
            return
        # Use the active dataframe (applies excluded rows/columns)
        active_df = dm.get_active_df()
        columns = list(active_df.columns)
        self.primary_combo.clear()
        self.primary_combo.addItems(columns)
        self.features_list.clear()
        self.features_list.addItems(columns)
        # Populate secondary outcomes list with available columns (can be mapped from presets)
        try:
            self.secondary_list.clear()
            self.secondary_list.addItems(columns)
        except Exception:
            pass
        # Enable training only if active dataframe has rows
        self.start_training_btn.setEnabled(len(active_df) > 0)
        self._set_status("ready", f"Ready to train — {len(active_df)} rows, {len(columns)} variables loaded")
        log.info(f"Training page updated with {len(columns)} columns from data model")
        # update rule builders with current columns
        try:
            self.inclusion_builder.set_columns(columns)
            self.exclusion_builder.set_columns(columns)
        except Exception:
            pass
        # If the data model contains a previously saved project_state, apply it
        try:
            state = getattr(dm, 'project_state', None)
            if state:
                # primary outcome
                po = state.get('primary_outcome')
                if po:
                    # po may be dict or string
                    po_label = po.get('label') if isinstance(po, dict) else str(po)
                    try:
                        idx = self.primary_combo.findText(po_label)
                        if idx >= 0:
                            self.primary_combo.setCurrentIndex(idx)
                    except Exception:
                        pass
                # selected features
                sf = state.get('selected_features')
                if sf and isinstance(sf, list):
                    try:
                        # clear selection first
                        self.features_list.clearSelection()
                        for i in range(self.features_list.count()):
                            it = self.features_list.item(i)
                            if it.text() in sf:
                                it.setSelected(True)
                    except Exception:
                        pass
                # selected secondary outcomes
                so = state.get('secondary_outcomes') or state.get('secondary')
                if so and isinstance(so, list):
                    try:
                        # clear selection first
                        self.secondary_list.clearSelection()
                        for i in range(self.secondary_list.count()):
                            it = self.secondary_list.item(i)
                            if it.text() in so:
                                it.setSelected(True)
                    except Exception:
                        pass
                # inclusion/exclusion rules
                inc = state.get('inclusion_rules') or state.get('inclusion_criteria')
                exc = state.get('exclusion_rules') or state.get('exclusion_criteria')
                try:
                    if inc and isinstance(inc, list):
                        self.inclusion_builder.set_rules(inc)
                    if exc and isinstance(exc, list):
                        self.exclusion_builder.set_rules(exc)
                except Exception:
                    pass
        except Exception:
            pass

        # A staged "duplicate a model" config wins over project_state: its
        # target/predictors are what the user just chose to reproduce.
        self._apply_pending_selection()

        # Connect change signals to persist user choices
        try:
            self.primary_combo.currentIndexChanged.connect(lambda _: self._save_project_state())
            self.features_list.itemSelectionChanged.connect(lambda: self._save_project_state())
            self.inclusion_builder.rules_changed.connect(lambda: self._save_project_state())
            self.exclusion_builder.rules_changed.connect(lambda: self._save_project_state())
        except Exception:
            pass

    def _save_project_state(self) -> None:
        """Collect UI choices and save them into the project_state.json via DataModel."""
        try:
            if self._data_model is None or self._project_dir is None:
                return
            extra: dict = {}
            # primary outcome
            try:
                po = self.primary_combo.currentText().strip()
                if po:
                    extra['primary_outcome'] = po
            except Exception:
                pass
            # selected features
            try:
                sel = [self.features_list.item(i).text() for i in range(self.features_list.count()) if self.features_list.item(i).isSelected()]
                extra['selected_features'] = sel
            except Exception:
                pass
            # selected secondary outcomes
            try:
                sec = [self.secondary_list.item(i).text() for i in range(self.secondary_list.count()) if self.secondary_list.item(i).isSelected()]
                extra['secondary_outcomes'] = sec
            except Exception:
                pass
            # rules
            try:
                extra['inclusion_rules'] = self.inclusion_builder.get_rules()
            except Exception:
                extra['inclusion_rules'] = []
            try:
                extra['exclusion_rules'] = self.exclusion_builder.get_rules()
            except Exception:
                extra['exclusion_rules'] = []

            # Delegate to DataModel
            try:
                self._data_model.save_state(self._project_dir, extra_state=extra)
            except Exception:
                log.warning("Failed to save project state from TrainingPage")
        except Exception:
            pass

    def _preview_rules(self, mode: str = 'include') -> None:
        """Run preview of the inclusion/exclusion rules against active df."""
        usage_log.event("Training", "click", f"Preview {'Inclusion' if mode == 'include' else 'Exclusion'} Rules button")
        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title="No dataset",
                content="Load a dataset first to preview rules.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            return
        active = self._data_model.get_active_df()
        if mode == 'include':
            self.inclusion_builder.preview_with_df(active, mode='include')
        else:
            self.exclusion_builder.preview_with_df(active, mode='exclude')

    def _select_all_features(self):
        pass

    def _deselect_all_features(self):
        pass

    def _toggle_hyperopt(self):
        """Toggle visibility of the advanced hyperparameter optimization section."""
        usage_log.event("Training", "click", "Advanced Options toggle")
        visible = not self._hyperopt_content.isVisible()
        self._hyperopt_content.setVisible(visible)
        self._hyperopt_toggle_btn.setText(
            t("training.btn.hide.options") if visible else t("training.btn.show.options")
        )
        log.debug(f"Hyperopt section {'expanded' if visible else 'collapsed'}")

    # ------------------------------------------------------------------
    # Project wiring
    # ------------------------------------------------------------------

    def set_project_dir(self, project_dir) -> None:
        """Receive the active project directory from MainWindow."""
        from pathlib import Path
        self._project_dir = Path(project_dir) if project_dir else None
        log.debug(f"TrainingPage: project_dir set to {self._project_dir}")
        # Populate presets combo from training_schemas folder if available
        try:
            if hasattr(self, 'preset_combo'):
                self.preset_combo.clear()
                if self._project_dir is not None:
                    schema_dir = self._project_dir / 'training_schemas'
                    if schema_dir.exists() and schema_dir.is_dir():
                        json_files = sorted([p.name for p in schema_dir.iterdir() if p.suffix.lower() == '.json'])
                        for jf in json_files:
                            self.preset_combo.addItem(jf)
                        log.debug(f"Loaded {len(json_files)} training presets from {schema_dir}")
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not populate presets combo: {exc}")


    def _set_status(self, state: str, message: str = "") -> None:
        """Update status label text and colour for the given state.

        Parameters
        ----------
        state:
            One of the keys in ``_STATUS_STYLES``
            (no_data / ready / training / done / error / cancelled).
        message:
            Optional override text.  When empty the previous text is kept.
        """
        self._status_state = state
        self.status_label.setStyleSheet(_status_style(state))
        if message:
            self.status_label.setText(message)
        log.debug(f"TrainingPage status → {state!r}: {message!r}")

    # ------------------------------------------------------------------
    # Preset handling (import / preview / apply)
    # ------------------------------------------------------------------

    def _on_preview_preset(self) -> None:
        """Load the selected preset JSON and show it in the preview box."""
        if self._project_dir is None:
            InfoBar.warning(title="No project", content="Open a project first.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        if not hasattr(self, 'preset_combo'):
            InfoBar.warning(title="Presets disabled", content="Preset preview is not available.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        name = self.preset_combo.currentText().strip()
        if not name:
            InfoBar.warning(title="No preset selected", content="Choose a preset from the dropdown.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        path = self._project_dir / 'training_schemas' / name
        try:
            text = path.read_text(encoding='utf-8')
            # pretty-print JSON if possible
            import json as _json
            try:
                obj = _json.loads(text)
                pretty = _json.dumps(obj, indent=2, ensure_ascii=False)
            except Exception:
                pretty = text
            self.preset_preview.setPlainText(pretty)
            InfoBar.success(title="Preset loaded", content=f"Previewing {name}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not load preset {path}: {exc}")
            InfoBar.error(title="Load failed", content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

    def _on_apply_preset(self) -> None:
        """Apply preset to Training UI: fill inclusion/exclusion and set primary outcome if possible."""
        if self._project_dir is None:
            InfoBar.warning(title="No project", content="Open a project first.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        if not hasattr(self, 'preset_combo'):
            InfoBar.warning(title="Presets disabled", content="Applying presets is not available.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        name = self.preset_combo.currentText().strip()
        if not name:
            InfoBar.warning(title="No preset selected", content="Choose a preset from the dropdown.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        path = self._project_dir / 'training_schemas' / name
        try:
            obj = json.loads(path.read_text(encoding='utf-8'))
            # Populate inclusion/exclusion rule builders
            inc = obj.get('inclusion_criteria', [])
            exc = obj.get('exclusion_criteria', [])
            inc_rules = []
            for i in inc:
                col = i.get('column')
                op = i.get('op')
                val = i.get('value')
                if col and op is not None:
                    # format value for display (strings quoted)
                    v = f"'{val}'" if isinstance(val, str) and not (str(val).startswith('[') and str(val).endswith(']')) else str(val)
                    inc_rules.append(f"{col} {op} {v}")
                else:
                    # fallback to label/description
                    lbl = i.get('label') or i.get('description') or str(i)
                    inc_rules.append(lbl)
            exc_rules = []
            for e in exc:
                col = e.get('column')
                op = e.get('op')
                val = e.get('value')
                if col and op is not None:
                    v = f"'{val}'" if isinstance(val, str) and not (str(val).startswith('[') and str(val).endswith(']')) else str(val)
                    exc_rules.append(f"{col} {op} {v}")
                else:
                    lbl = e.get('label') or e.get('description') or str(e)
                    exc_rules.append(lbl)
            try:
                self.inclusion_builder.set_rules(inc_rules)
                self.exclusion_builder.set_rules(exc_rules)
            except Exception:
                # As a fallback, show textual preview
                self.preset_preview.setPlainText('\n'.join(inc_rules + [''] + exc_rules))
            # Set primary outcome if derivation label exists and is a column
            po = obj.get('primary_outcome')
            if po:
                po_label = po.get('label') if isinstance(po, dict) else str(po)
                # If label matches column name, select it in combo
                if self._data_model is not None and po_label in list(self._data_model.df.columns):
                    idx = self.primary_combo.findText(po_label)
                    if idx >= 0:
                        self.primary_combo.setCurrentIndex(idx)
                else:
                    # If not a column, show a message for clinician to map it manually
                    InfoBar.info(title="Primary outcome", content=f"Preset primary outcome: {po_label}. Map it to a dataset column if needed.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=self)
            # Set secondary outcomes if present in preset
            sos = obj.get('secondary_outcomes') or obj.get('secondary') or []
            if sos and isinstance(sos, list):
                parsed = []
                for s in sos:
                    if isinstance(s, dict):
                        lbl = s.get('label') or s.get('column') or s.get('name')
                    else:
                        lbl = str(s)
                    if lbl:
                        parsed.append(lbl)
                # Populate secondary_list items if available, and select matches
                try:
                    # ensure list contains items (may have been populated from dataset columns in set_data_model)
                    if self.secondary_list.count() == 0 and self._data_model is not None and self._data_model.df is not None:
                        cols = list(self._data_model.df.columns)
                        self.secondary_list.addItems(cols)
                    # select matching items
                    self.secondary_list.clearSelection()
                    for i in range(self.secondary_list.count()):
                        it = self.secondary_list.item(i)
                        if it.text() in parsed:
                            it.setSelected(True)
                except Exception:
                    # fallback: show in preset preview
                    try:
                        self.preset_preview.append('\nSecondary outcomes:\n' + '\n'.join(parsed))
                    except Exception:
                        pass
            InfoBar.success(title="Preset applied", content=f"Applied {name}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not apply preset {path}: {exc}")
            InfoBar.error(title="Apply failed", content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

    def _on_preview_derived_csv(self) -> None:
        """Preview the derived CSV specified by common default location or preset export setting."""
        if self._project_dir is None:
            InfoBar.warning(title="No project", content="Open a project first.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        # Try default derived path
        default_path = self._project_dir / 'data' / 'UPS-BaseComplete_derived.csv'
        if default_path.exists():
            try:
                import pandas as _pd
                df = _pd.read_csv(default_path, low_memory=False)
                sample = df.head(8).to_string(index=False)
                dlg = QFileDialog(self)
                # show sample in preset_preview for quick inspection
                if hasattr(self, 'preset_preview'):
                    self.preset_preview.setPlainText(sample)
                else:
                    InfoBar.success(title="Derived CSV preview", content=f"Showing first rows of {default_path.name}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
                return
            except Exception as exc:  # noqa: BLE001
                log.warning(f"Could not preview derived CSV: {exc}")
                InfoBar.error(title="Preview failed", content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)
                return
        InfoBar.warning(title="No derived CSV", content=f"No derived CSV found at {default_path}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

    def _on_save_preset(self) -> None:
        """Save current UI settings as a preset JSON in training_schemas."""
        usage_log.event("Training", "click", "Save Preset button")
        if self._project_dir is None:
            InfoBar.warning(title="No project", content="Open a project first.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        # ask for filename (default folder training_schemas)
        schema_dir = self._project_dir / 'training_schemas'
        schema_dir.mkdir(exist_ok=True)
        name, ok = QInputDialog.getText(self, 'Preset name', 'Enter preset filename (without .json):')
        if not ok or not name:
            return
        fname = (schema_dir / f"{name}.json").resolve()

        # build basic preset from UI
        preset = {
            'metadata': {
                'study_id': name,
                'title': name,
                'version': '1.0'
            },
            'inclusion_criteria': [],
            'exclusion_criteria': [],
            'primary_outcome': None,
        }

        # parse inclusion/exclusion from rule builders
        try:
            inc_rules = self.inclusion_builder.get_rules()
            exc_rules = self.exclusion_builder.get_rules()
        except Exception:
            inc_rules = []
            exc_rules = []
        for r in inc_rules:
            preset['inclusion_criteria'].append({ 'label': r, 'description': r, 'rule': r })
        for r in exc_rules:
            preset['exclusion_criteria'].append({ 'label': r, 'description': r, 'rule': r })

        # primary outcome mapping
        target = self.primary_combo.currentText().strip()
        if target:
            preset['primary_outcome'] = { 'label': target, 'derivation': f"column:{target}", 'type': 'binary' }

        # write JSON
        try:
            import json as _json
            fname.write_text(_json.dumps(preset, indent=2, ensure_ascii=False), encoding='utf-8')
            # refresh preset combo if UI present
            if hasattr(self, 'preset_combo'):
                try:
                    self.preset_combo.addItem(fname.name)
                except Exception:
                    pass
            InfoBar.success(title="Preset saved", content=f"Saved {fname.name}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            log.info(f"Preset saved to {fname}")
            usage_log.event("Training", "saved", "Preset", fname.name)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not save preset {fname}: {exc}")
            InfoBar.error(title="Save failed", content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

    def _on_reset_preset(self) -> None:
        """Reset inclusion/exclusion editors and primary selection to empty/defaults."""
        usage_log.event("Training", "click", "Reset Preset button")
        try:
            self.inclusion_builder.set_rules([])
            self.exclusion_builder.set_rules([])
        except Exception:
            pass
        self.preset_preview.clear()
        # do not change primary combo selection automatically
        InfoBar.info(title="Reset", content="Cleared inclusion/exclusion fields.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=2500, parent=self)

    # ------------------------------------------------------------------
    # Training workflow
    # ------------------------------------------------------------------

    def prefill_from_config(self, payload: dict) -> None:
        """Stage a Ludwig config handed over by the interface dashboard's
        "duplicate a model" flow: fill in the model name, pick the target
        and predictor variables the config names, and arm the next
        "Start training" press to train with this exact config instead of
        letting AutoML choose. Nothing is written to disk here - the run is
        only persisted once the user actually trains it, same as any model."""
        config = payload.get("config", payload) if isinstance(payload, dict) else {}
        self._pending_config = config or None

        name = (payload.get("new_run_name") or "").strip() if isinstance(payload, dict) else ""
        if name:
            self.model_name_edit.setText(name)

        target = ""
        for feat in config.get("output_features", []):
            target = feat.get("column") or feat.get("name") or ""
            if target:
                break
        self._pending_target = target
        self._pending_features = list(self._features_from_config(config, target))
        self._apply_pending_selection()
        self._update_pending_config_ui()

        based_on = payload.get("based_on") if isinstance(payload, dict) else None
        status = t("training.status.duplicate_loaded")
        if based_on:
            status = f"{status} ({based_on})"
        self._set_status("ready", status)
        InfoBar.success(
            title=t("training.duplicate.infobar.title"),
            content=t("training.duplicate.infobar.body"),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=6000, parent=self,
        )

    def _apply_pending_selection(self) -> None:
        """(Re-)select the staged target + predictors in the variable pickers,
        for whichever of them the currently loaded dataset actually has.
        Called right after prefill_from_config() and again after
        set_data_model() rebuilds the pickers, so loading the dataset later
        doesn't lose the duplicated model's choices."""
        if self._pending_config is None:
            return
        if self._pending_target:
            idx = self.primary_combo.findText(self._pending_target)
            if idx >= 0:
                self.primary_combo.setCurrentIndex(idx)
        if self._pending_features:
            wanted = set(self._pending_features)
            self.features_list.clearSelection()
            for i in range(self.features_list.count()):
                item = self.features_list.item(i)
                item.setSelected(item.text() in wanted)

    def _too_soon_to_restart(self) -> bool:
        """True (with a warning InfoBar) if a Ludwig run is still active, or
        the last one ended less than _MIN_RESTART_GAP_S ago - see
        _last_training_end_ts's docstring in __init__ for the crash this
        guards against.

        A still-running worker is checked first and separately: starting a
        second LudwigTrainerWorker while one is active overwrites
        self._trainer_worker, orphaning the first worker with no Qt parent
        and no remaining Python reference. It gets garbage-collected on the
        spot while its background thread is still deep in a Ludwig training
        run - QThread's own destructor then hard-aborts the whole process
        ("QThread: Destroyed while thread is still running"), reproduced by
        starting training twice (once via _start_training, once via
        _start_training_from_config) about 2s apart - both ran to
        completion (~1252s each) before the abort, confirming two full
        trainings were active concurrently.
        """
        if self._trainer_worker is not None and self._trainer_worker.isRunning():
            InfoBar.warning(
                title="Training already in progress",
                content="Wait for the current run to finish (or stop it) before starting another.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return True
        elapsed = time.monotonic() - self._last_training_end_ts
        if elapsed >= _MIN_RESTART_GAP_S:
            return False
        InfoBar.warning(
            title="Please wait a moment",
            content="The previous run just finished cleaning up — try again in a second or two.",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self,
        )
        return True

    def _log_filled_fields(self) -> None:
        """One usage-log row per non-empty training config field, so a
        usability study can see exactly which training options people
        actually set vs. leave at their default, mirroring
        MetadataPage._log_filled_fields()."""
        n_predictors = len(self.features_list.selectedItems())
        n_secondary = len(self.secondary_list.selectedItems())
        try:
            n_inclusion = len(self.inclusion_builder.get_rules() or [])
        except Exception:
            n_inclusion = 0
        try:
            n_exclusion = len(self.exclusion_builder.get_rules() or [])
        except Exception:
            n_exclusion = 0
        fields = {
            "Model Name": self.model_name_edit.text().strip(),
            "Outcome Variable": self.primary_combo.currentText().strip(),
            "Predictors": f"{n_predictors} selected" if n_predictors else "",
            "Secondary Outcomes": f"{n_secondary} selected" if n_secondary else "",
            "Inclusion Criteria": f"{n_inclusion} rule(s)" if n_inclusion else "",
            "Exclusion Criteria": f"{n_exclusion} rule(s)" if n_exclusion else "",
            "Prediction Type": self.problem_type_combo.currentText(),
            "Evaluation Metric": self.metric_combo.currentText(),
            "Time Budget": self.time_budget.value(),
            "Final Evaluation Holdout": self.test_split.value(),
            "Random Seed": self.random_seed.value(),
            "Search Strategy": self.hyperopt_strategy.currentText(),
            "Max Iterations": self.hyperopt_trials.value(),
            "Parallel Trials": self.parallel_trials.value(),
            "Handle Class Imbalance": self.class_balance_switch.isChecked(),
            "Fill Missing Numeric Values": self.mean_impute_switch.isChecked(),
        }
        for element, value in fields.items():
            if value:
                usage_log.event("Training", "field_filled", element, str(value))

    def _start_training(self):
        """Validate config, build a LudwigTrainerWorker and start it."""
        usage_log.event("Training", "click", "Start Training button")
        log.info("Starting model training")

        if self._too_soon_to_restart():
            return

        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title="No dataset loaded",
                content="Please load a dataset in the Data tab before starting training.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        if not self.model_name_edit.text().strip():
            InfoBar.warning(
                title="No model name",
                content="Enter a name for this model before starting.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        target = self.primary_combo.currentText().strip()
        if not target:
            InfoBar.warning(
                title="No target variable",
                content="Select a target variable (outcome) before starting.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        selected_items = self.features_list.selectedItems()
        features = [item.text() for item in selected_items if item.text() != target]
        if not features and self._pending_config is not None:
            # A staged config already names exactly what the source model
            # trained on - reuse that rather than forcing a re-selection.
            features = self._features_from_config(self._pending_config, target)
        if not features:
            InfoBar.warning(
                title="No features selected",
                content="Select at least one predictor variable.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        train_from_config = self._pending_config is not None
        time_limit_s = 0 if train_from_config else self.time_budget.value() * 60

        self.start_training_btn.setEnabled(False)
        self.stop_training_btn.setEnabled(True)
        self.training_progress.setValue(0)
        self.training_progress.setVisible(False)
        self._training_spinner.setVisible(True)
        self._training_spinner.start()
        self._set_status(
            "training",
            t("training.status.training.from_config") if train_from_config
            else t("training.status.training"),
        )

        # Start from the active dataframe (already respects excluded_rows)
        df = self._data_model.get_active_df()

        # Apply inclusion/exclusion rules defined by the clinician (RuleBuilder)
        try:
            from hamelin.utils.rule_evaluator import apply_rules
            inc_rules = self.inclusion_builder.get_rules() or []
            exc_rules = self.exclusion_builder.get_rules() or []
            # Inclusion: keep rows that match ANY inclusion rule (OR semantics)
            if inc_rules:
                inc_result = apply_rules(df, inc_rules, mode='include')
                df = df.loc[inc_result['mask']]
            # Exclusion: remove rows that match any exclusion rule
            if exc_rules:
                exc_result = apply_rules(df, exc_rules, mode='exclude')
                df = df.loc[exc_result['mask']]
        except Exception as exc:  # noqa: BLE001
            log.warning(f"TrainingPage: rule application failed — {exc}")

        # Build backend kwargs: a staged config trains as-is, otherwise
        # AutoML picks the architecture, with the model-config card's
        # non-default choices layered on top via user_config (see
        # LudwigBackend._fields_to_user_config).
        if train_from_config:
            backend_kwargs = {"config": self._pending_config}
        else:
            backend_kwargs = {
                "test_split": float(self.test_split.value()),
                "random_seed": int(self.random_seed.value()),
            }
            # Only settings the user moved off their neutral default get
            # forced onto Ludwig; a never-touched card still trains exactly
            # like plain auto_train.
            fields: dict = {}
            # Unlike metric/search below, there's no neutral "let Ludwig
            # decide" option here - the combo always shows one of the 3
            # real choices, so it's always forced rather than only when
            # non-default.
            fields["problem_type"] = _PROBLEM_TYPES[self.problem_type_combo.currentIndex()][1]
            if self.metric_combo.currentIndex() != 0:
                fields["metric"] = self._current_metrics[self.metric_combo.currentIndex()][1]
            search = _SEARCH_STRATEGIES[self.hyperopt_strategy.currentIndex()][1]
            if search != "none":
                fields["search"] = search
                fields["max_iter"] = int(self.hyperopt_trials.value())
                fields["parallel_trials"] = int(self.parallel_trials.value())
            if self.class_balance_switch.isChecked():
                fields["class_imbalance"] = True
            if self.mean_impute_switch.isChecked():
                fields["mean_impute"] = True
            if fields:
                backend_kwargs["user_config_fields"] = fields
            # Ticked "Secondary outcomes" become additional Ludwig output
            # features (a real multi-output model), not just report
            # metadata - see LudwigBackend.run()'s secondary_outcomes kwarg.
            # A column ticked as both a feature and a secondary outcome
            # can't be both an input and an output, so features wins.
            secondary_outcomes = [
                self.secondary_list.item(i).text()
                for i in range(self.secondary_list.count())
                if self.secondary_list.item(i).isSelected()
                and self.secondary_list.item(i).text() != target
                and self.secondary_list.item(i).text() not in features
            ]
            if secondary_outcomes:
                backend_kwargs["secondary_outcomes"] = secondary_outcomes
        if self._project_dir is not None:
            backend_kwargs['output_directory'] = str(self._project_dir / "ludwig_runs")

        self._trainer_worker = LudwigTrainerWorker(
            df=df,
            target=target,
            features=features,
            time_limit_s=time_limit_s,
            backend_kwargs=backend_kwargs,
            parent=self,
        )
        self._trainer_worker.progress.connect(self.training_progress.setValue)
        self._trainer_worker.finished.connect(self._on_training_finished)
        self._trainer_worker.error.connect(self._on_training_error)
        self._trainer_worker.start()
        log.info(
            f"TrainingPage: worker started — target={target!r}, "
            f"features={len(features)}, time_limit={time_limit_s}s"
        )
        self._log_filled_fields()
        usage_log.event("Training", "started", self.model_name_edit.text().strip(), f"target={target}, features={len(features)}")

    def _on_import_config_clicked(self) -> None:
        usage_log.event("Training", "click", "Import Config button")
        self._start_training_from_config()

    def _start_training_from_config(self):
        """Train with a fixed Ludwig config loaded from a JSON file instead
        of letting AutoML pick the architecture - e.g. a config exported by
        another tool's "duplicate this model with different hyperparameters"
        flow. Accepts either a bare Ludwig config or {"config": {...}, ...}."""
        if self._too_soon_to_restart():
            return

        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title="No dataset loaded",
                content="Please load a dataset in the Data tab before starting training.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        if not self.model_name_edit.text().strip():
            InfoBar.warning(
                title="No model name",
                content="Enter a name for this model before starting.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        target = self.primary_combo.currentText().strip()
        if not target:
            InfoBar.warning(
                title="No target variable",
                content="Select a target variable (outcome) before starting.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Config File", "", "JSON files (*.json);;All Files (*)",
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            config = payload.get("config", payload)
        except Exception as exc:  # noqa: BLE001
            InfoBar.error(
                title="Could not read config file",
                content=str(exc),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=6000, parent=self,
            )
            return

        selected_items = self.features_list.selectedItems()
        features = [item.text() for item in selected_items if item.text() != target]
        if not features:
            # Nothing (re-)checked in the features list - see
            # _features_from_config's docstring for why this matters.
            features = self._features_from_config(config, target)

        if not features:
            InfoBar.warning(
                title="No features to train on",
                content=(
                    "Neither the features list nor the imported config "
                    "names any predictor variables."
                ),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=5000, parent=self,
            )
            return

        df = self._data_model.get_active_df()

        self.start_training_btn.setEnabled(False)
        self.stop_training_btn.setEnabled(True)
        self.training_progress.setValue(0)
        self.training_progress.setVisible(False)
        self._training_spinner.setVisible(True)
        self._training_spinner.start()
        self._set_status("training", "Training from imported config — please wait…")

        config_backend_kwargs = {"config": config}
        if self._project_dir is not None:
            config_backend_kwargs['output_directory'] = str(self._project_dir / "ludwig_runs")

        self._trainer_worker = LudwigTrainerWorker(
            df=df,
            target=target,
            features=features or None,
            time_limit_s=0,
            backend_kwargs=config_backend_kwargs,
            parent=self,
        )
        self._trainer_worker.progress.connect(self.training_progress.setValue)
        self._trainer_worker.finished.connect(self._on_training_finished)
        self._trainer_worker.error.connect(self._on_training_error)
        self._trainer_worker.start()
        log.info(f"TrainingPage: worker started from imported config — target={target!r}")
        usage_log.event("Training", "started", self.model_name_edit.text().strip(), f"from imported config, target={target}")

    @staticmethod
    def _sanitize_model_name(raw_name: str, fallback: str) -> str:
        """Turn free-text into a safe, non-empty folder name: strips
        characters that aren't safe across Windows/macOS/Linux filenames,
        collapses whitespace to underscores. Falls back to *fallback*
        (the run's model_id) when nothing usable is left, so a blank or
        emoji-only name never produces an empty/invalid path."""
        name = raw_name.strip()
        name = re.sub(r"\s+", "_", name)
        name = re.sub(r"[^A-Za-z0-9_-]", "", name)
        name = name.strip("._-")
        return name or fallback

    @staticmethod
    def _unique_checkpoint_name(base_name: str, checkpoints_dir: Path) -> str:
        """Append _2, _3, ... if base_name is already used under
        checkpoints_dir, so two runs named the same don't silently
        overwrite each other's saved model."""
        candidate = base_name
        n = 2
        while (checkpoints_dir / candidate).exists():
            candidate = f"{base_name}_{n}"
            n += 1
        return candidate

    @staticmethod
    def _features_from_config(config: dict, target: str) -> list:
        """Predictor variable names from a Ludwig config's own
        input_features - used by _start_training_from_config() as a
        fallback when nothing is (re-)checked in the features list, so
        that "train from imported config" flow (e.g. "duplicate this
        model" with tweaked settings) reuses exactly what the source
        model was actually trained on. Without this, an empty features
        list reached LudwigBackend.run() as features=None, which skips
        its own column subsetting entirely and silently trains on every
        column in the dataset instead."""
        names = [
            f.get("column") or f.get("name")
            for f in config.get("input_features", [])
            if f.get("column") or f.get("name")
        ]
        return [n for n in names if n != target]

    def _clear_pending_config(self) -> None:
        """Drop a staged "duplicate a model" config - it is single-use, a
        later normal run must not silently reuse it."""
        self._pending_config = None
        self._pending_target = ""
        self._pending_features = []
        self._update_pending_config_ui()

    def _update_pending_config_ui(self) -> None:
        """Reflect whether a "duplicate a model" config is staged: show the
        notice and grey out the model-configuration card, whose AutoML
        settings don't apply when training a fixed config."""
        active = self._pending_config is not None
        self._pending_banner.setVisible(active)
        self.model_card.setEnabled(not active)
        self._step4_label.setEnabled(not active)

    def _on_training_finished(self, result: AutoMLResult) -> None:
        """Handle successful training: populate UI, persist, emit signal."""
        log.info(f"TrainingPage: training finished — {result.model_type}")

        self._last_training_end_ts = time.monotonic()
        self._clear_pending_config()

        # Restore buttons and progress indicators
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self._training_spinner.stop()
        self._training_spinner.setVisible(False)
        self.training_progress.setValue(100)
        self.training_progress.setVisible(True)
        self._set_status("done", "Training completed successfully.")
        usage_log.event("Training", "created", "Model", self.model_name_edit.text().strip() or result.model_type)

        # ModelResultsWidget: KPI cards + charts + interpretation
        self._last_result = result
        self._results_widget.load(result)

        # Persist to ModelHistory (if project is open)
        if self._project_dir is not None and self._data_model is not None:
            try:
                from hamelin.analytics.automl.base import AutoMLBackend
                from hamelin.analytics.ludwig_trainer import LudwigTrainer, _dataset_hash
                from hamelin.core.model_history import ModelHistory, ModelTraining

                # Prefer the actual DataFrame used for training (worker._df) if available
                try:
                    training_df = getattr(self._trainer_worker, '_df', None)
                except Exception:
                    training_df = None
                df = training_df if training_df is not None else (self._data_model.df if self._data_model is not None else None)
                target = self.primary_combo.currentText().strip()
                selected_items = self.features_list.selectedItems()
                features = [item.text() for item in selected_items if item.text() != target]

                record = ModelTraining(
                    target_variable=target,
                    model_type=result.model_type,
                    hyperparameters=result.hyperparameters,
                    dataset_version=_dataset_hash(df),
                    num_samples=len(df) if df is not None else 0,
                    num_features=len(features),
                    train_metrics=result.train_metrics,
                    val_metrics=result.val_metrics,
                    test_metrics=result.test_metrics,
                    training_time_seconds=result.training_time_seconds,
                    num_trials=result.num_trials,
                )
                # Save the actual Ludwig model (weights + config), not just
                # its metrics, so other tools can reload it later.
                if result.trained_model is not None:
                    checkpoints_dir = Path(self._project_dir) / "model_checkpoints"
                    # Named after what the user typed in "Model name" (section
                    # 3) instead of the raw model_id UUID - this folder name
                    # is what shows up wherever a model gets picked by name
                    # later (Dashboard history, the "interface" comparison
                    # tool), so it needs to actually be that name, not just
                    # carry it as separate metadata alongside an opaque ID.
                    base_name = self._sanitize_model_name(
                        self.model_name_edit.text(), fallback=record.model_id
                    )
                    folder_name = self._unique_checkpoint_name(base_name, checkpoints_dir)
                    record.model_name = folder_name
                    checkpoint_dir = checkpoints_dir / folder_name
                    try:
                        result.trained_model.save(str(checkpoint_dir))
                        record.checkpoint_path = str(checkpoint_dir)
                    except Exception as exc:  # noqa: BLE001
                        log.warning(f"TrainingPage: could not save model checkpoint — {exc}")

                    # A minimal description.json - just enough for
                    # interface/utils/get_model_paths.get_model_dataset() to
                    # find this run's source CSV later (e.g. to recompute a
                    # live confusion matrix for a run saved without
                    # test_predictions.csv - see the block just below).
                    # Ludwig's own `ludwig experiment` CLI writes a fuller
                    # version of this file itself, recording the exact
                    # command that was run - LudwigBackend never goes
                    # through that CLI (it calls create_auto_config/
                    # train_with_config directly), so nothing else in this
                    # pipeline ever produces this file; every run trained
                    # here needs it written explicitly, not just this one.
                    if self._data_model is not None and self._data_model.filepath is not None:
                        try:
                            (checkpoint_dir / "description.json").write_text(
                                json.dumps({"dataset": str(self._data_model.filepath)}, indent=2)
                            )
                        except Exception as exc:  # noqa: BLE001
                            log.warning(f"TrainingPage: could not save run description — {exc}")

                    # Every test-set prediction, saved alongside the model -
                    # takes more disk space than just the aggregate metrics,
                    # but means the confusion matrix (and, later, a real
                    # bootstrap confidence interval) can be read straight off
                    # disk instead of reloading the model and re-running
                    # inference each time they're needed (see
                    # interface/utils/print_confusion_matrix.py).
                    predictions_df = result.extra.get("test_predictions") if result.extra else None
                    if predictions_df is not None:
                        try:
                            predictions_df.to_csv(checkpoint_dir / "test_predictions.csv", index=False)
                        except Exception as exc:  # noqa: BLE001
                            log.warning(f"TrainingPage: could not save test predictions — {exc}")

                    # LudwigModel.save() only writes weights/config, not a
                    # training_report.json - that file is otherwise only
                    # produced by Ludwig's own auto_train/hyperopt experiment
                    # output (ludwig_runs/), which this pipeline no longer
                    # uses. LudwigBackend now builds one itself (with
                    # Ludwig's own ludwig.utils.training_report generator,
                    # not a hand-typed dict) and hands it back here via
                    # result.extra - just save it alongside the checkpoint.
                    training_report = result.extra.get("training_report") if result.extra else None
                    if training_report is not None:
                        try:
                            (checkpoint_dir / "training_report.json").write_text(
                                json.dumps(training_report, indent=2, default=str)
                            )
                        except Exception as exc:  # noqa: BLE001
                            log.warning(f"TrainingPage: could not save training report — {exc}")

                history = ModelHistory(self._project_dir)
                history.add_training(record)
                log.info(f"TrainingPage: record persisted — {record.model_id}")
            except Exception as exc:  # noqa: BLE001
                log.warning(f"TrainingPage: could not persist record — {exc}")

        # Notify MainWindow (→ DashboardPage.refresh, history widgets)
        self.training_finished.emit(result)

    def _on_training_error(self, message: str) -> None:
        """Handle worker error or cancellation."""
        log.warning(f"TrainingPage: training error — {message}")
        self._last_training_end_ts = time.monotonic()
        self._clear_pending_config()
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self._training_spinner.stop()
        self._training_spinner.setVisible(False)
        self.training_progress.setVisible(True)
        if "cancelled" in message.lower():
            self._set_status("cancelled", "Training cancelled by user.")
            usage_log.event("Training", "stopped", "Model training", "cancelled by user")
            return
        self._set_status("error", f"Error: {message}")
        InfoBar.error(
            title="Training failed",
            content=message,
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=6000, parent=self,
        )

    def refresh_history(self, project_dir) -> None:
        """Reload the history and timeline widgets after a training run."""
        self._history_widget.load(project_dir)
        self._timeline_widget.load(project_dir)
        log.debug("TrainingPage: history widgets refreshed")
    
    def _stop_training(self):
        """Request worker cancellation."""
        usage_log.event("Training", "click", "Stop button")
        log.info("Stopping model training")
        self._last_training_end_ts = time.monotonic()
        if self._trainer_worker is not None:
            self._trainer_worker.stop()
            self._trainer_worker.quit()
            self._trainer_worker = None
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self._training_spinner.stop()
        self._training_spinner.setVisible(False)
        self.training_progress.setVisible(True)
        self._set_status("cancelled", "Training stopped by user.")
    
    def _export_model(self):
        """Export the trained model report as a JSON file."""
        usage_log.event("Training", "click", "Export Trained Model button")
        log.info("Exporting trained model")

        if self._last_result is None:
            InfoBar.warning(
                title="No trained model",
                content="Train a model first before exporting.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Model Report",
            "hamelin_model.json",
            "JSON files (*.json);;All Files (*)",
        )
        if not path:
            return

        from datetime import datetime
        result = self._last_result
        target = self.primary_combo.currentText().strip()
        selected_items = self.features_list.selectedItems()
        features = [item.text() for item in selected_items if item.text() != target]

        export_data = {
            "hamelin_version": "0.1.0",
            "export_timestamp": datetime.now().isoformat(),
            "model_type": result.model_type,
            "target_variable": target,
            "features": features,
            "secondary_outcomes": [self.secondary_list.item(i).text() for i in range(self.secondary_list.count()) if self.secondary_list.item(i).isSelected()],
            "training_time_seconds": round(result.training_time_seconds, 2),
            "num_trials": result.num_trials,
            "train_metrics": result.train_metrics,
            "val_metrics": result.val_metrics,
            "test_metrics": result.test_metrics,
            "hyperparameters": result.hyperparameters,
        }
        if result.extra:
            export_data["extra"] = result.extra
        if self._data_model is not None and self._data_model.filepath:
            export_data["dataset"] = str(self._data_model.filepath)
            export_data["dataset_rows"] = self._data_model.n_rows
            export_data["dataset_columns"] = self._data_model.n_columns
            if self._data_model.excluded_rows:
                export_data["excluded_rows_count"] = len(self._data_model.excluded_rows)

        Path(path).write_text(json.dumps(export_data, indent=2, default=str), encoding="utf-8")
        InfoBar.success(
            title="Model report saved",
            content=f"Saved to {path}",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self,
        )
        log.info(f"Model report exported to {path} ({len(export_data)} fields)")
        usage_log.event("Training", "exported", "Model report", Path(path).name)

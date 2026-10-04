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
    FluentIcon, ProgressBar, IndeterminateProgressBar, CheckBox, RadioButton,
    InfoBar, InfoBarPosition
)

from hamelin.analytics.automl.base import AutoMLResult
from hamelin.analytics.ludwig_trainer import LudwigTrainerWorker
from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.utils.export_paths import default_export_path
from hamelin.view.widgets import HelpButton, ModelHistoryWidget, ModelResultsWidget, PageHelpButton, TrainingTimelineWidget, attach_help_popup, attach_help_popup_hover
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style, colors, isDarkTheme, list_item_qss, on_theme_changed, scrollbar_qss, apply_transparent_container
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
    # configuration/features/binary_features.md, "Metrics"
    "binary": [
        ("training.metric.auc", "roc_auc"),
        ("training.metric.accuracy", "accuracy"),
        ("training.metric.precision", "precision"),
        ("training.metric.recall", "recall"),
        ("training.metric.specificity", "specificity"),
    ],
    # configuration/features/category_features.md, "Metrics"
    "category": [
        ("training.metric.accuracy", "accuracy"),
        ("training.metric.hitsatk", "hits_at_k"),
    ],
    # configuration/features/number_features.md, "Metrics"
    "number": [
        ("training.metric.rmse", "root_mean_squared_error"),
        ("training.metric.mae", "mean_absolute_error"),
        ("training.metric.mse", "mean_squared_error"),
        ("training.metric.rmspe", "root_mean_squared_percentage_error"),
    ],
}
# How early stopping is applied (see LudwigBackend._fields_to_user_config).
_EARLY_STOP_MODES = [
    ("training.earlystop.auto", "auto"),
    ("training.earlystop.patience", "patience"),
    ("training.earlystop.off", "off"),
]
_SEARCH_STRATEGIES = [
    ("training.strategy.none", "none"),
    ("training.strategy.random", "random"),
    ("training.strategy.bayesian", "bayesian"),
    ("training.strategy.exhaustive", "exhaustive"),
]
# Missing-value strategy for NUMBER input features - configuration/features/
# number_features.md, "missing_value_strategy" (default: fill_with_const,
# i.e. Ludwig's own behaviour, which is what index 0 here leaves in place).
_MISSING_STRATEGIES = [
    ("training.missingstrategy.default", None),
    ("training.missingstrategy.mean", "fill_with_mean"),
    ("training.missingstrategy.mode", "fill_with_mode"),
    ("training.missingstrategy.ffill", "ffill"),
    ("training.missingstrategy.bfill", "bfill"),
    ("training.missingstrategy.droprow", "drop_row"),
]


# Model size (advanced): None leaves AutoML's own network (a large, attention-
# based one for tabular data); "light" swaps in a small fully-connected one.
# See LudwigBackend._apply_architecture. No technical names in the labels.
_ARCHITECTURES = [
    ("training.architecture.auto", None),
    ("training.architecture.light", "light"),
]
# Learning method (advanced): None keeps AutoML's optimizer; "regularized" is
# the same method with a small penalty on large weights - see
# LudwigBackend._OPTIMIZERS.
_OPTIMIZERS = [
    ("training.optimizer.auto", None),
    ("training.optimizer.regularized", "regularized"),
]


def recommended_parallel_trials() -> int:
    """How many hyperparameter trials to run at once on THIS computer.

    Every trial is a full training process (about one CPU core and 1-2 GB
    of RAM), so the safe number is bounded by both: one per core, and one
    per 2 GB of memory, never fewer than 1 nor more than 8. On a 4-core,
    7 GB laptop that gives 3, which is also what avoided the out-of-memory
    kills seen with Ludwig's own unlimited default.
    """
    import os

    cores = os.cpu_count() or 2
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / 2 ** 30
    except Exception:  # noqa: BLE001
        ram_gb = 4.0
    return int(max(1, min(cores, ram_gb // 2, 8)))


# The predictor / secondary-outcome lists always show 10 rows (scrolling
# beyond that) and never grow past 12. Row height depends on the theme, so
# the pixel sizes are worked out from the real rows (see _fit_list_rows);
# these are only the first guess, before any row exists.
_LIST_MIN_ROWS, _LIST_MAX_ROWS = 10, 12
_LIST_ROW_PX = 14
_LIST_MIN_HEIGHT = _LIST_ROW_PX * _LIST_MIN_ROWS + 8
_LIST_MAX_HEIGHT = _LIST_ROW_PX * _LIST_MAX_ROWS + 8


def _fit_list_rows(lst) -> None:
    """Size *lst* to show 10 rows (12 at most) of its actual row height."""
    row = lst.sizeHintForRow(0) if lst.count() else _LIST_ROW_PX
    frame = 2 * lst.frameWidth() + 4
    lst.setMinimumHeight(row * _LIST_MIN_ROWS + frame)
    lst.setMaximumHeight(row * _LIST_MAX_ROWS + frame)


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
        self._run_settings: dict | None = None   # snapshot of the run in progress
        log.debug("Initializing Training Page")
        self._init_ui()
        # The form as first built = the defaults, so the pre-training summary
        # can tell a setting left alone from one the user changed.
        self._form_defaults = self._collect_form_state()
        self._refresh_default_model_name()

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
        self._all_columns: list[str] = []
        self.primary_combo.currentIndexChanged.connect(self._sync_predictors_with_outcome)
        self.primary_combo.currentIndexChanged.connect(self._auto_set_problem_type)
        self.features_list.setMinimumHeight(_LIST_MIN_HEIGHT)
        self.features_list.setMaximumHeight(_LIST_MAX_HEIGHT)
        self.features_list.setSelectionMode(QListWidget.MultiSelection)
        # Hover, not click (attach_help_popup_hover, not attach_help_popup) -
        # clicking an item in this list is how you select/deselect it, so a
        # click-triggered popup fired on every single one of those instead
        # of just an incidental first click.
        attach_help_popup_hover(
            self.features_list,
            t("training.txt.select_predictor_variables_features_use_")
        )
        variables_layout.addWidget(self.features_list)

        select_all_predictors_btn = PushButton(t("training.btn.select_all_predictors"), self)
        select_all_predictors_btn.clicked.connect(self._select_all_predictors)
        variables_layout.addWidget(select_all_predictors_btn)

        # Secondary outcomes (optional) — show presets / mapping
        secondary_label = BodyLabel(t("training.label.secondary_outcomes"))
        variables_layout.addWidget(secondary_label)

        self.secondary_list = QListWidget()
        self.secondary_list.setMinimumHeight(_LIST_MIN_HEIGHT)
        self.secondary_list.setMaximumHeight(_LIST_MAX_HEIGHT)
        self.secondary_list.setSelectionMode(QListWidget.MultiSelection)
        # Hover, not click - same reasoning as features_list above (an
        # item click here selects/deselects it, not a request for help).
        attach_help_popup_hover(
            self.secondary_list,
            t("training.txt.optional_other_outcomes_to_predict_at")
        )
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
            t("training.txt.add_inclusion_rules_visually_column_oper")
        )
        criteria_layout.addWidget(self.inclusion_builder)
        
        # Exclusion criteria
        exclusion_label = BodyLabel(t("training.label.exclusion"))
        criteria_layout.addWidget(exclusion_label)
        
        # Exclusion rule builder (visual)
        self.exclusion_builder = RuleBuilder(columns=[], parent=self)
        attach_help_popup(
            self.exclusion_builder,
            t("training.txt.add_exclusion_rules_visually_column_oper")
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
        # Pre-filled with a free name ("model_1", "model_2", ...) so the
        # user can just press Start; typing their own replaces it.
        self.model_name_edit = LineEdit()
        self._auto_model_name = ""
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

        # Time budget - no up/down arrows: typed directly in the field,
        # like Final Evaluation Holdout below. qfluentwidgets' SpinBox
        # already hides the native Qt spin arrows by default and instead
        # adds its OWN upButton/downButton pair (InlineSpinBoxBase) - those
        # are only removed via setSymbolVisible(False), not
        # setButtonSymbols().
        self.time_budget = SpinBox()
        # Always seconds (minimum 100). Every keystroke is applied at once.
        self.time_budget.setRange(100, 86400)
        self.time_budget.setKeyboardTracking(True)
        self.time_budget.setValue(300)
        self.time_budget.setSymbolVisible(False)
        self._add_form_row(advanced_form, t("training.label.timebudget"), self.time_budget)

        # Test split ("Final Evaluation Holdout") - typed directly (e.g.
        # "0.2"), no up/down arrows.
        self.test_split = DoubleSpinBox()
        self.test_split.setRange(0.1, 0.5)
        self.test_split.setValue(0.2)
        self.test_split.setSingleStep(0.05)
        self.test_split.setDecimals(2)
        self.test_split.setSymbolVisible(False)
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
        # 10 is both the minimum and the default. It is an upper bound: the
        # time budget always wins, so a short budget (say 300 s) simply
        # stops the search before all iterations have run.
        self.hyperopt_trials.setRange(10, 500)
        self.hyperopt_trials.setValue(10)
        self._add_form_row(advanced_form, t("training.label.maxiterations"), self.hyperopt_trials)

        # Parallelization
        self.parallel_trials = SpinBox()
        self.parallel_trials.setRange(1, 16)
        self.parallel_trials.setValue(recommended_parallel_trials())
        attach_help_popup(
            self.parallel_trials,
            t("training.txt.parallel_trials_help").format(recommended_parallel_trials()),
        )
        self._add_form_row(advanced_form, t("training.label.paralleltrials"), self.parallel_trials)

        # Early stopping. Three explicit modes instead of one number that
        # Ludwig silently overrode during AutoML's search (it forces
        # trainer.early_stop to -1 while a trial scheduler is active):
        #   Automatic - Ludwig's own scheduler stops weak trials (default);
        #   Patience  - each trial stops after N evaluation rounds without
        #               improvement (trainer.early_stop, configuration/
        #               trainer.md), which needs the scheduler switched to fifo;
        #   Off       - every trial trains all its epochs.
        self.early_stop_mode = ComboBox()
        self.early_stop_mode.addItems([t(label) for label, _ in _EARLY_STOP_MODES])
        attach_help_popup(self.early_stop_mode, t("training.earlystop.help"))
        self._add_form_row(advanced_form, t("training.label.earlystop_mode"), self.early_stop_mode)

        self.early_stop = SpinBox()          # patience, in evaluation rounds
        self.early_stop.setRange(1, 100)
        self.early_stop.setValue(5)
        self.early_stop.setEnabled(False)
        self._add_form_row(advanced_form, t("training.label.earlystop"), self.early_stop)
        self.early_stop_mode.currentIndexChanged.connect(self._on_early_stop_mode_changed)

        hyperopt_content_layout.addLayout(advanced_form)

        balance_row = QHBoxLayout()
        # A plain check box, not a SwitchButton: the animated switch was
        # reported to freeze/crash the window when toggled on some systems.
        self.class_balance_switch = CheckBox(t("training.label.imbalance"))
        balance_row.addWidget(self.class_balance_switch)
        balance_row.addStretch()
        hyperopt_content_layout.addLayout(balance_row)

        # Evaluation metric options and class-imbalance handling both
        # depend on the problem type (Ludwig docs: oversample_minority is
        # only supported for binary output features - configuration/
        # preprocessing.md, "Data Balancing").
        self.problem_type_combo.currentIndexChanged.connect(self._on_problem_type_changed)
        self._on_problem_type_changed()

        # Missing-value strategy for NUMBER features (configuration/
        # features/number_features.md, "missing_value_strategy"). Index 0
        # ("Ludwig default") sends no override, matching every other
        # "let Ludwig decide" default elsewhere on this page.
        self.missing_strategy_combo = ComboBox()
        self.missing_strategy_combo.addItems([t(label) for label, _ in _MISSING_STRATEGIES])
        self._add_form_row(advanced_form, t("training.label.meanimpute"), self.missing_strategy_combo)

        # Model size and learning method: both default to "Automatic" (index 0),
        # which sends nothing and trains exactly like plain AutoML.
        self.architecture_combo = ComboBox()
        self.architecture_combo.addItems([t(label) for label, _ in _ARCHITECTURES])
        attach_help_popup(self.architecture_combo, t("training.architecture.help"))
        self._add_form_row(advanced_form, t("training.label.architecture"), self.architecture_combo)

        self.optimizer_combo = ComboBox()
        self.optimizer_combo.addItems([t(label) for label, _ in _OPTIMIZERS])
        attach_help_popup(self.optimizer_combo, t("training.optimizer.help"))
        self._add_form_row(advanced_form, t("training.label.optimizer"), self.optimizer_combo)

        self._hyperopt_content.setVisible(False)
        model_layout.addWidget(self._hyperopt_content)

        self.model_card = model_card
        main_layout.addWidget(model_card)
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

        self.preview_config_btn = PushButton(t("training.btn.preview_config"), self)
        self.preview_config_btn.setIcon(FluentIcon.VIEW)
        attach_help_popup(self.preview_config_btn, t("training.help.preview_config"))
        self.preview_config_btn.clicked.connect(self._on_preview_config_clicked)
        control_buttons.addWidget(self.preview_config_btn)

        self.import_config_btn = PushButton(t("training.btn.import_config"), self)
        self.import_config_btn.setIcon(FluentIcon.FOLDER)
        attach_help_popup(
            self.import_config_btn,
            t("training.txt.train_using_a_fixed_ludwig_config")
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
        apply_transparent_container(content)

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
                t("training.txt.class_balancing_is_only_supported_for")
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

    def _suggest_problem_type(self, target: str) -> str | None:
        """Guess the Prediction Type ("binary"/"category"/"number") from the
        values of *target*, or None if it can't be told."""
        if self._data_model is None or self._data_model.df is None:
            return None
        df = self._data_model.get_active_df()
        if target not in df.columns:
            return None
        series = df[target].dropna()
        if series.empty:
            return None
        n_unique = series.nunique()
        if n_unique == 2:
            return "binary"
        import pandas as pd
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.isna().mean() > 0.05:
            return "category"
        # Numeric: integer codes with few distinct values are class labels
        # (e.g. 1/2/3), anything else is a continuous outcome.
        is_int = bool((numeric.dropna() % 1 == 0).all())
        if is_int and n_unique <= min(10, max(3, len(series) // 20)):
            return "category"
        return "number"

    def _auto_set_problem_type(self, *_args) -> None:
        """Pick the Prediction Type that fits the newly chosen outcome (the
        user can still change it afterwards)."""
        if getattr(self, "_restoring_form", False):
            return
        suggestion = self._suggest_problem_type(self.primary_combo.currentText().strip())
        if suggestion is None:
            return
        idx = next(i for i, (_, v) in enumerate(_PROBLEM_TYPES) if v == suggestion)
        if idx != self.problem_type_combo.currentIndex():
            self.problem_type_combo.setCurrentIndex(idx)  # fires _on_problem_type_changed

    def _sync_predictors_with_outcome(self, *_args) -> None:
        """The outcome variable can't also be a predictor: list every column
        except the chosen outcome, keeping the user's other selections."""
        outcome = self.primary_combo.currentText().strip()
        chosen = {i.text() for i in self.features_list.selectedItems()}
        self.features_list.blockSignals(True)
        self.features_list.clear()
        for col in self._all_columns:
            if col == outcome:
                continue
            self.features_list.addItem(col)
            if col in chosen:
                self.features_list.item(self.features_list.count() - 1).setSelected(True)
        self.features_list.blockSignals(False)
        self.features_list.itemSelectionChanged.emit()

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
        self._all_columns = columns
        self._sync_predictors_with_outcome()
        # Populate secondary outcomes list with available columns (can be mapped from presets)
        try:
            self.secondary_list.clear()
            self.secondary_list.addItems(columns)
        except Exception:
            pass
        _fit_list_rows(self.features_list)
        _fit_list_rows(self.secondary_list)
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
                form = state.get('training_form')
                if isinstance(form, dict):
                    self._restore_form_state(form)
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

        # Connect change signals to persist user choices (once: this method
        # runs again for every dataset load)
        if getattr(self, "_state_signals_connected", False):
            return
        self._state_signals_connected = True
        try:
            self.primary_combo.currentIndexChanged.connect(lambda _: self._save_project_state())
            self.features_list.itemSelectionChanged.connect(lambda: self._save_project_state())
            for w in self._form_widgets().values():
                for sig in ("currentIndexChanged", "valueChanged", "toggled"):
                    if hasattr(w, sig):
                        getattr(w, sig).connect(self._on_form_changed)
                        break
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
            # Model Configuration choices
            try:
                extra['training_form'] = self._collect_form_state()
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

    def _form_widgets(self) -> dict:
        """The Model Configuration controls that are remembered per project."""
        return {
            "problem_type": self.problem_type_combo, "metric": self.metric_combo,
            "time_budget": self.time_budget, "test_split": self.test_split,
            "random_seed": self.random_seed, "search_strategy": self.hyperopt_strategy,
            "max_iterations": self.hyperopt_trials, "parallel_trials": self.parallel_trials,
            "early_stop_mode": self.early_stop_mode, "early_stop": self.early_stop,
            "missing_values": self.missing_strategy_combo, "class_imbalance": self.class_balance_switch,
            "architecture": self.architecture_combo, "optimizer": self.optimizer_combo,
        }

    def _collect_form_state(self) -> dict:
        state: dict = {}
        for key, w in self._form_widgets().items():
            if hasattr(w, "currentIndex"):      # (a Fluent ComboBox also has isChecked)
                state[key] = int(w.currentIndex())
            elif hasattr(w, "isChecked"):
                state[key] = bool(w.isChecked())
            else:
                state[key] = w.value()
        return state

    def _restore_form_state(self, state: dict) -> None:
        """Re-apply the Model Configuration saved with the project."""
        widgets = self._form_widgets()
        self._restoring_form = True
        try:
            for key in ("problem_type", "metric", "search_strategy", "early_stop_mode",
                        "missing_values", "time_budget", "test_split", "random_seed",
                        "max_iterations", "parallel_trials", "early_stop", "class_imbalance",
                        "architecture", "optimizer"):
                if key not in state:
                    continue
                w, v = widgets[key], state[key]
                try:
                    if hasattr(w, "currentIndex"):
                        if 0 <= int(v) < w.count():
                            w.setCurrentIndex(int(v))
                    elif hasattr(w, "isChecked"):
                        w.setChecked(bool(v))
                    else:
                        w.setValue(v)
                except Exception:  # noqa: BLE001
                    pass
        finally:
            self._restoring_form = False

    def _on_form_changed(self, *_args) -> None:
        if not getattr(self, "_restoring_form", False):
            self._save_project_state()

    def _preview_rules(self, mode: str = 'include') -> None:
        """Run preview of the inclusion/exclusion rules against active df."""
        usage_log.event("Training", "click", f"Preview {'Inclusion' if mode == 'include' else 'Exclusion'} Rules button")
        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title=t("training.txt.no_dataset"),
                content=t("training.txt.load_a_dataset_first_to_preview"),
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
        self._refresh_default_model_name()
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


    def _suggest_model_name(self) -> str:
        """First "model_N" not already used by a saved model of this
        project (the checkpoint folders under results/models/)."""
        taken = set()
        if self._project_dir is not None:
            folder = Path(self._project_dir) / "results" / "models"
            if folder.is_dir():
                taken = {p.name for p in folder.iterdir()}
        n = 1
        while f"model_{n}" in taken:
            n += 1
        return f"model_{n}"

    def _refresh_default_model_name(self) -> None:
        """Put the suggested name in the field, unless the user has typed
        their own (anything other than empty or the previous suggestion)."""
        current = self.model_name_edit.text().strip()
        if current and current != self._auto_model_name:
            return
        self._auto_model_name = self._suggest_model_name()
        self.model_name_edit.setText(self._auto_model_name)

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
            InfoBar.warning(title=t("training.txt.no_project"), content=t("training.txt.open_a_project_first"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        if not hasattr(self, 'preset_combo'):
            InfoBar.warning(title=t("training.txt.presets_disabled"), content=t("training.txt.preset_preview_is_not_available"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        name = self.preset_combo.currentText().strip()
        if not name:
            InfoBar.warning(title=t("training.txt.no_preset_selected"), content=t("training.txt.choose_a_preset_from_the_dropdown"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
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
            InfoBar.success(title=t("training.txt.preset_loaded"), content=t("training.txt.previewing_0").format(name), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not load preset {path}: {exc}")
            InfoBar.error(title=t("training.txt.load_failed"), content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

    def _on_apply_preset(self) -> None:
        """Apply preset to Training UI: fill inclusion/exclusion and set primary outcome if possible."""
        if self._project_dir is None:
            InfoBar.warning(title=t("training.txt.no_project"), content=t("training.txt.open_a_project_first"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        if not hasattr(self, 'preset_combo'):
            InfoBar.warning(title=t("training.txt.presets_disabled"), content=t("training.txt.applying_presets_is_not_available"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        name = self.preset_combo.currentText().strip()
        if not name:
            InfoBar.warning(title=t("training.txt.no_preset_selected"), content=t("training.txt.choose_a_preset_from_the_dropdown"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
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
                    InfoBar.info(title=t("training.txt.primary_outcome"), content=t("training.txt.preset_primary_outcome_0_map_it").format(po_label), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=self)
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
            InfoBar.success(title=t("training.txt.preset_applied"), content=t("training.txt.applied_0").format(name), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not apply preset {path}: {exc}")
            InfoBar.error(title=t("training.txt.apply_failed"), content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

    def _on_preview_derived_csv(self) -> None:
        """Preview the derived CSV specified by common default location or preset export setting."""
        if self._project_dir is None:
            InfoBar.warning(title=t("training.txt.no_project"), content=t("training.txt.open_a_project_first"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
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
                    InfoBar.success(title=t("training.txt.derived_csv_preview"), content=t("training.txt.showing_first_rows_of_0").format(default_path.name), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
                return
            except Exception as exc:  # noqa: BLE001
                log.warning(f"Could not preview derived CSV: {exc}")
                InfoBar.error(title=t("training.txt.preview_failed"), content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)
                return
        InfoBar.warning(title=t("training.txt.no_derived_csv"), content=t("training.txt.no_derived_csv_found_at_0").format(default_path), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

    def _on_save_preset(self) -> None:
        """Save current UI settings as a preset JSON in training_schemas."""
        usage_log.event("Training", "click", "Save Preset button")
        if self._project_dir is None:
            InfoBar.warning(title=t("training.txt.no_project"), content=t("training.txt.open_a_project_first"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            return
        # ask for filename (default folder training_schemas)
        schema_dir = self._project_dir / 'training_schemas'
        name, ok = QInputDialog.getText(self, 'Preset name', 'Enter preset filename (without .json):')
        if not ok or not name:
            return
        schema_dir.mkdir(exist_ok=True)   # only once there is something to put in it
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
            InfoBar.success(title=t("training.txt.preset_saved"), content=t("training.txt.saved_0").format(fname.name), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self)
            log.info(f"Preset saved to {fname}")
            usage_log.event("Training", "saved", "Preset", fname.name)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not save preset {fname}: {exc}")
            InfoBar.error(title=t("training.txt.save_failed"), content=str(exc), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=self)

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
        InfoBar.info(title=t("training.txt.reset"), content=t("training.txt.cleared_inclusion_exclusion_fields"), orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=2500, parent=self)

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
                title=t("training.txt.training_already_in_progress"),
                content=t("training.txt.wait_for_the_current_run_to"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return True
        elapsed = time.monotonic() - self._last_training_end_ts
        if elapsed >= _MIN_RESTART_GAP_S:
            return False
        InfoBar.warning(
            title=t("training.txt.please_wait_a_moment"),
            content=t("training.txt.the_previous_run_just_finished_cleaning"),
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
            "Early Stopping Mode": self.early_stop_mode.currentText(),
            "Early Stopping Patience": self.early_stop.value(),
            "Handle Class Imbalance": self.class_balance_switch.isChecked(),
            "Missing Numeric Values Strategy": (
                self.missing_strategy_combo.currentText()
                if self.missing_strategy_combo.currentIndex() != 0 else ""
            ),
            "Model Size": (
                self.architecture_combo.currentText()
                if self.architecture_combo.currentIndex() != 0 else ""
            ),
            "Learning Method": (
                self.optimizer_combo.currentText()
                if self.optimizer_combo.currentIndex() != 0 else ""
            ),
        }
        for element, value in fields.items():
            if value:
                usage_log.event("Training", "field_filled", element, str(value))

    def _problem_type_mismatch(self, problem_type: str, target: str) -> str | None:
        """Return a plain-language error if *problem_type* is incompatible
        with the actual values in the *target* column, or None if it's
        fine. Checked before training starts (see _start_training)."""
        if self._data_model is None or self._data_model.df is None:
            return None
        df = self._data_model.get_active_df()
        if target not in df.columns:
            return None
        series = df[target].dropna()
        if series.empty:
            return None

        if problem_type == "number":
            import pandas as pd
            numeric = pd.to_numeric(series, errors="coerce")
            bad_pct = numeric.isna().mean()
            if bad_pct > 0.05:
                examples = series[numeric.isna()].astype(str).unique()[:3]
                return (
                    f"'{target}' isn't numeric — {bad_pct:.0%} of its values aren't valid "
                    f"numbers (e.g. {', '.join(examples)}). Regression needs a continuous "
                    f"numeric outcome; pick Binary or Multi-class classification instead, "
                    f"or choose a different outcome column."
                )
        elif problem_type == "binary":
            n_unique = series.nunique()
            if n_unique != 2:
                return (
                    f"'{target}' has {n_unique} distinct value(s), not 2 — Binary "
                    f"classification needs exactly two. Pick Multi-class classification "
                    f"instead, or choose a different outcome column."
                )
        return None

    def _collect_config_fields(self) -> dict:
        """The model-config card's current choices, as the flat ``fields``
        dict LudwigBackend turns into a partial Ludwig config (see
        LudwigBackend._fields_to_user_config). Shared by the real training
        run and the "Preview Config" button so both always agree."""
        # Only settings the user moved off their neutral default get
        # forced onto Ludwig; a never-touched card still trains exactly
        # like plain auto_train.
        fields: dict = {}
        # Unlike metric/search below, there's no neutral "let Ludwig
        # decide" option here - the combo always shows one of the 3
        # real choices, so it's always forced rather than only when
        # non-default.
        fields["problem_type"] = _PROBLEM_TYPES[self.problem_type_combo.currentIndex()][1]
        # Always sent - the UI's own default (5) already matches
        # Ludwig's, so sending it unchanged is a no-op.
        fields["early_stop_mode"] = _EARLY_STOP_MODES[self.early_stop_mode.currentIndex()][1]
        fields["early_stop"] = int(self.early_stop.value())
        if self.metric_combo.currentIndex() != 0:
            fields["metric"] = self._current_metrics[self.metric_combo.currentIndex()][1]
        search = _SEARCH_STRATEGIES[self.hyperopt_strategy.currentIndex()][1]
        # Always sent: it used to be ignored unless a search strategy was
        # picked, so "Parallel trials = 4" silently ran with a hidden cap of 3.
        fields["parallel_trials"] = int(self.parallel_trials.value())
        if search != "none":
            fields["search"] = search
            fields["max_iter"] = int(self.hyperopt_trials.value())
        if self.class_balance_switch.isChecked():
            fields["class_imbalance"] = True
        missing_strategy = _MISSING_STRATEGIES[self.missing_strategy_combo.currentIndex()][1]
        if missing_strategy is not None:
            fields["missing_strategy"] = missing_strategy
        architecture = _ARCHITECTURES[self.architecture_combo.currentIndex()][1]
        if architecture is not None:
            fields["architecture"] = architecture
        optimizer = _OPTIMIZERS[self.optimizer_combo.currentIndex()][1]
        if optimizer is not None:
            fields["optimizer"] = optimizer
        return fields

    def _rows_after_rules(self):
        """The active dataframe (already without excluded rows) narrowed by the
        inclusion / exclusion rules defined in the RuleBuilders."""
        df = self._data_model.get_active_df()
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
        return df

    def _build_training_summary(self, target: str, features: list, rows_used: int,
                                from_config: bool):
        """What the "Review before training" dialog shows: sections of rows
        (value, where it comes from, what it means), warnings and notes."""
        from hamelin.view.widgets.training_summary_dialog import (
            CHOSEN, DEFAULT, DETECTED, SummaryRow, SummarySection)

        dm = self._data_model
        defaults = self._form_defaults
        state = self._collect_form_state()

        def origin(key, detected=False):
            if detected:
                return DETECTED
            return DEFAULT if state[key] == defaults[key] else CHOSEN

        def label(key):
            return t(key).rstrip(": ")

        names = ", ".join(features[:8]) + (f" (+{len(features) - 8})" if len(features) > 8 else "")
        inc = self.inclusion_builder.get_rules() or []
        exc = self.exclusion_builder.get_rules() or []
        secondary = [self.secondary_list.item(i).text() for i in range(self.secondary_list.count())
                     if self.secondary_list.item(i).isSelected()
                     and self.secondary_list.item(i).text() not in (target, *features)]
        data_rows = [
            SummaryRow(t("training.summary.dataset"),
                       Path(str(dm.filepath)).name if getattr(dm, "filepath", None) else "—"),
            SummaryRow(t("training.summary.rows_used"),
                       t("training.summary.rows_value").format(rows_used, len(dm.df)),
                       hint=t("training.summary.rows_used.hint")),
            SummaryRow(t("training.label.outcome.full").rstrip(": "), target),
            SummaryRow(t("training.summary.predictors"),
                       f"{len(features)}: {names}"),
        ]
        if secondary:
            data_rows.append(SummaryRow(label("training.label.secondary_outcomes"), ", ".join(secondary)))
        if inc or exc:
            data_rows.append(SummaryRow(
                t("training.summary.selection"),
                t("training.summary.selection_value").format(len(inc), len(exc))))
        sections = [SummarySection(t("training.summary.section.data"), data_rows)]
        warnings: list[str] = []
        notes: list[str] = []

        if from_config:
            sections.append(SummarySection(t("training.summary.section.model"), [
                SummaryRow(t("training.summary.fixed_config"), t("training.summary.fixed_config.value"),
                           hint=t("training.summary.fixed_config.hint"))]))
        else:
            ptype = _PROBLEM_TYPES[state["problem_type"]][1]
            seconds = int(state["time_budget"])
            holdout = float(state["test_split"])
            strategy = _SEARCH_STRATEGIES[state["search_strategy"]][1]
            early = _EARLY_STOP_MODES[state["early_stop_mode"]][1]
            model_rows = [
                SummaryRow(label("training.label.predictiontype"),
                           t(_PROBLEM_TYPES[state["problem_type"]][0]),
                           origin("problem_type", ptype == self._suggest_problem_type(target)),
                           t("training.summary.hint.prediction_type")),
                SummaryRow(label("training.label.evaluationmetric"), self.metric_combo.currentText(),
                           origin("metric"), t("training.summary.hint.metric")),
                SummaryRow(label("training.label.timebudget"),
                           t("training.summary.time_value").format(seconds, seconds / 60),
                           origin("time_budget"), t("training.summary.hint.time")),
                SummaryRow(label("training.label.testsplit"),
                           t("training.summary.holdout_value").format(holdout * 100, round(rows_used * holdout)),
                           origin("test_split"), t("training.summary.hint.holdout")),
                SummaryRow(label("training.label.randomseed"), str(state["random_seed"]),
                           origin("random_seed"), t("training.summary.hint.seed")),
                SummaryRow(label("training.label.strategy"), t(_SEARCH_STRATEGIES[state["search_strategy"]][0]),
                           origin("search_strategy"), t("training.summary.hint.strategy")),
            ]
            if strategy != "none":
                model_rows.append(SummaryRow(label("training.label.maxiterations"), str(state["max_iterations"]),
                                             origin("max_iterations"), t("training.summary.hint.iterations")))
            model_rows += [
                SummaryRow(label("training.label.paralleltrials"), str(state["parallel_trials"]),
                           origin("parallel_trials"), t("training.summary.hint.parallel")),
                SummaryRow(label("training.label.earlystop_mode"), t(_EARLY_STOP_MODES[state["early_stop_mode"]][0]),
                           origin("early_stop_mode"), t("training.summary.hint.early_stop")),
            ]
            if early == "patience":
                model_rows.append(SummaryRow(label("training.label.earlystop"), str(state["early_stop"]),
                                             origin("early_stop")))
            model_rows += [
                SummaryRow(label("training.label.meanimpute"),
                           t(_MISSING_STRATEGIES[state["missing_values"]][0]),
                           origin("missing_values"), t("training.summary.hint.missing")),
                SummaryRow(label("training.label.imbalance"),
                           t("training.summary.yes") if state["class_imbalance"] else t("training.summary.no"),
                           origin("class_imbalance"), t("training.summary.hint.imbalance")),
                SummaryRow(label("training.label.architecture"), t(_ARCHITECTURES[state["architecture"]][0]),
                           origin("architecture"), t("training.summary.hint.architecture")),
                SummaryRow(label("training.label.optimizer"), t(_OPTIMIZERS[state["optimizer"]][0]),
                           origin("optimizer"), t("training.summary.hint.optimizer")),
            ]
            sections.append(SummarySection(t("training.summary.section.model"), model_rows))
            # Measured on this app's own runs: a 300 s budget took 355-490 s
            # in total (Ray start-up, the trial running when the budget ends,
            # final evaluation) - so roughly +45 s up to 1.5x + 2 min.
            low, high = seconds + 45, int(seconds * 1.5) + 120
            notes.insert(0, t("training.summary.estimate").format(
                max(1, round(low / 60)), max(2, round(high / 60))))
            if rows_used < 100:
                warnings.append(t("training.summary.warn.few_rows").format(rows_used))
            if features and rows_used < 10 * len(features):
                warnings.append(t("training.summary.warn.many_predictors").format(len(features), rows_used))
        notes.append(t("training.summary.note.saved"))
        return sections, warnings, notes

    def _start_training(self):
        """Validate config, build a LudwigTrainerWorker and start it."""
        usage_log.event("Training", "click", "Start Training button")
        log.info("Starting model training")

        if self._too_soon_to_restart():
            return

        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title=t("data.txt.no_dataset_loaded"),
                content=t("training.txt.please_load_a_dataset_in_the"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        if not self.model_name_edit.text().strip():
            InfoBar.warning(
                title=t("training.txt.no_model_name"),
                content=t("training.txt.enter_a_name_for_this_model"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        target = self.primary_combo.currentText().strip()
        if not target:
            InfoBar.warning(
                title=t("training.txt.no_target_variable"),
                content=t("training.txt.select_a_target_variable_outcome_before"),
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
                title=t("training.txt.no_features_selected"),
                content=t("training.txt.select_at_least_one_predictor_variable"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        train_from_config = self._pending_config is not None

        # Catch a Prediction Type that doesn't actually match the outcome
        # column's data BEFORE sending anything to Ludwig. Left uncaught,
        # this doesn't fail until minutes later, deep inside Ludwig's own
        # config validation (Ray cluster already started) with a cryptic
        # pydantic error - reproduced locally: forcing "number" on a
        # column of e.g. "tested_positive"/"tested_negative" text values
        # raises "Config validation error... Feature for stratify column
        # ... must be binary or category" or a validation_metric mismatch,
        # neither of which tells the user what's actually wrong.
        if not train_from_config:
            problem_type = _PROBLEM_TYPES[self.problem_type_combo.currentIndex()][1]
            mismatch = self._problem_type_mismatch(problem_type, target)
            if mismatch:
                InfoBar.error(
                    title=t("training.txt.prediction_type_doesn_t_match_this"),
                    content=mismatch,
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=8000, parent=self,
                )
                return

        from hamelin.view.widgets.training_summary_dialog import confirm_training
        sections, warnings, notes = self._build_training_summary(
            target, features, len(self._rows_after_rules()), train_from_config)
        if not confirm_training(self, sections, warnings, notes):
            usage_log.event("Training", "click", "Summary: back")
            return

        time_limit_s = 0 if train_from_config else self.time_budget.value()

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

        df = self._rows_after_rules()

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
            fields = self._collect_config_fields()
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

        try:
            self._run_settings = self._snapshot_settings(
                target, features, len(df), train_from_config,
                backend_kwargs.get("secondary_outcomes"))
        except Exception as exc:  # noqa: BLE001
            log.warning(f"TrainingPage: could not snapshot training settings — {exc}")
            self._run_settings = None

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

    def _snapshot_settings(self, target: str, features: list, rows_used: int,
                           from_config: bool, secondary: list | None = None) -> dict:
        """Everything chosen on this page for the run about to start, as one
        JSON-able dict. Saved next to the trained model as
        training_settings.json, so a single file answers "how was this model
        trained?": the Ludwig config Hamelin sent (partial - AutoML fills in
        the architecture) plus the settings that are not part of a Ludwig
        config at all (holdout, seed, time budget, patient selection...)."""
        from datetime import datetime, timezone

        from hamelin import __version__
        from hamelin.analytics.automl.ludwig_backend import _fields_to_effective_config

        dm = self._data_model
        fields = {} if from_config else self._collect_config_fields()
        settings: dict = {
            "saved_by": f"Hamelin {__version__} - Training page",
            "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "model_name": self.model_name_edit.text().strip(),
            "trained_from_fixed_config": from_config,
            "dataset": {
                "file": str(dm.filepath) if dm is not None and dm.filepath else None,
                "rows_in_file": int(len(dm.df)) if dm is not None and dm.df is not None else None,
                "rows_used_after_exclusions_and_rules": int(rows_used),
                "outlier_or_removed_rows_excluded": len(dm.excluded_rows) if dm is not None else 0,
                "columns_hidden": sorted(dm.excluded_columns) if dm is not None else [],
                "changes_record": "data_changes.json (in this model's folder)",
            },
            "outcome": target,
            "predictors": list(features),
            "secondary_outcomes": list(secondary or []),
            "patient_selection": {
                "inclusion_rules": self.inclusion_builder.get_rules() or [],
                "exclusion_rules": self.exclusion_builder.get_rules() or [],
            },
        }
        if from_config:
            settings["ludwig_config_used"] = self._pending_config
        else:
            settings["model_configuration"] = {
                "prediction_type": _PROBLEM_TYPES[self.problem_type_combo.currentIndex()][1],
                "evaluation_metric": fields.get("metric", "Ludwig default"),
                "time_budget_seconds": int(self.time_budget.value()),
                "final_evaluation_holdout": float(self.test_split.value()),
                "random_seed": int(self.random_seed.value()),
                "hyperparameter_search_strategy": _SEARCH_STRATEGIES[self.hyperopt_strategy.currentIndex()][1],
                "max_iterations": int(self.hyperopt_trials.value()),
                "parallel_trials": int(self.parallel_trials.value()),
                "early_stopping_mode": fields["early_stop_mode"],
                "early_stopping_patience_rounds": int(self.early_stop.value()),
                "missing_numeric_values_strategy": fields.get("missing_strategy", "Ludwig default"),
                "handle_class_imbalance": bool(fields.get("class_imbalance", False)),
                "model_size": fields.get("architecture", "automatic"),
                "learning_method": fields.get("optimizer", "automatic"),
            }
            settings["notes"] = [
                "early_stopping_mode: 'auto' lets Ludwig's own trial scheduler stop weak trials "
                "(Ludwig forces trainer.early_stop to -1 while that scheduler is active); "
                "'patience' stops each trial after N evaluation rounds without improvement "
                "(hyperopt scheduler switched to fifo); 'off' trains every trial to the end.",
                "final_evaluation_holdout and random_seed are applied by Hamelin when it splits "
                "the data; the seed is also given to Ludwig's search.",
                "time_budget_seconds is Ludwig's hyperopt executor.time_budget_s: a limit on the "
                "search, so the whole run (start-up, last trial, evaluation) takes a bit longer.",
            ]
            settings["partial_ludwig_config_sent"] = _fields_to_effective_config(fields, target)
        return settings

    def _on_early_stop_mode_changed(self) -> None:
        """The patience field only means something in "patience" mode."""
        self.early_stop.setEnabled(_EARLY_STOP_MODES[self.early_stop_mode.currentIndex()][1] == "patience")

    def _on_preview_config_clicked(self) -> None:
        """Show the Ludwig config this run would use, without training."""
        usage_log.event("Training", "click", "Preview Config button")
        from hamelin.analytics.automl.ludwig_backend import _fields_to_effective_config
        from hamelin.view.widgets.config_dialog import show_config_dialog

        target = self.primary_combo.currentText().strip()
        if self._pending_config is not None:
            config = self._pending_config
            note = t("training.preview_config.note.staged")
        else:
            config = _fields_to_effective_config(self._collect_config_fields(), target)
            note = t("training.preview_config.note.auto")
        show_config_dialog(self, t("training.preview_config.title"), config, note)

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
                title=t("data.txt.no_dataset_loaded"),
                content=t("training.txt.please_load_a_dataset_in_the"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        if not self.model_name_edit.text().strip():
            InfoBar.warning(
                title=t("training.txt.no_model_name"),
                content=t("training.txt.enter_a_name_for_this_model"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        target = self.primary_combo.currentText().strip()
        if not target:
            InfoBar.warning(
                title=t("training.txt.no_target_variable"),
                content=t("training.txt.select_a_target_variable_outcome_before"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        path, _ = QFileDialog.getOpenFileName(
            self.window(), t("training.txt.select_config_file"), "", t("training.txt.json_files_json_all_files"),
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            config = payload.get("config", payload)
        except Exception as exc:  # noqa: BLE001
            InfoBar.error(
                title=t("training.txt.could_not_read_config_file"),
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
                title=t("training.txt.no_features_to_train_on"),
                content=(
                    t("training.txt.neither_the_features_list_nor_the")
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
        try:
            self._pending_config = self._pending_config if self._pending_config is not None else config
            self._run_settings = self._snapshot_settings(target, features or [], len(df), True)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"TrainingPage: could not snapshot training settings — {exc}")
            self._run_settings = None

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
                    checkpoints_dir = Path(self._project_dir) / "results" / "models"
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

                    # Everything chosen on this page for this run (see
                    # _snapshot_settings): one readable file next to the
                    # model's own Ludwig config.
                    if getattr(self, "_run_settings", None):
                        try:
                            settings = dict(self._run_settings)
                            settings["saved_model_folder"] = str(checkpoint_dir)
                            (checkpoint_dir / "training_settings.json").write_text(
                                json.dumps(settings, indent=2, default=str), encoding="utf-8")
                        except Exception as exc:  # noqa: BLE001
                            log.warning(f"TrainingPage: could not save training settings — {exc}")

                    # The changes made to the dataset on the Data page (rows /
                    # columns removed, types overridden...), so the model can
                    # be traced back to the exact data it saw.
                    dm = self._data_model
                    if dm is not None and dm.filepath and self._project_dir is not None:
                        from hamelin.core.dataset_changes import copy_to_model, save_record
                        save_record(dm, self._project_dir)
                        copy_to_model(self._project_dir, dm.filepath, checkpoint_dir)

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

        # The winning model is saved above; Ludwig's per-trial dumps (hundreds
        # of MB of checkpoints) are of no further use.
        if self._project_dir is not None:
            from hamelin.core.project_layout import remove_trial_dumps
            remove_trial_dumps(self._project_dir)

        # Notify MainWindow (→ DashboardPage.refresh, history widgets)
        self.training_finished.emit(result)

    def _on_training_error(self, message: str) -> None:
        """Handle worker error or cancellation."""
        log.warning(f"TrainingPage: training error — {message}")
        self._last_training_end_ts = time.monotonic()
        if self._project_dir is not None:
            from hamelin.core.project_layout import remove_trial_dumps
            remove_trial_dumps(self._project_dir)
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
            title=t("training.txt.training_failed"),
            content=message,
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=6000, parent=self,
        )

    def refresh_history(self, project_dir) -> None:
        """Reload the history and timeline widgets after a training run."""
        self._history_widget.load(project_dir)
        self._timeline_widget.load(project_dir)
        self._refresh_default_model_name()
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
                title=t("training.txt.no_trained_model"),
                content=t("training.txt.train_a_model_first_before_exporting"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self.window(),
            t("training.txt.save_model_report"),
            default_export_path(self._project_dir, "reports", "hamelin_model.json"),
            t("training.txt.json_files_json_all_files"),
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
            title=t("training.txt.model_report_saved"),
            content=t("training.txt.saved_to_0").format(path),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self,
        )
        log.info(f"Model report exported to {path} ({len(export_data)} fields)")
        usage_log.event("Training", "exported", "Model report", Path(path).name)

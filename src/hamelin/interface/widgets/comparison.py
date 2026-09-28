from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize

import hamelin.interface.utils.get_model_paths as gmp
from hamelin.interface.utils.metrix_extractor import load_run_metrics, extract_test_metrics, get_target_column
from hamelin.interface.utils.metric_labels import get_metric_info
from hamelin.interface.utils.widgets import RoundedButton, BackgroundWidget, ErrorPopup, AdvancedModeToggle, set_asset_icon
from hamelin.interface.utils.colors import COLORS, themed, themed_add
from hamelin.interface.utils.app_state import app_state
from hamelin.interface.utils.favorites import is_favorite
from hamelin.interface.widgets.dropdowns import SimpleDropdown, CheckBoxDropdown

models = gmp.get_model_names()


# COMPARISON PAGE

class ComparisonWindow(BackgroundWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Comparison of Models")
        self.resize(1512, 982)
        self._known_models = models

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)

        # TOP BAR
        top = QHBoxLayout()

        self.home = RoundedButton("  Dashboard", 300, 80, 40)
        set_asset_icon(self.home, "home.svg")
        self.home.setIconSize(QSize(32, 32))

        top.addWidget(self.home)
        top.addStretch()

        self.advanced_toggle = AdvancedModeToggle()
        self.advanced_toggle.setChecked(app_state.advanced_mode)
        self.advanced_toggle.toggled.connect(app_state.set_advanced_mode)
        app_state.advancedModeChanged.connect(self._on_advanced_mode_changed)
        top.addWidget(self.advanced_toggle)

        root.addLayout(top)
        root.addSpacing(20)

        # CENTER
        center = QVBoxLayout()
        center.setSpacing(26)

        # TITLE
        self.title = QLabel("Comparison of Models")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setMaximumWidth(600)
        themed(self.title, lambda c: f"""
            background:{c.surface};
            color:{c.text};
            border: 2px solid {c.border};
            padding:10px 20px;
            font-size:48px;
            font-weight:700;
            border-radius: 10px;
        """)

        center.addWidget(self.title, alignment=Qt.AlignHCenter)

        self.empty_hint = QLabel(
            "No trained models found in ./results yet. Train a Ludwig "
            "model into that folder, then come back here to compare it."
        )
        self.empty_hint.setAlignment(Qt.AlignCenter)
        self.empty_hint.setWordWrap(True)
        self.empty_hint.setMaximumWidth(700)
        themed(self.empty_hint, f"color:{COLORS['white']}; font-size:20px;")
        self.empty_hint.setVisible(not models)
        center.addWidget(self.empty_hint, alignment=Qt.AlignHCenter)

        # MODELS
        self.model_dropdown = CheckBoxDropdown(
            "Select Models", models, favorite_check=is_favorite, annotate=self._annotate_model
        )
        center.addWidget(self.model_dropdown)

        # COMPARE CONFIGS (pairwise, so it only makes sense - and only
        # enables - once exactly 2 models are checked above)
        config_diff_row = QHBoxLayout()
        config_diff_row.addStretch()

        self.config_diff_btn = RoundedButton("Compare Settings", 340, 72, 36)
        themed_add(self.config_diff_btn, f"""
            QPushButton {{ font-size: 22px; }}
            QPushButton:disabled {{
                background: #7A7A7A;
                color: #D0D0D0;
                border: 2px solid #7A7A7A;
            }}
        """)
        self.config_diff_btn.setEnabled(False)
        self.config_diff_btn.setToolTip("Select exactly 2 models above to compare their settings.")
        self.config_diff_btn.clicked.connect(self.on_compare_configs_clicked)
        config_diff_row.addWidget(self.config_diff_btn)

        config_diff_row.addStretch()
        center.addLayout(config_diff_row)

        self.model_dropdown.selectionChanged.connect(self._update_config_diff_button)
        self._update_config_diff_button()

        # CRITERION (built from every metric available across all models)
        self.display_labels, self.metrics_keys = self._collect_criteria(models)

        self.criteria_dropdown = SimpleDropdown(
            "Select Metric",
            self.display_labels
        )

        center.addWidget(self.criteria_dropdown)

        # VIEW MODE
        self.view_dropdown = SimpleDropdown(
            "Select Visualization Mode",
            ["Graph", "Table", "Heatmap", "Radar"]
        )
        center.addWidget(self.view_dropdown)

        # LAUNCH
        self.launch = RoundedButton("⌕  Launch Comparison", 800, 96, 48)
        self._update_launch_state(models)
        center.addWidget(self.launch, alignment=Qt.AlignHCenter)

        root.addLayout(center)
        root.addStretch()

        # LOGIC
        self.launch.clicked.connect(self.on_compare_clicked)
        self.home.clicked.connect(self._go_back)

    @staticmethod
    def _annotate_model(model_name):
        # Shown next to each model in the selection list so it's harder to
        # pick models that don't even predict the same thing without
        # noticing - see get_target_column().
        target = get_target_column(model_name)
        return f"Predicts: {target}" if target else None

    def _go_back(self):
        if self.parent() and hasattr(self.parent(), "go_landing"):
            self.parent().go_landing()

    @staticmethod
    def _collect_criteria(model_names):
        """Every test metric available across the given models, deduplicated
        and paired (display name, full metrics.json key)."""
        display_names = []
        full_keys = []

        for m in model_names:
            metrics = load_run_metrics(m) or {}
            names, keys = extract_test_metrics(metrics)
            display_names.extend(names)
            full_keys.extend(keys)

        final_labels = []
        final_keys = []
        seen = set()

        for name, key in zip(display_names, full_keys):
            if key not in seen:
                seen.add(key)
                final_labels.append(get_metric_info(name)["label"])
                final_keys.append(key)

        return final_labels, final_keys

    def _update_launch_state(self, model_names):
        self.launch.setEnabled(bool(model_names))
        self.launch.setToolTip("" if model_names else "No models available to compare yet.")

    def showEvent(self, event):
        super().showEvent(event)
        # Models trained after this page was first built otherwise wouldn't
        # show up until the app was restarted, since the dropdowns were only
        # ever populated once, at construction time. Only touch anything if
        # the list actually changed, so simply navigating back to this page
        # doesn't wipe out models someone already checked.
        current_models = gmp.get_model_names()
        if current_models == self._known_models:
            self.model_dropdown.refresh_favorites()
            return
        self._known_models = current_models

        self.empty_hint.setVisible(not current_models)
        self.model_dropdown.set_items(current_models)

        self.display_labels, self.metrics_keys = self._collect_criteria(current_models)
        self.criteria_dropdown.clear()
        self.criteria_dropdown.addItems(self.display_labels)

        self._update_launch_state(current_models)

    def on_compare_clicked(self):
        if not self.get_selected_models():
            ErrorPopup(self, "Please select at least a model.").show()
            return

        if not self.criteria_dropdown.get_selected():
            ErrorPopup(self, "Please select a criterion.").show()
            return

        if not self.get_view_mode():
            ErrorPopup(self, "Please select a visualization mode.").show()
            return

        self.main_window.launch_comparison(
            self.get_selected_models(),
            self.get_selected_criterion(),
            self.get_view_mode()
        )

    def _update_config_diff_button(self):
        advanced = app_state.advanced_mode
        self.config_diff_btn.setVisible(advanced)
        self.config_diff_btn.setEnabled(advanced and len(self.model_dropdown.get_selected()) == 2)

    def _on_advanced_mode_changed(self, value):
        self.advanced_toggle.setChecked(value)
        self._update_config_diff_button()

    def on_compare_configs_clicked(self):
        selected = self.model_dropdown.get_selected()
        if len(selected) != 2:
            return
        self.main_window.launch_config_diff(selected[0], selected[1])

    def get_selected_models(self):
        return self.model_dropdown.get_selected()

    def get_view_mode(self):
        return self.view_dropdown.get_selected()

    def get_selected_criterion(self):
        label = self.criteria_dropdown.get_selected()
        idx = self.display_labels.index(label)
        return self.metrics_keys[idx]

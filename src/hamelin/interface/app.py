import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
)

import hamelin.interface.widgets.landing_page as landing
import hamelin.interface.widgets.confusion_matrix as cmx
import hamelin.interface.widgets.comparison as comparison
import hamelin.interface.widgets.visualise_comparison_table as visualise_comparison_table
import hamelin.interface.widgets.visualise_comparison_graphs as visualise_comparison_graphs
import hamelin.interface.widgets.one_model as one_model
import hamelin.interface.widgets.model_types as model_type_info
import hamelin.interface.widgets.visualise_gif as visualise_gif
import hamelin.interface.widgets.visualise_comparison_heatmap as visualise_comparison_heatmap
import hamelin.interface.widgets.visualise_comparison_radar as visualise_comparison_radar
import hamelin.interface.widgets.visualise_config_diff as visualise_config_diff
import hamelin.interface.widgets.duplicate_model as duplicate_model
import hamelin.interface.utils.get_model_paths as gmp
from hamelin.interface.utils.widgets import BackgroundWidget, ErrorPopup
from hamelin.interface.utils.colors import themed


class _ActivePageStack(QStackedWidget):
    """A plain QStackedWidget's own sizeHint/minimumSizeHint is the max
    across EVERY page it holds, not just whichever one is currently shown -
    so even a page as small as the landing page gets stretched (and, when
    embedded in something narrower than that max, made to scroll) to fit
    the single widest page anywhere in the app (a wide comparison table),
    regardless of which page is actually on screen. Sizing to only the
    current page instead means each page claims only the room it actually
    needs when it's the one showing."""

    def sizeHint(self):
        current = self.currentWidget()
        return current.sizeHint() if current is not None else super().sizeHint()

    def minimumSizeHint(self):
        current = self.currentWidget()
        return current.minimumSizeHint() if current is not None else super().minimumSizeHint()


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ML Dashboard")
        self.resize(1512, 982)

        # Main layout

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Background widget

        self.background = BackgroundWidget()
        root_layout.addWidget(self.background)

        bg_layout = QVBoxLayout(self.background)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)

        # Stacked pages

        self.stack = _ActivePageStack()

        themed(self.stack, """
            QStackedWidget {
                background: transparent;
            }
        """)

        bg_layout.addWidget(self.stack)

        # Pages

        self.landing = landing.LandingPage()

        self.confusion = cmx.ConfusionMatrixWidget()

        self.comparison = comparison.ComparisonWindow(self)
        self.comparison.main_window = self

        self.visualisecomparison_table = (
            visualise_comparison_table.VisualiseComparisonWidget()
        )

        self.visualisecomparison_graphs = (
            visualise_comparison_graphs.VisualiseComparisonGraphsWidget()
        )

        self.visualisecomparison_heatmap = (
            visualise_comparison_heatmap.VisualiseComparisonHeatmap()
        )

        self.visualisecomparison_radar = (
            visualise_comparison_radar.VisualiseComparisonRadarWidget()
        )

        self.one_model= one_model.VisualiseOneModel()

        self.visualisation_gif = visualise_gif.VisualiseGifWidget()

        self.model_type_info = model_type_info.ModelTypeInfoWidget()

        self.visualisecomparison_configdiff = (
            visualise_config_diff.VisualiseConfigDiffWidget()
        )

        self.duplicate_model = duplicate_model.DuplicateModelWidget()

        # Navigation

        self.landing.btn_confusion.clicked.connect(
            self.go_confusion
        )

        self.confusion.btn_home.clicked.connect(
            self.go_landing
        )

        self.landing.btn_comparison.clicked.connect(
            self.go_comparison
        )

        self.landing.btn_single_model_visualization.clicked.connect(
            self.go_visualisation
        )

        self.comparison.home.clicked.connect(
            self.go_landing
        )

        self.visualisecomparison_table.btn_home.clicked.connect(
            self.go_landing
        )

        self.visualisecomparison_table.btn_back.clicked.connect(
            self.go_comparison
        )

        self.visualisecomparison_graphs.btn_home.clicked.connect(
            self.go_landing
        )

        self.visualisecomparison_heatmap.btn_home.clicked.connect(
            self.go_landing
        )

        self.visualisecomparison_heatmap.btn_back.clicked.connect(
            self.go_comparison
        )

        self.visualisecomparison_graphs.btn_back.clicked.connect(
            self.go_comparison
        )

        self.visualisecomparison_radar.btn_home.clicked.connect(
            self.go_landing
        )

        self.visualisecomparison_radar.btn_back.clicked.connect(
            self.go_comparison
        )

        self.landing.btn_radar_comparison.clicked.connect(
            self.go_radar_comparison
        )

        self.one_model.btn_home.clicked.connect(
            self.go_landing
        )

        self.one_model.btn_back.clicked.connect(
            self.go_comparison
        )

        self.visualisation_gif.btn_home.clicked.connect(
            self.go_landing
        )

        self.visualisation_gif.btn_analyse_main.clicked.connect(
    self.go_model_from_gif
)

        self.visualisation_gif.btn_info.clicked.connect(
            self.go_model_types_from_gif
        )



        self.landing.btn_model_types.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.model_type_info)
        )

        self.model_type_info.btn_home.clicked.connect(
            self.go_landing
        )

        self.visualisecomparison_configdiff.btn_home.clicked.connect(
            self.go_landing
        )

        self.visualisecomparison_configdiff.btn_back.clicked.connect(
            self.go_comparison
        )

        self.landing.btn_duplicate_model.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.duplicate_model)
        )

        self.duplicate_model.btn_home.clicked.connect(
            self.go_landing
        )

        self.duplicate_model.btn_back.clicked.connect(
            self.go_landing
        )

        # "Continue to Training" only leads somewhere when this dashboard is
        # embedded in Hamelin (which connects open_training_requested to its
        # own training page). Standalone, there is no training page, so say so
        # instead of leaving the button looking broken.
        self.duplicate_model.open_training_requested.connect(
            self._on_duplicate_open_training
        )

        # Add pages

        self.stack.addWidget(self.landing)
        self.stack.addWidget(self.confusion)
        self.stack.addWidget(self.comparison)
        self.stack.addWidget(self.visualisecomparison_table)
        self.stack.addWidget(self.visualisecomparison_graphs)
        self.stack.addWidget(self.visualisecomparison_heatmap)
        self.stack.addWidget(self.visualisecomparison_radar)
        self.stack.addWidget(self.one_model)
        self.stack.addWidget(self.visualisation_gif)
        self.stack.addWidget(self.model_type_info)
        self.stack.addWidget(self.visualisecomparison_configdiff)
        self.stack.addWidget(self.duplicate_model)
        self.stack.setCurrentWidget(self.landing)

    # Navigation

    def go_confusion(self):
        self.stack.setCurrentWidget(self.confusion)

    def go_comparison(self):
        self.stack.setCurrentWidget(self.comparison)

    def go_landing(self):
        self.stack.setCurrentWidget(self.landing)

    def _on_duplicate_open_training(self, _payload):
        ErrorPopup(
            self.duplicate_model,
            "The training page is only available when this dashboard runs "
            "inside Hamelin.",
        ).show()

    def go_model(self, model):
        self.one_model.set_data(model, criterion=None, view_mode=None)
        self.stack.setCurrentWidget(self.one_model)

    def go_model_from_gif(self):
        model = self.visualisation_gif.current_model
        if not model:
            ErrorPopup(self.visualisation_gif, "Please select a model first.").show()
            return
        self.go_model(model)

    def go_model_types_from_gif(self):
        if not self.visualisation_gif.current_model:
            ErrorPopup(self.visualisation_gif, "Please select a model first.").show()
            return

        # RNN is what detect_model_type_from_ludwig() calls an LSTM-based
        # model; the info page's dropdown only offers CNN/MLP/LSTM.
        detected = self.visualisation_gif.model_type_badge.text()
        model_type = {"RNN": "LSTM"}.get(detected, detected)

        if model_type in ("CNN", "MLP", "LSTM"):
            self.model_type_info.dropdown.selected = model_type
            self.model_type_info.dropdown._update_label()

        self.stack.setCurrentWidget(self.model_type_info)

    def go_visualisation(self):
        self.stack.setCurrentWidget(self.visualisation_gif)

    def go_radar_comparison(self):
        # Opens the radar page directly - it has its own model selection
        # (a primary model + an "Include in comparison" multi-select, both
        # refreshed live from gmp.get_model_names()), so it doesn't need to
        # go through the Comparison Dashboard's picker first.
        self.visualisecomparison_radar.set_data([])
        self.stack.setCurrentWidget(self.visualisecomparison_radar)

    # Comparison callback

    def launch_comparison(self, models, criterion, view_mode):
        self.selected_models = models
        self.selected_criterion = criterion

        if view_mode == "Table":
            self.visualisecomparison_table.set_data(
                models,
                criterion,
            )
            self.stack.setCurrentWidget(self.visualisecomparison_table)
        elif view_mode == "Graph":
            self.visualisecomparison_graphs.set_data(
                models,
                criterion,
            )
            self.stack.setCurrentWidget(self.visualisecomparison_graphs)
        elif view_mode == "Heatmap":
            self.visualisecomparison_heatmap.set_data(
                models,
                criterion,
            )
            self.stack.setCurrentWidget(self.visualisecomparison_heatmap)
        elif view_mode == "Radar":
            self.visualisecomparison_radar.set_data(
                models,
                criterion,
            )
            self.stack.setCurrentWidget(self.visualisecomparison_radar)

    def launch_config_diff(self, model_a, model_b):
        self.visualisecomparison_configdiff.set_data(model_a, model_b)
        self.stack.setCurrentWidget(self.visualisecomparison_configdiff)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())
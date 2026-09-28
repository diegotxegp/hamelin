from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QLabel,
    QVBoxLayout, QHBoxLayout,
    QSizePolicy
)

from hamelin.interface.widgets.dropdowns import SimpleDropdown
from hamelin.interface.utils.widgets import RoundedButton, set_asset_icon
from hamelin.interface.utils.colors import COLORS, GRAY, WHITE, themed
import hamelin.interface.utils.get_model_paths as gmp
from hamelin.interface.utils.metrix_extractor import load_run_metrics
from hamelin.interface.utils.favorites import is_favorite, toggle_favorite

CARD_WIDTH = 1100
BUTTON_HEIGHT = 70
# 22, not the original 38 - root.setSpacing() already adds its own gap
# between every pair of top-level rows, so each addSpacing(GAP) call was
# stacking on top of that rather than replacing it, adding up (with the
# root spacing itself) to a page taller than most windows' usable height -
# the actual reason this page needed to scroll. Same fix pattern as the
# landing page and one_model.py earlier this session. Eased back up a bit
# from the first pass's 14 - that one felt cramped.
GAP = 22
ANALYSE_BTN_WIDTH = 400

# How many predictive-variable names to spell out before collapsing the
# rest into "+N more" - a clinical dataset can easily have 40+ columns,
# which would otherwise make the details card unreadably tall.
_FEATURES_SHOWN = 8


def _format_feature_list(names):
    if len(names) <= _FEATURES_SHOWN:
        return ", ".join(names)
    shown = ", ".join(names[:_FEATURES_SHOWN])
    return f"{shown}, … (+{len(names) - _FEATURES_SHOWN} more)"


def infer_output_type(model_path, metrics=None):
    """What kind of answer the model gives, read from the actual Ludwig run
    report rather than guessed from which metrics happen to be present
    (that heuristic previously mislabeled, e.g., regression models whose
    metric family also included generic error terms)."""
    info = gmp.get_output_feature_info(model_path)
    output_type = info.get("type")

    if output_type:
        label = gmp.OUTPUT_TYPE_LABELS.get(output_type, output_type.title())
        return label

    keys = set()
    for k in (metrics or {}).keys():
        if not k.startswith("test/"):
            continue
        keys.add(k.split("/")[-2].lower())

    classification_hints = {"accuracy", "acc", "precision", "recall", "f1", "specificity"}
    if keys & classification_hints:
        return "Classification (estimated)"
    if "loss" in keys:
        return "Regression (estimated)"
    return "Not identified"


class VisualiseGifWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.models = []
        self.current_model = None

        self.root = QVBoxLayout(self)
        themed(self, """
            QWidget {
                font-family: "Liberation Sans";
            }
        """)
        self.root.setContentsMargins(36, 28, 36, 32)
        self.root.setSpacing(18)

        top = QHBoxLayout()
        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        set_asset_icon(self.btn_home, "home.svg")
        self.btn_home.setIconSize(QSize(32, 32))
        top.addWidget(self.btn_home)
        top.addStretch()

        self.root.addLayout(top)

        self.title = QLabel("Visualisation of the Model's Execution")
        self.title.setAlignment(Qt.AlignCenter)
        themed(self.title, lambda c: f"""
            background: {c.surface};
            color: {c.text};
            border: 2px solid {c.border};
            padding: 14px 22px;
            font-size: 38px;
            font-weight: 700;
            border-radius: 10px;
        """)
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        self.root.addLayout(title_layout)

        self.root.addSpacing(16)

        self.model_selector = SimpleDropdown("Select Model", [], favorite_check=is_favorite)
        # Min/max instead of a hard fixed width so this can shrink on
        # narrower or scaled-DPI screens instead of clipping/overflowing.
        self.model_selector.setMinimumWidth(520)
        self.model_selector.setMaximumWidth(CARD_WIDTH)
        self.model_selector.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.model_selector)

        self.favorite_btn = RoundedButton("☆", 70, 70, 35)
        self.favorite_btn.setToolTip("Mark this model as a favorite")
        self.favorite_btn.clicked.connect(self._toggle_favorite)
        row.addWidget(self.favorite_btn)

        row.addStretch()
        self.root.addLayout(row)
        self.model_selector.currentIndexChanged.connect(self.on_model_changed)

        self.favorite_btn.hide()

        self.root.addSpacing(GAP)

        # One card, everything about the selected model in it: the type/
        # output badges up top, then the project + variables detail lines -
        # used to be two separate stacked cards (yellow badges, white
        # details), merged into one to cut the vertical space between them.
        self.details_card = details_card = QWidget()
        details_card.setMinimumWidth(780)
        details_card.setMaximumWidth(CARD_WIDTH)
        details_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        details_card.setObjectName("detailsCard")
        details_card.setAttribute(Qt.WA_StyledBackground, True)
        themed(details_card, lambda c: f"""
            QWidget#detailsCard {{
                background: {c.accent_fill};
                border-radius: 16px;
                border: 2px solid {c.accent_edge};
            }}
        """)
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(26, 18, 26, 18)
        details_layout.setSpacing(10)

        type_row = QHBoxLayout()
        type_row.setSpacing(14)

        type_prefix = QLabel("Model Type :")
        themed(type_prefix, lambda c: f"""
            font-size: 22px;
            font-weight: 600;
            color: {c.text};
            background: transparent;
            border: none;
        """)

        self.model_type_badge = QLabel("—")
        self.model_type_badge.setAlignment(Qt.AlignCenter)
        themed(self.model_type_badge, lambda c: f"""
            background: transparent;
            color: {c.text};
            font-size: 28px;
            font-weight: 700;
            border: none;
        """)

        output_prefix = QLabel("Predicts :")
        themed(output_prefix, lambda c: f"""
            font-size: 22px;
            font-weight: 600;
            color: {c.text};
            background: transparent;
            border: none;
        """)

        self.output_type_badge = QLabel("—")
        self.output_type_badge.setAlignment(Qt.AlignCenter)
        themed(self.output_type_badge, lambda c: f"""
            background: transparent;
            color: {c.text};
            font-size: 28px;
            font-weight: 700;
            border: none;
        """)

        type_row.addStretch()
        type_row.addWidget(type_prefix)
        type_row.addWidget(self.model_type_badge)
        type_row.addSpacing(20)
        type_row.addWidget(output_prefix)
        type_row.addWidget(self.output_type_badge)
        type_row.addStretch()
        details_layout.addLayout(type_row)

        label_style = lambda c: f"font-size: 16px; color: {c.text}; background: transparent; border: none;"

        self.project_label = QLabel("")
        self.project_label.setWordWrap(True)
        themed(self.project_label, lambda c: f"font-size: 19px; font-weight: 700; color: {c.text}; background: transparent; border: none;")
        self.project_label.setVisible(False)

        self.objective_label = QLabel("")
        self.objective_label.setWordWrap(True)
        themed(self.objective_label, label_style)
        self.objective_label.setVisible(False)

        self.target_label = QLabel("Target variable: —")
        self.target_label.setWordWrap(True)
        themed(self.target_label, label_style)

        self.features_label = QLabel("Predictive variables: —")
        self.features_label.setWordWrap(True)
        themed(self.features_label, label_style)

        self.eval_size_label = QLabel("Evaluated on: —")
        self.eval_size_label.setWordWrap(True)
        themed(self.eval_size_label, label_style)

        details_layout.addWidget(self.project_label)
        details_layout.addWidget(self.objective_label)
        details_layout.addWidget(self.target_label)
        details_layout.addWidget(self.features_label)
        details_layout.addWidget(self.eval_size_label)

        details_row = QHBoxLayout()
        details_row.addStretch()
        details_row.addWidget(details_card)
        details_row.addStretch()
        self.root.addLayout(details_row)

        self.root.addSpacing(GAP)

        self.btn_info = RoundedButton("Learn More about This Model Type", 600, BUTTON_HEIGHT, 30)
        themed(self.btn_info, lambda c: f"""
            QPushButton {{
                background: {GRAY};
                color: {WHITE};
                font-size: 26px;
                font-weight: 700;
                border-radius: 19px;
                border: none;
            }}
            QPushButton:hover {{ background: #106EBE; }}
        """)

        info_row = QHBoxLayout()
        info_row.addStretch()
        info_row.addWidget(self.btn_info)
        info_row.addStretch()
        self.root.addLayout(info_row)
        self.root.addSpacing(GAP)
        analyse_row = QHBoxLayout()

        self.btn_analyse_main = RoundedButton("Analyse the Model's Results", 700, BUTTON_HEIGHT, 30)
        themed(self.btn_analyse_main, lambda c: f"""
            QPushButton {{
                background: {c.primary_fill};
                color: {WHITE};
                font-size: 28px;
                font-weight: 700;
                border-radius: 30px;
                border: none;
            }}
            QPushButton:hover {{ background: {c.line}; }}
        """)

        analyse_row.addStretch()
        analyse_row.addWidget(self.btn_analyse_main)
        analyse_row.addStretch()
        self.root.addLayout(analyse_row)
        self.root.addStretch()

        self.init_models()

    def init_models(self):
        self.models = gmp.get_model_names() or []
        self.model_selector.clear()
        self.model_selector.addItems(self.models)
        self._set_results_visible(False)

    def _set_results_visible(self, visible):
        # The favorite button and the details card (badges + project/
        # variables) only mean something once a model is actually picked -
        # a card full of "—" placeholders isn't useful, just clutter. The
        # action buttons stay visible either way, so clicking them with
        # nothing selected is what surfaces the "please select a model"
        # error instead of the buttons themselves silently disappearing.
        self.favorite_btn.setVisible(visible)
        self.details_card.setVisible(visible)

    def on_model_changed(self):
        model = self.model_selector.currentText()
        if not model:
            self.current_model = None
            self.model_type_badge.setText("—")
            self.output_type_badge.setText("—")
            self.project_label.setVisible(False)
            self.objective_label.setVisible(False)
            self.target_label.setText("Target variable: —")
            self.features_label.setText("Predictive variables: —")
            self.features_label.setToolTip("")
            self.eval_size_label.setText("Evaluated on: —")
            self._set_results_visible(False)
            return

        self.current_model = model
        model_path = gmp.model_path_from_name(model)
        model_type = gmp.detect_model_type_from_ludwig(model_path)
        self.model_type_badge.setText(model_type)

        metrics = load_run_metrics(model) or {}
        self.output_type_badge.setText(infer_output_type(model_path, metrics))

        self._update_details_card(model_path)

        self._update_favorite_button(is_favorite(model))
        self._set_results_visible(True)

    def _update_details_card(self, model_path):
        project = gmp.get_project_info()
        if project.get("name"):
            header = project["name"]
            if project.get("protocol_number"):
                header += f" (protocol {project['protocol_number']})"
            self.project_label.setText(f"Project: {header}")
            self.project_label.setVisible(True)

            objective = project.get("primary_objective")
            if objective:
                self.objective_label.setText(f"Primary objective: {objective}")
                self.objective_label.setVisible(True)
            else:
                self.objective_label.setVisible(False)
        else:
            # Standalone interface, no INTERFACE_RESULTS_DIR project - no
            # metadata.json to read, so nothing to show here.
            self.project_label.setVisible(False)
            self.objective_label.setVisible(False)

        target = gmp.get_output_feature_info(model_path).get("name")
        self.target_label.setText(f"Target variable: {target}" if target else "Target variable: —")

        features = gmp.get_input_feature_names(model_path)
        self.features_label.setText(f"Predictive variables: {_format_feature_list(features)}"
                                     if features else "Predictive variables: —")
        self.features_label.setToolTip(", ".join(features) if len(features) > _FEATURES_SHOWN else "")

        size, is_exact = gmp.get_evaluated_size(model_path)
        if size is None:
            self.eval_size_label.setText("Evaluated on: unknown")
        elif is_exact:
            self.eval_size_label.setText(f"Evaluated on: {size} patients")
        else:
            self.eval_size_label.setText(
                f"Evaluated on: ~{size} patients (whole dataset - exact test size not recorded for this run)"
            )

    def _toggle_favorite(self):
        model = self.model_selector.currentText()
        if not model:
            return
        self._update_favorite_button(toggle_favorite(model))
        self.model_selector.refresh_favorites()

    def _update_favorite_button(self, is_fav):
        self.favorite_btn.setText("★" if is_fav else "☆")
        self.favorite_btn.set_accent(COLORS['yellow'] if is_fav else None)
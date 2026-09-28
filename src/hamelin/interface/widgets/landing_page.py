import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import shutil
from pathlib import Path

from PySide6.QtCore import Qt, QEvent, QUrl, QSize
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)

from hamelin.interface.utils.widgets import RoundedButton, Popup, ErrorPopup, set_asset_icon, load_app_fonts
from hamelin.interface.utils.colors import YELLOW, BLACK, INFO_YELLOW, INFO_YELLOW_HOVER, themed, themed_add
from hamelin.interface.utils.favorites import is_favorite
import hamelin.interface.utils.get_model_paths as gmp

ICON_SIZE = QSize(28, 28)


class LandingPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("landingPage")
        self.popup = None

        load_app_fonts()

        self.setFont(QFont("Inter", 11))

        self.init_ui()

    def init_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)
        # 20, not the original 40 - with ~13 top-level rows on this page,
        # that spacing alone was ~480px, nearly half the page's total
        # height and the main reason it needed to scroll vertically even
        # maximized. Same rows, same order, just a tighter vertical rhythm.
        main_layout.setSpacing(20)

        title_frame = QWidget()
        title_frame.setObjectName("titleFrame")
        title_frame.setAttribute(Qt.WA_StyledBackground, True)
        themed(title_frame, lambda c: f"QWidget#titleFrame {{ background: {c.surface}; border: 2px solid {c.border}; border-radius: 14px; }}")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(36, 20, 36, 20)
        title_layout.setSpacing(6)

        big_title = QLabel("Machine Learning Visualization Dashboard")
        big_title.setObjectName("bigTitle")
        big_title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(big_title)


        title_row = QHBoxLayout()
        title_row.addStretch()
        title_row.addWidget(title_frame)
        title_row.addStretch()
        main_layout.addLayout(title_row)

        model_count = len(gmp.get_model_names(gmp.RESULTS_DIR))
        self.models_badge = RoundedButton("", 550, 60, 22)
        set_asset_icon(self.models_badge, "models_badge.svg")
        self.models_badge.setIconSize(ICON_SIZE)
        self.models_badge.setCursor(Qt.PointingHandCursor)
        self.models_badge.setToolTip("Open the results folder")
        self.models_badge.clicked.connect(self.open_models_folder)

        badge_row = QHBoxLayout()
        badge_row.addStretch()
        badge_row.addWidget(self.models_badge)
        badge_row.addStretch()
        main_layout.addLayout(badge_row)

        self.cleanup_btn = RoundedButton("Delete non-favorite models", 380, 50, 20)
        themed_add(self.cleanup_btn, "QPushButton{font-size:16px;}")
        self.cleanup_btn.setCursor(Qt.PointingHandCursor)
        self.cleanup_btn.setToolTip(
            "Permanently deletes every trained model that isn't starred as a "
            "favorite. Keeps whatever you've marked as a favorite."
        )
        self.cleanup_btn.clicked.connect(self.delete_non_favorite_models)

        cleanup_row = QHBoxLayout()
        cleanup_row.addStretch()
        cleanup_row.addWidget(self.cleanup_btn)
        cleanup_row.addStretch()
        main_layout.addLayout(cleanup_row)

        self.empty_hint = QLabel(
            "No trained models found yet. Train a Ludwig model into "
            "the ./results folder (or click the badge above to open "
            "it), then reload this dashboard."
        )
        self.empty_hint.setAlignment(Qt.AlignCenter)
        self.empty_hint.setWordWrap(True)
        themed(self.empty_hint, lambda c: f"color:{c.muted}; font-size:16px;")
        hint_row = QHBoxLayout()
        hint_row.addStretch()
        hint_row.addWidget(self.empty_hint)
        hint_row.addStretch()
        main_layout.addLayout(hint_row)

        self._refresh_model_badge()

        main_layout.addSpacing(10)

        section_frame = QWidget()
        section_frame.setObjectName("sectionFrame")
        section_frame.setAttribute(Qt.WA_StyledBackground, True)
        # See title_frame above re: the "#sectionFrame" ID selector.
        themed(section_frame, lambda c: f"QWidget#sectionFrame {{ background: {c.surface}; border: 2px solid {c.border}; border-radius: 10px; }}")
        section_inner = QVBoxLayout(section_frame)
        section_inner.setContentsMargins(20, 10, 20, 10)

        section_title = QLabel("Available Tools")
        section_title.setObjectName("sectionTitle")
        section_inner.addWidget(section_title)

        section_row = QHBoxLayout()
        section_row.addWidget(section_frame)
        section_row.addStretch()
        main_layout.addLayout(section_row)

        # SINGLE-MODEL TOOLS
        single_title_frame = QWidget()
        single_title_frame.setObjectName("singleTitleFrame")
        single_title_frame.setAttribute(Qt.WA_StyledBackground, True)
        themed(single_title_frame, lambda c: f"QWidget#singleTitleFrame {{ background: {c.surface}; border: 2px solid {c.border}; border-radius: 10px; }}")
        single_title_inner = QVBoxLayout(single_title_frame)
        single_title_inner.setContentsMargins(16, 8, 16, 8)

        single_title = QLabel("Single-Model Tools")
        single_title.setObjectName("groupTitle")
        single_title_inner.addWidget(single_title)

        single_title_row = QHBoxLayout()
        single_title_row.addWidget(single_title_frame)
        single_title_row.addStretch()
        main_layout.addLayout(single_title_row)

        single_row = QHBoxLayout()
        single_row.setSpacing(28)

        self.btn_single_model_visualization = self.create_nav_button(
            "Single Model Visualization",
            icon_name="single_model_visualization.svg",
            width=400,
        )
        self.btn_confusion = self.create_nav_button(
            "Confusion Matrix", icon_name="confusion_matrix.svg", width=320
        )
        self.btn_model_types = self.create_nav_button(
            "Model Types Explanations",
            icon_name="model_execution_visualization.svg",
            width=400,
        )
        self.btn_duplicate_model = self.create_nav_button(
            "Duplicate a Model", width=320,
        )

        single_row.addWidget(self.btn_single_model_visualization)
        single_row.addWidget(self.btn_confusion)
        single_row.addWidget(self.btn_model_types)
        single_row.addWidget(self.btn_duplicate_model)
        single_row.addStretch()

        main_layout.addLayout(single_row)

        main_layout.addSpacing(14)

        # COMPARISON TOOLS
        comparison_title_frame = QWidget()
        comparison_title_frame.setObjectName("comparisonTitleFrame")
        comparison_title_frame.setAttribute(Qt.WA_StyledBackground, True)
        themed(comparison_title_frame, lambda c: f"QWidget#comparisonTitleFrame {{ background: {c.surface}; border: 2px solid {c.border}; border-radius: 10px; }}")
        comparison_title_inner = QVBoxLayout(comparison_title_frame)
        comparison_title_inner.setContentsMargins(16, 8, 16, 8)

        comparison_title = QLabel("Comparison Tools")
        comparison_title.setObjectName("groupTitle")
        comparison_title_inner.addWidget(comparison_title)

        comparison_title_row = QHBoxLayout()
        comparison_title_row.addWidget(comparison_title_frame)
        comparison_title_row.addStretch()
        main_layout.addLayout(comparison_title_row)



        self.btn_comparison = self.create_nav_button(
            "Comparison Dashboard", icon_name="comparison_dashboard.svg", width=430
        )
        self.btn_radar_comparison = self.create_nav_button(
            "Radar Chart Comparison", width=380
        )

        comparison_row = QHBoxLayout()
        comparison_row.setSpacing(28)
        comparison_row.addWidget(self.btn_comparison)
        comparison_row.addWidget(self.btn_radar_comparison)
        comparison_row.addStretch()
        main_layout.addLayout(comparison_row)

        # SEPARATOR 
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        themed(separator, lambda c: f"color: {c.muted}; margin-top: 14px; margin-bottom: 6px;")
        main_layout.addWidget(separator)

        main_layout.addStretch()

        # INFO BUTTON (opens the explanation popup)
        info_row = QHBoxLayout()
        info_row.addStretch()
        self.info_btn = RoundedButton("?", 58, 58, 29)
        self.info_btn.clicked.connect(self.show_help_popup)
        self._set_info_btn_style(INFO_YELLOW)
        info_row.addWidget(self.info_btn)
        main_layout.addLayout(info_row)

        themed(self, lambda c: f"""

        QWidget#landingPage {{
            background-color: {c.page};
            font-family: 'Inter';
        }}

        QLabel#bigTitle {{
            font-size: 44px;
            font-weight: 700;
            color: {c.text};
        }}

        QLabel#subtitle {{
            font-size: 19px;
            font-weight: 400;
            color: {c.muted};
        }}

        QLabel#sectionTitle {{
            font-size: 28px;
            font-weight: 700;
            color: {c.text};
        }}

        QLabel#groupTitle {{
            font-size: 20px;
            font-weight: 600;
            color: {c.text};
        }}
        """)


    def create_nav_button(self, text, icon_name=None, width=340, height=90, radius=30):
        btn = RoundedButton(text, width, height, radius)
        themed_add(btn, lambda c, btn=btn: "QPushButton{font-size:20px;}")
        if icon_name:
            set_asset_icon(btn, icon_name)
            btn.setIconSize(ICON_SIZE)
        return btn

    # MODELS BADGE — opens the /results folder

    def open_models_folder(self):
        folder = os.path.abspath(gmp.RESULTS_DIR)
        os.makedirs(folder, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _refresh_model_badge(self):
        model_count = len(gmp.get_model_names(gmp.RESULTS_DIR))
        label = "model" if model_count == 1 else "models"
        self.models_badge.setText(f"{model_count} {label} available")
        self.empty_hint.setVisible(model_count == 0)

    def delete_non_favorite_models(self):
        all_models = gmp.get_model_names(gmp.RESULTS_DIR)
        to_delete = [m for m in all_models if not is_favorite(m)]

        if not to_delete:
            ErrorPopup(self, "No non-favorite models to delete.").show()
            return

        count = len(to_delete)
        reply = QMessageBox.question(
            self,
            "Delete non-favorite models?",
            (
                f"This will permanently delete {count} model"
                f"{'s' if count != 1 else ''} not marked as favorite:\n\n"
                + "\n".join(f"- {m}" for m in to_delete)
                + "\n\nFavorited models are kept. This cannot be undone."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        failed = []
        for m in to_delete:
            run_dir = Path(gmp.RESULTS_DIR) / m
            try:
                shutil.rmtree(run_dir)
            except Exception:
                failed.append(m)

        self._refresh_model_badge()

        if failed:
            ErrorPopup(
                self,
                f"Deleted {count - len(failed)} of {count} models. "
                f"Could not delete: {', '.join(failed)}.",
                duration_ms=5000,
            ).show()

    # INFO BUTTON / POPUP

    def _set_info_btn_style(self, background_color):
        themed(self.info_btn, lambda c, background_color=background_color: f"""
            QPushButton {{
                font-size: 30px;
                font-weight: 700;
                background: {background_color};
                color: {BLACK};
                border: none;
                border-radius: 29px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: {INFO_YELLOW_HOVER};
            }}
        """)

    def eventFilter(self, obj, event):
        if self.popup is not None and obj is self.popup and event.type() == QEvent.Hide:
            self._set_info_btn_style(INFO_YELLOW)
        return super().eventFilter(obj, event)

    def show_help_popup(self):
        if self.popup is not None:
            self.popup.close()

        self.popup = Popup(
            parent=self,
            width=940,
            height=380,
            x=(self.width() - 940) // 2 if self.width() > 940 else 20,
            y=(self.height() - 380) // 2 if self.height() > 380 else 20,
            background=YELLOW,
        )
        self.popup.installEventFilter(self)

        text = QLabel(
            "This dashboard lets you explore and analyze models trained to "
            "predict patient outcomes, through interactive visualizations.\n\n"
            "Single-Model Tools (Single Model Visualization, Confusion Matrix, "
            "Model Execution Visualization) focus on one model at a time and show "
            "how it performs on the patients it was tested on. You can also duplicate an existing model and modify it slightly.\n\n"
            "Comparison Tools (Comparison) let you compare several models side by "
            "side, on the metric of your choice, to see which one performs best."
        )
        text.setWordWrap(True)
        themed(text, lambda c: f"""
            QLabel {{
                color: {c.text};
                font-size: 20px;
                font-weight: 500;
                background: transparent;
            }}
        """)

        self.popup.layout.addSpacing(40)
        self.popup.layout.addWidget(text)
        self.popup.close_btn.raise_()

        self._set_info_btn_style(INFO_YELLOW)
        self.popup.show()
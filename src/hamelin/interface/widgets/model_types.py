from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSizePolicy
)

from hamelin.interface.utils.widgets import RoundedButton, WidgetPopupOverlay, ErrorPopup, set_asset_icon
from hamelin.interface.utils.colors import WHITE, GRAY, themed
from hamelin.interface.widgets.dropdowns import SimpleDropdown
from hamelin.interface.widgets.cnn_visualisation import CNNVisualisationWidget
from hamelin.interface.widgets.mlp_visualisation import MLPVisualisationWidget
from hamelin.interface.widgets.lstm_visualisation import LSTMVisualisationWidget


# MAIN PAGE

class ModelTypeInfoWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_type = None

        # ROOT
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 60)
        root.setSpacing(24)

        # TOP BAR

        top = QHBoxLayout()

        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        set_asset_icon(self.btn_home, "home.svg")
        self.btn_home.setIconSize(QSize(32, 32))
        self.btn_home.setCursor(Qt.PointingHandCursor)

        top.addWidget(self.btn_home)
        top.addStretch()

        root.addLayout(top)

        # TITLE

        title = QLabel("Model Type Information")
        title.setAlignment(Qt.AlignCenter)
        themed(title, lambda c: f"""
            background: {c.surface};
            color: {c.text};
            border: 2px solid {c.border};
            padding: 18px 28px;
            font-size: 44px;
            font-weight: 700;
            border-radius: 10px;
        """)

        title_row = QHBoxLayout()
        title_row.addStretch()
        title_row.addWidget(title)
        title_row.addStretch()

        root.addLayout(title_row)

        root.addSpacing(24)

        # DROPDOWN

        self.dropdown = SimpleDropdown("Select Model Type", ["CNN", "MLP", "LSTM"])
        self.dropdown.setMinimumWidth(420)
        self.dropdown.setMaximumWidth(900)
        self.dropdown.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.dropdown)
        row.addStretch()

        root.addLayout(row)

        root.addSpacing(24)

        # BUTTON

        self.btn_info = RoundedButton("Learn More about the Type", 700, 90, 40)
        self.btn_info.setCursor(Qt.PointingHandCursor)
        themed(self.btn_info, lambda c: f"""
            QPushButton {{
                background: {GRAY};
                color: {WHITE};
                font-size: 28px;
                font-weight: 700;
                border-radius: 22px;
                border: none;
            }}
            QPushButton:hover {{
                background: #106EBE;
            }}
        """)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.btn_info)
        btn_row.addStretch()

        root.addLayout(btn_row)

        root.addSpacing(40)

        self.btn_info.clicked.connect(self.open_popup)

        root.addStretch()

    # OPEN POPUP 

    def open_popup(self):
        model_type = self.dropdown.currentText()
        if not model_type:
            ErrorPopup(self, "Please select a model type.").show()
            return

        widget_map = {
            "CNN": CNNVisualisationWidget,
            "MLP": MLPVisualisationWidget,
            "LSTM": LSTMVisualisationWidget,
        }

        widget_cls = widget_map.get(model_type)

        try:
            content = widget_cls()
        except Exception as e:
            error = QLabel(
                f"Failed to load {model_type} visualisation.\n\nError:\n{e}"
            )
            error.setAlignment(Qt.AlignCenter)
            themed(error, lambda c: f"""
                QLabel {{
                    font-size: 22px;
                    color: {c.text};
                    background: transparent;
                }}
            """)
            content = error

        popup = WidgetPopupOverlay(
            content,
            parent=self,
            title=f"{model_type} Explanation",
            width=1400,
            height=900,
        )

        popup.show()

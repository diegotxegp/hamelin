import os
import sys

# Forzar el uso de X11 en lugar de Wayland para evitar errores de display
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from utils.ui_to_py_converter import convert_ui_to_py
from controller.controller import Controller

def converter():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ui_folder = os.path.join(base_dir, "..", "ui")
    output_folder = os.path.join(base_dir, "view")

    if not os.path.exists(ui_folder):
        print(f"❌ The UI folder '{ui_folder}' does not exist. Please check the path.")
        return

    convert_ui_to_py(ui_folder, output_folder)

def start():
    app = QApplication(sys.argv)
    
    # Set application-wide icon (affects taskbar and window decorations)
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "Hamelin icono.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Set application-wide stylesheet with soft light blue background
    app.setStyleSheet("""
        QWidget {
            background-color: #f0f8ff;
            color: #000000;
        }
        QPushButton {
            background-color: #e6f2ff;
            color: #000000;
            border: 1px solid #b3d9ff;
            border-radius: 5px;
            padding: 5px;
            min-height: 25px;
        }
        QPushButton:hover {
            background-color: #d9edff;
            color: #000000;
            border: 1px solid #99ccff;
        }
        QPushButton:pressed {
            background-color: #cce5ff;
            color: #000000;
        }
        QComboBox {
            background-color: #e6f2ff;
            color: #000000;
            border: 1px solid #b3d9ff;
            border-radius: 3px;
            padding: 3px;
        }
        QComboBox:hover {
            border: 1px solid #99ccff;
        }
        QComboBox::drop-down {
            background-color: #d9edff;
            border-left: 1px solid #b3d9ff;
        }
        QComboBox QAbstractItemView {
            background-color: #f0f8ff;
            color: #000000;
            selection-background-color: #d9edff;
            selection-color: #000000;
        }
        QListWidget {
            background-color: #fafcff;
            color: #000000;
            border: 1px solid #b3d9ff;
        }
        QListWidget::item {
            color: #000000;
        }
        QListWidget::item:selected {
            background-color: #d9edff;
            color: #000000;
        }
        QTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #b3d9ff;
        }
        QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #b3d9ff;
            border-radius: 3px;
            padding: 3px;
        }
        QTabWidget::pane {
            background-color: #f0f8ff;
            border: 1px solid #b3d9ff;
        }
        QTabBar::tab {
            background-color: #e6f2ff;
            color: #000000;
            border: 1px solid #b3d9ff;
            padding: 5px 10px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #f0f8ff;
            color: #000000;
            border-bottom: 1px solid #f0f8ff;
        }
        QTabBar::tab:hover {
            background-color: #d9edff;
            color: #000000;
        }
        QTableWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #b3d9ff;
            gridline-color: #d9edff;
        }
        QTableWidget::item {
            color: #000000;
        }
        QTableWidget::item:selected {
            background-color: #d9edff;
            color: #000000;
        }
        QHeaderView::section {
            background-color: #e6f2ff;
            color: #000000;
            border: 1px solid #b3d9ff;
            padding: 4px;
        }
        QLabel {
            background-color: transparent;
            color: #000000;
        }
        QGroupBox {
            background-color: #f0f8ff;
            color: #000000;
            border: 1px solid #b3d9ff;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            background-color: transparent;
            color: #000000;
        }
    """)
    
    controller = Controller()
    controller.show()
    sys.exit(app.exec())

def main():
    converter()
    start()

if __name__ == "__main__":
    main()

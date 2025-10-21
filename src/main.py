import os
import sys

# Forzar el uso de X11 en lugar de Wayland para evitar errores de display
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PySide6.QtWidgets import QApplication
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
    controller = Controller()
    controller.show()
    sys.exit(app.exec())

def main():
    converter()
    start()

if __name__ == "__main__":
    main()

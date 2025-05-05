from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys

app = QApplication(sys.argv)

ui_file = QFile("/home/diegotxe/Visual-Studio/HAMELIN/HAMELIN/Interfaces/estudio_clinico.ui")
ui_file.open(QFile.ReadOnly)

loader = QUiLoader()
ventana = loader.load(ui_file)
ui_file.close()

ventana.show()

sys.exit(app.exec())

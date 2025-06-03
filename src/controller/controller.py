# controller/controller.py

from PySide6.QtWidgets import QMainWindow
from view.interface_ui import Ui_MainWindow

from controller.controller_inicio import ControllerInicio
from controller.controller_registro import ControllerRegistro
from controller.controller_observacional import ControllerObservacional
from controller.controller_clinico import ControllerClinico

from model.model import Model


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


class Controller:
    def __init__(self):
        self.model = Model()
        self.window = MainWindow()

        self.page = 0
        self.tab = 0

        # Set initial page and tab
        self.window.ui.stackedWidget.setCurrentIndex(self.page)
        self.window.ui.tabWidget_inicio.setCurrentIndex(self.tab)

        # Instantiate subcontrollers
        self.controller_inicio = ControllerInicio(
            self.window.ui.page_inicio, self.model, self
        )
        self.controller_registro = ControllerRegistro(
            self.window.ui.page_registro, self.model, self
        )
        
        self.controller_observacional = ControllerObservacional(
            self.window.ui.page_observacional, self.model, self
        )
        
        self.controller_clinico = ControllerClinico(
            self.window.ui.page_clinico, self.model, self
        )

    def show(self):
        self.window.showMaximized()

    def change_page(self, index: int):
        self.window.ui.stackedWidget.setCurrentIndex(index)

        # Set initial tab
        if index == 0:
            self.window.ui.tabWidget_inicio.setCurrentIndex(0)

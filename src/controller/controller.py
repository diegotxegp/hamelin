# controller/controller.py

from PySide6.QtWidgets import QMainWindow
from view.interface_ui import Ui_MainWindow

from controller.registro_controller import RegistroController
from controller.observacional_controller import ObservacionalController
from controller.clinico_controller import ClinicoController
from controller.inicio_controller import InicioController

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
        self.inicio_controller = InicioController(
            self.window.ui.page_inicio, self.model, self
        )

    def show(self):
        self.window.showMaximized()

    def change_page(self, option: str):
        pages = {
            "Inicio": 0,
            "Registro de pacientes": 1,
            "Estudio observacional": 2,
            "Estudio clínico": 3,
        }
        index = pages.get(option, 0)
        self.window.ui.stackedWidget.setCurrentIndex(index)

        if option == "Inicio":
            self.window.ui.tabWidget_inicio.setCurrentIndex(0)
        if option == "Registro de pacientes":
            self.window.ui.tabWidget_registro.setCurrentIndex(1)
        if option == "Estudio observacional":
            self.window.ui.tabWidget_observacional.setCurrentIndex(1)
        if option == "Estudio clínico":
            self.window.ui.tabWidget_clinico.setCurrentIndex(1)

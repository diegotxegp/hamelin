from controller.inicio_controller import InicioController
from model.model import Model

class Controller:
    def __init__(self):
        self.model = Model()
        self.current_window = None
        self.current_page = 0
        self.current_tab = 0

    def show_initial_window(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = InicioController(self, self.model)
        self.current_window.ui.stackedWidget.setCurrentIndex(self.current_page)
        self.current_window.ui.tabWidget_inicio.setCurrentIndex(self.current_tab)
        self.current_window.showMaximized()

    def change_page(self, option):
        if option == "Registro de pacientes":
            self.current_page = 1
        elif option == "Estudio observacional":
            self.current_page = 2
        elif option == "Estudio clínico":
            self.current_page = 3

        self.current_window.ui.stackedWidget.setCurrentIndex(self.current_page)
        

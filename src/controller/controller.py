from controller.inicio_controller import InicioController
from model.model import Model

class Controller:
    def __init__(self):
        self.model = Model()
        self.current_window = None

    def start(self):
        self.show_main_window()

    def show_main_window(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = InicioController(self, self.model)
        self.current_window.show()

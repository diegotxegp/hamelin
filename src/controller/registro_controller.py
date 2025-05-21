# controller/registro_controller.py

class RegistroController:
    def __init__(self, view, model, main_controller):
        self.view = view
        self.model = model
        self.main_controller = main_controller

        self.setup_connections()

    def setup_connections(self):
        # Ejemplo: conectar un botón a una función
        self.view.pushButton_guardar.clicked.connect(self.guardar_paciente)

    def guardar_paciente(self):
        # Interactuar con el modelo para guardar datos
        nombre = self.view.lineEdit_nombre.text()
        self.model.guardar_paciente(nombre)
        # Volver a la página de inicio si se desea
        self.main_controller.change_page("Inicio")

# controller/controller_clinico.py

class ControllerClinico:
    def __init__(self, ui, model, controller):
        """
        :param ui: QWidget corresponding to the page in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model = model
        self.controller = controller

        self._setup_signals()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        self.pushButton_adjuntar.clicked.connect(self.model.attach_csv)
        self.pushButton_opciones.clicked.connect(self._select_option)

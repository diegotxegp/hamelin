# controller/controller.py

from PySide6.QtWidgets import QMainWindow, QMessageBox
from view.interface_ui import Ui_MainWindow

from controller.controller_start import ControllerStart
from controller.controller_patient_registry import ControllerPatientRegistry
from controller.controller_observational_study import ControllerObservationalStudy
from controller.controller_clinical_trial import ControllerClinicalTrial

from model.model import Model


class MainWindow(QMainWindow):
    """
    Main window of the application.
    """
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


class Controller:
    """
    Controller for the main window.
    """
    def __init__(self):
        """
        Controller for the main window.
        """
        self.model = Model()
        self.window = MainWindow()

        self.page = 0
        self.tab = 0

        # Set initial page and tab
        self.window.ui.stackedWidget.setCurrentIndex(self.page)
        self.window.ui.tabWidget_start.setCurrentIndex(self.tab)

        # Set up controllers
        model_start = self.model.get_model_start()
        self.controller_start = ControllerStart(self.window.ui.page_start, model_start, self)
        """
        self.controller_patient_registry = ControllerPatientRegistry(
            self.window.ui.page_registry, self
        )
        
        self.controller_observational_study = ControllerObservationalStudy(
            self.window.ui.page_observational, self
        )
        
        self.controller_clinical_trial = ControllerClinicalTrial(
            self.window.ui.page_clinical, self
        )
        """

    def show(self):
        """
        Show the main window.
        """
        self.window.showMaximized()

    def change_page(self, index: int):
        """
        Change the current page.

        :param index: Index of the page to be displayed.
        """
        self.window.ui.stackedWidget.setCurrentIndex(index)
    
    def emerging_message(self, parent, title, text):
        """
        Displays a message box with the given title and text.
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()

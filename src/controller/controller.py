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

        # Set initial page and tab
        self.window.ui.stackedWidget.setCurrentIndex(0)
        self.window.ui.tabWidget_start.setCurrentIndex(0)

        # Set up controllers
        self.controller_start = ControllerStart(self.window.ui.page_start, self.model.model_start, self)
        self.controller_patient_registry = ControllerPatientRegistry(self.window.ui.page_registry, self.model.model_registry, self)
        self.controller_observational_study = ControllerObservationalStudy(self.window.ui.page_observational, self.model.model_observational, self)
        self.controller_clinical_trial = ControllerClinicalTrial(self.window.ui.page_clinical, self.model.model_clinical, self)

        self.window.ui.stackedWidget.currentChanged.connect(self.on_page_changed)

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

    def on_page_changed(self, index: int):
        """
        Triggered when the stackedWidget page changes.
        Used to update data dynamically when showing a page.
        """
        if index == 1 and self.controller_patient_registry:
            self.controller_patient_registry.update_page()
        elif index == 2 and self.controller_observational_study:
            self.controller_observational_study.update_page()
        elif index == 3 and self.controller_clinical_trial:
            self.controller_clinical_trial.update_page()
    
    def popup_message(self, parent, title, text):
        """
        Displays a message box with the given title and text.
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()

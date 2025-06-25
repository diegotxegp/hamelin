# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QScrollArea, QSizePolicy,
    QStackedWidget, QStatusBar, QTabWidget, QTextEdit,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(815, 630)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_start = QWidget()
        self.page_start.setObjectName(u"page_start")
        self.gridLayout_2 = QGridLayout(self.page_start)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget_start = QTabWidget(self.page_start)
        self.tabWidget_start.setObjectName(u"tabWidget_start")
        self.tabWidget_start.setEnabled(True)
        self.tab_start_welcome = QWidget()
        self.tab_start_welcome.setObjectName(u"tab_start_welcome")
        self.gridLayout_3 = QGridLayout(self.tab_start_welcome)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.textEdit_start_welcome = QTextEdit(self.tab_start_welcome)
        self.textEdit_start_welcome.setObjectName(u"textEdit_start_welcome")
        self.textEdit_start_welcome.setReadOnly(True)

        self.gridLayout_3.addWidget(self.textEdit_start_welcome, 0, 0, 1, 1)

        self.pushButton_start_welcome = QPushButton(self.tab_start_welcome)
        self.pushButton_start_welcome.setObjectName(u"pushButton_start_welcome")

        self.gridLayout_3.addWidget(self.pushButton_start_welcome, 1, 0, 1, 1)

        self.tabWidget_start.addTab(self.tab_start_welcome, "")
        self.tab_start_project = QWidget()
        self.tab_start_project.setObjectName(u"tab_start_project")
        self.gridLayout_29 = QGridLayout(self.tab_start_project)
        self.gridLayout_29.setObjectName(u"gridLayout_29")
        self.textEdit_start_project = QTextEdit(self.tab_start_project)
        self.textEdit_start_project.setObjectName(u"textEdit_start_project")
        self.textEdit_start_project.setReadOnly(True)

        self.gridLayout_29.addWidget(self.textEdit_start_project, 0, 0, 1, 1)

        self.pushButton_start_project = QPushButton(self.tab_start_project)
        self.pushButton_start_project.setObjectName(u"pushButton_start_project")

        self.gridLayout_29.addWidget(self.pushButton_start_project, 2, 0, 1, 1)

        self.listWidget_start_project = QListWidget(self.tab_start_project)
        self.listWidget_start_project.setObjectName(u"listWidget_start_project")

        self.gridLayout_29.addWidget(self.listWidget_start_project, 1, 0, 1, 1)

        self.tabWidget_start.addTab(self.tab_start_project, "")
        self.tab_start_data = QWidget()
        self.tab_start_data.setObjectName(u"tab_start_data")
        self.tab_start_data.setEnabled(True)
        self.gridLayout_4 = QGridLayout(self.tab_start_data)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.pushButton_start_data = QPushButton(self.tab_start_data)
        self.pushButton_start_data.setObjectName(u"pushButton_start_data")

        self.gridLayout_4.addWidget(self.pushButton_start_data, 2, 0, 1, 1)

        self.textEdit_start_data = QTextEdit(self.tab_start_data)
        self.textEdit_start_data.setObjectName(u"textEdit_start_data")
        self.textEdit_start_data.setEnabled(True)
        self.textEdit_start_data.setReadOnly(True)

        self.gridLayout_4.addWidget(self.textEdit_start_data, 0, 0, 1, 1)

        self.listWidget_start_data = QListWidget(self.tab_start_data)
        self.listWidget_start_data.setObjectName(u"listWidget_start_data")

        self.gridLayout_4.addWidget(self.listWidget_start_data, 1, 0, 1, 1)

        self.tabWidget_start.addTab(self.tab_start_data, "")
        self.tab_start_status = QWidget()
        self.tab_start_status.setObjectName(u"tab_start_status")
        self.gridLayout_5 = QGridLayout(self.tab_start_status)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.pushButton_start_status = QPushButton(self.tab_start_status)
        self.pushButton_start_status.setObjectName(u"pushButton_start_status")

        self.gridLayout_5.addWidget(self.pushButton_start_status, 2, 0, 1, 1)

        self.textEdit_start_status = QTextEdit(self.tab_start_status)
        self.textEdit_start_status.setObjectName(u"textEdit_start_status")
        self.textEdit_start_status.setReadOnly(True)

        self.gridLayout_5.addWidget(self.textEdit_start_status, 0, 0, 1, 1)

        self.textEdit_start_status_text = QTextEdit(self.tab_start_status)
        self.textEdit_start_status_text.setObjectName(u"textEdit_start_status_text")

        self.gridLayout_5.addWidget(self.textEdit_start_status_text, 1, 0, 1, 1)

        self.tabWidget_start.addTab(self.tab_start_status, "")
        self.tab_start_options = QWidget()
        self.tab_start_options.setObjectName(u"tab_start_options")
        self.gridLayout_6 = QGridLayout(self.tab_start_options)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.textEdit_start_options = QTextEdit(self.tab_start_options)
        self.textEdit_start_options.setObjectName(u"textEdit_start_options")
        self.textEdit_start_options.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textEdit_start_options, 0, 0, 1, 1)

        self.comboBox_start_options = QComboBox(self.tab_start_options)
        self.comboBox_start_options.addItem("")
        self.comboBox_start_options.addItem("")
        self.comboBox_start_options.addItem("")
        self.comboBox_start_options.setObjectName(u"comboBox_start_options")

        self.gridLayout_6.addWidget(self.comboBox_start_options, 1, 0, 1, 1)

        self.pushButton_start_options = QPushButton(self.tab_start_options)
        self.pushButton_start_options.setObjectName(u"pushButton_start_options")

        self.gridLayout_6.addWidget(self.pushButton_start_options, 2, 0, 1, 1)

        self.tabWidget_start.addTab(self.tab_start_options, "")

        self.gridLayout_2.addWidget(self.tabWidget_start, 1, 0, 1, 1)

        self.lineEdit_start_title = QLineEdit(self.page_start)
        self.lineEdit_start_title.setObjectName(u"lineEdit_start_title")
        self.lineEdit_start_title.setReadOnly(True)

        self.gridLayout_2.addWidget(self.lineEdit_start_title, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_start)
        self.page_registry = QWidget()
        self.page_registry.setObjectName(u"page_registry")
        self.gridLayout_7 = QGridLayout(self.page_registry)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.lineEdit_registry_title = QLineEdit(self.page_registry)
        self.lineEdit_registry_title.setObjectName(u"lineEdit_registry_title")
        self.lineEdit_registry_title.setReadOnly(True)

        self.gridLayout_7.addWidget(self.lineEdit_registry_title, 0, 0, 1, 1)

        self.tabWidget_registry = QTabWidget(self.page_registry)
        self.tabWidget_registry.setObjectName(u"tabWidget_registry")
        self.tab_registry_start = QWidget()
        self.tab_registry_start.setObjectName(u"tab_registry_start")
        self.gridLayout_8 = QGridLayout(self.tab_registry_start)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.textEdit_registry_start = QTextEdit(self.tab_registry_start)
        self.textEdit_registry_start.setObjectName(u"textEdit_registry_start")
        self.textEdit_registry_start.setReadOnly(True)

        self.gridLayout_8.addWidget(self.textEdit_registry_start, 0, 0, 1, 1)

        self.pushButton_registry_start = QPushButton(self.tab_registry_start)
        self.pushButton_registry_start.setObjectName(u"pushButton_registry_start")

        self.gridLayout_8.addWidget(self.pushButton_registry_start, 1, 0, 1, 1)

        self.tabWidget_registry.addTab(self.tab_registry_start, "")
        self.tab_registry_variable = QWidget()
        self.tab_registry_variable.setObjectName(u"tab_registry_variable")
        self.gridLayout_11 = QGridLayout(self.tab_registry_variable)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.textEdit_registry_variable = QTextEdit(self.tab_registry_variable)
        self.textEdit_registry_variable.setObjectName(u"textEdit_registry_variable")
        self.textEdit_registry_variable.setReadOnly(True)

        self.gridLayout_11.addWidget(self.textEdit_registry_variable, 0, 0, 1, 1)

        self.pushButton_registry_variable = QPushButton(self.tab_registry_variable)
        self.pushButton_registry_variable.setObjectName(u"pushButton_registry_variable")

        self.gridLayout_11.addWidget(self.pushButton_registry_variable, 2, 0, 1, 1)

        self.listWidget_registry_variable = QListWidget(self.tab_registry_variable)
        self.listWidget_registry_variable.setObjectName(u"listWidget_registry_variable")

        self.gridLayout_11.addWidget(self.listWidget_registry_variable, 1, 0, 1, 1)

        self.tabWidget_registry.addTab(self.tab_registry_variable, "")
        self.tab_registry_criteria = QWidget()
        self.tab_registry_criteria.setObjectName(u"tab_registry_criteria")
        self.gridLayout_10 = QGridLayout(self.tab_registry_criteria)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.pushButton_registry_criteria = QPushButton(self.tab_registry_criteria)
        self.pushButton_registry_criteria.setObjectName(u"pushButton_registry_criteria")

        self.gridLayout_10.addWidget(self.pushButton_registry_criteria, 2, 0, 1, 2)

        self.textEdit_registry_criteria = QTextEdit(self.tab_registry_criteria)
        self.textEdit_registry_criteria.setObjectName(u"textEdit_registry_criteria")
        self.textEdit_registry_criteria.setReadOnly(True)

        self.gridLayout_10.addWidget(self.textEdit_registry_criteria, 0, 0, 1, 2)

        self.scrollArea_registry_criteria = QScrollArea(self.tab_registry_criteria)
        self.scrollArea_registry_criteria.setObjectName(u"scrollArea_registry_criteria")
        self.scrollArea_registry_criteria.setWidgetResizable(True)
        self.scrollAreaWidgetContents_registry_criteria = QWidget()
        self.scrollAreaWidgetContents_registry_criteria.setObjectName(u"scrollAreaWidgetContents_registry_criteria")
        self.scrollAreaWidgetContents_registry_criteria.setGeometry(QRect(0, 0, 755, 220))
        self.gridLayout_30 = QGridLayout(self.scrollAreaWidgetContents_registry_criteria)
        self.gridLayout_30.setObjectName(u"gridLayout_30")
        self.widget_registry_criteria = QWidget(self.scrollAreaWidgetContents_registry_criteria)
        self.widget_registry_criteria.setObjectName(u"widget_registry_criteria")

        self.gridLayout_30.addWidget(self.widget_registry_criteria, 0, 0, 1, 1)

        self.scrollArea_registry_criteria.setWidget(self.scrollAreaWidgetContents_registry_criteria)

        self.gridLayout_10.addWidget(self.scrollArea_registry_criteria, 1, 0, 1, 2)

        self.tabWidget_registry.addTab(self.tab_registry_criteria, "")
        self.tab_registry_settings = QWidget()
        self.tab_registry_settings.setObjectName(u"tab_registry_settings")
        self.gridLayout_9 = QGridLayout(self.tab_registry_settings)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.textEdit_registry_settings = QTextEdit(self.tab_registry_settings)
        self.textEdit_registry_settings.setObjectName(u"textEdit_registry_settings")
        self.textEdit_registry_settings.setReadOnly(True)

        self.gridLayout_9.addWidget(self.textEdit_registry_settings, 0, 0, 1, 1)

        self.pushButton_registry_settings = QPushButton(self.tab_registry_settings)
        self.pushButton_registry_settings.setObjectName(u"pushButton_registry_settings")

        self.gridLayout_9.addWidget(self.pushButton_registry_settings, 2, 0, 1, 1)

        self.scrollArea_registry_settings = QScrollArea(self.tab_registry_settings)
        self.scrollArea_registry_settings.setObjectName(u"scrollArea_registry_settings")
        self.scrollArea_registry_settings.setWidgetResizable(True)
        self.scrollAreaWidgetContents_registry_settings = QWidget()
        self.scrollAreaWidgetContents_registry_settings.setObjectName(u"scrollAreaWidgetContents_registry_settings")
        self.scrollAreaWidgetContents_registry_settings.setGeometry(QRect(0, 0, 755, 220))
        self.gridLayout_32 = QGridLayout(self.scrollAreaWidgetContents_registry_settings)
        self.gridLayout_32.setObjectName(u"gridLayout_32")
        self.widget_registry_settings = QWidget(self.scrollAreaWidgetContents_registry_settings)
        self.widget_registry_settings.setObjectName(u"widget_registry_settings")

        self.gridLayout_32.addWidget(self.widget_registry_settings, 0, 0, 1, 1)

        self.scrollArea_registry_settings.setWidget(self.scrollAreaWidgetContents_registry_settings)

        self.gridLayout_9.addWidget(self.scrollArea_registry_settings, 1, 0, 1, 1)

        self.tabWidget_registry.addTab(self.tab_registry_settings, "")
        self.tab_registry_process = QWidget()
        self.tab_registry_process.setObjectName(u"tab_registry_process")
        self.gridLayout_12 = QGridLayout(self.tab_registry_process)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.pushButton_registry_process = QPushButton(self.tab_registry_process)
        self.pushButton_registry_process.setObjectName(u"pushButton_registry_process")

        self.gridLayout_12.addWidget(self.pushButton_registry_process, 2, 0, 1, 1)

        self.textEdit_registry_process = QTextEdit(self.tab_registry_process)
        self.textEdit_registry_process.setObjectName(u"textEdit_registry_process")
        self.textEdit_registry_process.setReadOnly(True)

        self.gridLayout_12.addWidget(self.textEdit_registry_process, 0, 0, 1, 1)

        self.textEdit_registry_process_config = QTextEdit(self.tab_registry_process)
        self.textEdit_registry_process_config.setObjectName(u"textEdit_registry_process_config")

        self.gridLayout_12.addWidget(self.textEdit_registry_process_config, 1, 0, 1, 1)

        self.tabWidget_registry.addTab(self.tab_registry_process, "")
        self.tab_registry_outcome = QWidget()
        self.tab_registry_outcome.setObjectName(u"tab_registry_outcome")
        self.gridLayout_14 = QGridLayout(self.tab_registry_outcome)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.textEdit_registry_outcome = QTextEdit(self.tab_registry_outcome)
        self.textEdit_registry_outcome.setObjectName(u"textEdit_registry_outcome")
        self.textEdit_registry_outcome.setReadOnly(True)

        self.gridLayout_14.addWidget(self.textEdit_registry_outcome, 0, 0, 1, 1)

        self.tabWidget_registry.addTab(self.tab_registry_outcome, "")

        self.gridLayout_7.addWidget(self.tabWidget_registry, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_registry)
        self.page_observational = QWidget()
        self.page_observational.setObjectName(u"page_observational")
        self.gridLayout_13 = QGridLayout(self.page_observational)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.tabWidget_observational = QTabWidget(self.page_observational)
        self.tabWidget_observational.setObjectName(u"tabWidget_observational")
        self.tab_observational_start = QWidget()
        self.tab_observational_start.setObjectName(u"tab_observational_start")
        self.gridLayout_15 = QGridLayout(self.tab_observational_start)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.textEdit_observational_start = QTextEdit(self.tab_observational_start)
        self.textEdit_observational_start.setObjectName(u"textEdit_observational_start")
        self.textEdit_observational_start.setReadOnly(True)

        self.gridLayout_15.addWidget(self.textEdit_observational_start, 0, 0, 1, 1)

        self.pushButton_observational_start = QPushButton(self.tab_observational_start)
        self.pushButton_observational_start.setObjectName(u"pushButton_observational_start")

        self.gridLayout_15.addWidget(self.pushButton_observational_start, 1, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_start, "")
        self.tab_observational_variable = QWidget()
        self.tab_observational_variable.setObjectName(u"tab_observational_variable")
        self.gridLayout_17 = QGridLayout(self.tab_observational_variable)
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.textEdit_observational_variable_new = QTextEdit(self.tab_observational_variable)
        self.textEdit_observational_variable_new.setObjectName(u"textEdit_observational_variable_new")

        self.gridLayout_17.addWidget(self.textEdit_observational_variable_new, 1, 0, 1, 1)

        self.textEdit_observational_variable = QTextEdit(self.tab_observational_variable)
        self.textEdit_observational_variable.setObjectName(u"textEdit_observational_variable")
        self.textEdit_observational_variable.setReadOnly(True)

        self.gridLayout_17.addWidget(self.textEdit_observational_variable, 0, 0, 1, 1)

        self.pushButton_observational_variable = QPushButton(self.tab_observational_variable)
        self.pushButton_observational_variable.setObjectName(u"pushButton_observational_variable")

        self.gridLayout_17.addWidget(self.pushButton_observational_variable, 2, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_variable, "")
        self.tab_observational_criteria = QWidget()
        self.tab_observational_criteria.setObjectName(u"tab_observational_criteria")
        self.gridLayout_16 = QGridLayout(self.tab_observational_criteria)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.textEdit_observational_criteria_new = QTextEdit(self.tab_observational_criteria)
        self.textEdit_observational_criteria_new.setObjectName(u"textEdit_observational_criteria_new")

        self.gridLayout_16.addWidget(self.textEdit_observational_criteria_new, 1, 0, 1, 1)

        self.textEdit_observational_criteria = QTextEdit(self.tab_observational_criteria)
        self.textEdit_observational_criteria.setObjectName(u"textEdit_observational_criteria")
        self.textEdit_observational_criteria.setReadOnly(True)

        self.gridLayout_16.addWidget(self.textEdit_observational_criteria, 0, 0, 1, 1)

        self.pushButton_observational_criteria = QPushButton(self.tab_observational_criteria)
        self.pushButton_observational_criteria.setObjectName(u"pushButton_observational_criteria")

        self.gridLayout_16.addWidget(self.pushButton_observational_criteria, 2, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_criteria, "")
        self.tab_observational_process = QWidget()
        self.tab_observational_process.setObjectName(u"tab_observational_process")
        self.gridLayout_18 = QGridLayout(self.tab_observational_process)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.pushButton_observational_process = QPushButton(self.tab_observational_process)
        self.pushButton_observational_process.setObjectName(u"pushButton_observational_process")

        self.gridLayout_18.addWidget(self.pushButton_observational_process, 2, 0, 1, 1)

        self.textEdit_observational_process = QTextEdit(self.tab_observational_process)
        self.textEdit_observational_process.setObjectName(u"textEdit_observational_process")
        self.textEdit_observational_process.setReadOnly(True)

        self.gridLayout_18.addWidget(self.textEdit_observational_process, 0, 0, 1, 1)

        self.textEdit_3 = QTextEdit(self.tab_observational_process)
        self.textEdit_3.setObjectName(u"textEdit_3")

        self.gridLayout_18.addWidget(self.textEdit_3, 1, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_process, "")
        self.tab_observational_outcome = QWidget()
        self.tab_observational_outcome.setObjectName(u"tab_observational_outcome")
        self.gridLayout_19 = QGridLayout(self.tab_observational_outcome)
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.textEdit_observational_outcome = QTextEdit(self.tab_observational_outcome)
        self.textEdit_observational_outcome.setObjectName(u"textEdit_observational_outcome")
        self.textEdit_observational_outcome.setReadOnly(True)

        self.gridLayout_19.addWidget(self.textEdit_observational_outcome, 0, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_outcome, "")

        self.gridLayout_13.addWidget(self.tabWidget_observational, 1, 0, 1, 1)

        self.lineEdit_observational_title = QLineEdit(self.page_observational)
        self.lineEdit_observational_title.setObjectName(u"lineEdit_observational_title")
        self.lineEdit_observational_title.setReadOnly(True)

        self.gridLayout_13.addWidget(self.lineEdit_observational_title, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_observational)
        self.page_clinical = QWidget()
        self.page_clinical.setObjectName(u"page_clinical")
        self.gridLayout_20 = QGridLayout(self.page_clinical)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.tabWidget_clinical = QTabWidget(self.page_clinical)
        self.tabWidget_clinical.setObjectName(u"tabWidget_clinical")
        self.tab_clinical_start = QWidget()
        self.tab_clinical_start.setObjectName(u"tab_clinical_start")
        self.gridLayout_21 = QGridLayout(self.tab_clinical_start)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.textEdit_clinical_start = QTextEdit(self.tab_clinical_start)
        self.textEdit_clinical_start.setObjectName(u"textEdit_clinical_start")
        self.textEdit_clinical_start.setReadOnly(True)

        self.gridLayout_21.addWidget(self.textEdit_clinical_start, 0, 0, 1, 1)

        self.pushButton_clinical_start = QPushButton(self.tab_clinical_start)
        self.pushButton_clinical_start.setObjectName(u"pushButton_clinical_start")

        self.gridLayout_21.addWidget(self.pushButton_clinical_start, 1, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_start, "")
        self.tab_clinical_variable = QWidget()
        self.tab_clinical_variable.setObjectName(u"tab_clinical_variable")
        self.gridLayout_23 = QGridLayout(self.tab_clinical_variable)
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.textEdit_clinical_variable = QTextEdit(self.tab_clinical_variable)
        self.textEdit_clinical_variable.setObjectName(u"textEdit_clinical_variable")
        self.textEdit_clinical_variable.setReadOnly(True)

        self.gridLayout_23.addWidget(self.textEdit_clinical_variable, 0, 0, 1, 1)

        self.textEdit_clinical_variable_new = QTextEdit(self.tab_clinical_variable)
        self.textEdit_clinical_variable_new.setObjectName(u"textEdit_clinical_variable_new")

        self.gridLayout_23.addWidget(self.textEdit_clinical_variable_new, 1, 0, 1, 1)

        self.pushButton_clinical_variable_add = QPushButton(self.tab_clinical_variable)
        self.pushButton_clinical_variable_add.setObjectName(u"pushButton_clinical_variable_add")

        self.gridLayout_23.addWidget(self.pushButton_clinical_variable_add, 2, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_variable, "")
        self.tab_clinical_criteria = QWidget()
        self.tab_clinical_criteria.setObjectName(u"tab_clinical_criteria")
        self.gridLayout_22 = QGridLayout(self.tab_clinical_criteria)
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.textEdit_clinico_criteria_new = QTextEdit(self.tab_clinical_criteria)
        self.textEdit_clinico_criteria_new.setObjectName(u"textEdit_clinico_criteria_new")

        self.gridLayout_22.addWidget(self.textEdit_clinico_criteria_new, 1, 0, 1, 1)

        self.textEdit_clinical_criteria = QTextEdit(self.tab_clinical_criteria)
        self.textEdit_clinical_criteria.setObjectName(u"textEdit_clinical_criteria")
        self.textEdit_clinical_criteria.setReadOnly(True)

        self.gridLayout_22.addWidget(self.textEdit_clinical_criteria, 0, 0, 1, 1)

        self.pushButton_clinical_criteria_add = QPushButton(self.tab_clinical_criteria)
        self.pushButton_clinical_criteria_add.setObjectName(u"pushButton_clinical_criteria_add")

        self.gridLayout_22.addWidget(self.pushButton_clinical_criteria_add, 2, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_criteria, "")
        self.tab_clinical_investigational = QWidget()
        self.tab_clinical_investigational.setObjectName(u"tab_clinical_investigational")
        self.gridLayout_28 = QGridLayout(self.tab_clinical_investigational)
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.textEdit_clinical_investigational = QTextEdit(self.tab_clinical_investigational)
        self.textEdit_clinical_investigational.setObjectName(u"textEdit_clinical_investigational")
        self.textEdit_clinical_investigational.setReadOnly(True)

        self.gridLayout_28.addWidget(self.textEdit_clinical_investigational, 0, 0, 1, 1)

        self.textEdit_clinical_investigational_new = QTextEdit(self.tab_clinical_investigational)
        self.textEdit_clinical_investigational_new.setObjectName(u"textEdit_clinical_investigational_new")

        self.gridLayout_28.addWidget(self.textEdit_clinical_investigational_new, 1, 0, 1, 1)

        self.pushButton_clinical_investigational_add = QPushButton(self.tab_clinical_investigational)
        self.pushButton_clinical_investigational_add.setObjectName(u"pushButton_clinical_investigational_add")

        self.gridLayout_28.addWidget(self.pushButton_clinical_investigational_add, 2, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_investigational, "")
        self.tab_clinical_control_drug = QWidget()
        self.tab_clinical_control_drug.setObjectName(u"tab_clinical_control_drug")
        self.gridLayout_26 = QGridLayout(self.tab_clinical_control_drug)
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.textEdit_clinical_control = QTextEdit(self.tab_clinical_control_drug)
        self.textEdit_clinical_control.setObjectName(u"textEdit_clinical_control")
        self.textEdit_clinical_control.setReadOnly(True)

        self.gridLayout_26.addWidget(self.textEdit_clinical_control, 0, 0, 1, 1)

        self.textEdit_clinical_control_new = QTextEdit(self.tab_clinical_control_drug)
        self.textEdit_clinical_control_new.setObjectName(u"textEdit_clinical_control_new")

        self.gridLayout_26.addWidget(self.textEdit_clinical_control_new, 1, 0, 1, 1)

        self.pushButton_clinical_control_add = QPushButton(self.tab_clinical_control_drug)
        self.pushButton_clinical_control_add.setObjectName(u"pushButton_clinical_control_add")

        self.gridLayout_26.addWidget(self.pushButton_clinical_control_add, 2, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_control_drug, "")
        self.tab_clinical_disease = QWidget()
        self.tab_clinical_disease.setObjectName(u"tab_clinical_disease")
        self.gridLayout_27 = QGridLayout(self.tab_clinical_disease)
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.textEdit_clinical_disease = QTextEdit(self.tab_clinical_disease)
        self.textEdit_clinical_disease.setObjectName(u"textEdit_clinical_disease")
        self.textEdit_clinical_disease.setReadOnly(True)

        self.gridLayout_27.addWidget(self.textEdit_clinical_disease, 0, 0, 1, 1)

        self.textEdit_clinical_disease_new = QTextEdit(self.tab_clinical_disease)
        self.textEdit_clinical_disease_new.setObjectName(u"textEdit_clinical_disease_new")

        self.gridLayout_27.addWidget(self.textEdit_clinical_disease_new, 1, 0, 1, 1)

        self.pushButton_clinical_disease_add = QPushButton(self.tab_clinical_disease)
        self.pushButton_clinical_disease_add.setObjectName(u"pushButton_clinical_disease_add")

        self.gridLayout_27.addWidget(self.pushButton_clinical_disease_add, 2, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_disease, "")
        self.tab_clinical_process = QWidget()
        self.tab_clinical_process.setObjectName(u"tab_clinical_process")
        self.gridLayout_24 = QGridLayout(self.tab_clinical_process)
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.pushButton_clinical_process = QPushButton(self.tab_clinical_process)
        self.pushButton_clinical_process.setObjectName(u"pushButton_clinical_process")

        self.gridLayout_24.addWidget(self.pushButton_clinical_process, 2, 0, 1, 1)

        self.textEdit_clinical_process = QTextEdit(self.tab_clinical_process)
        self.textEdit_clinical_process.setObjectName(u"textEdit_clinical_process")
        self.textEdit_clinical_process.setReadOnly(True)

        self.gridLayout_24.addWidget(self.textEdit_clinical_process, 0, 0, 1, 1)

        self.textEdit_4 = QTextEdit(self.tab_clinical_process)
        self.textEdit_4.setObjectName(u"textEdit_4")

        self.gridLayout_24.addWidget(self.textEdit_4, 1, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_process, "")
        self.tab_clinical_outcome = QWidget()
        self.tab_clinical_outcome.setObjectName(u"tab_clinical_outcome")
        self.gridLayout_25 = QGridLayout(self.tab_clinical_outcome)
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.textEdit_clinical_outcome = QTextEdit(self.tab_clinical_outcome)
        self.textEdit_clinical_outcome.setObjectName(u"textEdit_clinical_outcome")
        self.textEdit_clinical_outcome.setReadOnly(True)

        self.gridLayout_25.addWidget(self.textEdit_clinical_outcome, 0, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_outcome, "")

        self.gridLayout_20.addWidget(self.tabWidget_clinical, 1, 0, 1, 1)

        self.lineEdit_clinical_title = QLineEdit(self.page_clinical)
        self.lineEdit_clinical_title.setObjectName(u"lineEdit_clinical_title")
        self.lineEdit_clinical_title.setReadOnly(True)

        self.gridLayout_20.addWidget(self.lineEdit_clinical_title, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_clinical)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 815, 19))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)
        self.tabWidget_start.setCurrentIndex(3)
        self.tabWidget_registry.setCurrentIndex(3)
        self.tabWidget_observational.setCurrentIndex(1)
        self.tabWidget_clinical.setCurrentIndex(6)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Hamelin", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.textEdit_start_welcome.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Hamelin is an application that empowers Clinical Research Professionals (CRPs) to build their own predictive Machine Learning (ML) models</span></p></body></html>", None))
        self.pushButton_start_welcome.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_welcome), QCoreApplication.translate("MainWindow", u"Welcome", None))
        self.textEdit_start_project.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Select a saved project or create a new one</span></p></body></html>", None))
        self.pushButton_start_project.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_project), QCoreApplication.translate("MainWindow", u"Project", None))
        self.pushButton_start_data.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.textEdit_start_data.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Select a CSV dataset or attach a new one</span></p></body></html>", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_data), QCoreApplication.translate("MainWindow", u"Data", None))
        self.pushButton_start_status.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.textEdit_start_status.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Current status of the project</span></p></body></html>", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_status), QCoreApplication.translate("MainWindow", u"Status", None))
        self.textEdit_start_options.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Select an option</span></p></body></html>", None))
        self.comboBox_start_options.setItemText(0, QCoreApplication.translate("MainWindow", u"Patient registry", None))
        self.comboBox_start_options.setItemText(1, QCoreApplication.translate("MainWindow", u"Observational study", None))
        self.comboBox_start_options.setItemText(2, QCoreApplication.translate("MainWindow", u"Clinical trial", None))

        self.pushButton_start_options.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_options), QCoreApplication.translate("MainWindow", u"Options", None))
        self.lineEdit_start_title.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.lineEdit_registry_title.setText(QCoreApplication.translate("MainWindow", u"Patient registry", None))
        self.textEdit_registry_start.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Back to start</span></p></body></html>", None))
        self.pushButton_registry_start.setText(QCoreApplication.translate("MainWindow", u"Back to start", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_start), QCoreApplication.translate("MainWindow", u"Start", None))
        self.textEdit_registry_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate a primary variable (target)</span></p></body></html>", None))
        self.pushButton_registry_variable.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_variable), QCoreApplication.translate("MainWindow", u"Primary variable", None))
        self.pushButton_registry_criteria.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.textEdit_registry_criteria.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate the inclusion and exclusion criteria</span></p></body></html>", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_criteria), QCoreApplication.translate("MainWindow", u"Inclusion/Exclusion criteria", None))
        self.textEdit_registry_settings.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate some settings:</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Separator, missing data, samples, runtime, metric.</span></p></body></html>", None))
        self.pushButton_registry_settings.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_settings), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.pushButton_registry_process.setText(QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_registry_process.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Before processing data, check the summary.</span></p></body></html>", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_process), QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_registry_outcome.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Outcome</span></p></body></html>", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_outcome), QCoreApplication.translate("MainWindow", u"Outcome", None))
        self.textEdit_observational_start.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Back to start</span></p></body></html>", None))
        self.pushButton_observational_start.setText(QCoreApplication.translate("MainWindow", u"Back to start", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_start), QCoreApplication.translate("MainWindow", u"Start", None))
        self.textEdit_observational_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Select a primary variable</span></p></body></html>", None))
        self.pushButton_observational_variable.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_variable), QCoreApplication.translate("MainWindow", u"Primary variable", None))
        self.textEdit_observational_criteria.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate inclusion/exclusion criteria</span></p></body></html>", None))
        self.pushButton_observational_criteria.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_criteria), QCoreApplication.translate("MainWindow", u"Inclusion/Exclusion criteria", None))
        self.pushButton_observational_process.setText(QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_observational_process.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">These are the data. Do you agree?</span></p></body></html>", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_process), QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_observational_outcome.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset</span></p></body></html>", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_outcome), QCoreApplication.translate("MainWindow", u"Outcome", None))
        self.lineEdit_observational_title.setText(QCoreApplication.translate("MainWindow", u"Observational study", None))
        self.textEdit_clinical_start.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio</span></p></body></html>", None))
        self.pushButton_clinical_start.setText(QCoreApplication.translate("MainWindow", u"Back to start", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_start), QCoreApplication.translate("MainWindow", u"Start", None))
        self.textEdit_clinical_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate the primary variable</span></p></body></html>", None))
        self.pushButton_clinical_variable_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_variable), QCoreApplication.translate("MainWindow", u"Primary variable", None))
        self.textEdit_clinical_criteria.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate the inclusion/exclusion criteria</span></p></body></html>", None))
        self.pushButton_clinical_criteria_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_criteria), QCoreApplication.translate("MainWindow", u"Inclusion/Exclusion criteria", None))
        self.textEdit_clinical_investigational.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate the investigational drug</span></p></body></html>", None))
        self.pushButton_clinical_investigational_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_investigational), QCoreApplication.translate("MainWindow", u"Investigational drug", None))
        self.textEdit_clinical_control.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate the control drug</span></p></body></html>", None))
        self.pushButton_clinical_control_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_control_drug), QCoreApplication.translate("MainWindow", u"Control drug", None))
        self.textEdit_clinical_disease.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indicate the disease or disorder</span></p></body></html>", None))
        self.pushButton_clinical_disease_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_disease), QCoreApplication.translate("MainWindow", u"Disease/Disorder", None))
        self.pushButton_clinical_process.setText(QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_clinical_process.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">These are the data. Do you agree?</span></p></body></html>", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_process), QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_clinical_outcome.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Outcome</span></p></body></html>", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_outcome), QCoreApplication.translate("MainWindow", u"Outcome", None))
        self.lineEdit_clinical_title.setText(QCoreApplication.translate("MainWindow", u"Clinical trial", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi


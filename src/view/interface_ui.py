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
    QVBoxLayout, QWidget)

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
        self.textEdit_start_status_text.setReadOnly(True)

        self.gridLayout_5.addWidget(self.textEdit_start_status_text, 1, 0, 1, 1)

        self.tabWidget_start.addTab(self.tab_start_status, "")

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

        self.textEdit_registry_process_summary = QTextEdit(self.tab_registry_process)
        self.textEdit_registry_process_summary.setObjectName(u"textEdit_registry_process_summary")

        self.gridLayout_12.addWidget(self.textEdit_registry_process_summary, 1, 0, 1, 1)

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
        self.textEdit_observational_variable = QTextEdit(self.tab_observational_variable)
        self.textEdit_observational_variable.setObjectName(u"textEdit_observational_variable")
        self.textEdit_observational_variable.setReadOnly(True)

        self.gridLayout_17.addWidget(self.textEdit_observational_variable, 0, 0, 1, 1)

        self.pushButton_observational_variable = QPushButton(self.tab_observational_variable)
        self.pushButton_observational_variable.setObjectName(u"pushButton_observational_variable")

        self.gridLayout_17.addWidget(self.pushButton_observational_variable, 2, 0, 1, 1)

        self.listWidget_observational_variable = QListWidget(self.tab_observational_variable)
        self.listWidget_observational_variable.setObjectName(u"listWidget_observational_variable")

        self.gridLayout_17.addWidget(self.listWidget_observational_variable, 1, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_variable, "")
        self.tab_observational_criteria = QWidget()
        self.tab_observational_criteria.setObjectName(u"tab_observational_criteria")
        self.gridLayout_16 = QGridLayout(self.tab_observational_criteria)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.pushButton_observational_criteria = QPushButton(self.tab_observational_criteria)
        self.pushButton_observational_criteria.setObjectName(u"pushButton_observational_criteria")

        self.gridLayout_16.addWidget(self.pushButton_observational_criteria, 2, 0, 1, 1)

        self.textEdit_observational_criteria = QTextEdit(self.tab_observational_criteria)
        self.textEdit_observational_criteria.setObjectName(u"textEdit_observational_criteria")
        self.textEdit_observational_criteria.setReadOnly(True)

        self.gridLayout_16.addWidget(self.textEdit_observational_criteria, 0, 0, 1, 1)

        self.scrollArea_observational_criteria = QScrollArea(self.tab_observational_criteria)
        self.scrollArea_observational_criteria.setObjectName(u"scrollArea_observational_criteria")
        self.scrollArea_observational_criteria.setWidgetResizable(True)
        self.scrollAreaWidgetContents_observational_criteria = QWidget()
        self.scrollAreaWidgetContents_observational_criteria.setObjectName(u"scrollAreaWidgetContents_observational_criteria")
        self.scrollAreaWidgetContents_observational_criteria.setGeometry(QRect(0, 0, 755, 220))
        self.gridLayout_33 = QGridLayout(self.scrollAreaWidgetContents_observational_criteria)
        self.gridLayout_33.setObjectName(u"gridLayout_33")
        self.widget_observational_criteria = QWidget(self.scrollAreaWidgetContents_observational_criteria)
        self.widget_observational_criteria.setObjectName(u"widget_observational_criteria")

        self.gridLayout_33.addWidget(self.widget_observational_criteria, 0, 0, 1, 1)

        self.scrollArea_observational_criteria.setWidget(self.scrollAreaWidgetContents_observational_criteria)

        self.gridLayout_16.addWidget(self.scrollArea_observational_criteria, 1, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_criteria, "")
        self.tab_observational_settings = QWidget()
        self.tab_observational_settings.setObjectName(u"tab_observational_settings")
        self.gridLayout_31 = QGridLayout(self.tab_observational_settings)
        self.gridLayout_31.setObjectName(u"gridLayout_31")
        self.textEdit_observational_settings = QTextEdit(self.tab_observational_settings)
        self.textEdit_observational_settings.setObjectName(u"textEdit_observational_settings")

        self.gridLayout_31.addWidget(self.textEdit_observational_settings, 0, 0, 1, 1)

        self.scrollArea_observational_settings = QScrollArea(self.tab_observational_settings)
        self.scrollArea_observational_settings.setObjectName(u"scrollArea_observational_settings")
        self.scrollArea_observational_settings.setWidgetResizable(True)
        self.scrollAreaWidgetContents_observational_settings = QWidget()
        self.scrollAreaWidgetContents_observational_settings.setObjectName(u"scrollAreaWidgetContents_observational_settings")
        self.scrollAreaWidgetContents_observational_settings.setGeometry(QRect(0, 0, 755, 220))
        self.gridLayout_34 = QGridLayout(self.scrollAreaWidgetContents_observational_settings)
        self.gridLayout_34.setObjectName(u"gridLayout_34")
        self.widget_observational_settings = QWidget(self.scrollAreaWidgetContents_observational_settings)
        self.widget_observational_settings.setObjectName(u"widget_observational_settings")

        self.gridLayout_34.addWidget(self.widget_observational_settings, 0, 0, 1, 1)

        self.scrollArea_observational_settings.setWidget(self.scrollAreaWidgetContents_observational_settings)

        self.gridLayout_31.addWidget(self.scrollArea_observational_settings, 1, 0, 1, 1)

        self.pushButton_observational_settings = QPushButton(self.tab_observational_settings)
        self.pushButton_observational_settings.setObjectName(u"pushButton_observational_settings")

        self.gridLayout_31.addWidget(self.pushButton_observational_settings, 2, 0, 1, 1)

        self.tabWidget_observational.addTab(self.tab_observational_settings, "")
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

        self.textEdit_observational_process_summary = QTextEdit(self.tab_observational_process)
        self.textEdit_observational_process_summary.setObjectName(u"textEdit_observational_process_summary")

        self.gridLayout_18.addWidget(self.textEdit_observational_process_summary, 1, 0, 1, 1)

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

        self.listWidget_clinical_variable = QListWidget(self.tab_clinical_variable)
        self.listWidget_clinical_variable.setObjectName(u"listWidget_clinical_variable")

        self.gridLayout_23.addWidget(self.listWidget_clinical_variable, 1, 0, 1, 1)

        self.pushButton_clinical_variable_add = QPushButton(self.tab_clinical_variable)
        self.pushButton_clinical_variable_add.setObjectName(u"pushButton_clinical_variable_add")

        self.gridLayout_23.addWidget(self.pushButton_clinical_variable_add, 2, 0, 1, 1)

        self.tabWidget_clinical.addTab(self.tab_clinical_variable, "")
        self.tab_clinical_criteria = QWidget()
        self.tab_clinical_criteria.setObjectName(u"tab_clinical_criteria")
        self.gridLayout_22 = QGridLayout(self.tab_clinical_criteria)
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.textEdit_clinical_criteria = QTextEdit(self.tab_clinical_criteria)
        self.textEdit_clinical_criteria.setObjectName(u"textEdit_clinical_criteria")
        self.textEdit_clinical_criteria.setReadOnly(True)

        self.gridLayout_22.addWidget(self.textEdit_clinical_criteria, 0, 0, 1, 1)

        self.scrollArea_clinical_criteria = QScrollArea(self.tab_clinical_criteria)
        self.scrollArea_clinical_criteria.setObjectName(u"scrollArea_clinical_criteria")
        self.scrollArea_clinical_criteria.setWidgetResizable(True)
        self.scrollAreaWidgetContents_clinical_criteria = QWidget()
        self.scrollAreaWidgetContents_clinical_criteria.setObjectName(u"scrollAreaWidgetContents_clinical_criteria")
        self.scrollAreaWidgetContents_clinical_criteria.setGeometry(QRect(0, 0, 597, 69))
        self.verticalLayout_clinical_criteria = QVBoxLayout(self.scrollAreaWidgetContents_clinical_criteria)
        self.verticalLayout_clinical_criteria.setObjectName(u"verticalLayout_clinical_criteria")
        self.scrollArea_clinical_criteria.setWidget(self.scrollAreaWidgetContents_clinical_criteria)

        self.gridLayout_22.addWidget(self.scrollArea_clinical_criteria, 1, 0, 1, 1)

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

        self.scrollArea_clinical_investigational = QScrollArea(self.tab_clinical_investigational)
        self.scrollArea_clinical_investigational.setObjectName(u"scrollArea_clinical_investigational")
        self.scrollArea_clinical_investigational.setWidgetResizable(True)
        self.scrollAreaWidgetContents_clinical_investigational = QWidget()
        self.scrollAreaWidgetContents_clinical_investigational.setObjectName(u"scrollAreaWidgetContents_clinical_investigational")
        self.scrollAreaWidgetContents_clinical_investigational.setGeometry(QRect(0, 0, 597, 69))
        self.verticalLayout_clinical_investigational = QVBoxLayout(self.scrollAreaWidgetContents_clinical_investigational)
        self.verticalLayout_clinical_investigational.setObjectName(u"verticalLayout_clinical_investigational")
        self.scrollArea_clinical_investigational.setWidget(self.scrollAreaWidgetContents_clinical_investigational)

        self.gridLayout_28.addWidget(self.scrollArea_clinical_investigational, 1, 0, 1, 1)

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

        self.scrollArea_clinical_control = QScrollArea(self.tab_clinical_control_drug)
        self.scrollArea_clinical_control.setObjectName(u"scrollArea_clinical_control")
        self.scrollArea_clinical_control.setWidgetResizable(True)
        self.scrollAreaWidgetContents_clinical_control = QWidget()
        self.scrollAreaWidgetContents_clinical_control.setObjectName(u"scrollAreaWidgetContents_clinical_control")
        self.scrollAreaWidgetContents_clinical_control.setGeometry(QRect(0, 0, 597, 69))
        self.verticalLayout_clinical_control = QVBoxLayout(self.scrollAreaWidgetContents_clinical_control)
        self.verticalLayout_clinical_control.setObjectName(u"verticalLayout_clinical_control")
        self.scrollArea_clinical_control.setWidget(self.scrollAreaWidgetContents_clinical_control)

        self.gridLayout_26.addWidget(self.scrollArea_clinical_control, 1, 0, 1, 1)

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

        self.scrollArea_clinical_disease = QScrollArea(self.tab_clinical_disease)
        self.scrollArea_clinical_disease.setObjectName(u"scrollArea_clinical_disease")
        self.scrollArea_clinical_disease.setWidgetResizable(True)
        self.scrollAreaWidgetContents_clinical_disease = QWidget()
        self.scrollAreaWidgetContents_clinical_disease.setObjectName(u"scrollAreaWidgetContents_clinical_disease")
        self.scrollAreaWidgetContents_clinical_disease.setGeometry(QRect(0, 0, 597, 69))
        self.verticalLayout_clinical_disease = QVBoxLayout(self.scrollAreaWidgetContents_clinical_disease)
        self.verticalLayout_clinical_disease.setObjectName(u"verticalLayout_clinical_disease")
        self.scrollArea_clinical_disease.setWidget(self.scrollAreaWidgetContents_clinical_disease)

        self.gridLayout_27.addWidget(self.scrollArea_clinical_disease, 1, 0, 1, 1)

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

        self.stackedWidget.setCurrentIndex(2)
        self.tabWidget_start.setCurrentIndex(1)
        self.tabWidget_registry.setCurrentIndex(4)
        self.tabWidget_observational.setCurrentIndex(5)
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
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;\">Welcome to Hamelin!</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; tex"
                        "t-indent:0px;\"><span style=\" font-size:13pt;\">Hamelin is a user-friendly tool designed for clinical research professionals who want to create predictive models using artificial intelligence.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:13pt;\">With this application, you can analyze medical data and obtain predictions to help with clinical decision-making, without needing advanced programming knowledge.</span></p></body></html>", None))
        self.pushButton_start_welcome.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_welcome), QCoreApplication.translate("MainWindow", u"Welcome", None))
        self.textEdit_start_options.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Study Type</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:"
                        "0px;\"><span style=\" font-size:12pt;\">Please select the type of study that best describes your research:</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\u2022 </span><span style=\" font-size:11pt; font-weight:600;\">Patient registry</span><span style=\" font-size:11pt;\">: Follow-up of patients with a specific condition</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\u2022 </span><span style=\" font-size:11pt; font-weight:600;\">Observational study</span><span style=\" font-size:11pt;\">: Observation of patients without intervention</span></p>\n"
"<p align=\"ce"
                        "nter\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\u2022 </span><span style=\" font-size:11pt; font-weight:600;\">Clinical trial</span><span style=\" font-size:11pt;\">: Study with controlled intervention or treatment</span></p></body></html>", None))
        self.comboBox_start_options.setItemText(0, QCoreApplication.translate("MainWindow", u"Patient registry", None))
        self.comboBox_start_options.setItemText(1, QCoreApplication.translate("MainWindow", u"Observational study", None))
        self.comboBox_start_options.setItemText(2, QCoreApplication.translate("MainWindow", u"Clinical trial", None))

        self.pushButton_start_options.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_options), QCoreApplication.translate("MainWindow", u"Options", None))
        self.textEdit_start_project.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Project Management</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text"
                        "-indent:0px;\"><span style=\" font-size:12pt;\">A project is like a folder where all information about your study is saved: data, settings, and results.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">You can </span><span style=\" font-size:12pt; font-weight:600;\">create a new project</span><span style=\" font-size:12pt;\"> to start a fresh analysis, or </span><span style=\" font-size:12pt; font-weight:600;\">select an existing project</span><span style=\" font-size:12pt;\"> to continue working on a previous analysis.</span></p></body></html>", None))
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
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Study Data</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:"
                        "0px;\"><span style=\" font-size:12pt;\">The data is the clinical information from your patients that will be analyzed by artificial intelligence. It should be organized in a CSV file format (like a spreadsheet).</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">You can </span><span style=\" font-size:12pt; font-weight:600;\">select an existing data file</span><span style=\" font-size:12pt;\"> from the list, or </span><span style=\" font-size:12pt; font-weight:600;\">upload a new file</span><span style=\" font-size:12pt;\"> from your computer.</span></p></body></html>", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_data), QCoreApplication.translate("MainWindow", u"Data", None))
        self.pushButton_start_status.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.textEdit_start_status.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Project Status</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-ind"
                        "ent:0px;\"><span style=\" font-size:12pt;\">Here you can review the current status of your project and add notes or comments about the progress of your research.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">This information will be saved and help you remember where you left off when you return to work on this project.</span></p></body></html>", None))
        self.tabWidget_start.setTabText(self.tabWidget_start.indexOf(self.tab_start_status), QCoreApplication.translate("MainWindow", u"Status", None))
        self.lineEdit_start_title.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.lineEdit_registry_title.setText(QCoreApplication.translate("MainWindow", u"Patient registry", None))
        self.textEdit_registry_start.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Patient Registry Analysis</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:"
                        "0; text-indent:0px;\"><span style=\" font-size:12pt;\">You are now working with a Patient Registry study. This type of analysis is used to track and analyze patients with a specific medical condition over time.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">You will configure the analysis parameters step by step to create a predictive model that can help identify patterns and outcomes in your patient data.</span></p></body></html>", None))
        self.pushButton_registry_start.setText(QCoreApplication.translate("MainWindow", u"Back to start", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_start), QCoreApplication.translate("MainWindow", u"Start", None))
        self.textEdit_registry_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Primary Variable (Target)</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:"
                        "0; text-indent:0px;\"><span style=\" font-size:12pt;\">Select the main outcome you want to predict or analyze. This is called the </span><span style=\" font-size:12pt; font-weight:600;\">target variable</span><span style=\" font-size:12pt;\"> or </span><span style=\" font-size:12pt; font-weight:600;\">primary endpoint</span><span style=\" font-size:12pt;\">.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Examples: patient survival, treatment response, disease progression, readmission risk, or any clinical outcome you want to predict.</span></p></body></html>", None))
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
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Inclusion and Exclusion Criteria</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-"
                        "indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Define which patients should be </span><span style=\" font-size:12pt; font-weight:600;\">included</span><span style=\" font-size:12pt;\"> in your analysis and which should be </span><span style=\" font-size:12pt; font-weight:600;\">excluded</span><span style=\" font-size:12pt;\">.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Set conditions based on patient characteristics such as age ranges, specific diagnoses, treatment history, or any other clinical parameters relevant to your study.</span></p></body></html>", None))
        self.tabWidget_registry.setTabText(self.tabWidget_registry.indexOf(self.tab_registry_criteria), QCoreApplication.translate("MainWindow", u"Inclusion/Exclusion criteria", None))
        self.textEdit_registry_settings.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Analysis Settings</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-"
                        "indent:0px;\"><span style=\" font-size:12pt;\">Configure technical parameters for your analysis:</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\u2022 </span><span style=\" font-size:11pt; font-weight:600;\">Data separator</span><span style=\" font-size:11pt;\">: How data columns are separated in your file</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\u2022 </span><span style=\" font-size:11pt; font-weight:600;\">Missing data handling</span><span style=\" font-size:11pt;\">: How to treat incomplete patient records</span></p>\n"
"<p align=\"center\" style=\" mar"
                        "gin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\u2022 </span><span style=\" font-size:11pt; font-weight:600;\">Performance metric</span><span style=\" font-size:11pt;\">: How to measure model accuracy</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\u2022 </span><span style=\" font-size:11pt; font-weight:600;\">Analysis goal</span><span style=\" font-size:11pt;\">: Optimize for speed vs. accuracy</span></p></body></html>", None))
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
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Ready to Process</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-i"
                        "ndent:0px;\"><span style=\" font-size:10pt;\">Review the summary below to verify all your settings are correct before starting the analysis.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">The artificial intelligence will analyze your patient registry data and create a predictive model. This process may take several minutes depending on the size of your dataset.</span></p></body></html>", None))
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
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Observational Study Analysis</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-inde"
                        "nt:0; text-indent:0px;\"><span style=\" font-size:10pt;\">You are now working with an Observational Study. This type of analysis examines patient data without any intervention, looking for natural patterns and associations.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">You will set up the analysis parameters to discover relationships between different factors and outcomes in your observational data.</span></p></body></html>", None))
        self.pushButton_observational_start.setText(QCoreApplication.translate("MainWindow", u"Back to start", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_start), QCoreApplication.translate("MainWindow", u"Start", None))
        self.textEdit_observational_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Primary Variable (Outcome of Interest)</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-"
                        "block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Select the main outcome you want to study or predict. This is the </span><span style=\" font-size:10pt; font-weight:600;\">dependent variable</span><span style=\" font-size:10pt;\"> that you believe may be influenced by other factors.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Examples: disease occurrence, treatment effectiveness, quality of life scores, laboratory values, or any clinical measurement you want to analyze.</span></p></body></html>", None))
        self.pushButton_observational_variable.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_variable), QCoreApplication.translate("MainWindow", u"Primary variable", None))
        self.pushButton_observational_criteria.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.textEdit_observational_criteria.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Selection Criteria</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text"
                        "-indent:0px;\"><span style=\" font-size:10pt;\">Define which subjects should be </span><span style=\" font-size:10pt; font-weight:600;\">included</span><span style=\" font-size:10pt;\"> or </span><span style=\" font-size:10pt; font-weight:600;\">excluded</span><span style=\" font-size:10pt;\"> from your observational analysis.</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Set conditions based on demographics, exposure history, baseline characteristics, or any other factors that define your study population.</span></p></body></html>", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_criteria), QCoreApplication.translate("MainWindow", u"Inclusion/Exclusion criteria", None))
        self.textEdit_observational_settings.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Analysis Configuration</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                        "text-indent:0px;\"><span style=\" font-size:10pt;\">Configure technical parameters for your observational analysis:</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">\u2022 </span><span style=\" font-size:9pt; font-weight:600;\">Data format</span><span style=\" font-size:9pt;\">: How your data is structured and separated</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">\u2022 </span><span style=\" font-size:9pt; font-weight:600;\">Missing data strategy</span><span style=\" font-size:9pt;\">: How to handle incomplete observations</span></p>\n"
"<p align=\"center\" style="
                        "\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">\u2022 </span><span style=\" font-size:9pt; font-weight:600;\">Evaluation metric</span><span style=\" font-size:9pt;\">: How to measure prediction performance</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">\u2022 </span><span style=\" font-size:9pt; font-weight:600;\">Optimization goal</span><span style=\" font-size:9pt;\">: Balance between speed and accuracy</span></p></body></html>", None))
        self.pushButton_observational_settings.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_settings), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.pushButton_observational_process.setText(QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_observational_process.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Data Processing and Analysis</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">In this final phase, we will process and analyze your collected data to extract meaningful insights from your observational study:</p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px;"
                        " margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">What happens during processing:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Data Cleaning:</span> Remove inconsistencies and handle missing values in your dataset</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Statistical Analysis:</span> Identify patterns, correlations, and trends in your observational data</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Hypothesis Testing:</span> Test your research questions against the collected evide"
                        "nce</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Results Generation:</span> Create charts, tables, and summaries of your findings</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Tip: Before processing, review the data summary below to ensure all information is correct and complete.</span></p></body></html>", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_process), QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_observational_outcome.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Outcome</span></p></body></html>", None))
        self.tabWidget_observational.setTabText(self.tabWidget_observational.indexOf(self.tab_observational_outcome), QCoreApplication.translate("MainWindow", u"Outcome", None))
        self.lineEdit_observational_title.setText(QCoreApplication.translate("MainWindow", u"Observational study", None))
        self.textEdit_clinical_start.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Clinical Trial Data Analysis</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">You are now working with data from a completed Clinical Trial. This analysis will help you evaluate the effectiveness and safety of experimental treatments compared to control groups.</p"
                        ">\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">What makes clinical trial data special:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Controlled environment:</span> Participants were randomly assigned to treatment groups</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Standardized measurements:</span> Data was collected following strict protocols</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Treatment comparison:</span> Direct compar"
                        "ison between experimental and control treatments</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Safety monitoring:</span> Systematic tracking of adverse events and side effects</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Follow the next steps to configure your clinical trial data analysis and discover treatment efficacy patterns.</span></p></body></html>", None))
        self.pushButton_clinical_start.setText(QCoreApplication.translate("MainWindow", u"Back to start", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_start), QCoreApplication.translate("MainWindow", u"Start", None))
        self.textEdit_clinical_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Primary Endpoint Selection</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Select the <span style=\" font-weight:600;\">primary endpoint</span> from your clinical trial dataset. This is the main outcome that was used to measure treatment effectiveness.</p>\n"
"<p"
                        " style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Common types of primary endpoints:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Clinical response:</span> Treatment success/failure, remission rates</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Time-to-event:</span> Survival time, time to progression, relapse-free survival</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Continuous measures:</span> Blood pressure reduction, symptom scores, qua"
                        "lity of life</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Biomarkers:</span> Laboratory values, imaging measurements</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Choose the variable that best represents the treatment's intended therapeutic effect.</span></p></body></html>", None))
        self.pushButton_clinical_variable_add.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_variable), QCoreApplication.translate("MainWindow", u"Primary variable", None))
        self.textEdit_clinical_criteria.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Patient Selection Criteria</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Define criteria to filter patients from your clinical trial dataset. This helps focus the analysis on the intended study population and ensures data quality.</p>\n"
"<p style=\" margin-top"
                        ":12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Typical inclusion criteria in clinical trials:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Demographics:</span> Age ranges, gender requirements</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Disease stage:</span> Specific disease severity or staging</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Treatment history:</span> Previous therapies, washout periods</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px;"
                        " margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Biomarkers:</span> Laboratory values, genetic markers</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Common exclusion criteria:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Protocol violations, incomplete data, safety concerns</li>\n"
"</ul></body></html>", None))
        self.pushButton_clinical_criteria_add.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_criteria), QCoreApplication.translate("MainWindow", u"Inclusion/Exclusion criteria", None))
        self.textEdit_clinical_investigational.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Experimental Treatment Group</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Identify the <span style=\" font-weight:600;\">experimental treatment group</span> in your clinical trial dataset. This represents patients who received the new treatment being tested.</"
                        "p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">What to specify:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Treatment group identifier:</span> Column name or values that identify experimental arm</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Drug name/code:</span> Name or code of the investigational treatment</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Dosage information:</span> Dose levels or regimens if applicable</li>\n"
""
                        "<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Administration route:</span> How the treatment was given (oral, IV, etc.)</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">This information helps the AI identify which patients received the experimental treatment for comparison analysis.</span></p></body></html>", None))
        self.pushButton_clinical_investigational_add.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_investigational), QCoreApplication.translate("MainWindow", u"Investigational drug", None))
        self.textEdit_clinical_control.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Control Group Identification</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Identify the <span style=\" font-weight:600;\">control group</span> in your clinical trial dataset. This is the comparison group used to evaluate the effectiveness of the experimental tr"
                        "eatment.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Types of control groups:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Placebo:</span> Inactive treatment that looks identical to the experimental drug</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Active control:</span> Standard treatment or existing approved medication</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">No treatment:</span> Natural course of disease without int"
                        "ervention</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Historical control:</span> Comparison with past patient data</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">What to specify:</span> Control group identifier, treatment name/code, and any relevant dosage information.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Accurate control group identification is essential for meaningful treatment comparisons.</span></p></body></html>", None))
        self.pushButton_clinical_control_add.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_control_drug), QCoreApplication.translate("MainWindow", u"Control drug", None))
        self.textEdit_clinical_disease.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Target Condition Specification</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Specify the <span style=\" font-weight:600;\">medical condition</span> that was studied in your clinical trial. This helps contextualize the treatment effects and analysis results.</p>"
                        "\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Information to include:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Disease name:</span> Primary condition being treated (e.g., diabetes, hypertension, cancer)</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Disease stage/severity:</span> Early stage, advanced, mild, moderate, severe</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Medical classification:</span> ICD codes, disease subtype"
                        "s, specific variants</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Study population:</span> Specific patient characteristics or demographics</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Clear disease specification helps ensure the analysis focuses on relevant clinical outcomes and safety considerations.</span></p></body></html>", None))
        self.pushButton_clinical_disease_add.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_disease), QCoreApplication.translate("MainWindow", u"Disease/Disorder", None))
        self.pushButton_clinical_process.setText(QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_clinical_process.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Clinical Trial Data Analysis</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Now we will process your clinical trial data to evaluate treatment efficacy and safety. The AI will perform specialized analyses designed for controlled clinical studies.</p>\n"
"<p styl"
                        "e=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Analysis components:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Efficacy analysis:</span> Compare primary endpoint between treatment groups</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Safety assessment:</span> Analyze adverse events and side effects</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Statistical testing:</span> Determine treatment effect significance</li>\n"
"<li style=\" margin-to"
                        "p:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Subgroup analysis:</span> Identify patient populations with different responses</li>\n"
"<li style=\" margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Predictive modeling:</span> Identify factors that predict treatment success</li>\n"
"</ul>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Review the data summary below and click Process to begin the comprehensive clinical trial analysis.</span></p></body></html>", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_process), QCoreApplication.translate("MainWindow", u"Process", None))
        self.textEdit_clinical_outcome.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Analysis Results</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Your clinical trial analysis is complete. The results below show treatment efficacy, safety profile, and predictive insights from your study data.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:"
                        "0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Results include:</span> Treatment comparison outcomes, statistical significance, safety analysis, and patient subgroup insights.</p></body></html>", None))
        self.tabWidget_clinical.setTabText(self.tabWidget_clinical.indexOf(self.tab_clinical_outcome), QCoreApplication.translate("MainWindow", u"Outcome", None))
        self.lineEdit_clinical_title.setText(QCoreApplication.translate("MainWindow", u"Clinical trial", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi


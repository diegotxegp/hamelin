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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStackedWidget,
    QStatusBar, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1177, 464)
        self.actionAcerca_de_Hamelin = QAction(MainWindow)
        self.actionAcerca_de_Hamelin.setObjectName(u"actionAcerca_de_Hamelin")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_tabs = QWidget()
        self.page_tabs.setObjectName(u"page_tabs")
        self.layout_tabs = QVBoxLayout(self.page_tabs)
        self.layout_tabs.setObjectName(u"layout_tabs")
        self.tabWidget = QTabWidget(self.page_tabs)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_bienvenida = QWidget()
        self.tab_bienvenida.setObjectName(u"tab_bienvenida")
        self.layout_bienvenida = QVBoxLayout(self.tab_bienvenida)
        self.layout_bienvenida.setObjectName(u"layout_bienvenida")
        self.textEdit_bienvenida = QTextEdit(self.tab_bienvenida)
        self.textEdit_bienvenida.setObjectName(u"textEdit_bienvenida")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_bienvenida.sizePolicy().hasHeightForWidth())
        self.textEdit_bienvenida.setSizePolicy(sizePolicy)
        self.textEdit_bienvenida.setHtml(u"\n"
"      <!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"      <html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" />\n"
"      <style type=\"text/css\">p, li { white-space: pre-wrap; }</style></head>\n"
"      <body style=\" font-family:'Sans Serif'; font-size:9pt;\">\n"
"      <p align=\"center\"><span style=\" font-size:12pt;\">\n"
"      Hamelin es una aplicaci\u00f3n que capacita a los Profesionales de Investigaci\u00f3n Cl\u00ednica (CRPs) para crear sus propios modelos predictivos de Aprendizaje Autom\u00e1tico (ML).\n"
"      </span></p>\n"
"      </body></html>\n"
"     ")

        self.layout_bienvenida.addWidget(self.textEdit_bienvenida)

        self.tabWidget.addTab(self.tab_bienvenida, "")
        self.tab_datos = QWidget()
        self.tab_datos.setObjectName(u"tab_datos")
        self.layout_datos = QVBoxLayout(self.tab_datos)
        self.layout_datos.setObjectName(u"layout_datos")
        self.textEdit_datos = QTextEdit(self.tab_datos)
        self.textEdit_datos.setObjectName(u"textEdit_datos")
        self.textEdit_datos.setHtml(u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Adjunta un fichero CSV para analizar los datos.</span></p></body></html>")

        self.layout_datos.addWidget(self.textEdit_datos)

        self.pushButton_adjuntar = QPushButton(self.tab_datos)
        self.pushButton_adjuntar.setObjectName(u"pushButton_adjuntar")

        self.layout_datos.addWidget(self.pushButton_adjuntar, 0, Qt.AlignmentFlag.AlignHCenter)

        self.tabWidget.addTab(self.tab_datos, "")
        self.tab_estado = QWidget()
        self.tab_estado.setObjectName(u"tab_estado")
        self.layout_estado = QVBoxLayout(self.tab_estado)
        self.layout_estado.setObjectName(u"layout_estado")
        self.textEdit_estado = QTextEdit(self.tab_estado)
        self.textEdit_estado.setObjectName(u"textEdit_estado")
        self.textEdit_estado.setHtml(u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Estado de los datos.</span></p></body></html>")

        self.layout_estado.addWidget(self.textEdit_estado)

        self.tabWidget.addTab(self.tab_estado, "")
        self.tab_opciones = QWidget()
        self.tab_opciones.setObjectName(u"tab_opciones")
        self.layout_opciones = QVBoxLayout(self.tab_opciones)
        self.layout_opciones.setObjectName(u"layout_opciones")
        self.textEdit_opciones = QTextEdit(self.tab_opciones)
        self.textEdit_opciones.setObjectName(u"textEdit_opciones")
        self.textEdit_opciones.setHtml(u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona un procedimiento a seguir.</span></p></body></html>")

        self.layout_opciones.addWidget(self.textEdit_opciones)

        self.comboBox_opciones = QComboBox(self.tab_opciones)
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.setObjectName(u"comboBox_opciones")

        self.layout_opciones.addWidget(self.comboBox_opciones, 0, Qt.AlignmentFlag.AlignHCenter)

        self.pushButton_opciones = QPushButton(self.tab_opciones)
        self.pushButton_opciones.setObjectName(u"pushButton_opciones")

        self.layout_opciones.addWidget(self.pushButton_opciones, 0, Qt.AlignmentFlag.AlignHCenter)

        self.tabWidget.addTab(self.tab_opciones, "")

        self.layout_tabs.addWidget(self.tabWidget)

        self.stackedWidget.addWidget(self.page_tabs)
        self.page_extra1 = QWidget()
        self.page_extra1.setObjectName(u"page_extra1")
        self.layout_extra1 = QVBoxLayout(self.page_extra1)
        self.layout_extra1.setObjectName(u"layout_extra1")
        self.tabWidget_2 = QTabWidget(self.page_extra1)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tabWidget_2.setEnabled(True)
        self.tab_inicio = QWidget()
        self.tab_inicio.setObjectName(u"tab_inicio")
        self.tab_inicio.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.textEdit = QTextEdit(self.tab_inicio)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 10, 1121, 121))
        self.pushButton_3 = QPushButton(self.tab_inicio)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(460, 170, 83, 22))
        self.tabWidget_2.addTab(self.tab_inicio, "")
        self.tab_dataset = QWidget()
        self.tab_dataset.setObjectName(u"tab_dataset")
        self.textEdit_2 = QTextEdit(self.tab_dataset)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(10, 10, 1121, 121))
        self.widget = QWidget(self.tab_dataset)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 150, 651, 161))
        self.tabWidget_2.addTab(self.tab_dataset, "")
        self.tab_criterios_inclusion_exclusion = QWidget()
        self.tab_criterios_inclusion_exclusion.setObjectName(u"tab_criterios_inclusion_exclusion")
        self.textEdit_3 = QTextEdit(self.tab_criterios_inclusion_exclusion)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setGeometry(QRect(10, 10, 1131, 121))
        self.listWidget_2 = QListWidget(self.tab_criterios_inclusion_exclusion)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        self.listWidget_2.setObjectName(u"listWidget_2")
        self.listWidget_2.setGeometry(QRect(10, 140, 1131, 192))
        self.listWidget_2.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget_2.addTab(self.tab_criterios_inclusion_exclusion, "")
        self.tab_variable_principal = QWidget()
        self.tab_variable_principal.setObjectName(u"tab_variable_principal")
        self.textEdit_4 = QTextEdit(self.tab_variable_principal)
        self.textEdit_4.setObjectName(u"textEdit_4")
        self.textEdit_4.setGeometry(QRect(10, 10, 1021, 121))
        self.listWidget_3 = QListWidget(self.tab_variable_principal)
        QListWidgetItem(self.listWidget_3)
        QListWidgetItem(self.listWidget_3)
        QListWidgetItem(self.listWidget_3)
        self.listWidget_3.setObjectName(u"listWidget_3")
        self.listWidget_3.setGeometry(QRect(10, 140, 1021, 192))
        self.listWidget_3.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget_2.addTab(self.tab_variable_principal, "")
        self.tab_procesar = QWidget()
        self.tab_procesar.setObjectName(u"tab_procesar")
        self.textEdit_5 = QTextEdit(self.tab_procesar)
        self.textEdit_5.setObjectName(u"textEdit_5")
        self.textEdit_5.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton = QPushButton(self.tab_procesar)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(290, 180, 83, 22))
        self.tabWidget_2.addTab(self.tab_procesar, "")
        self.tab_resultados = QWidget()
        self.tab_resultados.setObjectName(u"tab_resultados")
        self.textEdit_6 = QTextEdit(self.tab_resultados)
        self.textEdit_6.setObjectName(u"textEdit_6")
        self.textEdit_6.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget_2.addTab(self.tab_resultados, "")

        self.layout_extra1.addWidget(self.tabWidget_2)

        self.stackedWidget.addWidget(self.page_extra1)
        self.page_extra2 = QWidget()
        self.page_extra2.setObjectName(u"page_extra2")
        self.layout_extra2 = QVBoxLayout(self.page_extra2)
        self.layout_extra2.setObjectName(u"layout_extra2")
        self.label_extra2 = QLabel(self.page_extra2)
        self.label_extra2.setObjectName(u"label_extra2")

        self.layout_extra2.addWidget(self.label_extra2)

        self.stackedWidget.addWidget(self.page_extra2)

        self.mainLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1177, 19))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuEdici_n = QMenu(self.menubar)
        self.menuEdici_n.setObjectName(u"menuEdici_n")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuEdici_n.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuAyuda.addAction(self.actionAcerca_de_Hamelin)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(3)
        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Hamelin", None))
        self.actionAcerca_de_Hamelin.setText(QCoreApplication.translate("MainWindow", u"Acerca de Hamelin", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_bienvenida), QCoreApplication.translate("MainWindow", u"Bienvenida", None))
        self.pushButton_adjuntar.setText(QCoreApplication.translate("MainWindow", u"Adjuntar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_datos), QCoreApplication.translate("MainWindow", u"Datos", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_estado), QCoreApplication.translate("MainWindow", u"Estado", None))
        self.comboBox_opciones.setItemText(0, QCoreApplication.translate("MainWindow", u"Registro de pacientes", None))
        self.comboBox_opciones.setItemText(1, QCoreApplication.translate("MainWindow", u"Estudio observacional", None))
        self.comboBox_opciones.setItemText(2, QCoreApplication.translate("MainWindow", u"Estudio cl\u00ednico", None))

        self.pushButton_opciones.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_opciones), QCoreApplication.translate("MainWindow", u"Opciones", None))
#if QT_CONFIG(accessibility)
        self.tab_inicio.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.textEdit.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio.</span></p></body></html>", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_inicio), QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Modificar dataset.</span></p></body></html>", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_dataset), QCoreApplication.translate("MainWindow", u"Dataset", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n.</span></p></body></html>", None))

        __sortingEnabled = self.listWidget_2.isSortingEnabled()
        self.listWidget_2.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget_2.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"Pacientes con consentimiento informado", None));
        ___qlistwidgetitem1 = self.listWidget_2.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Pacientes de cualquier edad y sexo, incluyendo menores de edad y embarazadas", None));
        ___qlistwidgetitem2 = self.listWidget_2.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Ingreso hospitalario con diagn\u00f3stico de COVID-19 seg\u00fan los criterios cl\u00ednicos y microbiol\u00f3gicos que se establezcan por las Autoridades Sanitarias y la pr\u00e1ctica cl\u00ednica (\u00e9stos pueden modificarse en base al \u201cDocumento t\u00e9cnico. Manejo cl\u00ednico del COVID-19: atenci\u00f3n hospitalaria\u201d del Ministerio de Sanidad)", None));
        ___qlistwidgetitem3 = self.listWidget_2.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Pacientes que reciban cualquier tratamiento espec\u00edfico para tratar la enfermedad COVID-19 (seg\u00fan el \u201cDocumento T\u00e9cnico. Manejo cl\u00ednico del COVID-19: tratamiento medico\u201d del Ministerio de Sanidad, y \u201cTratamientos disponibles para el manejo de la infecci\u00f3n respiratoria por SARS-CoV-2\u201d de la AEMPS)", None));
        ___qlistwidgetitem4 = self.listWidget_2.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Pacientes que ingresen pero no reciban un tratamiento espec\u00edfico para tratar la enfermedad COVID-19", None));
        self.listWidget_2.setSortingEnabled(__sortingEnabled)

        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_criterios_inclusion_exclusion), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_4.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal.</span></p></body></html>", None))

        __sortingEnabled1 = self.listWidget_3.isSortingEnabled()
        self.listWidget_3.setSortingEnabled(False)
        ___qlistwidgetitem5 = self.listWidget_3.item(0)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Respuesta al tratamiento", None));
        ___qlistwidgetitem6 = self.listWidget_3.item(1)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Recuperaci\u00f3n", None));
        ___qlistwidgetitem7 = self.listWidget_3.item(2)
        ___qlistwidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Mortalidad", None));
        self.listWidget_3.setSortingEnabled(__sortingEnabled1)

        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_variable_principal), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.textEdit_5.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset.</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_procesar), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.textEdit_6.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset.</span></p></body></html>", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_resultados), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.label_extra2.setText(QCoreApplication.translate("MainWindow", u"P\u00e1gina adicional 2 - M\u00e1s contenido aqu\u00ed.", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("MainWindow", u"Archivo", None))
        self.menuEdici_n.setTitle(QCoreApplication.translate("MainWindow", u"Edici\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("MainWindow", u"Ayuda", None))
    # retranslateUi


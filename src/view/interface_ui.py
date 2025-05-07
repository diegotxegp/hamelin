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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGridLayout,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStackedWidget,
    QStatusBar, QTabWidget, QTextEdit, QWidget)

class Ui_ventana_inicio(object):
    def setupUi(self, ventana_inicio):
        if not ventana_inicio.objectName():
            ventana_inicio.setObjectName(u"ventana_inicio")
        ventana_inicio.resize(1043, 454)
        self.actionAbout = QAction(ventana_inicio)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionAcerca_de_Hamelin = QAction(ventana_inicio)
        self.actionAcerca_de_Hamelin.setObjectName(u"actionAcerca_de_Hamelin")
        self.centralwidget = QWidget(ventana_inicio)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(9, -1, 681, 371))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.gridLayoutWidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.tabWidget = QTabWidget(self.page)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QRect(0, 0, 679, 369))
        self.tab_bienvenida = QWidget()
        self.tab_bienvenida.setObjectName(u"tab_bienvenida")
        self.tab_bienvenida.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.textEdit_bienvenida = QTextEdit(self.tab_bienvenida)
        self.textEdit_bienvenida.setObjectName(u"textEdit_bienvenida")
        self.textEdit_bienvenida.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget.addTab(self.tab_bienvenida, "")
        self.tab_datos = QWidget()
        self.tab_datos.setObjectName(u"tab_datos")
        self.textEdit_datos = QTextEdit(self.tab_datos)
        self.textEdit_datos.setObjectName(u"textEdit_datos")
        self.textEdit_datos.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_adjuntar = QPushButton(self.tab_datos)
        self.pushButton_adjuntar.setObjectName(u"pushButton_adjuntar")
        self.pushButton_adjuntar.setGeometry(QRect(290, 180, 83, 22))
        self.tabWidget.addTab(self.tab_datos, "")
        self.tab_estado = QWidget()
        self.tab_estado.setObjectName(u"tab_estado")
        self.textEdit_estado = QTextEdit(self.tab_estado)
        self.textEdit_estado.setObjectName(u"textEdit_estado")
        self.textEdit_estado.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget.addTab(self.tab_estado, "")
        self.tab_opciones = QWidget()
        self.tab_opciones.setObjectName(u"tab_opciones")
        self.comboBox_opciones = QComboBox(self.tab_opciones)
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.setObjectName(u"comboBox_opciones")
        self.comboBox_opciones.setGeometry(QRect(250, 170, 161, 22))
        self.textEdit_opciones = QTextEdit(self.tab_opciones)
        self.textEdit_opciones.setObjectName(u"textEdit_opciones")
        self.textEdit_opciones.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_opciones = QPushButton(self.tab_opciones)
        self.pushButton_opciones.setObjectName(u"pushButton_opciones")
        self.pushButton_opciones.setGeometry(QRect(290, 210, 83, 22))
        self.tabWidget.addTab(self.tab_opciones, "")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.tabWidget_2 = QTabWidget(self.page_2)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tabWidget_2.setEnabled(True)
        self.tabWidget_2.setGeometry(QRect(0, 0, 679, 369))
        self.tab_inicio = QWidget()
        self.tab_inicio.setObjectName(u"tab_inicio")
        self.tab_inicio.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.textEdit = QTextEdit(self.tab_inicio)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_3 = QPushButton(self.tab_inicio)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(290, 170, 83, 22))
        self.tabWidget_2.addTab(self.tab_inicio, "")
        self.tab_dataset = QWidget()
        self.tab_dataset.setObjectName(u"tab_dataset")
        self.textEdit_2 = QTextEdit(self.tab_dataset)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(10, 10, 651, 121))
        self.widget = QWidget(self.tab_dataset)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 150, 651, 161))
        self.tabWidget_2.addTab(self.tab_dataset, "")
        self.tab_criterios_inclusion_exclusion = QWidget()
        self.tab_criterios_inclusion_exclusion.setObjectName(u"tab_criterios_inclusion_exclusion")
        self.textEdit_3 = QTextEdit(self.tab_criterios_inclusion_exclusion)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setGeometry(QRect(10, 10, 651, 121))
        self.listWidget_2 = QListWidget(self.tab_criterios_inclusion_exclusion)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        self.listWidget_2.setObjectName(u"listWidget_2")
        self.listWidget_2.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_2.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget_2.addTab(self.tab_criterios_inclusion_exclusion, "")
        self.tab_variable_principal = QWidget()
        self.tab_variable_principal.setObjectName(u"tab_variable_principal")
        self.textEdit_4 = QTextEdit(self.tab_variable_principal)
        self.textEdit_4.setObjectName(u"textEdit_4")
        self.textEdit_4.setGeometry(QRect(10, 10, 651, 121))
        self.listWidget_3 = QListWidget(self.tab_variable_principal)
        QListWidgetItem(self.listWidget_3)
        QListWidgetItem(self.listWidget_3)
        QListWidgetItem(self.listWidget_3)
        self.listWidget_3.setObjectName(u"listWidget_3")
        self.listWidget_3.setGeometry(QRect(10, 140, 651, 192))
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
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.tabWidget_3 = QTabWidget(self.page_3)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        self.tabWidget_3.setEnabled(True)
        self.tabWidget_3.setGeometry(QRect(0, 0, 679, 369))
        self.tab_inicio_2 = QWidget()
        self.tab_inicio_2.setObjectName(u"tab_inicio_2")
        self.tab_inicio_2.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.textEdit_7 = QTextEdit(self.tab_inicio_2)
        self.textEdit_7.setObjectName(u"textEdit_7")
        self.textEdit_7.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_4 = QPushButton(self.tab_inicio_2)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(290, 170, 83, 22))
        self.tabWidget_3.addTab(self.tab_inicio_2, "")
        self.tab_criterios_inclusion_exclusion_2 = QWidget()
        self.tab_criterios_inclusion_exclusion_2.setObjectName(u"tab_criterios_inclusion_exclusion_2")
        self.textEdit_8 = QTextEdit(self.tab_criterios_inclusion_exclusion_2)
        self.textEdit_8.setObjectName(u"textEdit_8")
        self.textEdit_8.setGeometry(QRect(10, 10, 651, 121))
        self.listWidget_4 = QListWidget(self.tab_criterios_inclusion_exclusion_2)
        QListWidgetItem(self.listWidget_4)
        QListWidgetItem(self.listWidget_4)
        QListWidgetItem(self.listWidget_4)
        QListWidgetItem(self.listWidget_4)
        QListWidgetItem(self.listWidget_4)
        QListWidgetItem(self.listWidget_4)
        QListWidgetItem(self.listWidget_4)
        self.listWidget_4.setObjectName(u"listWidget_4")
        self.listWidget_4.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_4.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget_3.addTab(self.tab_criterios_inclusion_exclusion_2, "")
        self.tab_variable_principal_2 = QWidget()
        self.tab_variable_principal_2.setObjectName(u"tab_variable_principal_2")
        self.textEdit_9 = QTextEdit(self.tab_variable_principal_2)
        self.textEdit_9.setObjectName(u"textEdit_9")
        self.textEdit_9.setGeometry(QRect(10, 10, 651, 121))
        self.listWidget_5 = QListWidget(self.tab_variable_principal_2)
        QListWidgetItem(self.listWidget_5)
        self.listWidget_5.setObjectName(u"listWidget_5")
        self.listWidget_5.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_5.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget_3.addTab(self.tab_variable_principal_2, "")
        self.tab_procesar_2 = QWidget()
        self.tab_procesar_2.setObjectName(u"tab_procesar_2")
        self.textEdit_10 = QTextEdit(self.tab_procesar_2)
        self.textEdit_10.setObjectName(u"textEdit_10")
        self.textEdit_10.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_2 = QPushButton(self.tab_procesar_2)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(290, 180, 83, 22))
        self.tabWidget_3.addTab(self.tab_procesar_2, "")
        self.tab_resultados_2 = QWidget()
        self.tab_resultados_2.setObjectName(u"tab_resultados_2")
        self.textEdit_11 = QTextEdit(self.tab_resultados_2)
        self.textEdit_11.setObjectName(u"textEdit_11")
        self.textEdit_11.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget_3.addTab(self.tab_resultados_2, "")
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.stackedWidget.addWidget(self.page_4)

        self.gridLayout.addWidget(self.stackedWidget, 0, 1, 1, 1)

        self.tabWidget_4 = QTabWidget(self.centralwidget)
        self.tabWidget_4.setObjectName(u"tabWidget_4")
        self.tabWidget_4.setEnabled(True)
        self.tabWidget_4.setGeometry(QRect(10, 0, 1021, 369))
        self.tab_inicio_3 = QWidget()
        self.tab_inicio_3.setObjectName(u"tab_inicio_3")
        self.tab_inicio_3.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.textEdit_12 = QTextEdit(self.tab_inicio_3)
        self.textEdit_12.setObjectName(u"textEdit_12")
        self.textEdit_12.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_5 = QPushButton(self.tab_inicio_3)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(290, 170, 83, 22))
        self.tabWidget_4.addTab(self.tab_inicio_3, "")
        self.tab_criterios_inclusion_exclusion_3 = QWidget()
        self.tab_criterios_inclusion_exclusion_3.setObjectName(u"tab_criterios_inclusion_exclusion_3")
        self.textEdit_13 = QTextEdit(self.tab_criterios_inclusion_exclusion_3)
        self.textEdit_13.setObjectName(u"textEdit_13")
        self.textEdit_13.setGeometry(QRect(10, 10, 651, 121))
        self.listWidget_6 = QListWidget(self.tab_criterios_inclusion_exclusion_3)
        QListWidgetItem(self.listWidget_6)
        QListWidgetItem(self.listWidget_6)
        QListWidgetItem(self.listWidget_6)
        QListWidgetItem(self.listWidget_6)
        QListWidgetItem(self.listWidget_6)
        QListWidgetItem(self.listWidget_6)
        QListWidgetItem(self.listWidget_6)
        QListWidgetItem(self.listWidget_6)
        self.listWidget_6.setObjectName(u"listWidget_6")
        self.listWidget_6.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_6.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget_4.addTab(self.tab_criterios_inclusion_exclusion_3, "")
        self.tab_farmaco_experimental = QWidget()
        self.tab_farmaco_experimental.setObjectName(u"tab_farmaco_experimental")
        self.tabWidget_4.addTab(self.tab_farmaco_experimental, "")
        self.tab_farmaco_control = QWidget()
        self.tab_farmaco_control.setObjectName(u"tab_farmaco_control")
        self.tabWidget_4.addTab(self.tab_farmaco_control, "")
        self.tab_enfermedad_trastorno = QWidget()
        self.tab_enfermedad_trastorno.setObjectName(u"tab_enfermedad_trastorno")
        self.tabWidget_4.addTab(self.tab_enfermedad_trastorno, "")
        self.tab_variable_principal_3 = QWidget()
        self.tab_variable_principal_3.setObjectName(u"tab_variable_principal_3")
        self.textEdit_14 = QTextEdit(self.tab_variable_principal_3)
        self.textEdit_14.setObjectName(u"textEdit_14")
        self.textEdit_14.setGeometry(QRect(10, 10, 651, 121))
        self.listWidget_7 = QListWidget(self.tab_variable_principal_3)
        QListWidgetItem(self.listWidget_7)
        self.listWidget_7.setObjectName(u"listWidget_7")
        self.listWidget_7.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_7.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget_4.addTab(self.tab_variable_principal_3, "")
        self.tab_procesar_3 = QWidget()
        self.tab_procesar_3.setObjectName(u"tab_procesar_3")
        self.textEdit_15 = QTextEdit(self.tab_procesar_3)
        self.textEdit_15.setObjectName(u"textEdit_15")
        self.textEdit_15.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_6 = QPushButton(self.tab_procesar_3)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(290, 180, 83, 22))
        self.tabWidget_4.addTab(self.tab_procesar_3, "")
        self.tab_resultados_3 = QWidget()
        self.tab_resultados_3.setObjectName(u"tab_resultados_3")
        self.textEdit_16 = QTextEdit(self.tab_resultados_3)
        self.textEdit_16.setObjectName(u"textEdit_16")
        self.textEdit_16.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget_4.addTab(self.tab_resultados_3, "")
        ventana_inicio.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(ventana_inicio)
        self.statusbar.setObjectName(u"statusbar")
        ventana_inicio.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(ventana_inicio)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1043, 19))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuEdici_n = QMenu(self.menubar)
        self.menuEdici_n.setObjectName(u"menuEdici_n")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        ventana_inicio.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuEdici_n.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuAyuda.addAction(self.actionAcerca_de_Hamelin)

        self.retranslateUi(ventana_inicio)

        self.stackedWidget.setCurrentIndex(3)
        self.tabWidget.setCurrentIndex(3)
        self.tabWidget_2.setCurrentIndex(1)
        self.tabWidget_3.setCurrentIndex(4)
        self.tabWidget_4.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(ventana_inicio)
    # setupUi

    def retranslateUi(self, ventana_inicio):
        ventana_inicio.setWindowTitle(QCoreApplication.translate("ventana_inicio", u"Hamelin", None))
        self.actionAbout.setText(QCoreApplication.translate("ventana_inicio", u"Acerca", None))
        self.actionAcerca_de_Hamelin.setText(QCoreApplication.translate("ventana_inicio", u"Acerca de Hamelin", None))
#if QT_CONFIG(accessibility)
        self.tab_bienvenida.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.textEdit_bienvenida.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Hamelin es una aplicaci\u00f3n que capacita a los Profesionales de Investigaci\u00f3n Cl\u00ednica (CRPs) para crear sus propios modelos predictivos de Aprendizaje Autom\u00e1tico (ML).</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_bienvenida), QCoreApplication.translate("ventana_inicio", u"Bienvenida", None))
        self.textEdit_datos.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Adjunta un fichero CSV para analizar los datos.</span></p></body></html>", None))
        self.pushButton_adjuntar.setText(QCoreApplication.translate("ventana_inicio", u"Adjuntar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_datos), QCoreApplication.translate("ventana_inicio", u"Datos", None))
        self.textEdit_estado.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Estado de los datos.</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_estado), QCoreApplication.translate("ventana_inicio", u"Estado", None))
        self.comboBox_opciones.setItemText(0, QCoreApplication.translate("ventana_inicio", u"Registro de pacientes", None))
        self.comboBox_opciones.setItemText(1, QCoreApplication.translate("ventana_inicio", u"Estudio observacional", None))
        self.comboBox_opciones.setItemText(2, QCoreApplication.translate("ventana_inicio", u"Estudio cl\u00ednico", None))

        self.textEdit_opciones.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona un procedimiento a seguir.</span></p></body></html>", None))
        self.pushButton_opciones.setText(QCoreApplication.translate("ventana_inicio", u"Ok", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_opciones), QCoreApplication.translate("ventana_inicio", u"Opciones", None))
#if QT_CONFIG(accessibility)
        self.tab_inicio.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.textEdit.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio.</span></p></body></html>", None))
        self.pushButton_3.setText(QCoreApplication.translate("ventana_inicio", u"Inicio", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_inicio), QCoreApplication.translate("ventana_inicio", u"Inicio", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Modificar dataset.</span></p></body></html>", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_dataset), QCoreApplication.translate("ventana_inicio", u"Dataset", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
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
        ___qlistwidgetitem.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes con consentimiento informado", None));
        ___qlistwidgetitem1 = self.listWidget_2.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes de cualquier edad y sexo, incluyendo menores de edad y embarazadas", None));
        ___qlistwidgetitem2 = self.listWidget_2.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("ventana_inicio", u"Ingreso hospitalario con diagn\u00f3stico de COVID-19 seg\u00fan los criterios cl\u00ednicos y microbiol\u00f3gicos que se establezcan por las Autoridades Sanitarias y la pr\u00e1ctica cl\u00ednica (\u00e9stos pueden modificarse en base al \u201cDocumento t\u00e9cnico. Manejo cl\u00ednico del COVID-19: atenci\u00f3n hospitalaria\u201d del Ministerio de Sanidad)", None));
        ___qlistwidgetitem3 = self.listWidget_2.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes que reciban cualquier tratamiento espec\u00edfico para tratar la enfermedad COVID-19 (seg\u00fan el \u201cDocumento T\u00e9cnico. Manejo cl\u00ednico del COVID-19: tratamiento medico\u201d del Ministerio de Sanidad, y \u201cTratamientos disponibles para el manejo de la infecci\u00f3n respiratoria por SARS-CoV-2\u201d de la AEMPS)", None));
        ___qlistwidgetitem4 = self.listWidget_2.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes que ingresen pero no reciban un tratamiento espec\u00edfico para tratar la enfermedad COVID-19", None));
        self.listWidget_2.setSortingEnabled(__sortingEnabled)

        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_criterios_inclusion_exclusion), QCoreApplication.translate("ventana_inicio", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_4.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
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
        ___qlistwidgetitem5.setText(QCoreApplication.translate("ventana_inicio", u"Respuesta al tratamiento", None));
        ___qlistwidgetitem6 = self.listWidget_3.item(1)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("ventana_inicio", u"Recuperaci\u00f3n", None));
        ___qlistwidgetitem7 = self.listWidget_3.item(2)
        ___qlistwidgetitem7.setText(QCoreApplication.translate("ventana_inicio", u"Mortalidad", None));
        self.listWidget_3.setSortingEnabled(__sortingEnabled1)

        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_variable_principal), QCoreApplication.translate("ventana_inicio", u"Variable principal", None))
        self.textEdit_5.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset.</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("ventana_inicio", u"Procesar", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_procesar), QCoreApplication.translate("ventana_inicio", u"Procesar", None))
        self.textEdit_6.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset.</span></p></body></html>", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_resultados), QCoreApplication.translate("ventana_inicio", u"Resultados", None))
#if QT_CONFIG(accessibility)
        self.tab_inicio_2.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.textEdit_7.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio.</span></p></body></html>", None))
        self.pushButton_4.setText(QCoreApplication.translate("ventana_inicio", u"Inicio", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_inicio_2), QCoreApplication.translate("ventana_inicio", u"Inicio", None))
        self.textEdit_8.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n.</span></p></body></html>", None))

        __sortingEnabled2 = self.listWidget_4.isSortingEnabled()
        self.listWidget_4.setSortingEnabled(False)
        ___qlistwidgetitem8 = self.listWidget_4.item(0)
        ___qlistwidgetitem8.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes que comprenden y firman el consentimiento informado que se le presentar\u00e1 antes de entrar al quir\u00f3fano", None));
        ___qlistwidgetitem9 = self.listWidget_4.item(1)
        ___qlistwidgetitem9.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes adultos de ambos sexos que van a ser sometidos a una cirug\u00eda programada de m\u00e1s de 3 horas de duraci\u00f3n, por parte del serviciode Neurocirug\u00eda Unidad de Raquis del HUMV, entre el a\u00f1o 2023 y 2024", None));
        ___qlistwidgetitem10 = self.listWidget_4.item(2)
        ___qlistwidgetitem10.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes posicionados en dec\u00fabito prono, supino, lateral y en silla de playa/ sentado", None));
        ___qlistwidgetitem11 = self.listWidget_4.item(3)
        ___qlistwidgetitem11.setText(QCoreApplication.translate("ventana_inicio", u"Cirug\u00edas susceptibles de colocaci\u00f3n de sondaje vesical con medici\u00f3n de la temperatura corporal", None));
        ___qlistwidgetitem12 = self.listWidget_4.item(4)
        ___qlistwidgetitem12.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes ingresados el d\u00eda previo a la cirug\u00eda", None));
        ___qlistwidgetitem13 = self.listWidget_4.item(5)
        ___qlistwidgetitem13.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes con lesiones por presi\u00f3n visibles presentes antes de la cirug\u00eda", None));
        ___qlistwidgetitem14 = self.listWidget_4.item(6)
        ___qlistwidgetitem14.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes con trastorno cognitivo o dificultad de conocimiento escrito y oral", None));
        self.listWidget_4.setSortingEnabled(__sortingEnabled2)

        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_criterios_inclusion_exclusion_2), QCoreApplication.translate("ventana_inicio", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_9.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal.</span></p></body></html>", None))

        __sortingEnabled3 = self.listWidget_5.isSortingEnabled()
        self.listWidget_5.setSortingEnabled(False)
        ___qlistwidgetitem15 = self.listWidget_5.item(0)
        ___qlistwidgetitem15.setText(QCoreApplication.translate("ventana_inicio", u"Aparici\u00f3n de LPP en pacientes neuroquir\u00farjicos en un periodo >3 horas de intervenci\u00f3n", None));
        self.listWidget_5.setSortingEnabled(__sortingEnabled3)

        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_variable_principal_2), QCoreApplication.translate("ventana_inicio", u"Variable principal", None))
        self.textEdit_10.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset.</span></p></body></html>", None))
        self.pushButton_2.setText(QCoreApplication.translate("ventana_inicio", u"Procesar", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_procesar_2), QCoreApplication.translate("ventana_inicio", u"Procesar", None))
        self.textEdit_11.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset.</span></p></body></html>", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_resultados_2), QCoreApplication.translate("ventana_inicio", u"Resultados", None))
#if QT_CONFIG(accessibility)
        self.tab_inicio_3.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.textEdit_12.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio.</span></p></body></html>", None))
        self.pushButton_5.setText(QCoreApplication.translate("ventana_inicio", u"Inicio", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_inicio_3), QCoreApplication.translate("ventana_inicio", u"Inicio", None))
        self.textEdit_13.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n.</span></p></body></html>", None))

        __sortingEnabled4 = self.listWidget_6.isSortingEnabled()
        self.listWidget_6.setSortingEnabled(False)
        ___qlistwidgetitem16 = self.listWidget_6.item(0)
        ___qlistwidgetitem16.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes que firmen el consentimiento informado", None));
        ___qlistwidgetitem17 = self.listWidget_6.item(1)
        ___qlistwidgetitem17.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes mayores de 18 a\u00f1os", None));
        ___qlistwidgetitem18 = self.listWidget_6.item(2)
        ___qlistwidgetitem18.setText(QCoreApplication.translate("ventana_inicio", u"Portadores de pr\u00f3tesis de cadera o rodilla, diagnosticados de una infecci\u00f3n prot\u00e9sica", None));
        ___qlistwidgetitem19 = self.listWidget_6.item(3)
        ___qlistwidgetitem19.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes sin posibilidad de tratamiento curativo", None));
        ___qlistwidgetitem20 = self.listWidget_6.item(4)
        ___qlistwidgetitem20.setText(QCoreApplication.translate("ventana_inicio", u"Sin infecciones monomicrobianas", None));
        ___qlistwidgetitem21 = self.listWidget_6.item(5)
        ___qlistwidgetitem21.setText(QCoreApplication.translate("ventana_inicio", u"Sin infecciones polimicrobianas", None));
        ___qlistwidgetitem22 = self.listWidget_6.item(6)
        ___qlistwidgetitem22.setText(QCoreApplication.translate("ventana_inicio", u"Sin infecciones f\u00fangicas o por micobacterias", None));
        ___qlistwidgetitem23 = self.listWidget_6.item(7)
        ___qlistwidgetitem23.setText(QCoreApplication.translate("ventana_inicio", u"Pacientes sin tratamiento con inmunosupresores o corticoides > 5mg/d\u00eda en los \u00faltimos 3 meses", None));
        self.listWidget_6.setSortingEnabled(__sortingEnabled4)

        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_criterios_inclusion_exclusion_3), QCoreApplication.translate("ventana_inicio", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_farmaco_experimental), QCoreApplication.translate("ventana_inicio", u"F\u00e1rmaco experimental", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_farmaco_control), QCoreApplication.translate("ventana_inicio", u"F\u00e1rmaco de control", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_enfermedad_trastorno), QCoreApplication.translate("ventana_inicio", u"Enfermedad/Trastorno", None))
        self.textEdit_14.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal.</span></p></body></html>", None))

        __sortingEnabled5 = self.listWidget_7.isSortingEnabled()
        self.listWidget_7.setSortingEnabled(False)
        ___qlistwidgetitem24 = self.listWidget_7.item(0)
        ___qlistwidgetitem24.setText(QCoreApplication.translate("ventana_inicio", u"Aparici\u00f3n de LPP en pacientes neuroquir\u00farjicos en un periodo >3 horas de intervenci\u00f3n", None));
        self.listWidget_7.setSortingEnabled(__sortingEnabled5)

        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_variable_principal_3), QCoreApplication.translate("ventana_inicio", u"Variable principal", None))
        self.textEdit_15.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset.</span></p></body></html>", None))
        self.pushButton_6.setText(QCoreApplication.translate("ventana_inicio", u"Procesar", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_procesar_3), QCoreApplication.translate("ventana_inicio", u"Procesar", None))
        self.textEdit_16.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset.</span></p></body></html>", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_resultados_3), QCoreApplication.translate("ventana_inicio", u"Resultados", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("ventana_inicio", u"Archivo", None))
        self.menuEdici_n.setTitle(QCoreApplication.translate("ventana_inicio", u"Edici\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("ventana_inicio", u"Ayuda", None))
    # retranslateUi


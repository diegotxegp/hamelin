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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStackedWidget, QStatusBar, QTabWidget, QTextEdit,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(815, 630)
        self.actionAcerca_de = QAction(MainWindow)
        self.actionAcerca_de.setObjectName(u"actionAcerca_de")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_inicio = QWidget()
        self.page_inicio.setObjectName(u"page_inicio")
        self.gridLayout_2 = QGridLayout(self.page_inicio)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget_inicio = QTabWidget(self.page_inicio)
        self.tabWidget_inicio.setObjectName(u"tabWidget_inicio")
        self.tabWidget_inicio.setEnabled(True)
        self.tab_bienvenida = QWidget()
        self.tab_bienvenida.setObjectName(u"tab_bienvenida")
        self.gridLayout_3 = QGridLayout(self.tab_bienvenida)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.textEdit_bienvenida = QTextEdit(self.tab_bienvenida)
        self.textEdit_bienvenida.setObjectName(u"textEdit_bienvenida")

        self.gridLayout_3.addWidget(self.textEdit_bienvenida, 0, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_bienvenida, "")
        self.tab_datos = QWidget()
        self.tab_datos.setObjectName(u"tab_datos")
        self.tab_datos.setEnabled(True)
        self.gridLayout_4 = QGridLayout(self.tab_datos)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.textEdit_datos = QTextEdit(self.tab_datos)
        self.textEdit_datos.setObjectName(u"textEdit_datos")
        self.textEdit_datos.setEnabled(True)

        self.gridLayout_4.addWidget(self.textEdit_datos, 0, 0, 1, 1)

        self.pushButton_adjuntar = QPushButton(self.tab_datos)
        self.pushButton_adjuntar.setObjectName(u"pushButton_adjuntar")

        self.gridLayout_4.addWidget(self.pushButton_adjuntar, 1, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_datos, "")
        self.tab_estado = QWidget()
        self.tab_estado.setObjectName(u"tab_estado")
        self.gridLayout_5 = QGridLayout(self.tab_estado)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.textEdit_2 = QTextEdit(self.tab_estado)
        self.textEdit_2.setObjectName(u"textEdit_2")

        self.gridLayout_5.addWidget(self.textEdit_2, 0, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_estado, "")
        self.tab_opciones = QWidget()
        self.tab_opciones.setObjectName(u"tab_opciones")
        self.gridLayout_6 = QGridLayout(self.tab_opciones)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.textEdit_3 = QTextEdit(self.tab_opciones)
        self.textEdit_3.setObjectName(u"textEdit_3")

        self.gridLayout_6.addWidget(self.textEdit_3, 0, 0, 1, 1)

        self.comboBox_opciones = QComboBox(self.tab_opciones)
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.setObjectName(u"comboBox_opciones")

        self.gridLayout_6.addWidget(self.comboBox_opciones, 1, 0, 1, 1)

        self.pushButton_opciones = QPushButton(self.tab_opciones)
        self.pushButton_opciones.setObjectName(u"pushButton_opciones")

        self.gridLayout_6.addWidget(self.pushButton_opciones, 2, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_opciones, "")

        self.gridLayout_2.addWidget(self.tabWidget_inicio, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_inicio)
        self.page_registro = QWidget()
        self.page_registro.setObjectName(u"page_registro")
        self.gridLayout_7 = QGridLayout(self.page_registro)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.tabWidget_registro = QTabWidget(self.page_registro)
        self.tabWidget_registro.setObjectName(u"tabWidget_registro")
        self.tab_inicio = QWidget()
        self.tab_inicio.setObjectName(u"tab_inicio")
        self.gridLayout_8 = QGridLayout(self.tab_inicio)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.textEdit_volver_inicio = QTextEdit(self.tab_inicio)
        self.textEdit_volver_inicio.setObjectName(u"textEdit_volver_inicio")

        self.gridLayout_8.addWidget(self.textEdit_volver_inicio, 0, 0, 1, 1)

        self.pushButton_registro_volver_inicio = QPushButton(self.tab_inicio)
        self.pushButton_registro_volver_inicio.setObjectName(u"pushButton_registro_volver_inicio")

        self.gridLayout_8.addWidget(self.pushButton_registro_volver_inicio, 1, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_inicio, "")
        self.tab_dataset = QWidget()
        self.tab_dataset.setObjectName(u"tab_dataset")
        self.gridLayout_9 = QGridLayout(self.tab_dataset)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.textEdit_dataset = QTextEdit(self.tab_dataset)
        self.textEdit_dataset.setObjectName(u"textEdit_dataset")

        self.gridLayout_9.addWidget(self.textEdit_dataset, 0, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_dataset, "")
        self.tab_criterios = QWidget()
        self.tab_criterios.setObjectName(u"tab_criterios")
        self.gridLayout_10 = QGridLayout(self.tab_criterios)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.textEdit_criterios = QTextEdit(self.tab_criterios)
        self.textEdit_criterios.setObjectName(u"textEdit_criterios")

        self.gridLayout_10.addWidget(self.textEdit_criterios, 0, 0, 1, 1)

        self.textEdit_6 = QTextEdit(self.tab_criterios)
        self.textEdit_6.setObjectName(u"textEdit_6")

        self.gridLayout_10.addWidget(self.textEdit_6, 1, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_criterios, "")
        self.tab_variable = QWidget()
        self.tab_variable.setObjectName(u"tab_variable")
        self.gridLayout_11 = QGridLayout(self.tab_variable)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.textEdit_variable = QTextEdit(self.tab_variable)
        self.textEdit_variable.setObjectName(u"textEdit_variable")

        self.gridLayout_11.addWidget(self.textEdit_variable, 0, 0, 1, 1)

        self.textEdit_8 = QTextEdit(self.tab_variable)
        self.textEdit_8.setObjectName(u"textEdit_8")

        self.gridLayout_11.addWidget(self.textEdit_8, 1, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_variable, "")
        self.tab_procesar = QWidget()
        self.tab_procesar.setObjectName(u"tab_procesar")
        self.gridLayout_12 = QGridLayout(self.tab_procesar)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.textEdit_procesar = QTextEdit(self.tab_procesar)
        self.textEdit_procesar.setObjectName(u"textEdit_procesar")

        self.gridLayout_12.addWidget(self.textEdit_procesar, 0, 0, 1, 1)

        self.pushButton_3 = QPushButton(self.tab_procesar)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.gridLayout_12.addWidget(self.pushButton_3, 1, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_procesar, "")
        self.tab_resultados = QWidget()
        self.tab_resultados.setObjectName(u"tab_resultados")
        self.gridLayout_14 = QGridLayout(self.tab_resultados)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.textEdit = QTextEdit(self.tab_resultados)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout_14.addWidget(self.textEdit, 0, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_resultados, "")

        self.gridLayout_7.addWidget(self.tabWidget_registro, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_registro)
        self.page_observacional = QWidget()
        self.page_observacional.setObjectName(u"page_observacional")
        self.gridLayout_13 = QGridLayout(self.page_observacional)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.tabWidget_observacional = QTabWidget(self.page_observacional)
        self.tabWidget_observacional.setObjectName(u"tabWidget_observacional")
        self.tab_inicio1 = QWidget()
        self.tab_inicio1.setObjectName(u"tab_inicio1")
        self.gridLayout_15 = QGridLayout(self.tab_inicio1)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.textEdit_inicio = QTextEdit(self.tab_inicio1)
        self.textEdit_inicio.setObjectName(u"textEdit_inicio")

        self.gridLayout_15.addWidget(self.textEdit_inicio, 0, 0, 1, 1)

        self.pushButton_inicio = QPushButton(self.tab_inicio1)
        self.pushButton_inicio.setObjectName(u"pushButton_inicio")

        self.gridLayout_15.addWidget(self.pushButton_inicio, 1, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_inicio1, "")
        self.tab_criterios1 = QWidget()
        self.tab_criterios1.setObjectName(u"tab_criterios1")
        self.gridLayout_16 = QGridLayout(self.tab_criterios1)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.textEdit_criterios_2 = QTextEdit(self.tab_criterios1)
        self.textEdit_criterios_2.setObjectName(u"textEdit_criterios_2")

        self.gridLayout_16.addWidget(self.textEdit_criterios_2, 0, 0, 1, 1)

        self.textEdit_7 = QTextEdit(self.tab_criterios1)
        self.textEdit_7.setObjectName(u"textEdit_7")

        self.gridLayout_16.addWidget(self.textEdit_7, 1, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_criterios1, "")
        self.tab_variable1 = QWidget()
        self.tab_variable1.setObjectName(u"tab_variable1")
        self.gridLayout_17 = QGridLayout(self.tab_variable1)
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.textEdit_variable_2 = QTextEdit(self.tab_variable1)
        self.textEdit_variable_2.setObjectName(u"textEdit_variable_2")

        self.gridLayout_17.addWidget(self.textEdit_variable_2, 0, 0, 1, 1)

        self.textEdit_10 = QTextEdit(self.tab_variable1)
        self.textEdit_10.setObjectName(u"textEdit_10")

        self.gridLayout_17.addWidget(self.textEdit_10, 1, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_variable1, "")
        self.tab_procesar1 = QWidget()
        self.tab_procesar1.setObjectName(u"tab_procesar1")
        self.gridLayout_18 = QGridLayout(self.tab_procesar1)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.textEdit_procesar_2 = QTextEdit(self.tab_procesar1)
        self.textEdit_procesar_2.setObjectName(u"textEdit_procesar_2")

        self.gridLayout_18.addWidget(self.textEdit_procesar_2, 0, 0, 1, 1)

        self.pushButton_4 = QPushButton(self.tab_procesar1)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.gridLayout_18.addWidget(self.pushButton_4, 1, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_procesar1, "")
        self.tab_resultados1 = QWidget()
        self.tab_resultados1.setObjectName(u"tab_resultados1")
        self.gridLayout_19 = QGridLayout(self.tab_resultados1)
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.textEdit_12 = QTextEdit(self.tab_resultados1)
        self.textEdit_12.setObjectName(u"textEdit_12")

        self.gridLayout_19.addWidget(self.textEdit_12, 0, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_resultados1, "")

        self.gridLayout_13.addWidget(self.tabWidget_observacional, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_observacional)
        self.page_clinico = QWidget()
        self.page_clinico.setObjectName(u"page_clinico")
        self.gridLayout_20 = QGridLayout(self.page_clinico)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.tabWidget_clinico = QTabWidget(self.page_clinico)
        self.tabWidget_clinico.setObjectName(u"tabWidget_clinico")
        self.tab_inicio2 = QWidget()
        self.tab_inicio2.setObjectName(u"tab_inicio2")
        self.gridLayout_21 = QGridLayout(self.tab_inicio2)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.textEdit_4 = QTextEdit(self.tab_inicio2)
        self.textEdit_4.setObjectName(u"textEdit_4")

        self.gridLayout_21.addWidget(self.textEdit_4, 0, 0, 1, 1)

        self.pushButton_2 = QPushButton(self.tab_inicio2)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout_21.addWidget(self.pushButton_2, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_inicio2, "")
        self.tab_criterios2 = QWidget()
        self.tab_criterios2.setObjectName(u"tab_criterios2")
        self.gridLayout_22 = QGridLayout(self.tab_criterios2)
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.textEdit_5 = QTextEdit(self.tab_criterios2)
        self.textEdit_5.setObjectName(u"textEdit_5")

        self.gridLayout_22.addWidget(self.textEdit_5, 0, 0, 1, 1)

        self.textEdit_9 = QTextEdit(self.tab_criterios2)
        self.textEdit_9.setObjectName(u"textEdit_9")

        self.gridLayout_22.addWidget(self.textEdit_9, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_criterios2, "")
        self.tab_farmaco_experimental = QWidget()
        self.tab_farmaco_experimental.setObjectName(u"tab_farmaco_experimental")
        self.gridLayout_28 = QGridLayout(self.tab_farmaco_experimental)
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.textEdit_20 = QTextEdit(self.tab_farmaco_experimental)
        self.textEdit_20.setObjectName(u"textEdit_20")

        self.gridLayout_28.addWidget(self.textEdit_20, 0, 0, 1, 1)

        self.textEdit_21 = QTextEdit(self.tab_farmaco_experimental)
        self.textEdit_21.setObjectName(u"textEdit_21")

        self.gridLayout_28.addWidget(self.textEdit_21, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_farmaco_experimental, "")
        self.tab_farmaco_control = QWidget()
        self.tab_farmaco_control.setObjectName(u"tab_farmaco_control")
        self.gridLayout_26 = QGridLayout(self.tab_farmaco_control)
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.textEdit_16 = QTextEdit(self.tab_farmaco_control)
        self.textEdit_16.setObjectName(u"textEdit_16")

        self.gridLayout_26.addWidget(self.textEdit_16, 0, 0, 1, 1)

        self.textEdit_17 = QTextEdit(self.tab_farmaco_control)
        self.textEdit_17.setObjectName(u"textEdit_17")

        self.gridLayout_26.addWidget(self.textEdit_17, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_farmaco_control, "")
        self.tab_enfermedad = QWidget()
        self.tab_enfermedad.setObjectName(u"tab_enfermedad")
        self.gridLayout_27 = QGridLayout(self.tab_enfermedad)
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.textEdit_18 = QTextEdit(self.tab_enfermedad)
        self.textEdit_18.setObjectName(u"textEdit_18")

        self.gridLayout_27.addWidget(self.textEdit_18, 0, 0, 1, 1)

        self.textEdit_19 = QTextEdit(self.tab_enfermedad)
        self.textEdit_19.setObjectName(u"textEdit_19")

        self.gridLayout_27.addWidget(self.textEdit_19, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_enfermedad, "")
        self.tab_variable2 = QWidget()
        self.tab_variable2.setObjectName(u"tab_variable2")
        self.gridLayout_23 = QGridLayout(self.tab_variable2)
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.textEdit_11 = QTextEdit(self.tab_variable2)
        self.textEdit_11.setObjectName(u"textEdit_11")

        self.gridLayout_23.addWidget(self.textEdit_11, 0, 0, 1, 1)

        self.textEdit_13 = QTextEdit(self.tab_variable2)
        self.textEdit_13.setObjectName(u"textEdit_13")

        self.gridLayout_23.addWidget(self.textEdit_13, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_variable2, "")
        self.tab_procesar2 = QWidget()
        self.tab_procesar2.setObjectName(u"tab_procesar2")
        self.gridLayout_24 = QGridLayout(self.tab_procesar2)
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.textEdit_14 = QTextEdit(self.tab_procesar2)
        self.textEdit_14.setObjectName(u"textEdit_14")

        self.gridLayout_24.addWidget(self.textEdit_14, 0, 0, 1, 1)

        self.pushButton_5 = QPushButton(self.tab_procesar2)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.gridLayout_24.addWidget(self.pushButton_5, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_procesar2, "")
        self.tab_resultados2 = QWidget()
        self.tab_resultados2.setObjectName(u"tab_resultados2")
        self.gridLayout_25 = QGridLayout(self.tab_resultados2)
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.textEdit_15 = QTextEdit(self.tab_resultados2)
        self.textEdit_15.setObjectName(u"textEdit_15")

        self.gridLayout_25.addWidget(self.textEdit_15, 0, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_resultados2, "")

        self.gridLayout_20.addWidget(self.tabWidget_clinico, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_clinico)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 815, 19))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuOpciones = QMenu(self.menubar)
        self.menuOpciones.setObjectName(u"menuOpciones")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuOpciones.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuAyuda.addAction(self.actionAcerca_de)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)
        self.tabWidget_inicio.setCurrentIndex(3)
        self.tabWidget_registro.setCurrentIndex(0)
        self.tabWidget_observacional.setCurrentIndex(2)
        self.tabWidget_clinico.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Hamelin", None))
        self.actionAcerca_de.setText(QCoreApplication.translate("MainWindow", u"Acerca de...", None))
        self.textEdit_bienvenida.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Hamelin es una aplicaci\u00f3n que capacita a los Profesionales de Investigaci\u00f3n Cl\u00ednica (CRPs) para crear sus propios modelos predictivos de Aprendizaje Autom\u00e1tico (ML)</span></p></body></html>", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_bienvenida), QCoreApplication.translate("MainWindow", u"Bienvenida", None))
        self.textEdit_datos.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Adjunta un fichero CSV para analizar los datos</span></p></body></html>", None))
        self.pushButton_adjuntar.setText(QCoreApplication.translate("MainWindow", u"Adjuntar", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_datos), QCoreApplication.translate("MainWindow", u"Datos", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Estado</span></p></body></html>", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_estado), QCoreApplication.translate("MainWindow", u"Estado", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona un procedimiento a seguir</span></p></body></html>", None))
        self.comboBox_opciones.setItemText(0, QCoreApplication.translate("MainWindow", u"Registro de pacientes", None))
        self.comboBox_opciones.setItemText(1, QCoreApplication.translate("MainWindow", u"Estudio observacional", None))
        self.comboBox_opciones.setItemText(2, QCoreApplication.translate("MainWindow", u"Estudio cl\u00ednico", None))

        self.pushButton_opciones.setText(QCoreApplication.translate("MainWindow", u"Aceptar", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_opciones), QCoreApplication.translate("MainWindow", u"Opciones", None))
        self.textEdit_volver_inicio.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio</span></p></body></html>", None))
        self.pushButton_registro_volver_inicio.setText(QCoreApplication.translate("MainWindow", u"Volver a inicio", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_inicio), QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.textEdit_dataset.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Modificar dataset</span></p></body></html>", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_dataset), QCoreApplication.translate("MainWindow", u"Dataset", None))
        self.textEdit_criterios.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n</span></p></body></html>", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_criterios), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal</span></p></body></html>", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_variable), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.textEdit_procesar.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset</span></p></body></html>", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_procesar), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.textEdit.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesamiento del dataset</span></p></body></html>", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_resultados), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.textEdit_inicio.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio</span></p></body></html>", None))
        self.pushButton_inicio.setText(QCoreApplication.translate("MainWindow", u"Volver a inicio", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_inicio1), QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.textEdit_criterios_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n</span></p></body></html>", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_criterios1), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_variable_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal</span></p></body></html>", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_variable1), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.textEdit_procesar_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset</span></p></body></html>", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_procesar1), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.textEdit_12.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset</span></p></body></html>", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_resultados1), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_inicio2), QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_criterios2), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_farmaco_experimental), QCoreApplication.translate("MainWindow", u"F\u00e1rmaco experimental", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_farmaco_control), QCoreApplication.translate("MainWindow", u"F\u00e1rmaco de control", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_enfermedad), QCoreApplication.translate("MainWindow", u"Enfermedad/Trastorno", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_variable2), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_procesar2), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_resultados2), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("MainWindow", u"Archivo", None))
        self.menuOpciones.setTitle(QCoreApplication.translate("MainWindow", u"Opciones", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("MainWindow", u"Ayuda", None))
    # retranslateUi


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
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QStackedWidget, QStatusBar, QTabWidget,
    QTextEdit, QWidget)

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
        self.tab_inicio_bienvenida = QWidget()
        self.tab_inicio_bienvenida.setObjectName(u"tab_inicio_bienvenida")
        self.gridLayout_3 = QGridLayout(self.tab_inicio_bienvenida)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.textEdit_inicio_bienvenida = QTextEdit(self.tab_inicio_bienvenida)
        self.textEdit_inicio_bienvenida.setObjectName(u"textEdit_inicio_bienvenida")
        self.textEdit_inicio_bienvenida.setReadOnly(True)

        self.gridLayout_3.addWidget(self.textEdit_inicio_bienvenida, 0, 0, 1, 1)

        self.pushButton_inicio_bienvenida_aceptar = QPushButton(self.tab_inicio_bienvenida)
        self.pushButton_inicio_bienvenida_aceptar.setObjectName(u"pushButton_inicio_bienvenida_aceptar")

        self.gridLayout_3.addWidget(self.pushButton_inicio_bienvenida_aceptar, 1, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_inicio_bienvenida, "")
        self.tab_inicio_datos = QWidget()
        self.tab_inicio_datos.setObjectName(u"tab_inicio_datos")
        self.tab_inicio_datos.setEnabled(True)
        self.gridLayout_4 = QGridLayout(self.tab_inicio_datos)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.textEdit_datos = QTextEdit(self.tab_inicio_datos)
        self.textEdit_datos.setObjectName(u"textEdit_datos")
        self.textEdit_datos.setEnabled(True)
        self.textEdit_datos.setReadOnly(True)

        self.gridLayout_4.addWidget(self.textEdit_datos, 0, 0, 1, 1)

        self.pushButton_inicio_datos_adjuntar = QPushButton(self.tab_inicio_datos)
        self.pushButton_inicio_datos_adjuntar.setObjectName(u"pushButton_inicio_datos_adjuntar")

        self.gridLayout_4.addWidget(self.pushButton_inicio_datos_adjuntar, 1, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_inicio_datos, "")
        self.tab_inicio_estado = QWidget()
        self.tab_inicio_estado.setObjectName(u"tab_inicio_estado")
        self.gridLayout_5 = QGridLayout(self.tab_inicio_estado)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.textEdit_2 = QTextEdit(self.tab_inicio_estado)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setReadOnly(True)

        self.gridLayout_5.addWidget(self.textEdit_2, 0, 0, 1, 1)

        self.pushButton_inicio_estado_aceptar = QPushButton(self.tab_inicio_estado)
        self.pushButton_inicio_estado_aceptar.setObjectName(u"pushButton_inicio_estado_aceptar")

        self.gridLayout_5.addWidget(self.pushButton_inicio_estado_aceptar, 1, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_inicio_estado, "")
        self.tab_inicio_opciones = QWidget()
        self.tab_inicio_opciones.setObjectName(u"tab_inicio_opciones")
        self.gridLayout_6 = QGridLayout(self.tab_inicio_opciones)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.textEdit_3 = QTextEdit(self.tab_inicio_opciones)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textEdit_3, 0, 0, 1, 1)

        self.comboBox_inicio_opciones = QComboBox(self.tab_inicio_opciones)
        self.comboBox_inicio_opciones.addItem("")
        self.comboBox_inicio_opciones.addItem("")
        self.comboBox_inicio_opciones.addItem("")
        self.comboBox_inicio_opciones.setObjectName(u"comboBox_inicio_opciones")

        self.gridLayout_6.addWidget(self.comboBox_inicio_opciones, 1, 0, 1, 1)

        self.pushButton_inicio_opciones_aceptar = QPushButton(self.tab_inicio_opciones)
        self.pushButton_inicio_opciones_aceptar.setObjectName(u"pushButton_inicio_opciones_aceptar")

        self.gridLayout_6.addWidget(self.pushButton_inicio_opciones_aceptar, 2, 0, 1, 1)

        self.tabWidget_inicio.addTab(self.tab_inicio_opciones, "")

        self.gridLayout_2.addWidget(self.tabWidget_inicio, 1, 0, 1, 1)

        self.lineEdit_inicio_titulo = QLineEdit(self.page_inicio)
        self.lineEdit_inicio_titulo.setObjectName(u"lineEdit_inicio_titulo")
        self.lineEdit_inicio_titulo.setReadOnly(True)

        self.gridLayout_2.addWidget(self.lineEdit_inicio_titulo, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_inicio)
        self.page_registro = QWidget()
        self.page_registro.setObjectName(u"page_registro")
        self.gridLayout_7 = QGridLayout(self.page_registro)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.lineEdit_registro_titulo = QLineEdit(self.page_registro)
        self.lineEdit_registro_titulo.setObjectName(u"lineEdit_registro_titulo")
        self.lineEdit_registro_titulo.setReadOnly(True)

        self.gridLayout_7.addWidget(self.lineEdit_registro_titulo, 0, 0, 1, 1)

        self.tabWidget_registro = QTabWidget(self.page_registro)
        self.tabWidget_registro.setObjectName(u"tabWidget_registro")
        self.tab_registro_inicio = QWidget()
        self.tab_registro_inicio.setObjectName(u"tab_registro_inicio")
        self.gridLayout_8 = QGridLayout(self.tab_registro_inicio)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.textEdit_registro_inicio = QTextEdit(self.tab_registro_inicio)
        self.textEdit_registro_inicio.setObjectName(u"textEdit_registro_inicio")
        self.textEdit_registro_inicio.setReadOnly(True)

        self.gridLayout_8.addWidget(self.textEdit_registro_inicio, 0, 0, 1, 1)

        self.pushButton_registro_inicio = QPushButton(self.tab_registro_inicio)
        self.pushButton_registro_inicio.setObjectName(u"pushButton_registro_inicio")

        self.gridLayout_8.addWidget(self.pushButton_registro_inicio, 1, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_registro_inicio, "")
        self.tab_regisro_dataset = QWidget()
        self.tab_regisro_dataset.setObjectName(u"tab_regisro_dataset")
        self.gridLayout_9 = QGridLayout(self.tab_regisro_dataset)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.textEdit_registro_dataset = QTextEdit(self.tab_regisro_dataset)
        self.textEdit_registro_dataset.setObjectName(u"textEdit_registro_dataset")
        self.textEdit_registro_dataset.setReadOnly(True)

        self.gridLayout_9.addWidget(self.textEdit_registro_dataset, 0, 0, 1, 1)

        self.pushButton_registro_dataset_aceptar = QPushButton(self.tab_regisro_dataset)
        self.pushButton_registro_dataset_aceptar.setObjectName(u"pushButton_registro_dataset_aceptar")

        self.gridLayout_9.addWidget(self.pushButton_registro_dataset_aceptar, 1, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_regisro_dataset, "")
        self.tab_registro_criterios = QWidget()
        self.tab_registro_criterios.setObjectName(u"tab_registro_criterios")
        self.gridLayout_10 = QGridLayout(self.tab_registro_criterios)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.textEdit_registro_criterios_nuevos = QTextEdit(self.tab_registro_criterios)
        self.textEdit_registro_criterios_nuevos.setObjectName(u"textEdit_registro_criterios_nuevos")

        self.gridLayout_10.addWidget(self.textEdit_registro_criterios_nuevos, 1, 0, 1, 1)

        self.textEdit_registro_criterios = QTextEdit(self.tab_registro_criterios)
        self.textEdit_registro_criterios.setObjectName(u"textEdit_registro_criterios")
        self.textEdit_registro_criterios.setReadOnly(True)

        self.gridLayout_10.addWidget(self.textEdit_registro_criterios, 0, 0, 1, 1)

        self.pushButton_registro_criterios_annadir = QPushButton(self.tab_registro_criterios)
        self.pushButton_registro_criterios_annadir.setObjectName(u"pushButton_registro_criterios_annadir")

        self.gridLayout_10.addWidget(self.pushButton_registro_criterios_annadir, 2, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_registro_criterios, "")
        self.tab_registro_variable = QWidget()
        self.tab_registro_variable.setObjectName(u"tab_registro_variable")
        self.gridLayout_11 = QGridLayout(self.tab_registro_variable)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.textEdit_registro_variable = QTextEdit(self.tab_registro_variable)
        self.textEdit_registro_variable.setObjectName(u"textEdit_registro_variable")
        self.textEdit_registro_variable.setReadOnly(True)

        self.gridLayout_11.addWidget(self.textEdit_registro_variable, 0, 0, 1, 1)

        self.textEdit_registro_variable_nuevo = QTextEdit(self.tab_registro_variable)
        self.textEdit_registro_variable_nuevo.setObjectName(u"textEdit_registro_variable_nuevo")

        self.gridLayout_11.addWidget(self.textEdit_registro_variable_nuevo, 1, 0, 1, 1)

        self.pushButton_registro_variable_annadir = QPushButton(self.tab_registro_variable)
        self.pushButton_registro_variable_annadir.setObjectName(u"pushButton_registro_variable_annadir")

        self.gridLayout_11.addWidget(self.pushButton_registro_variable_annadir, 2, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_registro_variable, "")
        self.tab_registro_procesar = QWidget()
        self.tab_registro_procesar.setObjectName(u"tab_registro_procesar")
        self.gridLayout_12 = QGridLayout(self.tab_registro_procesar)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.textEdit_registro_procesar = QTextEdit(self.tab_registro_procesar)
        self.textEdit_registro_procesar.setObjectName(u"textEdit_registro_procesar")
        self.textEdit_registro_procesar.setReadOnly(True)

        self.gridLayout_12.addWidget(self.textEdit_registro_procesar, 0, 0, 1, 1)

        self.pushButton_registro_procesar = QPushButton(self.tab_registro_procesar)
        self.pushButton_registro_procesar.setObjectName(u"pushButton_registro_procesar")

        self.gridLayout_12.addWidget(self.pushButton_registro_procesar, 1, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_registro_procesar, "")
        self.tab_registro_resultados = QWidget()
        self.tab_registro_resultados.setObjectName(u"tab_registro_resultados")
        self.gridLayout_14 = QGridLayout(self.tab_registro_resultados)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.textEdit_registro_resultados = QTextEdit(self.tab_registro_resultados)
        self.textEdit_registro_resultados.setObjectName(u"textEdit_registro_resultados")
        self.textEdit_registro_resultados.setReadOnly(True)

        self.gridLayout_14.addWidget(self.textEdit_registro_resultados, 0, 0, 1, 1)

        self.tabWidget_registro.addTab(self.tab_registro_resultados, "")

        self.gridLayout_7.addWidget(self.tabWidget_registro, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_registro)
        self.page_observacional = QWidget()
        self.page_observacional.setObjectName(u"page_observacional")
        self.gridLayout_13 = QGridLayout(self.page_observacional)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.tabWidget_observacional = QTabWidget(self.page_observacional)
        self.tabWidget_observacional.setObjectName(u"tabWidget_observacional")
        self.tab_observacional_inicio = QWidget()
        self.tab_observacional_inicio.setObjectName(u"tab_observacional_inicio")
        self.gridLayout_15 = QGridLayout(self.tab_observacional_inicio)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.textEdit_observacional_inicio = QTextEdit(self.tab_observacional_inicio)
        self.textEdit_observacional_inicio.setObjectName(u"textEdit_observacional_inicio")
        self.textEdit_observacional_inicio.setReadOnly(True)

        self.gridLayout_15.addWidget(self.textEdit_observacional_inicio, 0, 0, 1, 1)

        self.pushButton_observacional_inicio = QPushButton(self.tab_observacional_inicio)
        self.pushButton_observacional_inicio.setObjectName(u"pushButton_observacional_inicio")

        self.gridLayout_15.addWidget(self.pushButton_observacional_inicio, 1, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_observacional_inicio, "")
        self.tab_observacional_criterios = QWidget()
        self.tab_observacional_criterios.setObjectName(u"tab_observacional_criterios")
        self.gridLayout_16 = QGridLayout(self.tab_observacional_criterios)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.textEdit_observacional_criterios_nuevos = QTextEdit(self.tab_observacional_criterios)
        self.textEdit_observacional_criterios_nuevos.setObjectName(u"textEdit_observacional_criterios_nuevos")

        self.gridLayout_16.addWidget(self.textEdit_observacional_criterios_nuevos, 1, 0, 1, 1)

        self.textEdit_observacional_criterios = QTextEdit(self.tab_observacional_criterios)
        self.textEdit_observacional_criterios.setObjectName(u"textEdit_observacional_criterios")
        self.textEdit_observacional_criterios.setReadOnly(True)

        self.gridLayout_16.addWidget(self.textEdit_observacional_criterios, 0, 0, 1, 1)

        self.pushButton_observacional_criterios_annadir = QPushButton(self.tab_observacional_criterios)
        self.pushButton_observacional_criterios_annadir.setObjectName(u"pushButton_observacional_criterios_annadir")

        self.gridLayout_16.addWidget(self.pushButton_observacional_criterios_annadir, 2, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_observacional_criterios, "")
        self.tab_observacional_variable = QWidget()
        self.tab_observacional_variable.setObjectName(u"tab_observacional_variable")
        self.gridLayout_17 = QGridLayout(self.tab_observacional_variable)
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.textEdit_observacional_variable_nuevo = QTextEdit(self.tab_observacional_variable)
        self.textEdit_observacional_variable_nuevo.setObjectName(u"textEdit_observacional_variable_nuevo")

        self.gridLayout_17.addWidget(self.textEdit_observacional_variable_nuevo, 1, 0, 1, 1)

        self.textEdit_observacional_variable = QTextEdit(self.tab_observacional_variable)
        self.textEdit_observacional_variable.setObjectName(u"textEdit_observacional_variable")
        self.textEdit_observacional_variable.setReadOnly(True)

        self.gridLayout_17.addWidget(self.textEdit_observacional_variable, 0, 0, 1, 1)

        self.pushButton_observacional_variable_annadir = QPushButton(self.tab_observacional_variable)
        self.pushButton_observacional_variable_annadir.setObjectName(u"pushButton_observacional_variable_annadir")

        self.gridLayout_17.addWidget(self.pushButton_observacional_variable_annadir, 2, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_observacional_variable, "")
        self.tab_observacional_procesar = QWidget()
        self.tab_observacional_procesar.setObjectName(u"tab_observacional_procesar")
        self.gridLayout_18 = QGridLayout(self.tab_observacional_procesar)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.textEdit_observacional_procesar = QTextEdit(self.tab_observacional_procesar)
        self.textEdit_observacional_procesar.setObjectName(u"textEdit_observacional_procesar")
        self.textEdit_observacional_procesar.setReadOnly(True)

        self.gridLayout_18.addWidget(self.textEdit_observacional_procesar, 0, 0, 1, 1)

        self.pushButton_observacional_procesar = QPushButton(self.tab_observacional_procesar)
        self.pushButton_observacional_procesar.setObjectName(u"pushButton_observacional_procesar")

        self.gridLayout_18.addWidget(self.pushButton_observacional_procesar, 1, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_observacional_procesar, "")
        self.tab_observacional_resultados = QWidget()
        self.tab_observacional_resultados.setObjectName(u"tab_observacional_resultados")
        self.gridLayout_19 = QGridLayout(self.tab_observacional_resultados)
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.textEdit_observacional_resultados = QTextEdit(self.tab_observacional_resultados)
        self.textEdit_observacional_resultados.setObjectName(u"textEdit_observacional_resultados")
        self.textEdit_observacional_resultados.setReadOnly(True)

        self.gridLayout_19.addWidget(self.textEdit_observacional_resultados, 0, 0, 1, 1)

        self.tabWidget_observacional.addTab(self.tab_observacional_resultados, "")

        self.gridLayout_13.addWidget(self.tabWidget_observacional, 1, 0, 1, 1)

        self.lineEdit_observacional_titulo = QLineEdit(self.page_observacional)
        self.lineEdit_observacional_titulo.setObjectName(u"lineEdit_observacional_titulo")
        self.lineEdit_observacional_titulo.setReadOnly(True)

        self.gridLayout_13.addWidget(self.lineEdit_observacional_titulo, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_observacional)
        self.page_clinico = QWidget()
        self.page_clinico.setObjectName(u"page_clinico")
        self.gridLayout_20 = QGridLayout(self.page_clinico)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.tabWidget_clinico = QTabWidget(self.page_clinico)
        self.tabWidget_clinico.setObjectName(u"tabWidget_clinico")
        self.tab_clinico_inicio = QWidget()
        self.tab_clinico_inicio.setObjectName(u"tab_clinico_inicio")
        self.gridLayout_21 = QGridLayout(self.tab_clinico_inicio)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.textEdit_clinico_inicio = QTextEdit(self.tab_clinico_inicio)
        self.textEdit_clinico_inicio.setObjectName(u"textEdit_clinico_inicio")
        self.textEdit_clinico_inicio.setReadOnly(True)

        self.gridLayout_21.addWidget(self.textEdit_clinico_inicio, 0, 0, 1, 1)

        self.pushButton_clinico_inicio = QPushButton(self.tab_clinico_inicio)
        self.pushButton_clinico_inicio.setObjectName(u"pushButton_clinico_inicio")

        self.gridLayout_21.addWidget(self.pushButton_clinico_inicio, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_inicio, "")
        self.tab_clinico_criterios = QWidget()
        self.tab_clinico_criterios.setObjectName(u"tab_clinico_criterios")
        self.gridLayout_22 = QGridLayout(self.tab_clinico_criterios)
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.textEdit_clinico_criterios_nuevos = QTextEdit(self.tab_clinico_criterios)
        self.textEdit_clinico_criterios_nuevos.setObjectName(u"textEdit_clinico_criterios_nuevos")

        self.gridLayout_22.addWidget(self.textEdit_clinico_criterios_nuevos, 1, 0, 1, 1)

        self.textEdit_clinico_criterios = QTextEdit(self.tab_clinico_criterios)
        self.textEdit_clinico_criterios.setObjectName(u"textEdit_clinico_criterios")
        self.textEdit_clinico_criterios.setReadOnly(True)

        self.gridLayout_22.addWidget(self.textEdit_clinico_criterios, 0, 0, 1, 1)

        self.pushButton_clinico_criterios_annadir = QPushButton(self.tab_clinico_criterios)
        self.pushButton_clinico_criterios_annadir.setObjectName(u"pushButton_clinico_criterios_annadir")

        self.gridLayout_22.addWidget(self.pushButton_clinico_criterios_annadir, 2, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_criterios, "")
        self.tab_clinico_farmaco_experimental = QWidget()
        self.tab_clinico_farmaco_experimental.setObjectName(u"tab_clinico_farmaco_experimental")
        self.gridLayout_28 = QGridLayout(self.tab_clinico_farmaco_experimental)
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.textEdit_clinico_experimental = QTextEdit(self.tab_clinico_farmaco_experimental)
        self.textEdit_clinico_experimental.setObjectName(u"textEdit_clinico_experimental")
        self.textEdit_clinico_experimental.setReadOnly(True)

        self.gridLayout_28.addWidget(self.textEdit_clinico_experimental, 0, 0, 1, 1)

        self.textEdit_clinico_experimental_nuevo = QTextEdit(self.tab_clinico_farmaco_experimental)
        self.textEdit_clinico_experimental_nuevo.setObjectName(u"textEdit_clinico_experimental_nuevo")

        self.gridLayout_28.addWidget(self.textEdit_clinico_experimental_nuevo, 1, 0, 1, 1)

        self.pushButton_clinico_experimental_annadir = QPushButton(self.tab_clinico_farmaco_experimental)
        self.pushButton_clinico_experimental_annadir.setObjectName(u"pushButton_clinico_experimental_annadir")

        self.gridLayout_28.addWidget(self.pushButton_clinico_experimental_annadir, 2, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_farmaco_experimental, "")
        self.tab_clinico_farmaco_control = QWidget()
        self.tab_clinico_farmaco_control.setObjectName(u"tab_clinico_farmaco_control")
        self.gridLayout_26 = QGridLayout(self.tab_clinico_farmaco_control)
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.textEdit_clinico_control = QTextEdit(self.tab_clinico_farmaco_control)
        self.textEdit_clinico_control.setObjectName(u"textEdit_clinico_control")
        self.textEdit_clinico_control.setReadOnly(True)

        self.gridLayout_26.addWidget(self.textEdit_clinico_control, 0, 0, 1, 1)

        self.textEdit_clinico_control_nuevo = QTextEdit(self.tab_clinico_farmaco_control)
        self.textEdit_clinico_control_nuevo.setObjectName(u"textEdit_clinico_control_nuevo")

        self.gridLayout_26.addWidget(self.textEdit_clinico_control_nuevo, 1, 0, 1, 1)

        self.pushButton_clinico_control_annadir = QPushButton(self.tab_clinico_farmaco_control)
        self.pushButton_clinico_control_annadir.setObjectName(u"pushButton_clinico_control_annadir")

        self.gridLayout_26.addWidget(self.pushButton_clinico_control_annadir, 2, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_farmaco_control, "")
        self.tab_clinico_enfermedad = QWidget()
        self.tab_clinico_enfermedad.setObjectName(u"tab_clinico_enfermedad")
        self.gridLayout_27 = QGridLayout(self.tab_clinico_enfermedad)
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.textEdit_clinico_enfermedad = QTextEdit(self.tab_clinico_enfermedad)
        self.textEdit_clinico_enfermedad.setObjectName(u"textEdit_clinico_enfermedad")
        self.textEdit_clinico_enfermedad.setReadOnly(True)

        self.gridLayout_27.addWidget(self.textEdit_clinico_enfermedad, 0, 0, 1, 1)

        self.textEdit_clinico_enfermedad_nuevo = QTextEdit(self.tab_clinico_enfermedad)
        self.textEdit_clinico_enfermedad_nuevo.setObjectName(u"textEdit_clinico_enfermedad_nuevo")

        self.gridLayout_27.addWidget(self.textEdit_clinico_enfermedad_nuevo, 1, 0, 1, 1)

        self.pushButton_clinico_enfermedad_annadir = QPushButton(self.tab_clinico_enfermedad)
        self.pushButton_clinico_enfermedad_annadir.setObjectName(u"pushButton_clinico_enfermedad_annadir")

        self.gridLayout_27.addWidget(self.pushButton_clinico_enfermedad_annadir, 2, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_enfermedad, "")
        self.tab_clinico_variable = QWidget()
        self.tab_clinico_variable.setObjectName(u"tab_clinico_variable")
        self.gridLayout_23 = QGridLayout(self.tab_clinico_variable)
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.textEdit_clinico_variable = QTextEdit(self.tab_clinico_variable)
        self.textEdit_clinico_variable.setObjectName(u"textEdit_clinico_variable")
        self.textEdit_clinico_variable.setReadOnly(True)

        self.gridLayout_23.addWidget(self.textEdit_clinico_variable, 0, 0, 1, 1)

        self.textEdit_clinico_variable_nuevo = QTextEdit(self.tab_clinico_variable)
        self.textEdit_clinico_variable_nuevo.setObjectName(u"textEdit_clinico_variable_nuevo")

        self.gridLayout_23.addWidget(self.textEdit_clinico_variable_nuevo, 1, 0, 1, 1)

        self.pushButton_clinico_variable_annadir = QPushButton(self.tab_clinico_variable)
        self.pushButton_clinico_variable_annadir.setObjectName(u"pushButton_clinico_variable_annadir")

        self.gridLayout_23.addWidget(self.pushButton_clinico_variable_annadir, 2, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_variable, "")
        self.tab_clinico_procesar = QWidget()
        self.tab_clinico_procesar.setObjectName(u"tab_clinico_procesar")
        self.gridLayout_24 = QGridLayout(self.tab_clinico_procesar)
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.textEdit_clinico_procesar = QTextEdit(self.tab_clinico_procesar)
        self.textEdit_clinico_procesar.setObjectName(u"textEdit_clinico_procesar")
        self.textEdit_clinico_procesar.setReadOnly(True)

        self.gridLayout_24.addWidget(self.textEdit_clinico_procesar, 0, 0, 1, 1)

        self.pushButton_clinico_procesar = QPushButton(self.tab_clinico_procesar)
        self.pushButton_clinico_procesar.setObjectName(u"pushButton_clinico_procesar")

        self.gridLayout_24.addWidget(self.pushButton_clinico_procesar, 1, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_procesar, "")
        self.tab_clinico_resultados = QWidget()
        self.tab_clinico_resultados.setObjectName(u"tab_clinico_resultados")
        self.gridLayout_25 = QGridLayout(self.tab_clinico_resultados)
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.textEdit_clinico_resultados = QTextEdit(self.tab_clinico_resultados)
        self.textEdit_clinico_resultados.setObjectName(u"textEdit_clinico_resultados")
        self.textEdit_clinico_resultados.setReadOnly(True)

        self.gridLayout_25.addWidget(self.textEdit_clinico_resultados, 0, 0, 1, 1)

        self.tabWidget_clinico.addTab(self.tab_clinico_resultados, "")

        self.gridLayout_20.addWidget(self.tabWidget_clinico, 1, 0, 1, 1)

        self.lineEdit_clinico_titulo = QLineEdit(self.page_clinico)
        self.lineEdit_clinico_titulo.setObjectName(u"lineEdit_clinico_titulo")
        self.lineEdit_clinico_titulo.setReadOnly(True)

        self.gridLayout_20.addWidget(self.lineEdit_clinico_titulo, 0, 0, 1, 1)

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

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget_inicio.setCurrentIndex(3)
        self.tabWidget_registro.setCurrentIndex(0)
        self.tabWidget_observacional.setCurrentIndex(0)
        self.tabWidget_clinico.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Hamelin", None))
        self.actionAcerca_de.setText(QCoreApplication.translate("MainWindow", u"Acerca de...", None))
        self.textEdit_inicio_bienvenida.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Hamelin es una aplicaci\u00f3n que capacita a los Profesionales de Investigaci\u00f3n Cl\u00ednica (CRPs) para crear sus propios modelos predictivos de Aprendizaje Autom\u00e1tico (ML)</span></p></body></html>", None))
        self.pushButton_inicio_bienvenida_aceptar.setText(QCoreApplication.translate("MainWindow", u"Aceptar", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_inicio_bienvenida), QCoreApplication.translate("MainWindow", u"Bienvenida", None))
        self.textEdit_datos.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Adjunta un fichero CSV para analizar los datos</span></p></body></html>", None))
        self.pushButton_inicio_datos_adjuntar.setText(QCoreApplication.translate("MainWindow", u"Adjuntar", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_inicio_datos), QCoreApplication.translate("MainWindow", u"Datos", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Estado</span></p></body></html>", None))
        self.pushButton_inicio_estado_aceptar.setText(QCoreApplication.translate("MainWindow", u"Aceptar", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_inicio_estado), QCoreApplication.translate("MainWindow", u"Estado", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona un procedimiento a seguir</span></p></body></html>", None))
        self.comboBox_inicio_opciones.setItemText(0, QCoreApplication.translate("MainWindow", u"Registro de pacientes", None))
        self.comboBox_inicio_opciones.setItemText(1, QCoreApplication.translate("MainWindow", u"Estudio observacional", None))
        self.comboBox_inicio_opciones.setItemText(2, QCoreApplication.translate("MainWindow", u"Estudio cl\u00ednico", None))

        self.pushButton_inicio_opciones_aceptar.setText(QCoreApplication.translate("MainWindow", u"Aceptar", None))
        self.tabWidget_inicio.setTabText(self.tabWidget_inicio.indexOf(self.tab_inicio_opciones), QCoreApplication.translate("MainWindow", u"Opciones", None))
        self.lineEdit_inicio_titulo.setText(QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.lineEdit_registro_titulo.setText(QCoreApplication.translate("MainWindow", u"Registro de pacientes", None))
        self.textEdit_registro_inicio.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio</span></p></body></html>", None))
        self.pushButton_registro_inicio.setText(QCoreApplication.translate("MainWindow", u"Volver a inicio", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_registro_inicio), QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.textEdit_registro_dataset.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Modificar dataset</span></p></body></html>", None))
        self.pushButton_registro_dataset_aceptar.setText(QCoreApplication.translate("MainWindow", u"Aceptar", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_regisro_dataset), QCoreApplication.translate("MainWindow", u"Dataset", None))
        self.textEdit_registro_criterios.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n</span></p></body></html>", None))
        self.pushButton_registro_criterios_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_registro_criterios), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_registro_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal</span></p></body></html>", None))
        self.pushButton_registro_variable_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_registro_variable), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.textEdit_registro_procesar.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset</span></p></body></html>", None))
        self.pushButton_registro_procesar.setText(QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_registro_procesar), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.textEdit_registro_resultados.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesamiento del dataset</span></p></body></html>", None))
        self.tabWidget_registro.setTabText(self.tabWidget_registro.indexOf(self.tab_registro_resultados), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.textEdit_observacional_inicio.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio</span></p></body></html>", None))
        self.pushButton_observacional_inicio.setText(QCoreApplication.translate("MainWindow", u"Volver a inicio", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_observacional_inicio), QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.textEdit_observacional_criterios.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n</span></p></body></html>", None))
        self.pushButton_observacional_criterios_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_observacional_criterios), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_observacional_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal</span></p></body></html>", None))
        self.pushButton_observacional_variable_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_observacional_variable), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.textEdit_observacional_procesar.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset</span></p></body></html>", None))
        self.pushButton_observacional_procesar.setText(QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_observacional_procesar), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.textEdit_observacional_resultados.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset</span></p></body></html>", None))
        self.tabWidget_observacional.setTabText(self.tabWidget_observacional.indexOf(self.tab_observacional_resultados), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.lineEdit_observacional_titulo.setText(QCoreApplication.translate("MainWindow", u"Estudio observacional", None))
        self.textEdit_clinico_inicio.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio</span></p></body></html>", None))
        self.pushButton_clinico_inicio.setText(QCoreApplication.translate("MainWindow", u"Volver a inicio", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_inicio), QCoreApplication.translate("MainWindow", u"Inicio", None))
        self.textEdit_clinico_criterios.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica los criterios de inclusi\u00f3n y exclusi\u00f3n</span></p></body></html>", None))
        self.pushButton_clinico_criterios_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_criterios), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_clinico_experimental.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica el f\u00e1rmaco experimental</span></p></body></html>", None))
        self.pushButton_clinico_experimental_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_farmaco_experimental), QCoreApplication.translate("MainWindow", u"F\u00e1rmaco experimental", None))
        self.textEdit_clinico_control.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica el f\u00e1rmaco de control</span></p></body></html>", None))
        self.pushButton_clinico_control_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_farmaco_control), QCoreApplication.translate("MainWindow", u"F\u00e1rmaco de control", None))
        self.textEdit_clinico_enfermedad.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Indica la enfermedad o trastorno</span></p></body></html>", None))
        self.pushButton_clinico_enfermedad_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_enfermedad), QCoreApplication.translate("MainWindow", u"Enfermedad/Trastorno", None))
        self.textEdit_clinico_variable.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal</span></p></body></html>", None))
        self.pushButton_clinico_variable_annadir.setText(QCoreApplication.translate("MainWindow", u"A\u00f1adir", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_variable), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.textEdit_clinico_procesar.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar</span></p></body></html>", None))
        self.pushButton_clinico_procesar.setText(QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_procesar), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.textEdit_clinico_resultados.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset</span></p></body></html>", None))
        self.tabWidget_clinico.setTabText(self.tabWidget_clinico.indexOf(self.tab_clinico_resultados), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.lineEdit_clinico_titulo.setText(QCoreApplication.translate("MainWindow", u"Estudio cl\u00ednico", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("MainWindow", u"Archivo", None))
        self.menuOpciones.setTitle(QCoreApplication.translate("MainWindow", u"Opciones", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("MainWindow", u"Ayuda", None))
    # retranslateUi


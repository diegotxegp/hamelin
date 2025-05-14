# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'inicio.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_ventana_inicio(object):
    def setupUi(self, ventana_inicio):
        if not ventana_inicio.objectName():
            ventana_inicio.setObjectName(u"ventana_inicio")
        self.actionAcerca_de_Hamelin = QAction(ventana_inicio)
        self.actionAcerca_de_Hamelin.setObjectName(u"actionAcerca_de_Hamelin")
        self.centralwidget = QWidget(ventana_inicio)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_bienvenida = QWidget()
        self.tab_bienvenida.setObjectName(u"tab_bienvenida")
        self.layout_bienvenida = QVBoxLayout(self.tab_bienvenida)
        self.layout_bienvenida.setObjectName(u"layout_bienvenida")
        self.textEdit_bienvenida = QTextEdit(self.tab_bienvenida)
        self.textEdit_bienvenida.setObjectName(u"textEdit_bienvenida")
        self.textEdit_bienvenida.setHtml(u"<p align=\"center\"><span style=\"font-size:12pt;\">Hamelin es una aplicaci\u00f3n que capacita a los Profesionales de Investigaci\u00f3n Cl\u00ednica (CRPs) para crear sus propios modelos predictivos de Aprendizaje Autom\u00e1tico (ML).</span></p>")

        self.layout_bienvenida.addWidget(self.textEdit_bienvenida)

        self.tabWidget.addTab(self.tab_bienvenida, "")
        self.tab_datos = QWidget()
        self.tab_datos.setObjectName(u"tab_datos")
        self.layout_datos = QVBoxLayout(self.tab_datos)
        self.layout_datos.setObjectName(u"layout_datos")
        self.textEdit_datos = QTextEdit(self.tab_datos)
        self.textEdit_datos.setObjectName(u"textEdit_datos")
        self.textEdit_datos.setHtml(u"<p align=\"center\"><span style=\"font-size:12pt;\">Adjunta un fichero CSV para analizar los datos.</span></p>")

        self.layout_datos.addWidget(self.textEdit_datos)

        self.pushButton_adjuntar = QPushButton(self.tab_datos)
        self.pushButton_adjuntar.setObjectName(u"pushButton_adjuntar")

        self.layout_datos.addWidget(self.pushButton_adjuntar, 0, Qt.AlignHCenter)

        self.tabWidget.addTab(self.tab_datos, "")
        self.tab_estado = QWidget()
        self.tab_estado.setObjectName(u"tab_estado")
        self.layout_estado = QVBoxLayout(self.tab_estado)
        self.layout_estado.setObjectName(u"layout_estado")
        self.textEdit_estado = QTextEdit(self.tab_estado)
        self.textEdit_estado.setObjectName(u"textEdit_estado")
        self.textEdit_estado.setHtml(u"<p align=\"center\"><span style=\"font-size:12pt;\">Estado de los datos.</span></p>")

        self.layout_estado.addWidget(self.textEdit_estado)

        self.tabWidget.addTab(self.tab_estado, "")
        self.tab_opciones = QWidget()
        self.tab_opciones.setObjectName(u"tab_opciones")
        self.layout_opciones = QVBoxLayout(self.tab_opciones)
        self.layout_opciones.setObjectName(u"layout_opciones")
        self.textEdit_opciones = QTextEdit(self.tab_opciones)
        self.textEdit_opciones.setObjectName(u"textEdit_opciones")
        self.textEdit_opciones.setHtml(u"<p align=\"center\"><span style=\"font-size:12pt;\">Selecciona un procedimiento a seguir.</span></p>")

        self.layout_opciones.addWidget(self.textEdit_opciones)

        self.comboBox_opciones = QComboBox(self.tab_opciones)
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.addItem("")
        self.comboBox_opciones.setObjectName(u"comboBox_opciones")

        self.layout_opciones.addWidget(self.comboBox_opciones, 0, Qt.AlignHCenter)

        self.pushButton_opciones = QPushButton(self.tab_opciones)
        self.pushButton_opciones.setObjectName(u"pushButton_opciones")

        self.layout_opciones.addWidget(self.pushButton_opciones, 0, Qt.AlignHCenter)

        self.tabWidget.addTab(self.tab_opciones, "")

        self.mainLayout.addWidget(self.tabWidget)

        ventana_inicio.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(ventana_inicio)
        self.statusbar.setObjectName(u"statusbar")
        ventana_inicio.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(ventana_inicio)
        self.menubar.setObjectName(u"menubar")
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

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ventana_inicio)
    # setupUi

    def retranslateUi(self, ventana_inicio):
        ventana_inicio.setWindowTitle(QCoreApplication.translate("ventana_inicio", u"Hamelin", None))
        self.actionAcerca_de_Hamelin.setText(QCoreApplication.translate("ventana_inicio", u"Acerca de Hamelin", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_bienvenida), QCoreApplication.translate("ventana_inicio", u"Bienvenida", None))
        self.pushButton_adjuntar.setText(QCoreApplication.translate("ventana_inicio", u"Adjuntar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_datos), QCoreApplication.translate("ventana_inicio", u"Datos", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_estado), QCoreApplication.translate("ventana_inicio", u"Estado", None))
        self.comboBox_opciones.setItemText(0, QCoreApplication.translate("ventana_inicio", u"Registro de pacientes", None))
        self.comboBox_opciones.setItemText(1, QCoreApplication.translate("ventana_inicio", u"Estudio observacional", None))
        self.comboBox_opciones.setItemText(2, QCoreApplication.translate("ventana_inicio", u"Estudio cl\u00ednico", None))

        self.pushButton_opciones.setText(QCoreApplication.translate("ventana_inicio", u"Ok", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_opciones), QCoreApplication.translate("ventana_inicio", u"Opciones", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("ventana_inicio", u"Archivo", None))
        self.menuEdici_n.setTitle(QCoreApplication.translate("ventana_inicio", u"Edici\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("ventana_inicio", u"Ayuda", None))
    # retranslateUi


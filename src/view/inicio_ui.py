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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTabWidget, QTextEdit, QWidget)

class Ui_ventana_inicio(object):
    def setupUi(self, ventana_inicio):
        if not ventana_inicio.objectName():
            ventana_inicio.setObjectName(u"ventana_inicio")
        ventana_inicio.resize(704, 420)
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
        self.tabWidget = QTabWidget(self.gridLayoutWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tab_inicio = QWidget()
        self.tab_inicio.setObjectName(u"tab_inicio")
        self.tab_inicio.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.textEdit = QTextEdit(self.tab_inicio)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget.addTab(self.tab_inicio, "")
        self.tab_datos = QWidget()
        self.tab_datos.setObjectName(u"tab_datos")
        self.textEdit_2 = QTextEdit(self.tab_datos)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton = QPushButton(self.tab_datos)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(290, 180, 83, 22))
        self.tabWidget.addTab(self.tab_datos, "")
        self.tab_estado = QWidget()
        self.tab_estado.setObjectName(u"tab_estado")
        self.textEdit_3 = QTextEdit(self.tab_estado)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget.addTab(self.tab_estado, "")
        self.tab_opciones = QWidget()
        self.tab_opciones.setObjectName(u"tab_opciones")
        self.comboBox = QComboBox(self.tab_opciones)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(250, 170, 161, 22))
        self.textEdit_4 = QTextEdit(self.tab_opciones)
        self.textEdit_4.setObjectName(u"textEdit_4")
        self.textEdit_4.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_2 = QPushButton(self.tab_opciones)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(290, 210, 83, 22))
        self.tabWidget.addTab(self.tab_opciones, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        ventana_inicio.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(ventana_inicio)
        self.statusbar.setObjectName(u"statusbar")
        ventana_inicio.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(ventana_inicio)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 704, 19))
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
        self.actionAbout.setText(QCoreApplication.translate("ventana_inicio", u"Acerca", None))
        self.actionAcerca_de_Hamelin.setText(QCoreApplication.translate("ventana_inicio", u"Acerca de Hamelin", None))
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
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Hamelin es una aplicaci\u00f3n que capacita a los Profesionales de Investigaci\u00f3n Cl\u00ednica (CRPs) para crear sus propios modelos predictivos de Aprendizaje Autom\u00e1tico (ML).</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_inicio), QCoreApplication.translate("ventana_inicio", u"Inicio", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Adjunta un fichero CSV para analizar los datos.</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("ventana_inicio", u"Adjuntar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_datos), QCoreApplication.translate("ventana_inicio", u"Datos", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Estado de los datos.</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_estado), QCoreApplication.translate("ventana_inicio", u"Estado", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("ventana_inicio", u"Registro de pacientes", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("ventana_inicio", u"Estudio observacional", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("ventana_inicio", u"Estudio cl\u00ednico", None))

        self.textEdit_4.setHtml(QCoreApplication.translate("ventana_inicio", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona un procedimiento a seguir.</span></p></body></html>", None))
        self.pushButton_2.setText(QCoreApplication.translate("ventana_inicio", u"Ok", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_opciones), QCoreApplication.translate("ventana_inicio", u"Opciones", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("ventana_inicio", u"Archivo", None))
        self.menuEdici_n.setTitle(QCoreApplication.translate("ventana_inicio", u"Edici\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("ventana_inicio", u"Ayuda", None))
    # retranslateUi


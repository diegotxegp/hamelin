# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'estudio_clinico.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QTextEdit,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1170, 359)
        self.actionAcerca_de_Hamelin = QAction(MainWindow)
        self.actionAcerca_de_Hamelin.setObjectName(u"actionAcerca_de_Hamelin")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QRect(0, 0, 1161, 369))
        self.tab_inicio = QWidget()
        self.tab_inicio.setObjectName(u"tab_inicio")
        self.tab_inicio.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.textEdit = QTextEdit(self.tab_inicio)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton_3 = QPushButton(self.tab_inicio)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(290, 170, 83, 22))
        self.tabWidget.addTab(self.tab_inicio, "")
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
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        self.listWidget_2.setObjectName(u"listWidget_2")
        self.listWidget_2.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_2.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget.addTab(self.tab_criterios_inclusion_exclusion, "")
        self.tab_farmaco_experimental = QWidget()
        self.tab_farmaco_experimental.setObjectName(u"tab_farmaco_experimental")
        self.tabWidget.addTab(self.tab_farmaco_experimental, "")
        self.tab_farmaco_control = QWidget()
        self.tab_farmaco_control.setObjectName(u"tab_farmaco_control")
        self.tabWidget.addTab(self.tab_farmaco_control, "")
        self.tab_enfermedad_trastorno = QWidget()
        self.tab_enfermedad_trastorno.setObjectName(u"tab_enfermedad_trastorno")
        self.tabWidget.addTab(self.tab_enfermedad_trastorno, "")
        self.tab_variable_principal = QWidget()
        self.tab_variable_principal.setObjectName(u"tab_variable_principal")
        self.textEdit_4 = QTextEdit(self.tab_variable_principal)
        self.textEdit_4.setObjectName(u"textEdit_4")
        self.textEdit_4.setGeometry(QRect(10, 10, 651, 121))
        self.listWidget_3 = QListWidget(self.tab_variable_principal)
        QListWidgetItem(self.listWidget_3)
        self.listWidget_3.setObjectName(u"listWidget_3")
        self.listWidget_3.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_3.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget.addTab(self.tab_variable_principal, "")
        self.tab_procesar = QWidget()
        self.tab_procesar.setObjectName(u"tab_procesar")
        self.textEdit_5 = QTextEdit(self.tab_procesar)
        self.textEdit_5.setObjectName(u"textEdit_5")
        self.textEdit_5.setGeometry(QRect(10, 10, 651, 121))
        self.pushButton = QPushButton(self.tab_procesar)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(290, 180, 83, 22))
        self.tabWidget.addTab(self.tab_procesar, "")
        self.tab_resultados = QWidget()
        self.tab_resultados.setObjectName(u"tab_resultados")
        self.textEdit_6 = QTextEdit(self.tab_resultados)
        self.textEdit_6.setObjectName(u"textEdit_6")
        self.textEdit_6.setGeometry(QRect(10, 10, 651, 121))
        self.tabWidget.addTab(self.tab_resultados, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1170, 19))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuEdici_n = QMenu(self.menubar)
        self.menuEdici_n.setObjectName(u"menuEdici_n")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuEdici_n.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuAyuda.addAction(self.actionAcerca_de_Hamelin)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Hamelin", None))
        self.actionAcerca_de_Hamelin.setText(QCoreApplication.translate("MainWindow", u"Acerca de Hamelin", None))
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
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_inicio), QCoreApplication.translate("MainWindow", u"Inicio", None))
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
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"Pacientes que firmen el consentimiento informado", None));
        ___qlistwidgetitem1 = self.listWidget_2.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Pacientes mayores de 18 a\u00f1os", None));
        ___qlistwidgetitem2 = self.listWidget_2.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Portadores de pr\u00f3tesis de cadera o rodilla, diagnosticados de una infecci\u00f3n prot\u00e9sica", None));
        ___qlistwidgetitem3 = self.listWidget_2.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Pacientes sin posibilidad de tratamiento curativo", None));
        ___qlistwidgetitem4 = self.listWidget_2.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Sin infecciones monomicrobianas", None));
        ___qlistwidgetitem5 = self.listWidget_2.item(5)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Sin infecciones polimicrobianas", None));
        ___qlistwidgetitem6 = self.listWidget_2.item(6)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Sin infecciones f\u00fangicas o por micobacterias", None));
        ___qlistwidgetitem7 = self.listWidget_2.item(7)
        ___qlistwidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Pacientes sin tratamiento con inmunosupresores o corticoides > 5mg/d\u00eda en los \u00faltimos 3 meses", None));
        self.listWidget_2.setSortingEnabled(__sortingEnabled)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_criterios_inclusion_exclusion), QCoreApplication.translate("MainWindow", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_farmaco_experimental), QCoreApplication.translate("MainWindow", u"F\u00e1rmaco experimental", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_farmaco_control), QCoreApplication.translate("MainWindow", u"F\u00e1rmaco de control", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_enfermedad_trastorno), QCoreApplication.translate("MainWindow", u"Enfermedad/Trastorno", None))
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
        ___qlistwidgetitem8 = self.listWidget_3.item(0)
        ___qlistwidgetitem8.setText(QCoreApplication.translate("MainWindow", u"Aparici\u00f3n de LPP en pacientes neuroquir\u00farjicos en un periodo >3 horas de intervenci\u00f3n", None));
        self.listWidget_3.setSortingEnabled(__sortingEnabled1)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_variable_principal), QCoreApplication.translate("MainWindow", u"Variable principal", None))
        self.textEdit_5.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset.</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_procesar), QCoreApplication.translate("MainWindow", u"Procesar", None))
        self.textEdit_6.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset.</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_resultados), QCoreApplication.translate("MainWindow", u"Resultados", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("MainWindow", u"Archivo", None))
        self.menuEdici_n.setTitle(QCoreApplication.translate("MainWindow", u"Edici\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("MainWindow", u"Ayuda", None))
    # retranslateUi


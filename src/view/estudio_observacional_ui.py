# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'estudio_observacional.ui'
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

class Ui_ventana_estudio_observacional(object):
    def setupUi(self, ventana_estudio_observacional):
        if not ventana_estudio_observacional.objectName():
            ventana_estudio_observacional.setObjectName(u"ventana_estudio_observacional")
        ventana_estudio_observacional.resize(704, 413)
        self.actionAcerca_de_Hamelin = QAction(ventana_estudio_observacional)
        self.actionAcerca_de_Hamelin.setObjectName(u"actionAcerca_de_Hamelin")
        self.centralwidget = QWidget(ventana_estudio_observacional)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QRect(0, 0, 679, 369))
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
        self.listWidget_2.setObjectName(u"listWidget_2")
        self.listWidget_2.setGeometry(QRect(10, 140, 651, 192))
        self.listWidget_2.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tabWidget.addTab(self.tab_criterios_inclusion_exclusion, "")
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
        ventana_estudio_observacional.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ventana_estudio_observacional)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 704, 19))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuEdici_n = QMenu(self.menubar)
        self.menuEdici_n.setObjectName(u"menuEdici_n")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        ventana_estudio_observacional.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(ventana_estudio_observacional)
        self.statusbar.setObjectName(u"statusbar")
        ventana_estudio_observacional.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuEdici_n.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuAyuda.addAction(self.actionAcerca_de_Hamelin)

        self.retranslateUi(ventana_estudio_observacional)

        self.tabWidget.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(ventana_estudio_observacional)
    # setupUi

    def retranslateUi(self, ventana_estudio_observacional):
        ventana_estudio_observacional.setWindowTitle(QCoreApplication.translate("ventana_estudio_observacional", u"Hamelin", None))
        self.actionAcerca_de_Hamelin.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Acerca de Hamelin", None))
#if QT_CONFIG(accessibility)
        self.tab_inicio.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.textEdit.setHtml(QCoreApplication.translate("ventana_estudio_observacional", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio.</span></p></body></html>", None))
        self.pushButton_3.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Inicio", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_inicio), QCoreApplication.translate("ventana_estudio_observacional", u"Inicio", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("ventana_estudio_observacional", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
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
        ___qlistwidgetitem.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Pacientes que comprenden y firman el consentimiento informado que se le presentar\u00e1 antes de entrar al quir\u00f3fano", None));
        ___qlistwidgetitem1 = self.listWidget_2.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Pacientes adultos de ambos sexos que van a ser sometidos a una cirug\u00eda programada de m\u00e1s de 3 horas de duraci\u00f3n, por parte del serviciode Neurocirug\u00eda Unidad de Raquis del HUMV, entre el a\u00f1o 2023 y 2024", None));
        ___qlistwidgetitem2 = self.listWidget_2.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Pacientes posicionados en dec\u00fabito prono, supino, lateral y en silla de playa/ sentado", None));
        ___qlistwidgetitem3 = self.listWidget_2.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Cirug\u00edas susceptibles de colocaci\u00f3n de sondaje vesical con medici\u00f3n de la temperatura corporal", None));
        ___qlistwidgetitem4 = self.listWidget_2.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Pacientes ingresados el d\u00eda previo a la cirug\u00eda", None));
        ___qlistwidgetitem5 = self.listWidget_2.item(5)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Pacientes con lesiones por presi\u00f3n visibles presentes antes de la cirug\u00eda", None));
        ___qlistwidgetitem6 = self.listWidget_2.item(6)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Pacientes con trastorno cognitivo o dificultad de conocimiento escrito y oral", None));
        self.listWidget_2.setSortingEnabled(__sortingEnabled)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_criterios_inclusion_exclusion), QCoreApplication.translate("ventana_estudio_observacional", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_4.setHtml(QCoreApplication.translate("ventana_estudio_observacional", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Selecciona la variable principal.</span></p></body></html>", None))

        __sortingEnabled1 = self.listWidget_3.isSortingEnabled()
        self.listWidget_3.setSortingEnabled(False)
        ___qlistwidgetitem7 = self.listWidget_3.item(0)
        ___qlistwidgetitem7.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Aparici\u00f3n de LPP en pacientes neuroquir\u00farjicos en un periodo >3 horas de intervenci\u00f3n", None));
        self.listWidget_3.setSortingEnabled(__sortingEnabled1)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_variable_principal), QCoreApplication.translate("ventana_estudio_observacional", u"Variable principal", None))
        self.textEdit_5.setHtml(QCoreApplication.translate("ventana_estudio_observacional", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset.</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("ventana_estudio_observacional", u"Procesar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_procesar), QCoreApplication.translate("ventana_estudio_observacional", u"Procesar", None))
        self.textEdit_6.setHtml(QCoreApplication.translate("ventana_estudio_observacional", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset.</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_resultados), QCoreApplication.translate("ventana_estudio_observacional", u"Resultados", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("ventana_estudio_observacional", u"Archivo", None))
        self.menuEdici_n.setTitle(QCoreApplication.translate("ventana_estudio_observacional", u"Edici\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("ventana_estudio_observacional", u"Ayuda", None))
    # retranslateUi


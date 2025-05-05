# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'registro_pacientes.ui'
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

class Ui_ventana_registro_pacientes(object):
    def setupUi(self, ventana_registro_pacientes):
        if not ventana_registro_pacientes.objectName():
            ventana_registro_pacientes.setObjectName(u"ventana_registro_pacientes")
        ventana_registro_pacientes.resize(704, 413)
        self.actionAcerca_de_Hamelin = QAction(ventana_registro_pacientes)
        self.actionAcerca_de_Hamelin.setObjectName(u"actionAcerca_de_Hamelin")
        self.centralwidget = QWidget(ventana_registro_pacientes)
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
        self.tab_dataset = QWidget()
        self.tab_dataset.setObjectName(u"tab_dataset")
        self.textEdit_2 = QTextEdit(self.tab_dataset)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(10, 10, 651, 121))
        self.widget = QWidget(self.tab_dataset)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 150, 651, 161))
        self.tabWidget.addTab(self.tab_dataset, "")
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
        self.tabWidget.addTab(self.tab_criterios_inclusion_exclusion, "")
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
        ventana_registro_pacientes.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ventana_registro_pacientes)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 704, 19))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuEdici_n = QMenu(self.menubar)
        self.menuEdici_n.setObjectName(u"menuEdici_n")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        ventana_registro_pacientes.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(ventana_registro_pacientes)
        self.statusbar.setObjectName(u"statusbar")
        ventana_registro_pacientes.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuEdici_n.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuAyuda.addAction(self.actionAcerca_de_Hamelin)

        self.retranslateUi(ventana_registro_pacientes)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(ventana_registro_pacientes)
    # setupUi

    def retranslateUi(self, ventana_registro_pacientes):
        ventana_registro_pacientes.setWindowTitle(QCoreApplication.translate("ventana_registro_pacientes", u"Hamelin", None))
        self.actionAcerca_de_Hamelin.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Acerca de Hamelin", None))
#if QT_CONFIG(accessibility)
        self.tab_inicio.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.textEdit.setHtml(QCoreApplication.translate("ventana_registro_pacientes", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Volver a la pantalla de inicio.</span></p></body></html>", None))
        self.pushButton_3.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Inicio", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_inicio), QCoreApplication.translate("ventana_registro_pacientes", u"Inicio", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("ventana_registro_pacientes", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Modificar dataset.</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_dataset), QCoreApplication.translate("ventana_registro_pacientes", u"Dataset", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("ventana_registro_pacientes", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
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
        ___qlistwidgetitem.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Pacientes con consentimiento informado", None));
        ___qlistwidgetitem1 = self.listWidget_2.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Pacientes de cualquier edad y sexo, incluyendo menores de edad y embarazadas", None));
        ___qlistwidgetitem2 = self.listWidget_2.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Ingreso hospitalario con diagn\u00f3stico de COVID-19 seg\u00fan los criterios cl\u00ednicos y microbiol\u00f3gicos que se establezcan por las Autoridades Sanitarias y la pr\u00e1ctica cl\u00ednica (\u00e9stos pueden modificarse en base al \u201cDocumento t\u00e9cnico. Manejo cl\u00ednico del COVID-19: atenci\u00f3n hospitalaria\u201d del Ministerio de Sanidad)", None));
        ___qlistwidgetitem3 = self.listWidget_2.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Pacientes que reciban cualquier tratamiento espec\u00edfico para tratar la enfermedad COVID-19 (seg\u00fan el \u201cDocumento T\u00e9cnico. Manejo cl\u00ednico del COVID-19: tratamiento medico\u201d del Ministerio de Sanidad, y \u201cTratamientos disponibles para el manejo de la infecci\u00f3n respiratoria por SARS-CoV-2\u201d de la AEMPS)", None));
        ___qlistwidgetitem4 = self.listWidget_2.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Pacientes que ingresen pero no reciban un tratamiento espec\u00edfico para tratar la enfermedad COVID-19", None));
        self.listWidget_2.setSortingEnabled(__sortingEnabled)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_criterios_inclusion_exclusion), QCoreApplication.translate("ventana_registro_pacientes", u"Criterios de inclusi\u00f3n/exclusi\u00f3n", None))
        self.textEdit_4.setHtml(QCoreApplication.translate("ventana_registro_pacientes", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
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
        ___qlistwidgetitem5.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Respuesta al tratamiento", None));
        ___qlistwidgetitem6 = self.listWidget_3.item(1)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Recuperaci\u00f3n", None));
        ___qlistwidgetitem7 = self.listWidget_3.item(2)
        ___qlistwidgetitem7.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Mortalidad", None));
        self.listWidget_3.setSortingEnabled(__sortingEnabled1)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_variable_principal), QCoreApplication.translate("ventana_registro_pacientes", u"Variable principal", None))
        self.textEdit_5.setHtml(QCoreApplication.translate("ventana_registro_pacientes", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Procesar el dataset.</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("ventana_registro_pacientes", u"Procesar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_procesar), QCoreApplication.translate("ventana_registro_pacientes", u"Procesar", None))
        self.textEdit_6.setHtml(QCoreApplication.translate("ventana_registro_pacientes", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Resultados del procesado del dataset.</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_resultados), QCoreApplication.translate("ventana_registro_pacientes", u"Resultados", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("ventana_registro_pacientes", u"Archivo", None))
        self.menuEdici_n.setTitle(QCoreApplication.translate("ventana_registro_pacientes", u"Edici\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("ventana_registro_pacientes", u"Ayuda", None))
    # retranslateUi


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\client\start_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(380, 160)
        Dialog.setMinimumSize(QtCore.QSize(380, 160))
        Dialog.setMaximumSize(QtCore.QSize(380, 160))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        Dialog.setFont(font)
        Dialog.setStyleSheet("background-color: purple;\n"
"color: white;\n"
"font: 63 12pt \"Lucida Sans\";")
        self.lbl_name = QtWidgets.QLabel(Dialog)
        self.lbl_name.setGeometry(QtCore.QRect(10, 20, 150, 20))
        self.lbl_name.setObjectName("lbl_name")
        self.lbl_pass = QtWidgets.QLabel(Dialog)
        self.lbl_pass.setGeometry(QtCore.QRect(10, 50, 150, 20))
        self.lbl_pass.setObjectName("lbl_pass")
        self.lineEdit_name = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_name.setGeometry(QtCore.QRect(170, 20, 200, 20))
        self.lineEdit_name.setStyleSheet("background-color: white;\n"
"color: black;")
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.lineEdit_pass = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_pass.setGeometry(QtCore.QRect(170, 50, 200, 20))
        self.lineEdit_pass.setStyleSheet("background-color: white;\n"
"color: black;")
        self.lineEdit_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_pass.setObjectName("lineEdit_pass")
        self.btn_ok = QtWidgets.QPushButton(Dialog)
        self.btn_ok.setGeometry(QtCore.QRect(60, 90, 100, 25))
        self.btn_ok.setObjectName("btn_ok")
        self.btn_cancel = QtWidgets.QPushButton(Dialog)
        self.btn_cancel.setGeometry(QtCore.QRect(220, 90, 100, 25))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.btn_cancel.setFont(font)
        self.btn_cancel.setObjectName("btn_cancel")
        self.lbl_status = QtWidgets.QLabel(Dialog)
        self.lbl_status.setGeometry(QtCore.QRect(10, 130, 360, 15))
        self.lbl_status.setText("")
        self.lbl_status.setObjectName("lbl_status")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Start Dialog"))
        self.lbl_name.setText(_translate("Dialog", "Account name"))
        self.lbl_pass.setText(_translate("Dialog", "Account password"))
        self.btn_ok.setText(_translate("Dialog", "Start"))
        self.btn_cancel.setText(_translate("Dialog", "Cancel"))

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\client\client.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(802, 606)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(802, 606))
        MainWindow.setMaximumSize(QtCore.QSize(802, 606))
        MainWindow.setStyleSheet("QWidget {\n"
                                 "    color: black;\n"
                                 "    background-color: purple;\n"
                                 "}\n"
                                 "\n"
                                 "QLineEdit {\n"
                                 "    background-color: violet;\n"
                                 "}\n"
                                 "\n"
                                 "QListView {\n"
                                 "    background-color: white;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton {\n"
                                 "    color: white;\n"
                                 "    background-color:grey;\n"
                                 "    font: 63 14pt \"Lucida Sans\";\n"
                                 "}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 780, 550))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_chat = QtWidgets.QWidget()
        self.tab_chat.setStyleSheet("")
        self.tab_chat.setObjectName("tab_chat")
        self.lineEdit_input = QtWidgets.QLineEdit(self.tab_chat)
        self.lineEdit_input.setGeometry(QtCore.QRect(170, 414, 594, 60))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(12)
        font.setItalic(True)
        self.lineEdit_input.setFont(font)
        self.lineEdit_input.setStyleSheet("background-color: white;\n"
                                          "color: black;")
        self.lineEdit_input.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.lineEdit_input.setObjectName("lineEdit_input")
        self.btn_add_user = QtWidgets.QPushButton(self.tab_chat)
        self.btn_add_user.setGeometry(QtCore.QRect(10, 484, 70, 30))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.btn_add_user.setFont(font)
        self.btn_add_user.setObjectName("btn_add_user")
        self.btn_del_user = QtWidgets.QPushButton(self.tab_chat)
        self.btn_del_user.setGeometry(QtCore.QRect(90, 484, 70, 30))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.btn_del_user.setFont(font)
        self.btn_del_user.setObjectName("btn_del_user")
        self.btn_send = QtWidgets.QPushButton(self.tab_chat)
        self.btn_send.setGeometry(QtCore.QRect(680, 484, 70, 30))
        self.btn_send.setObjectName("btn_send")
        self.btn_clear = QtWidgets.QPushButton(self.tab_chat)
        self.btn_clear.setGeometry(QtCore.QRect(590, 484, 70, 30))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.btn_clear.setFont(font)
        self.btn_clear.setObjectName("btn_clear")
        self.list_chat = QtWidgets.QListView(self.tab_chat)
        self.list_chat.setGeometry(QtCore.QRect(170, 10, 594, 394))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(12)
        self.list_chat.setFont(font)
        self.list_chat.setObjectName("list_chat")
        self.list_contacts = QtWidgets.QListView(self.tab_chat)
        self.list_contacts.setGeometry(QtCore.QRect(10, 10, 150, 464))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(12)
        self.list_contacts.setFont(font)
        self.list_contacts.setStyleSheet("background-color: violet;\n"
                                         "color: white;")
        self.list_contacts.setObjectName("list_contacts")
        self.tabWidget.addTab(self.tab_chat, "")
        self.tab_settings = QtWidgets.QWidget()
        self.tab_settings.setObjectName("tab_settings")
        self.lineEdit_address = QtWidgets.QLineEdit(self.tab_settings)
        self.lineEdit_address.setGeometry(QtCore.QRect(10, 60, 754, 40))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_address.setFont(font)
        self.lineEdit_address.setObjectName("lineEdit_address")
        self.lineEdit_port = QtWidgets.QLineEdit(self.tab_settings)
        self.lineEdit_port.setGeometry(QtCore.QRect(10, 110, 754, 40))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_port.setFont(font)
        self.lineEdit_port.setObjectName("lineEdit_port")
        self.btn_connect = QtWidgets.QPushButton(self.tab_settings)
        self.btn_connect.setGeometry(QtCore.QRect(50, 170, 674, 40))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.btn_connect.setFont(font)
        self.btn_connect.setObjectName("btn_connect")
        self.lineEdit_name = QtWidgets.QLineEdit(self.tab_settings)
        self.lineEdit_name.setGeometry(QtCore.QRect(10, 10, 754, 40))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_name.setFont(font)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.tabWidget.addTab(self.tab_settings, "")
        self.lbl_time = QtWidgets.QLabel(self.centralwidget)
        self.lbl_time.setGeometry(QtCore.QRect(670, 0, 120, 20))
        self.lbl_time.setStyleSheet("background-color: violet;\n"
                                    "padding-left: 5px;")
        self.lbl_time.setObjectName("lbl_time")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 802, 19))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setBold(True)
        font.setWeight(75)
        self.menubar.setFont(font)
        self.menubar.setStyleSheet("color: white;")
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuContacts = QtWidgets.QMenu(self.menubar)
        self.menuContacts.setObjectName("menuContacts")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAdd_contact = QtWidgets.QAction(MainWindow)
        self.actionAdd_contact.setObjectName("actionAdd_contact")
        self.actionDelete_contact = QtWidgets.QAction(MainWindow)
        self.actionDelete_contact.setObjectName("actionDelete_contact")
        self.menuFile.addAction(self.actionExit)
        self.menuContacts.addAction(self.actionAdd_contact)
        self.menuContacts.addAction(self.actionDelete_contact)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuContacts.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Chat"))
        self.lineEdit_input.setPlaceholderText(_translate("MainWindow", "Message..."))
        self.btn_add_user.setText(_translate("MainWindow", "Add"))
        self.btn_del_user.setText(_translate("MainWindow", "Del"))
        self.btn_send.setText(_translate("MainWindow", ">>>"))
        self.btn_clear.setText(_translate("MainWindow", "Clear"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_chat), _translate("MainWindow", "Chat Room"))
        self.lineEdit_address.setPlaceholderText(_translate("MainWindow", "Server address..."))
        self.lineEdit_port.setPlaceholderText(_translate("MainWindow", "Server port..."))
        self.btn_connect.setText(_translate("MainWindow", "Connect"))
        self.lineEdit_name.setPlaceholderText(_translate("MainWindow", "NickName..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_settings), _translate("MainWindow", "Settings"))
        self.lbl_time.setText(_translate("MainWindow", "Time"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuContacts.setTitle(_translate("MainWindow", "Contacts"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAdd_contact.setText(_translate("MainWindow", "Add contact"))
        self.actionDelete_contact.setText(_translate("MainWindow", "Delete contact"))

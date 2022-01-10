"""Модуль, формирующий основное окно приложения на стороне сервера."""

import os
import sys
import binascii
import hashlib
from PyQt5.QtWidgets import QMainWindow, qApp, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from server.server_form import Ui_MainWindow


class ServerMainWindow(QMainWindow):
    def __init__(self, server, database, config):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.server = server
        self.database = database
        self.config = config
        # Выход:
        self.ui.btn_exit.clicked.connect(qApp.quit)
        # Обновление списка клиентов:
        self.ui.btn_refresh.clicked.connect(self.create_clients_list)
        # Вкладка настройки:
        self.ui.lineEdit_db_path.setReadOnly(True)
        self.ui.btn_find_db.clicked.connect(self.open_file_dialog)

        # Вкладка авторизации/удаления:
        self.ui.btn_reg.clicked.connect(self.save_user)
        self.ui.btn_reg_cancel.clicked.connect(self.clear_reg_data)

        self.selector = self.ui.comboBox
        self.fill_selector()
        self.ui.btn_del.clicked.connect(self.remove_user)
        self.ui.btn_del_cancel.clicked.connect(self.clear_del_data)

        self.show()

        # self.ui.lineEdit_db_path.insert(self.config['SETTINGS']['database-path'])
        # self.ui.lineEdit_db_name.insert(self.config['SETTINGS']['database_file'])
        # self.ui.lineEdit_address.insert(self.config['SETTINGS']['default_address'])
        # self.ui.lineEdit_port.insert(self.config['SETTINGS']['default_port'])
        # self.ui.btn_save.clicked.connect(self.save_config)

    def create_clients_list(self):
        """Формирует список клиентов."""
        users_list = self.database.get_active_users()
        users = QStandardItemModel()
        users.setHorizontalHeaderLabels(['Name', 'IP-address', 'Port', 'Login-time'])
        for user in users_list:
            name, ip, port, time = user
            name = QStandardItem(name)
            ip = QStandardItem(str(ip))
            port = QStandardItem(str(port))
            time = QStandardItem(str(time.replace(microseconds=0)))
            name.setEditable(False)
            ip.setEditable(False)
            port.setEditable(False)
            time.setEditable(False)
            users.appendRow([name, ip, port, time])
        self.ui.tableView_clients.setModel(users)

    def create_statistic_list(self):
        """Формирует статистику клиентов."""
        statistic_list = self.database.get_history()
        users = QStandardItemModel()
        users.setHorizontalHeaderLabels(['Name', 'Last-time', 'IP-address', 'Port'])
        for user in statistic_list:
            name, time, ip, port = user
            name = QStandardItem(name)
            time = QStandardItem(str(time.replace(microseconds=0)))
            ip = QStandardItem(str(ip))
            port = QStandardItem(str(port))
            name.setEditable(False)
            time.setEditable(False)
            ip.setEditable(False)
            port.setEditable(False)
            users.appendRow([name, time, ip, port])
        self.ui.tableView_statistic.setModel(users)

    def open_file_dialog(self):
        """Вызывает стандартный диалог выбора файла."""
        global dialog
        dialog = QFileDialog(self)
        file_path = dialog.getExistingDirectory()
        self.ui.lineEdit_db_path.clear()
        self.ui.lineEdit_db_path.insert(file_path)

    def save_config(self):
        """Сохраняет настройки в .ini файл."""
        try:
            port = int(self.ui.lineEdit_port.text())
        except ValueError:
            err_message = QMessageBox()
            err_message.warning(self, 'Error', 'Port must be a number!')
        else:
            if port < 1024 or port > 65535:
                err_message = QMessageBox()
                err_message.warning(self, 'Error', 'Port must be from 1024 to 65535!')
            else:
                self.config['SETTINGS']['default_port'] = str(port)
                self.config['SETTINGS']['default_address'] = self.ui.lineEdit_address.text()
                self.config['SETTINGS']['database_path'] = self.ui.lineEdit_db_path.text()
                self.config['SETTINGS']['database_file'] = self.ui.lineEdit_db_name.text()
                dir_path = os.getcwd()
                with open(f'{dir_path}/server.ini', 'w') as conf:
                    conf.write(self.config)
                message = QMessageBox()
                message.information(self, 'Success', 'Settings have been saved!')

    def save_user(self):
        """Сохраняет нового пользователя."""
        if not self.ui.line_reg_name.text():
            err_message = QMessageBox()
            err_message.critical(self, 'Error', 'Enter the name!')
            return
        elif self.ui.line_pass.text() != self.ui.line_pass2.text():
            err_message = QMessageBox()
            err_message.critical(self, 'Error', 'Passwords do not match!')
            return
        elif self.database.check_user(self.ui.line_reg_name.text()):
            err_message = QMessageBox()
            err_message.critical(self, 'Error', 'This name is already taken!')
            return
        else:
            pass_bytes = self.ui.line_pass.text().encode('utf-8')
            salt = self.ui.line_reg_name.text().lower().encode('utf-8')
            pass_hash = hashlib.pbkdf2_hmac('sha256', pass_bytes, salt, 10000)
            pass_string = binascii.hexlify(pass_hash)
            self.database.add_user(self.ui.line_reg_name.text(), pass_string)
            print(3)
            message = QMessageBox()
            message.information(self, 'Success', 'User is registered!')
            self.server.update_data()

    def clear_reg_data(self):
        """Очищает данные для регистрации пользователя."""
        self.ui.line_reg_name.clear()
        self.ui.line_pass.clear()
        self.ui.line_pass2.clear()

    def fill_selector(self):
        """Запоняет селектор существующими пользователями."""
        users_list = []
        for user in self.database.get_users_list():
            users_list.append(user[0])

        self.selector.addItems(users_list)

    def remove_user(self):
        """Удаляет выбранного пользователя."""
        self.database.remove_user(self.selector.currentText())
        if self.selector.currentText() in self.server.names:
            client_socket = self.server.names[self.selector.currentText()]
            del self.server.names[self.selector.currentText()]
            self.server.remove_client(client_socket)
        self.server.update_data()

    def clear_del_data(self):
        """Очищает данные для удаления пользователя."""
        pass

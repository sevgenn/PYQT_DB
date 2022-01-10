"""Модуль окна, в котором обрабатывается добавление нового контакта."""

import logging
from PyQt5.QtWidgets import QDialog, qApp, QMessageBox
from client.add_form import Ui_Dialog


class AddContactDialog(QDialog):
    """Класс, описывающий форму добавления контакта в список."""

    def __init__(self, socket):
        super().__init__()
        self.client_socket = socket
        self.database = socket.database
        self.logger = logging.getLogger('client')

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.btn_cancel.clicked.connect(self.close)
        self.selector = self.ui.comboBox

        self.get_existing_users()
        self.ui.btn_refresh.clicked.connect(self.update_existing_users)

    def get_existing_users(self):
        """Формирует список существующих клиентов для добавления в контакты."""
        self.selector.clear()
        users_list = self.database.get_users()
        contacts_list = self.database.get_contacts()
        # Удаляем из списка самого клиента:
        users_list.remove(self.client_socket.account_name)
        exist_users = set(users_list) - set(contacts_list)
        self.selector.addItems(exist_users)

    def update_existing_users(self):
        """Обновляет список существующих клиентов для добавления в контакты."""
        try:
            self.client_socket.update_users()
        except OSError:
            pass
        else:
            self.logger.debug('Список существующих пользователей обновлен.')
            self.get_existing_users()

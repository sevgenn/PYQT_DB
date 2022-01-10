"""Модуль, формирующий основное окно приложения на стороне клиента."""

import base64
import json
import logging
from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QBrush, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from client.client_form import Ui_MainWindow
from client.add_window import AddContactDialog
from client.remove_window import RemoveContactDialog
from common.variables import *


class ClientMainWindow(QMainWindow):
    def __init__(self, socket, database, key):
        super().__init__()
        self.client_socket = socket
        self.database = database

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Кнопка выход (exit) меню:
        self.ui.actionExit.triggered.connect(qApp.quit)

        # Добавление контакта:
        self.ui.btn_add_user.clicked.connect(self.call_add_contact_window)
        self.ui.actionAdd_contact.triggered.connect(
            self.call_add_contact_window)

        # Удаление контакта:
        self.ui.btn_del_user.clicked.connect(self.call_remove_contact_window)
        self.ui.actionDelete_contact.triggered.connect(
            self.call_remove_contact_window)

        # Выбор контакта для переписки:
        self.ui.list_contacts.doubleClicked.connect(self.select_contact)

        # Отправка сообщения:
        self.ui.btn_send.clicked.connect(self.send_message)

        self.logger = logging.getLogger('client')
        # Список контактов:
        self.contacts_list = None
        # Шифратор:
        self.encryptor = None
        # Дешифратор:
        self.decrypter = PKCS1_OAEP.new(key)
        # Текущий собеседник:
        self.current_contact = None
        # Ключ текущего собеседника:
        self.current_contact_key = None
        # История сообщений:
        self.chat_history = None

        self.update_contacts()
        self.set_disabled()
        self.show()

    def set_disabled(self):
        """Делает недоступной отправку сообщений."""
        self.ui.lineEdit_input.clear()
        if self.chat_history:
            self.chat_history.clear()

        self.ui.btn_clear.setEnabled(False)
        self.ui.btn_send.setEnabled(False)
        self.ui.lineEdit_input.setEnabled(False)

        self.encryptor = None
        self.current_contact = None
        self.current_contact_key = None

    def update_contacts(self):
        """Обновляет список контактов."""
        contacts = self.database.get_contacts()
        self.contacts_list = QStandardItemModel()
        for item in contacts:
            contact = QStandardItem(item)
            contact.setEditable(False)
            self.contacts_list.appendRow(contact)
        self.ui.list_contacts.setModel(self.contacts_list)

    def update_message_list(self):
        """Заполняет поле переписки с собеседником."""
        # Сортируются сообщения по дате:
        message_list = sorted(
            self.database.get_message_history(
                self.current_contact),
            key=lambda item: item[3])
        if not self.chat_history:
            self.chat_history = QStandardItemModel()
            self.ui.list_chat.setModel(self.chat_history)
        # Отбор последних 20 записей:
        self.chat_history.clear()
        quantity = len(message_list)
        start_index = 0
        if quantity > 20:
            start_index = quantity - 20
        for i in range(start_index, quantity):
            item = message_list[i]
            if item[0] == self.client_socket.account_name:
                message = QStandardItem(f'me:\n {item[2]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(255, 213, 213)))
                message.setTextAlignment(Qt.AlignLeft)
                self.chat_history.appendRow(message)
            else:
                message = QStandardItem(f'{item[0]}:\n {item[2]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(204, 255, 204)))
                message.setTextAlignment(Qt.AlignRight)
                self.chat_history.appendRow(message)
        self.ui.list_chat.scrollToBottom()

    def select_contact(self):
        """Выбирает собеседника по двойному клику."""
        self.current_contact = self.ui.list_contacts.currentIndex().data()
        self.set_active_contact()

    def set_active_contact(self):
        """Активирует чат с выбранным собеседником."""
        # Шифрование:
        try:
            self.current_contact_key = self.client_socket.get_key(
                self.current_contact)
            if self.current_contact_key:
                self.encryptor = PKCS1_OAEP.new(
                    RSA.importKey(self.current_contact_key))
        except (OSError, json.JSONDecodeError):
            self.current_contact_key = None
            self.encryptor = None
            self.logger.error(f'Ключ для {self.current_contact} не получен.')

        if not self.current_contact_key:
            err_message = QMessageBox()
            err_message.critical(self, 'Error', 'No key!')
            return

        self.ui.btn_clear.setEnabled(True)
        self.ui.btn_send.setEnabled(True)
        self.ui.lineEdit_input.setEnabled(True)

        self.update_message_list()

    def add_contact(self, new_contact):
        """Добавляет новый контакт в БД."""
        try:
            self.client_socket.add_contact(new_contact)
        except Exception:
            err_message = QMessageBox()
            err_message.critical(self, 'Server error', 'Server error!')
        else:
            self.database.add_contact(new_contact)
            new_cont = QStandardItem(new_contact)
            new_cont.setEditable(False)
            self.contacts_list.appendRow(new_cont)
            self.logger.debug(f'Добавлен новый контакт {new_contact}')
            info_message = QMessageBox()
            info_message.information(self, 'Add a contact', 'Success!')

    def call_add_contact_window(self):
        """Вызывает диалог добавления контакта."""
        global select_dialog
        select_dialog = AddContactDialog(self.client_socket)
        select_dialog.ui.btn_add.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        """Обрабатывает добавление контакта."""
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def remove_contact(self, item):
        """Удаляет контакт из БД."""
        contact = item.selector.currentText()
        try:
            self.client_socket.remove_contact(contact)
        except Exception:
            err_message = QMessageBox()
            err_message.critical(self, 'Server error', 'Server error!')
        else:
            self.database.remove_contact(contact)
            self.update_contacts()
            self.logger.debug(f'Удален контакт {contact}')
            info_message = QMessageBox()
            info_message.information(self, 'Delete a contact', 'Success!')
            item.close()
            if contact == self.current_contact:
                self.current_contact = None
                self.set_disabled()

    def call_remove_contact_window(self):
        """Вызывает диалог удаления контакта."""
        global remove_dialog
        remove_dialog = RemoveContactDialog(self.database)
        remove_dialog.ui.btn_del.clicked.connect(lambda: self.remove_contact(remove_dialog))
        remove_dialog.show()

    def send_message(self):
        """Отправляет сообщение собеседнику."""
        message_text = self.ui.lineEdit_input.text()
        self.ui.lineEdit_input.clear()
        if not message_text:
            return
        # Шифруем сообщение:
        message_text_encrypted = self.encryptor.encrypt(
            message_text.encode('utf-8'))
        message_text_encrypted_base64 = base64.b64encode(
            message_text_encrypted)
        try:
            self.client_socket.create_message(
                self.current_contact,
                message_text_encrypted_base64.decode('utf-8'))
        except (OSError, ConnectionError, ConnectionResetError, ConnectionAbortedError):
            err_message = QMessageBox()
            err_message.critical(self, 'Server error', 'Server error!')
            self.close()
        else:
            self.database.save_message(
                self.client_socket.account_name,
                self.current_contact,
                message_text)
            self.logger.debug(
                f'Отправлено сообщение для {self.current_contact}')

    def connect_slots(self, socket):
        """Соединяет сигналы со слотами."""
        socket.new_message.connect(self.manage_message)
        socket.connection_lost.connect(self.connection_lost)
        socket.message_205.connect(self.manage_205)

    @pyqtSlot(dict)
    def manage_message(self, message):
        """Слот обрабатывает входящие сообщения."""
        encrypted_message = base64.b64decode(message[MESSAGE_TEXT])
        try:
            decrypted_message = self.decrypter.decrypt(encrypted_message)
        except (ValueError, TypeError):
            err_message = QMessageBox()
            err_message.warning(self, 'Error', 'Failed to decode!')
            return
        # # Сохраняем в БД:
        # self.database.save_message(self.current_contact, self.client_socket.account_name, decrypted_message.decode('utf-8'))
        sender = message[SENDER]
        # Если сообщение от текущего собеседника:
        if sender == self.current_contact:
            self.update_message_list()
        # Если не текущий собеседник:
        else:
            # Если есть в контактах:
            if self.database.check_contact(sender):
                quest_message = QMessageBox()
                quest_message.question(
                    self,
                    'New message',
                    f'Start a chat with {sender}?',
                    QMessageBox.Yes,
                    QMessageBox.No)
                if quest_message == QMessageBox.Yes:
                    self.current_contact = sender
                    self.set_active_contact()
            # Если нет в контактах:
            else:
                quest_message = QMessageBox()
                quest_message.question(
                    self,
                    'New message',
                    f'{sender} is not in Contacts. Start a chat?',
                    QMessageBox.Yes,
                    QMessageBox.No)
                if quest_message == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_contact = sender
                    self.set_active_contact()
        self.database.save_message(
            self.current_contact,
            self.client_socket.account_name,
            decrypted_message.decode('utf-8'))

    @pyqtSlot()
    def connection_lost(self):
        """Слот обрабатывает потери соединения."""
        err_message = QMessageBox()
        err_message.critical(self, 'Server error', 'No connection!')
        self.close()

    @pyqtSlot()
    def manage_205(self):
        """Слот обновляет БД."""
        if self.current_contact and not self.database.check_user(
                self.current_contact):
            message = QMessageBox()
            message.warning(self, 'Attention', 'No such user!')
            self.set_disabled()
            self.current_contact = None
        self.update_contacts()

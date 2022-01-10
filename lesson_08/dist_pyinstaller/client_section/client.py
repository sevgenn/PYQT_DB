"""Модуль "Клиент", описывающий логику класса-клиента и запускающий приложение."""

import os
import sys
import logging
import argparse
import socket
import threading
import time
import json
import hashlib
import hmac
import binascii

from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from common.variables import *
from common.utils import get_message, send_message
from common.decorators import Log
from common.metaclasses import ClientVerifier
from client.client_db import ClientStorage
from client.client_window import ClientMainWindow
from client.start_dialog import StartDialog
import logs.configs.config_log_client

CLIENT_LOGGER = logging.getLogger('client')
socket_lock = threading.Lock()


class Client(threading.Thread, QObject):
    """Класс-клиент, отвечающий за взаимодействие с сервером."""
    __metaclass__ = ClientVerifier
    # Сигналы:
    new_message = pyqtSignal(dict)
    connection_lost = pyqtSignal()
    message_205 = pyqtSignal()

    def __init__(
            self,
            ip_address,
            port,
            account_name,
            password,
            database,
            key):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.account_name = account_name
        self.password = password
        self.logger = logging.getLogger('client')
        self.database = database
        self.key = key
        self.connect_server(ip_address, port)
        try:
            self.update_users()
            self.update_contacts()
        except (OSError, json.JSONDecodeError):
            self.logger.critical('Соединение разорвано.')
            raise Exception('Соединение разорвано!')
        self.running = True

    def connect_server(self, ip_address, port):
        """Устанавливает соединение с сервером."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        connection = False
        # Пять попыток подключения
        for _ in range(5):
            try:
                self.sock.connect((ip_address, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connection = True
                break
            time.sleep(1)

        if not connection:
            self.logger.critical('Не удалось подключиться к серверу.')
        self.logger.debug('Соединение установлено.')

        pass_bytes = self.password.encode('utf-8')
        salt = self.account_name.lower().encode('utf-8')
        pass_hash = hashlib.pbkdf2_hmac('sha256', pass_bytes, salt, 10000)
        pass_string = binascii.hexlify(pass_hash)

        # Публичный ключ
        pubkey = self.key.publickey().exportKey().decode('utf-8')

        # Авторизация
        with socket_lock:
            presence_msg = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.account_name,
                    PUBLIC_KEY: pubkey
                }
            }
            try:
                send_message(self.sock, presence_msg)
                answer = get_message(self.sock)
                if RESPONSE in answer:
                    if answer[RESPONSE] == 400:
                        raise Exception(answer[ERROR])
                    elif answer[RESPONSE] == 511:
                        data = answer[DATA].encode('utf-8')
                        hash = hmac.new(pass_string, data, 'sha256')
                        client_digest = hash.digest()
                        answer_of_client = {
                            RESPONSE: 511, DATA: binascii.b2a_base64(client_digest).decode('utf-8')}
                        send_message(self.sock, answer_of_client)
                        confirm = get_message(self.sock)
                        self.manage_message(confirm)
            except (OSError, json.JSONDecodeError):
                raise Exception('Ошибка авторизации.')

    def get_key(self, user):
        """Запрашивает публичный ключ."""
        self.logger.debug(f'Клиент {user} запросил публичный ключ.')
        request = {
            ACTION: GET_KEY,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_message(self.sock, request)
            answer = get_message(self.sock)
        if RESPONSE in answer and answer[RESPONSE] == 511:
            return answer[DATA]
        else:
            self.logger.error(f'Ключ для {user} не получен.')

    def manage_message(self, message):
        """Обрабатывает сообщения от сервера."""
        self.logger.debug(f'Обработка сообщения {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise Exception(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.update_users()
                self.update_contacts()
                self.message_205.emit()
            else:
                self.logger.error(f'Код {message[RESPONSE]} не определен.')

        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message and \
                message[DESTINATION] == self.account_name and MESSAGE_TEXT in message:
            self.logger.info(
                f'Клиентом {message[DESTINATION]} от клиента {message[SENDER]} '
                f'получено сообщение: {message[MESSAGE_TEXT]}')
            self.new_message.emit(message)

    def update_users(self):
        """Обновляет список пользователей."""
        self.logger.debug(
            f'Обновление списка пользователей клиентом {self.account_name}')
        request = {
            ACTION: UPDATE_USERS,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }
        with socket_lock:
            send_message(self.sock, request)
            answer = get_message(self.sock)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            self.database.add_users(answer[DATA_LIST])
        else:
            self.logger.error('Список пользователей не обновлен.')

    def update_contacts(self):
        """Обновляет список контактов."""
        self.logger.debug(
            f'Обновление списка контактов клиентом {self.account_name}')
        self.database.clear_contacts()
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }
        with socket_lock:
            send_message(self.sock, request)
            answer = get_message(self.sock)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            for contact in answer[CONTACTS_LIST]:
                self.database.add_contact(contact)
        else:
            self.logger.error('Список контактов не обновлен.')

    def add_contact(self, contact_name):
        """Отправляет запрос на добавление контакта."""
        self.logger.debug(f'Запрос на добавление контакта {contact_name}')
        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name,
            USER: contact_name
        }
        with socket_lock:
            send_message(self.sock, request)
            answer = get_message(self.sock)
            self.manage_message(answer)

    def remove_contact(self, contact_name):
        """Отправляет запрос на удаление контакта."""
        self.logger.debug(f'Запрос на удаление контакта {contact_name}')
        request = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name,
            USER: contact_name
        }
        with socket_lock:
            send_message(self.sock, request)
            answer = get_message(self.sock)
            self.manage_message(answer)

    def create_message(self, destination, message_text):
        """Отправляет сообщение для другого клиента."""
        self.logger.debug(
            f'Попытка отправить сообщение клиенту {destination}.')
        message = {
            ACTION: MESSAGE,
            TIME: time.time(),
            SENDER: self.account_name,
            DESTINATION: destination,
            MESSAGE_TEXT: message_text
        }
        with socket_lock:
            send_message(self.sock, message)
            answer = get_message(self.sock)
            self.manage_message(answer)
            self.logger.debug(
                f'Клиент {self.account_name} отправил сообщение клиенту {destination}.')

    def close_socket(self):
        """Отправляет сообщение о выходе клиента."""
        self.running = False
        request = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }
        with socket_lock:
            try:
                send_message(self.sock, request)
            except OSError:
                pass
        self.logger.debug(f'Клиент {self.account_name} завершил сеанс.')
        time.sleep(0.2)

    def run(self):
        """Основной цикл."""
        while self.running:
            time.sleep(1)
            message = None
            with socket_lock:
                try:
                    self.sock.settimeout(0.5)
                    message = get_message(self.sock)
                except (OSError, ConnectionError, ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError):
                    self.logger.critical('Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                finally:
                    self.sock.settimeout(5)
            if message:
                self.manage_message(message)
                self.logger.debug(f'Получено сообщение {message}.')


@Log(CLIENT_LOGGER)
def args_parser():
    """Парсер командной сроки."""
    parser = argparse.ArgumentParser(description='Аргументы командной строки')
    parser.add_argument('-a', default=DEFAULT_IP_ADDRESS, help='Адрес сервера')
    parser.add_argument(
        '-p',
        default=DEFAULT_PORT,
        type=int,
        help='Номер порта')
    parser.add_argument('-n', '--name', default=None, help='Имя клиента')
    parser.add_argument('--pswrd', default='', help='Пароль')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.a
    server_port = namespace.p
    account_name = namespace.name
    account_pass = namespace.pswrd

    if not 1024 <= server_port <= 65535:
        CLIENT_LOGGER.critical(
            f'Значение порта должно лежать в диапазоне 1024 - 65535.\n'
            f'Значение {server_port} вне допустимого диапазона!')
        sys.exit(1)
    return server_address, server_port, account_name, account_pass


if __name__ == '__main__':
    server_address, server_port, account_name, account_pass = args_parser()

    app = QApplication(sys.argv)

    start_dialog = StartDialog()
    if not account_name or not account_pass:
        app.exec_()
        if start_dialog.ok_pressed:
            account_name = start_dialog.account_name.text()
            account_pass = start_dialog.account_pass.text()
        else:
            sys.exit(0)

    CLIENT_LOGGER.info(f'Запуск клиента.\n'
                       f'Адрес сервера - {server_address}.'
                       f'Порт для подключения - {server_port}.'
                       f'Имя пользователя - {account_name}')

    # Загружаем ключи:
    key_path = os.getcwd()
    key_file = os.path.join(key_path, f'{account_name}.key')
    if not os.path.exists(key_file):
        key = RSA.generate(1024, os.urandom)
        with open(key_file, 'wb') as file:
            file.write(key.exportKey())
    else:
        with open(key_file, 'rb') as file:
            key = RSA.importKey(file.read())
    key.publickey().exportKey()

    # Создаем объект БД:
    database = ClientStorage(account_name)

    # Запускаем поток клиентского сокета:
    try:
        client_socket = Client(
            server_address,
            server_port,
            account_name,
            account_pass,
            database,
            key)
    except Exception:
        error_message = QMessageBox()
        error_message.critical(
            start_dialog,
            'Server error!',
            'Не удалось подключиться к серверу!')
        sys.exit(1)
    # Удаляем начальный диалог:
    del start_dialog

    client_socket.daemon = True
    client_socket.start()
    client_socket.join()

    # Запускаем основное окно:
    window = ClientMainWindow(client_socket, database, key)
    window.connect_slots(client_socket)
    app.exec_()

    # client_socket.close_socket()

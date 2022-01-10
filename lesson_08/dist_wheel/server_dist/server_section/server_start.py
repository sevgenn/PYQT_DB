"""Сервер."""

import binascii
import hmac
import select
import logging
import argparse
import socket
import threading
import configparser
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from common.utils import *
from common.variables import *
from common.decorators import Log, login_required
from common.metaclasses import ServerVerifier
from common.descriptors import Port
from server.storage_db import Storage
from server.server_window import ServerMainWindow
import logs.configs.config_log_server

SERVER_LOGGER = logging.getLogger('server')


class Server(threading.Thread):
    """Класс Сервер, обрабатывающий сообщения."""
    __metaclass__ = ServerVerifier
    listened_port = Port()

    def __init__(self, listened_address, listened_port, database):
        self.address = listened_address
        self.port = listened_port
        self.sock = None
        # Список клиентов:
        self.clients = []
        self.recv_list = []
        self.send_list = []
        self.err_list = []
        # Список отправляемых сообщений:
        self.messages = []
        # Словарь имя-сокет:
        self.names = dict()
        self.logger = logging.getLogger('server')
        self.database = database
        self.running = True
        super().__init__()

    def create_socket(self):
        """Создает сокет."""
        self.logger.info(
            f'Запущен сервер по адресу: {self.address} на порту: {self.port}.')
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.address, self.port))
        server_sock.settimeout(0.2)

        self.sock = server_sock
        self.sock.listen(MAX_CONNECTIONS)

    def run(self):
        """Запускает основной цикл сервера."""
        # Инициализируем сокет сервера:
        self.create_socket()
        # Запускаем цикл:
        while self.running:
            # Ждем подключения, пока не вышел таймаут:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                self.logger.info(f'Установлено соединение с {client_address}.')
                client.settimeout(5)
                self.clients.append(client)

            # Проверяем наличие ждущих клиентов:
            try:
                if self.clients:
                    self.recv_list, self.send_list, self.err_list = select.select(
                        self.clients, self.clients, [], 0)
            except OSError:
                pass
            # Принимаем сообщения от ждущих клиентов:
            if self.recv_list:
                for client_with_message in self.recv_list:
                    try:
                        message = get_message(client_with_message)
                        self.manage_message(message, client_with_message)
                    except ConnectionResetError:
                        self.logger.debug(f'Клиент {client_with_message.getpeername()} отключился от сервера')
                        self.remove_client(client_with_message)
                    except Exception as err:
                        self.logger.error(f'Ошибка при получении сообщения: {err}')
                        self.remove_client(client_with_message)

            for item in self.messages:
                try:
                    self.process_message(item)
                except Exception:
                    self.remove_client(self.names[item[DESTINATION]])
            self.messages.clear()

    def check_client_presence(self, message, client):
        """Обрабатывает сообщение о присутствии клиента PRESENCE."""
        client_name = message[USER][ACCOUNT_NAME]
        # Если имя занято:
        if client_name in self.names.keys():
            response = {RESPONSE: 400,
                        ERROR: 'Имя уже занято'}
            try:
                self.logger.debug('Попытка отправить сообщение клиенту, что имя занято')
                send_message(client, response)
            except OSError:
                self.logger.critical('Сообщение, что имя занято, не отправлено!')
                pass
            self.clients.remove(client)
            # client.close()
            return
        # Если не зарегистрирован:
        elif not self.database.check_user(client_name):
            response = {RESPONSE: 400,
                        ERROR: 'Пользователь не зарегистрирован'}
            try:
                self.logger.debug('Попытка отправить сообщение, что клиент не зарегистрирован')
                send_message(client, response)
            except OSError:
                self.logger.critical('Сообщение, что клиент не зарегистрирован, не отправлено!')
                pass
            self.clients.remove(client)
            # client.close()
            return
        # Авторизация:
        else:
            random_str = binascii.hexlify(os.urandom(64))
            response = {
                RESPONSE: 511,
                DATA: random_str.decode('utf-8')
            }
            hash = hmac.new(self.database.get_password(client_name), random_str, 'sha256')
            server_digest = hash.digest()
            try:
                send_message(client, response)
                # Ответ от клиента:
                answer = get_message(client)
            except OSError:
                self.logger.critical('Ошибка при авторизации!')
                self.clients.remove(client)
                # client.close()
                return
            client_digest = binascii.a2b_base64(answer[DATA])

            if RESPONSE in answer and answer[RESPONSE] == 511 and hmac.compare_digest(
                    server_digest, client_digest):
                self.names[client_name] = client
                client_ip, client_port = client.getpeername()
                try:
                    send_message(client, {RESPONSE: 200})
                except OSError:
                    self.remove_client(client_name)
                # Добавление в БД:
                self.database.login_user(
                    client_name,
                    client_ip,
                    client_port,
                    message[USER][PUBLIC_KEY])
            else:
                response = {RESPONSE: 400,
                            ERROR: 'Неверный пароль!'
                            }
                try:
                    send_message(client, response)
                except OSError:
                    pass
                self.clients.remove(client)
                # client.close()
                return

    def remove_client(self, client):
        """Удаляет клиента из списка клиентов."""
        # self.logger.debug(f'Клиент {client.getpeername()} отключился.')
        for name in self.names:
            if self.names[name] == client:
                # Регистрируем в базе выход клиента:
                self.database.logout_user(name)
                del self.names[name]
                break
        # Удаляем его из списка:
        if client in self.clients:
            self.clients.remove(client)
            self.recv_list.remove(client)
            client.close()

    @login_required
    def manage_message(self, message, client):
        """Обрабатывае входящие сообщения по параметру ACTION."""
        self.logger.debug(f'Разбор сообщения от клиента {client}: {message}.')
        # Проверяем регистрацию клиента:
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            self.check_client_presence(message, client)
        # Обрабатываем собственно сообщения:
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
        # Обрабатываем запрос на выход:
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message and self.names[
                message[ACCOUNT_NAME]] == client:
            self.remove_client(client)
        # Обрабатываем запрос списка контактов:
        elif ACTION in message and message[ACTION] == GET_CONTACTS and ACCOUNT_NAME in message:
            response = {
                RESPONSE: 202,
                CONTACTS_LIST: self.database.get_user_contacts(message[ACCOUNT_NAME])
            }
            try:
                self.logger.debug('Попытка отправить клиенту список контактов')
                send_message(client, response)
            except OSError:
                self.logger.critical('Попытка отправить клиенту список контактов не удалась!')
                self.remove_client(client)
        # Обрабатываем добавление контакта:
        elif ACTION in message and message[ACTION] == ADD_CONTACT and USER in message and ACCOUNT_NAME in message:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            try:
                self.logger.debug('Попытка отправить сообщение о добавлении контакта')
                send_message(client, {RESPONSE: 200})
            except OSError:
                self.logger.critical('Попытка отправить сообщение о добавлении контакта не удалась!')
                self.remove_client(client)
        # Обрабатываем удаление контакта:
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and USER in message and ACCOUNT_NAME in message:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            try:
                self.logger.debug('Попытка отправить сообщение об удалении контакта')
                send_message(client, {RESPONSE: 200})
            except OSError:
                self.logger.critical('Попытка отправить сообщение об удалении контакта не удалась!')
                self.remove_client(client)
        # Обрабатываем запрос списка клиентов:
        elif ACTION in message and message[ACTION] == UPDATE_USERS and ACCOUNT_NAME in message:
            users_list = []
            for user in self.database.get_users_list():
                users_list.append(user[0])
            response = {
                RESPONSE: 202,
                DATA_LIST: users_list
            }
            try:
                self.logger.debug('Попытка отправить список пользователей')
                send_message(client, response)
            except OSError:
                self.logger.critical('Попытка отправить список пользователей не удалась!')
                self.remove_client(client)
        # Обрабатываем запрос публичного ключа:
        elif ACTION in message and message[ACTION] == GET_KEY and ACCOUNT_NAME in message:
            key = self.database.get_pubkey(message[ACCOUNT_NAME])
            # Если ключ есть:
            if key:
                response = {
                    RESPONSE: 511,
                    DATA: key
                }
                try:
                    self.logger.debug('Попытка отправить контакту pubkey')
                    send_message(client, response)
                except OSError:
                    self.logger.critical('Попытка отправить контакту pubkey не удалась!')
                    self.remove_client(client)
            # Если ключа нет:
            else:
                response = {
                    RESPONSE: 400,
                    ERROR: 'У клиента нет публичного ключа.'
                }
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)
        else:
            response = {
                RESPONSE: 400,
                ERROR: 'Некорректный запрос.'
            }
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

    def process_message(self, message):
        """Отправляет сообщения из списка получателям."""
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]
                                                             ] in self.send_list:
            try:
                # Заисываем в базу:
                send_message(self.names[message[DESTINATION]], message)
                # Заисываем в базу:
                self.database.save_message(
                    message[SENDER],
                    message[DESTINATION],
                    message[MESSAGE_TEXT])
                self.logger.info(
                    f'Отправлено сообщение клиенту {message[DESTINATION]} от клиента {message[SENDER]}.')
            except OSError:
                print('error')
                self.remove_client(self.names[message[DESTINATION]])
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in self.send_list:
            self.logger.error(
                f'Клиент {message[DESTINATION]} отключился. Отправка невозможна.')
            self.remove_client(self.names[message[DESTINATION]])
        else:
            self.logger.error(
                f'Клиент {message[DESTINATION]} не зарегистрирован. Отправка невозможна.')

    def update_data(self):
        """Формирует сообщение об обновлении данных."""
        for client in self.names:
            try:
                send_message(self.names[client], {RESPONSE: 205})
            except OSError:
                self.remove_client(self.names[client])


@Log(SERVER_LOGGER)
def args_parser(default_address, default_port):
    """Парсер командной сроки"""
    parser = argparse.ArgumentParser(description='Аргументы командной строки')
    parser.add_argument('-a', default=default_address, help='Адрес сервера')
    parser.add_argument(
        '-p',
        default=default_port,
        type=int,
        help='Номер порта')
    namespace = parser.parse_args(sys.argv[1:])
    listened_address = namespace.a
    listened_port = namespace.p
    return listened_address, listened_port


@Log(SERVER_LOGGER)
def load_config():
    """Парсер .ini файла."""
    config = configparser.ConfigParser()
    dir_path = os.getcwd()
    config_file = f'{dir_path}/server.ini'
    config.read(config_file)
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'default_address', '')
        config.set('SETTINGS', 'default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'database_path', '')
        config.set('SETTINGS', 'database_file', 'server_db.db3')
        return config


def main():
    """Создает экземпляр сервера и запускает основной цикл."""
    print('[Server started...]')
    config = load_config()
    listened_address, listened_port = args_parser(
        config['SETTINGS']['default_address'], config['SETTINGS']['default_port'])
    # База данных:
    db_path = os.path.join(
        config['SETTINGS']['database_path'],
        config['SETTINGS']['database_file'])
    database = Storage(db_path)
    # Все клиенты при запуске сервера неактивны:
    database.deactivate_users()
    # Запуск сервера:
    server = Server(listened_address, listened_port, database)
    server.daemon = True
    server.start()

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    window = ServerMainWindow(server, database, config)
    window.statusBar().showMessage('[Server started...]')
    app.exec_()
    # server.running = False


if __name__ == '__main__':
    main()

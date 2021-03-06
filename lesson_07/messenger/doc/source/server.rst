Server module
=================================================

Серверный модуль мессенджера. Обрабатывает словари - сообщения, хранит публичные ключи клиентов.

Использование

Модуль подерживает аргементы командной стороки:

1. -a - Адрес с которого принимаются соединения.
2. -p - Порт на котором принимаются соединения

Примеры использования:

``python server.py -p 7777``

*Запуск сервера на порту 7777*

``python server.py -a localhost``

*Запуск сервера принимающего только соединения с localhost*

server_start.py
~~~~~~~~~~~~~~~

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

server. **arg_parser** ()
    Парсер аргументов командной строки, возвращает кортеж из 3 элементов:

	* адрес с которого принимать соединения
	* порт

server. **load_config** ()
    Функция загрузки параметров конфигурации из .ini файла.
    В случае отсутствия файла задаются параметры по умолчанию.

storage_db.py
~~~~~~~~~~~~~

.. autoclass:: server.storage_db.Storage
	:members:

server_window.py
~~~~~~~~~~~~~~~~

.. autoclass:: server.server_window.ServerMainWindow
	:members:
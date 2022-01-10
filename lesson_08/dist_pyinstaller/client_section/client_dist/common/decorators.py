"""Декораторы."""

import inspect
import socket
import sys
import traceback

sys.path.append('../')


class Log:
    """Класс-декоратор"""

    def __init__(self, logger):
        """Назначение соответствующего loggera."""
        self.logger = logger

    def __call__(self, func_to_log):
        def log_saver(*args, **kwargs):
            """Обертка"""
            res = func_to_log(*args, **kwargs)
            self.logger.debug(
                f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
                f'Вызов из модуля {func_to_log.__module__}. Вызов из'
                f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                f'Вызов из функции {inspect.stack()[1][3]}')
            return res

        return log_saver


def login_required(func):
    """Проверяет, что клиент авторизован."""

    def checker(*args, **kwargs):
        from server_start import Server
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], Server):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker

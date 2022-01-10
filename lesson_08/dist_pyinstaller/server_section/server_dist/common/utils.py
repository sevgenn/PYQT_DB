"""Утилиты."""

import json
import logging
import sys
# from builtins import function
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from common.decorators import Log

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


# if function.__module__ == 'client.py':
#     LOGGER = logging.getLogger('client')
# else:
#     LOGGER = logging.getLogger('server')

@Log(LOGGER)
def get_message(sock):
    """Принимает байты и декодирует в словарь."""
    encoded_response = sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        response = json.loads(encoded_response.decode(ENCODING))
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@Log(LOGGER)
def send_message(sock, message):
    """Кодирует словарь и отправляет его."""
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)

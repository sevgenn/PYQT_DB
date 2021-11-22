"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping
будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел
должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес
сетевого узла должен создаваться с помощью функции ip_address().
"""


from sys import platform
from ipaddress import ip_network
from subprocess import Popen, DEVNULL
import socket
from loguru import logger
import timeit


def get_hosts_list(net):
    """Возвращает список хостов по адресу сети в формате '127.0.0.1/24'."""
    subnet = ip_network(net)
    return list(subnet.hosts())


def validate_hostname(hostname):
    """
    Принимает адрес хоста или имя хоста в формате ipaddress или string.
    Возвращает ip-адрес в формате string или False в случае некорректного имени.
    """
    try:
        host = socket.gethostbyname(hostname)
        return host
    except socket.gaierror:
        return False


def host_ping(hosts_list, requests_number='1'):
    """Проверяет список адресов на доступность с помощью утилиты ping. Выводит соответствующие списки."""
    reachable_list = []
    unreachable_list = []
    incorrect_list = []
    key = '-c'
    if platform == 'win32':
        key = '-n'

    for address in hosts_list:
        host = validate_hostname(str(address))
        if not host:
            logger.error(f'Incorrect host-name or ip-address <{address}> in list.')
            incorrect_list.append(str(address))
            continue

        print(f'Waiting for ping of address {host}')
        args = ['ping', key, requests_number, str(host)]
        proc = Popen(args, stdout=DEVNULL)
        proc.wait()
        if proc.returncode == 0:
            print(f'Host {host} is reachable.')
            reachable_list.append(host)
        else:
            print(f'Host {host} is not reachable.')
            unreachable_list.append(host)
    print('\nThe list of reachable hosts:')
    print(reachable_list)
    print('The list of unreachable hosts:')
    print(unreachable_list)
    print('The list of incorrect hosts:')
    print(incorrect_list)


if __name__ == '__main__':
    start = timeit.default_timer()
    # Список адресов в сети:
    hosts_list = get_hosts_list('192.168.0.0/29')
    # Добавление адресов в список:
    hosts_list.extend(['gogle.co', '127.0.0.1', '256.0.0.3', 'ya.ru'])

    host_ping(hosts_list)

    print(timeit.default_timer() - start)

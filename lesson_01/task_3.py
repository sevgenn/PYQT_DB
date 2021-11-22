"""
Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
"""


from ipaddress import ip_address, IPv4Address, IPv6Address
from loguru import logger
import subprocess
from subprocess import Popen, DEVNULL
from sys import platform
from tabulate import tabulate
from itertools import repeat


def validate_address(address):
    if not type(address) in (IPv4Address, IPv6Address):
        try:
            host = ip_address(address)
        except ValueError as err:
            logger.error(err)
            return False
    return host


def host_ping(hosts_list, requests_number='2'):
    """Проверяет список адресов на доступность с помощью утилиты ping. Выводит соответствующие списки."""
    reachable_list = []
    unreachable_list = []
    # Выбор параметров в зависимости от ОС:
    key = '-c'
    pattern = b'ttl'
    if platform == 'win32':
        key = '-n'
        pattern = b'TTL'

    for host in hosts_list:
        print(f'\nWaiting for ping of address {host}')
        args = ['ping', key, requests_number, str(host)]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE).stdout.read()
        if pattern in proc:
            print(f'Host {host} is reachable.')
            reachable_list.append(host)
        else:
            print(f'Host {host} is not reachable.')
            unreachable_list.append(host)
    return reachable_list, unreachable_list


def get_table(data):
    header = ['Address', 'Ping']
    reachable_list = list(zip(data[0], repeat('Yes')))
    unreachable_list = list(zip(data[1], repeat('No')))
    result = reachable_list + unreachable_list
    print(tabulate(result, headers=header, tablefmt='pretty'))


def host_range_ping_tab(range_list):
    hosts_list = []
    for item in range_list:
        if '-' in item:
            hosts = item.split('-')
            start_host = validate_address(hosts[0])
            if not start_host:
                continue
            prefix = hosts[0].split('.')[:-1]

            end_host = validate_address(hosts[1])
            if not end_host:
                prefix.append(hosts[1])
                end_host = '.'.join(prefix)
                end_host = validate_address(end_host)
        else:
            start_host = end_host = validate_address(item)
            if not start_host:
                continue

        result_list = [str(ip_address(elem)) for elem in range(int(start_host), int(end_host)+1)]
        logger.debug(f'result_list: {result_list}')
        hosts_list.extend(result_list)
        logger.debug(f'hosts_list: {hosts_list}')
    result = host_ping(hosts_list)
    get_table(result)



if __name__ == '__main__':
    example_list = ['192.168.0.1-2', '8.8.8.7-8.8.8.8', '127.0.0.1']
    host_range_ping_tab(example_list)

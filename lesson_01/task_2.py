"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
# ['192.168.0.1-3', '8.8.8.5-8.8.8.8', '127.0.0.1']


from ipaddress import ip_address, IPv4Address, IPv6Address
from loguru import logger
from subprocess import Popen, DEVNULL
from sys import platform


def validate_address(address):
    if not type(address) in (IPv4Address, IPv6Address):
        try:
            host = ip_address(address)
        except ValueError as err:
            logger.error(err)
            return False
    return host


def host_ping(hosts_list, requests_number='1'):
    """Проверяет список адресов на доступность с помощью утилиты ping. Выводит соответствующие списки."""
    reachable_list = []
    unreachable_list = []
    key = '-c'
    if platform == 'win32':
        key = '-n'

    for host in hosts_list:
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
    return reachable_list, unreachable_list


def host_range_ping(range_list):
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
    print(f'\nThe list of reachable hosts: \n{result[0]}'
          f'\nThe list of unreachable hosts: \n{result[1]}')



if __name__ == '__main__':
    example_list = ['192.168.0.1-3', '8.8.8.5-8.8.8.8', '127.0.0.1']
    host_range_ping(example_list)

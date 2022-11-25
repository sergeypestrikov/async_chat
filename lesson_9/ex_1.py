# Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность
# сетевых узлов. Аргументом функции является список, в котором каждый сетевой узел должен быть представлен
# именем хоста или ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом
# соответствующего сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться
# с помощью функции ip_address().

from ipaddress import ip_address
from lesson_3.sub_file import Popen, PIPE


def host_ping(list_ip_addresses, timeout=500, request=1):
    result = {'Узлы доступны': '', 'Узлы недоступны': ''}
    for ip in list_ip_addresses:
        try:
            ip = ip_address(ip)
        except ValueError:
            pass
        process = Popen(f'ping {ip} -i {timeout} -n {request}', shell=True, stdout=PIPE)
        process.wait()

        if process.returncode == 0:
            result['Узлы доступны'] += f'{str(ip)}'
            responsible = f'{ip} - узел доступен'
        else:
            result['Узлы недоступны'] += f'{str(ip)}'
            responsible = f'{ip} - узел недоступен'
        print(responsible)
    print(result)


if __name__ == '__main__':
    ip_addresses = ['mail.ru', '1.1.1.1', '217.69.128.44']
    host_ping(ip_addresses)
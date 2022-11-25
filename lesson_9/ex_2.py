# Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
# Меняться должен только последний октет каждого адреса.
# По результатам проверки должно выводиться соответствующее сообщение.

from ipaddress import ip_address
from lesson_9.ex_1 import host_ping


def host_range_ping():
    while True:
        first_ip = input('Введите первый ip адрес: ')
        try:
            last_octet = int(first_ip.split('.')[3])
            break
        except Exception as expt:
            print(expt)
    while True:
        last_ip = input('Кол-во проверяемых адресов: ')
        if not last_ip.isnumeric():
            print('Число введите: ')
        else:
            if (last_octet + int(last_ip)) > 254:
                print(f'По условию должен меняться только последний октет. Макс число хостов {254 - last_octet}')
            else:
                break

    host_list = []
    [host_list.append(str(ip_address(first_ip) + ip)) for ip in range(int(last_ip))]
    return host_ping(host_list)


if __name__ == '__main__':
    host_range_ping()
import sys
import argparse

from variables import *
from wrapper import log
from errors import ServerError
from transport import ClientTransport
from database import ClientDataBase
from start_dialog import UserNameDialog
from main_window import MainClientWindow

from PyQt6.QtWidgets import QApplication


# CLIENT_LOG = logging.getLogger('client_log')
logger = logging.getLogger('client')


@log
def arg_parser():
    '''
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов
    адрес сервера, порт, имя пользователя, пароль.
    Выполняет проверку на корректность номера порта
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # Проверка номера порта
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимые адреса с 1024 до 65535. Клиент завершается')
        sys.exit(1)

    return server_address, server_port, client_name

# Основная функция клиента
if __name__ == '__main__':
    # Загрузка командной строки
    server_address, server_port, client_name = arg_parser()
    # Создание клиентского приложения
    client_app = QApplication(sys.argv)
    # Если имя пользователя не было указано в командной строке, то запросим его
    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект, иначе выход
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            sys.exit(0)

    # Запись в лог
    logger.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address}, порт: {server_port}, имя пользователя: {client_name}')

    # Создание объекта БД
    database = ClientDataBase(client_name)

    # Создание объекта - транспорт + запуск транспортного потока
    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        sys.exit(1)

    transport.setDaemon(True)
    transport.start()

    # Создание GUI
    main_window = MainClientWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Программа myChat - {client_name}')
    client_app.exec()

    # Если графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
import socket
import sys
import os
import argparse
import select
import threading
import configparser

import database
import log.server_log_config
from common.variables import *
from common.utils import get_msg, send_msg
from server.core import ProcessorMSG
from server.main_winwow import MainWindow
from common.wrapper import log
from common.metaclasses import ServerVerifier
from common.descriptor import Port, logger
from server.server_data_base import ServerStorage

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from server_gui import MainWindow, gui_model, HistoryWindow, create_msg_history_model, ConfigWindow


logger = logging.getLogger('server')

# new_connection = False
# conflag_lock = threading.Lock()


@log
def arg_parser(default_port, default_address):
    '''Парсер аргументов командной строки'''
    logger.debug(f'Инициализация парсера командной строки: {sys.argv}')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    logger.debug('Аргументы загружены')
    return listen_address, listen_port, gui_flag


@log
def config_load():
    '''Парсер конфигурационного файла ini'''
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по умолчанию
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


@log
def main():
    '''Основная функция'''
    # Загрузка файла конфигурации сервера
    config = config_load()
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умолчанию
    listen_address, listen_port, gui_flag = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])
    # Инициализация базы данных
    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))
    # создание экземпляра класса - сервера и его запуск:
    server = ProcessorMSG(listen_address, listen_port, database)
    server.daemon = True
    server.start()
    # если указан параметр без GUI, то запускаем простенький обработчик консольного ввода
    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера')
            if command == 'exit':
                # если выход, то завершаем основной цикл сервера.
                server.running = False
                server.join()
                break
    # Если не указан запуск без GUI, то запускаем GUI
    else:
        # Создаём графическое окружение для сервера
        server_app = QApplication(sys.argv)
        # server_app.setAttribute(Qt.WindowType.WindowContextHelpButtonHint)
        main_window = MainWindow() # database, server, config

        # Запуск GUI
        server_app.exec()

        # По закрытию окон останавливаем обработчик сообщений
        server.running = False


if __name__ == '__main__':
    main()
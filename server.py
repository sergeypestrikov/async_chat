import socket
import sys
import os
import argparse
import select
import threading
import configparser
import log.server_log_config

import database
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


# Парсер аргументов командной строки.
@log
def arg_parser(default_port, default_address):
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

# парсер файла ini
@log
def config_load():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    # если конфиг файл загружен правильно, запускаемся, иначе конфиг по умолчанию.
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config

# основная функция
@log
def main():
    # загрузка файла конфигурации сервера
    config = config_load()
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию
    listen_address, listen_port, gui_flag = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])
    # инициализация базы данных
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
    # если не указан запуск без GUI, то запускаем GUI
    else:
        # создаём графическое окружение для сервера
        server_app = QApplication(sys.argv)
        # server_app.setAttribute(Qt.WindowType.WindowContextHelpButtonHint)
        main_window = MainWindow() # database, server, config

        # запуск GUI
        server_app.exec()

        # по закрытию окон останавливаем обработчик сообщений
        server.running = False


if __name__ == '__main__':
    main()

# #основной класс сервера
# class Server(metaclass=ServerVerifier):
#     port = Port()
#
#     def __init__(self, listen_address, listen_port):
#         #параметры подключения
#         self.address = listen_address
#         self.port = listen_port
#         #БД Сервера
#         self.database = database
#         #список подключенных клиентов
#         self.clients = []
#         #список сообщений к отправке
#         self.messages = []
#         #словарь с именами и сокетами
#         self.names = dict()
#
#     def init_socket(self):
#         logger.info(f'Сервер запущен. Порт {self.port}, адрес с которого принимаются подключения {self.address}, если адрес не указан принимаются соединения слюбых адресов')
#         #готовим сокет
#         transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         transport.bind((self.address, self.port))
#         transport.settimeout(0.5)
#         #слушаем сокет
#         self.sock = transport
#         self.sock.listen()
#
#     def main_loop(self):
#         self.init_socket() #инициализируем сокет
#
#         while True:
#             try:
#                 client, client_address = self.sock.accept()
#             except OSError:
#                 pass
#             else:
#                 logger.info(f'Соединение установлено с ПК {client_address}')
#                 self.clients.append(client)
#
#             recv_data_list = []
#             send_data_list = []
#             error_list = []
#             #проверяем ожидающих клиентов
#             try:
#                 if self.clients:
#                     recv_data_list, send_data_list, error_list = select.select(self.clients, self.clients, [], 0)
#             except OSError:
#                 pass
#             #принимаем сообщение, а при ошибке исключаем клиента
#             if recv_data_list:
#                 for client_with_msg in recv_data_list:
#                     try:
#                         self.process_client_msg(get_msg(client_with_msg), client_with_msg)
#                     except:
#                         logger.info(f'Клиент {client_with_msg.getpeername()} отключился от сервера')
#                         self.clients.remove(client_with_msg)
#             #если есть сообщения, тогда обрабатываем
#             for message in self.messages:
#                 try:
#                     self.process_msg(message, send_data_list)
#                 except:
#                     logger.info(f'Связь с клиентом по имени {message[DESTINATION]} была потеряна')
#                     self.clients.remove(self.names[message[DESTINATION]])
#                     del self.names[message[DESTINATION]]
#             self.messages.clear()
#
# #функция адресной отправки сообщения клиенту. Принимает словарь, список пользователей и слушащие сокеты.
# def process_msg(self, message, listen_socks):
#     if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
#         send_msg(self.names[message[DESTINATION]], message)
#         logger.info(f'Пользователю отправлено сообщение {message[DESTINATION]} от пользователя {message[SENDER]}')
#     elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
#         raise ConnectionError
#     else:
#         logger.error(f'Пользователь {message[DESTINATION]} не зарегистрирован, отправка сообщения невозможна')
#
# #обработчик сообщений от клиентов принимает словарь - сообщение, проверяет корректность, отправляет ответ
# def process_client_msg(self, message, client):
#     logger.debug(f'Проверка сообщения от клиента {message}')
#     #если сообщение о присутствии отвечаем
#     if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
#     #если пользователь не зарегистрирован регистрируем или завершаем соединение
#         if message[USER][ACCOUNT_NAME] not in self.names.keys():
#             self.names[message[USER][ACCOUNT_NAME]] = client
#             send_msg(client, RESPONSE_200)
#         else:
#             response = RESPONSE_400
#             response[ERROR] = 'Такое имя уже занято'
#             send_msg(client, response)
#             self.clients.remove(client)
#             client.close()
#         return
#     #если это сообщение, то добавляем его в очередь сообщений
#     elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
#         and SENDER in message and MESSAGE_TXT in message:
#         self.message.append(message)
#         return
#     #если клиент выходит
#     elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
#         self.clients.remove(self.names[ACCOUNT_NAME])
#         self.names[ACCOUNT_NAME].close()
#         del self.names[ACCOUNT_NAME]
#         with conflag_lock:
#             new_connection = True
#         return
#     #если это запрос контакт-листа
#     elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
#              self.names[message[USER]] == client:
#         response = RESPONSE_202
#         response[LIST_INFO] = self.database.get_contacts(message[USER])
#         send_msg(client, response)
#     #если добавление контакта
#     elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
#             and self.names[message[USER]] == client:
#         self.database.add_contact(message[USER], message[ACCOUNT_NAME])
#         send_msg(client, RESPONSE_200)
#     #если удаление контакта
#     elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and USER in message \
#             and self.names[message[USER]] == client:
#         self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
#         send_msg(client, RESPONSE_200)
#     #если запрос известных пользователей
#     elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
#             and self.names[message[ACCOUNT_NAME]] == client:
#         response = RESPONSE_202
#         response[LIST_INFO] = [user[0]
#                                for user in self.database.users_list()]
#         send_msg(client, response)
#     #иначе ждет bad request
#     else:
#         response = RESPONSE_400
#         response[ERROR] = 'Некорректный запрос'
#         send_msg(client, response)
#         return
#
#
# def main():
#     #загрузка файла конфигурации сервера
#     config = configparser.ConfigParser()
#
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     config.read(f"{dir_path}/{'server.ini'}")
#
#     #загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
#     listen_address, listen_port = arg_parser(
#         config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])
#
#     #инициализация базы данных
#     database = ServerStorage(
#         os.path.join(
#             config['SETTINGS']['Database_path'],
#             config['SETTINGS']['Database_file']))
#
#     #создание экземпляра класса - сервера и его запуск:
#     server = Server(listen_address, listen_port, database)
#     server.daemon = True
#     server.start()
#
#     #создание графического окуружение для сервера:
#     server_app = QApplication(sys.argv)
#     main_window = MainWindow()
#
#     #инициализация параметров в окна
#     main_window.statusBar().showMessage('Server Working')
#     main_window.active_clients_table.setModel(gui_model(database))
#     main_window.active_clients_table.resizeColumnsToContents()
#     main_window.active_clients_table.resizeRowsToContents()
#
#     #обновление списка подключённых, проверка флага подключения, если надо обновление списка
#     def list_update():
#         global new_connection
#         if new_connection:
#             main_window.active_clients_table.setModel(
#                 gui_model(database))
#             main_window.active_clients_table.resizeColumnsToContents()
#             main_window.active_clients_table.resizeRowsToContents()
#             with conflag_lock:
#                 new_connection = False
#
#     #создание окна со статистикой клиентов
#     def show_statistics():
#         global stat_window
#         stat_window = HistoryWindow()
#         stat_window.history_table.setModel(create_msg_history_model(database))
#         stat_window.history_table.resizeColumnsToContents()
#         stat_window.history_table.resizeRowsToContents()
#         stat_window.show()
#
#     #создание окна с настройками сервера.
#     def server_config():
#         global config_window
#         #создание окна и внесение в него текущих параметров
#         config_window = ConfigWindow()
#         config_window.db_path.insert(config['SETTINGS']['Database_path'])
#         config_window.db_file.insert(config['SETTINGS']['Database_file'])
#         config_window.port.insert(config['SETTINGS']['Default_port'])
#         config_window.ip.insert(config['SETTINGS']['Listen_Address'])
#         config_window.save_btn.clicked.connect(save_server_config)
#
#     #сохранение настроек
#     def save_server_config():
#         global config_window
#         message = QMessageBox()
#         config['SETTINGS']['Database_path'] = config_window.db_path.text()
#         config['SETTINGS']['Database_file'] = config_window.db_file.text()
#         try:
#             port = int(config_window.port.text())
#         except ValueError:
#             message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
#         else:
#             config['SETTINGS']['Listen_Address'] = config_window.ip.text()
#             if 1023 < port < 65536:
#                 config['SETTINGS']['Default_port'] = str(port)
#                 print(port)
#                 with open('server.ini', 'w') as conf:
#                     config.write(conf)
#                     message.information(
#                         config_window, 'OK', 'Настройки успешно сохранены!')
#             else:
#                 message.warning(
#                     config_window,
#                     'Ошибка',
#                     'Порт должен быть от 1024 до 65536')
#
#     #таймер, обновляющий список клиентов 1 раз в секунду
#     timer = QTimer()
#     timer.timeout.connect(list_update)
#     timer.start(1000)
#
#     #связь кнопки с процедурами
#     main_window.refresh_button.triggered.connect(list_update)
#     main_window.show_history_button.triggered.connect(show_statistics)
#     main_window.config_btn.triggered.connect(server_config)
#
#     #запуск GUI
#     server_app.exec()
#
#
# if __name__ == '__main__':
#     main()
#
#
# def core():
#     return None
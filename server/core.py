import threading
import logging
import select
import socket
import json
import hmac
import binascii
import os

from common.metaclasses import ServerVerifier
from common.descriptor import Port
from common.variables import *
from common.utils import send_msg, get_msg
from common.wrapper import login_required

logger = logging.getLogger('server')


class ProcessorMSG(threading.Thread):
    '''
    Основной класс сервера. Принимает соединения, словари - пакеты
    от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока.
    '''
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        # Параметры подключения
        self.address = listen_address
        self.port = listen_port
        # БД сервера
        self.database = database
        # Сокет для работы
        self.sock = None
        # Список подключенных клиентов
        self.clients = []
        # Сокеты
        self.listen_sock = None
        self.error_sock = None
        # Флаг продолжения работы
        self.running = True
        # Словарь с именами и соответствующими сокетами
        self.names = dict()
        # Конструктор предка
        super().__init__()

    def run(self):
        '''Метод - основной цикл потока'''
        self.init_socket()
        # Основной цикл программы сервеера
        while self.running:
            # Ждем подключения
            try:
                client, client_address = self.sock.accept()
            # Либо исключения, если тайм аут вышел
            except OSError:
                pass
            else:
                logger.info(f'Установлено соединение с {client_address}')
                client.settimeout(5)
                self.clients.append(client)

            recv_data_list = []
            send_data_list = []
            error_list = []
            # Проверка наличия ожидающих клиентов
            try:
                if self.clients:
                    recv_data_list, self.listen_sock, self.error_sock = select.select(self.clients, self.clients, [], 0)
            except OSError as err:
                logger.error(f'Ошибка работы с сокетами: {err.errno}')
            # Прием сообщений и если ошибка удаление клиента
            if recv_data_list:
                for client_with_msg in recv_data_list:
                    try:
                        self.process_client_msg(get_msg(client_with_msg), client_with_msg)
                    except (OSError, json.JSONDecodeError, TypeError) as err:
                        logger.debug(f'Получение данных из клиентского исключения', exc_info=err)
                        self.remove_client(client_with_msg)

    def remove_client(self, client):
        '''
        Метод обработчик клиента с которым прервана связь.
        Ищет клиента и удаляет его из списков и базы
        '''
        logger.info(f'Клиент {client.getpeername()} отключился от сервера')
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
            self.clients.remove(client)
            client.close()

    def init_socket(self):
        '''Метод - инициализатор сокета'''
        logger.info(f'Запущен сервер. Порт для подключений: {self.port} , адрес с которого принимаются подключения: {self.address}. Если адрес не указан, принимаются соединения с любых адресов')
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)
        # Начинаем слушать сокет
        self.sock = transport
        self.sock.listen(MAX_CONNECTION)

    def process_msg(self, message):
        '''Метод отправки сообщения клиенту'''
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]
        ] in self.listen_sock:
            try:
                send_msg(self.names[message[DESTINATION]], message)
                logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}')
            except OSError:
                self.remove_client(message[DESTINATION])
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in self.listen_sockets:
            logger.error(f'Связь с клиентом {message[DESTINATION]} потеряна. Соединение закрыто')
            self.remove_client(self.names[message[DESTINATION]])
        else:
            logger.error(f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна')

        @login_required
        def process_client_msg(self, message, client):
            '''Метод - обработчик входящих сообщений'''
            logger.debug(f'Разбор сообщения от клиента : {message}')
            # Если это сообщение об присутствии, принимаем и отвечаем
            if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
                # А если сообщение о присутствии то вызываем функцию авторизации
                self.autorize_user(message, client)
            # И если это сообщение, то отправляем его получателю.
            elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                    and SENDER in message and MESSAGE_TXT in message and self.names[message[SENDER]] == client:
                if message[DESTINATION] in self.names:
                    self.database.process_message(
                        message[SENDER], message[DESTINATION])
                    self.process_message(message)
                    try:
                        send_msg(client, RESPONSE_200)
                    except OSError:
                        self.remove_client(client)
                else:
                    response = RESPONSE_400
                    response[ERROR] = 'Пользователь не зарегистрирован на сервере'
                    try:
                        send_msg(client, response)
                    except OSError:
                        pass
                return
            # Если клиент выходит
            elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                     and self.names[message[ACCOUNT_NAME]] == client:
                self.remove_client(client)
            # А если это запрос контакт-листа
            elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                    self.names[message[USER]] == client:
                response = RESPONSE_202
                response[LIST_INFO] = self.database.get_contacts(message[USER])
                try:
                    send_msg(client, response)
                except OSError:
                    self.remove_client(client)
            # И если это добавление контакта
            elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                         and self.names[message[USER]] == client:
                self.database.add_contact(message[USER], message[ACCOUNT_NAME])
                try:
                    send_msg(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            # Еще если это удаление контакта
            elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and USER in message \
                         and self.names[message[USER]] == client:
                self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
                try:
                    send_msg(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            # А так же если запрос известных пользователей
            elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                        and self.names[message[ACCOUNT_NAME]] == client:
                response = RESPONSE_202
                response[LIST_INFO] = [user[0] for user in self.database.users_list()]
                try:
                    send_msg(client, response)
                except OSError:
                    self.remove_client(client)
            # Ну и если запрос публичного ключа пользователя
            elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and ACCOUNT_NAME in message:
                response = RESPONSE_511
                response[DATA] = self.database.get_pubkey(message[ACCOUNT_NAME])
                # Может быть, что ключа ещё нет (пользователь никогда не логинился, тогда выдаем 400)
                if response[DATA]:
                    try:
                        send_msg(client, response)
                    except OSError:
                        self.remove_client(client)
                else:
                    response = RESPONSE_400
                    response[ERROR] = 'Нет публичного ключа для данного пользователя'
                    try:
                        send_msg(client, response)
                    except OSError:
                        self.remove_client(client)

    def autorize_user(self, message, sock):
        '''Метод реализующий авторизцию пользователей'''
        logger.debug(f'Авторизация начата для {message[USER]}')
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'Такое имя пользователя занято'
            try:
                logger.debug(f'Имя занято {response}')
                send_msg(sock, response)
            except OSError:
                logger.debug('OS Error')
                pass
            self.clients.remove(sock)
            sock.close()
        # Проверяем что пользователь зарегистрирован на сервере
        elif not self.database.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'Пользователь не зарегистрирован'
            try:
                logger.debug(f'Unknown username, sending {response}')
                send_msg(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            logger.debug('Имя корректное. Проверяем пароль')
            # Иначе отвечаем 511 и проводим процедуру авторизации
            # Словарь - заготовка
            message_auth = RESPONSE_511
            # Набор байтов в hex представлении
            random_str = binascii.hexlify(os.urandom(64))
            # В словарь байты нельзя => декодируем (json.dumps => TypeError)
            message_auth[DATA] = random_str.decode('ascii')
            # Создаём хэш пароля и связки с рандомной строкой, сохраняем серверную версию ключа
            hash = hmac.new(self.database.get_hash(message[USER][ACCOUNT_NAME]), random_str, 'MD5')
            digest = hash.digest()
            logger.debug(f'Auth message = {message_auth}')
            try:
                # Обмен с клиентом
                send_msg(sock, message_auth)
                ans = get_msg(sock)
            except OSError as err:
                logger.debug('Error in auth, data:', exc_info=err)
                sock.close()
                return
            client_digest = binascii.a2b_base64(ans[DATA])
            # Если ответ клиента корректный, то сохраняем его в список пользователей.
            if RESPONSE in ans and ans[RESPONSE] == 511 and hmac.compare_digest(digest, client_digest):
                self.names[message[USER][ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    send_msg(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])
                # Добавляем пользователя в список активных и если у него изменился открытый ключ сохраняем новый
                self.database.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    message[USER][PUBLIC_KEY])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Неверный пароль'
                try:
                    send_msg(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def service_update_lists(self):
        '''Метод реализующий отправки сервисного сообщения (205) клиентам'''
        for client in self.names:
            try:
                send_msg(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])
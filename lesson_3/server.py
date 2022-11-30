import socket
import sys
import argparse
import json
import logging
import select
import time
import log.server_log_config
from variables import *
from utils import get_msg, send_msg
from wrapper import log
from lesson_10.metaclasses import ServerVerifier
from lesson_10.descriptor import Port, logger


SERVER_LOG = logging.getLogger('server_log')


# Парсер аргументов коммандной строки.
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port

#основной класс сервера
class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port):
        #параметры подключения
        self.address = listen_address
        self.port = listen_port

        #список подключенных клиентов
        self.clients = []

        #список сообщений к отправке
        self.messages = []

        #словарь с именами и сокетами
        self.names = dict()

    def init_socket(self):
        logger.info(f'Сервер запущен. Порт {self.port}, адрес с которого принимаются подключения {self.address}, если адрес не указан принимаются соединения слюбых адресов')
        #готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)
        #слушаем сокет
        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        self.init_socket() #инициализируем сокет

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Соединение установлено с ПК {client_address}')
                self.clients.append(client)

            recv_data_list = []
            send_data_list = []
            error_list = []
            #проверяем ожидающих клиентов
            try:
                if self.clients:
                    recv_data_list, send_data_list, error_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            #принимаем сообщение, а при ошибке исключаем клиента
            if recv_data_list:
                for client_with_msg in recv_data_list:
                    try:
                        self.process_client_msg(get_msg(client_with_msg), client_with_msg)
                    except:
                        logger.info(f'Клиент {client_with_msg.getpeername()} отключился от сервера')
                        self.clients.remove(client_with_msg)
            #если есть сообщения, тогда обрабатываем
            for message in self.messages:
                try:
                    self.process_msg(message, send_data_list)
                except:
                    logger.info(f'Связь с клиентом по имени {message[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

#функция адресной отправки сообщения клиенту. Принимает словарь, список пользователей и слушащие сокеты.
def process_msg(self, message, listen_socks):
    if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
        send_msg(self.names[message[DESTINATION]], message)
        logger.info(f'Пользователю отправлено сообщение {message[DESTINATION]} от пользователя {message[SENDER]}')
    elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        logger.error(f'Пользователь {message[DESTINATION]} не зарегистрирован, отправка сообщения невозможна')

#обработчик сообщений от клиентов принимает словарь - сообщение, проверяет корректность, отправляет ответ
def process_client_msg(self, message, client):
    logger.debug(f'Проверка сообщения от клиента {message}')
    #если сообщение о присутствии отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
    #если пользователь не зарегистрирован регистрируем или завершаем соединение
        if message[USER][ACCOUNT_NAME] not in self.names.keys():
            self.names[message[USER][ACCOUNT_NAME]] = client
            send_msg(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Такое имя уже занято'
            send_msg(client, response)
            self.clients.remove(client)
            client.close()
        return
    #если это сообщение, то добавляем его в очередь сообщений
    elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
        and SENDER in message and MESSAGE_TXT in message:
        self.message.append(message)
        return
    #если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        self.clients.remove(self.names[ACCOUNT_NAME])
        self.names[ACCOUNT_NAME].close()
        del self.names[ACCOUNT_NAME]
        return
    #иначе ждет bad request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Некорректный запрос'
        send_msg(client, response)
        return

def main():
    # загрузка параметров командной строки
    listen_address, listen_port = arg_parser()
    #создание экз класса сервера
    server = Server(listen_address, listen_port)
    server.main_loop()
#
#
# @log
# def get_client_msg(message):
#
#     SERVER_LOG.debug(f'Проверка сообщения от клиента: {message}')
#     if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
#             and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
#         send_msg(client, {RESPONSE: 200})
#         return
#     else:
#         send_msg(client, {
#             RESPONSE: 400,
#             ERROR: 'Bad Request'
#         })
#         return
#
#
# @log
# def main():
#     try:
#         if '-p' in sys.argv:
#             listen_port = int(sys.argv[sys.argv.index('-p') + 1])
#         else:
#             listen_port = DEFAULT_PORT
#         if listen_port < 1024 or listen_port > 65535:
#             raise ValueError
#     except IndexError:
#         print('Укажите номер порта после параметра -p')
#         sys.exit(1)
#     except ValueError:
#         SERVER_LOG.critical(f'Номер порта {listen_port} указан некорректно. Нужно указать в диапазоне 1024 - 65535')
#         sys.exit(1)
#
#     try:
#         if '-a' in sys.argv:
#             listen_address = sys.argv[sys.argv.index('-a') + 1]
#         else:
#             listen_address = ''
#     except IndexError:
#         print('Укажите адрес после параметра -a')
#         sys.exit(1)
#     SERVER_LOG.info(f'Сервер запущен. порт: {listen_port}')
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind((listen_address, listen_port))
#     s.settimeout(0.2)
#
#     clients = []
#     messages = []
#
#     s.listen(MAX_CONNECTION)
#
#     while True:
#         try:
#             client, client_address = s.accept()
#             SERVER_LOG.info(f'соединение установлено c {client_address}')
#         except OSError:
#             pass
#
#         else:
#             SERVER_LOG.info(f'Установлено соединение с {client_address}')
#             clients.append(client)
#
#         recv_data_list = []
#         send_data_list = []
#         error_list = []
#
#         try:
#             if clients:
#                 recv_data_list, send_data_list, error_list = select.select(clients, clients, [], 0)
#         except OSError:
#             pass
#         if recv_data_list:
#             for client_with_msg in recv_data_list:
#                 try:
#                     process_client_msg(get_msg(client_with_msg), messages, client_with_msg)
#                 except:
#                     SERVER_LOG.info(f'Клиент {client_with_msg.getpeername()} отключился от сервера')
#                     clients.remove(client_with_msg)
#
#         if messages and send_data_list:
#             message = {
#                 ACTION: MESSAGE,
#                 SENDER: messages[0][0],
#                 TIME: time.time(),
#                 MESSAGE_TXT: messages[0][1]
#             }
#             del messages[0]
#             for waiting_client in send_data_list:
#                 try:
#                     send_msg(waiting_client, message)
#                 except:
#                     SERVER_LOG.info(f'Клиент {waiting_client.getpeername()} отключился от сервера')
#                     clients.remove(waiting_client)
#

if __name__ == '__main__':
    main()
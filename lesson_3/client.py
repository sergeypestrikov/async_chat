import json
import sys
import socket
import threading
import dis
import argparse
import logging
from threading import Thread
import namespace as namespace
import log.client_log_config
import time
from variables import *
from utils import get_msg, send_msg
from wrapper import log
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from lesson_10.metaclasses import ClientVerifier

# CLIENT_LOG = logging.getLogger('client_log')
logger = logging.getLogger('client')

#отправка сообщений на сервер и возаимодействие с пользователем
class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    #создание словаря с сообщением о выходе
    def create_msg_exit(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    #формирование сообщения и кому его отправлять + отправка данных на сервер
    @log
    def create_msg(self):
        to = input('Получатель сообщения: ')
        message = input('Введите сообщение: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TXT: message
        }
        logger.debug(f'Сформирован словарь сообщения {message_dict}')
        try:
            send_msg(self.sock, message_dict)
            logger.info(f'Сообщение отправлено пользователю {to}')
        except:
            logger.critical('Соединение потеряно')
            exit(1)

    #взаимодействие с пользователем
    def communicaton(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_msg()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_msg(self.sock, self.create_msg_exit())
                except:
                    pass
                print('Завершение соединения')
                logger.info('Завершение работы по команде пользователя')
                time.sleep(0.5) #что бы успейло уйти сообщение
                break
            else:
                print('Команда не распознана. Воспользуйтесь help и попробуйте снова')

    #функция выводит справку по испльзованию
    def print_help(self):
        print('Используемые команды: ')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

#прием сообщений и вывод информации
class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    #прием сообщений и вывод информации
    def msg_from_server(self):
        while True:
            try:
                message = get_msg(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                    and MESSAGE_TXT in message and message[DESTINATION] == self.account_name:
                    print(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера {message}')
            except IncorrectDataRecivedError:
                logger.error(f'Не удалось декодировать полученное сообщение')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером')
                break

#генерация запроса о присутствии клиента
@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out

#разбор ответа сервера о присутствии
@log
def answer_process(message):
    logger.debug(f'Проверка сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        elif message[RESPONSE] == 400:
            raise ServerError (f'400: {message[ERROR]}')
    raise ReqFieldMissingError

# Парсер аргументов коммандной строки
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

#проверка подходящий номера порта
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с некорректным номером порта: {server_port}. Допустимые адреса от 1024 до 65535. Клиент завершается')
        exit(1)
    return server_address, server_port, client_name


def main():
    #сообщаем о запуске
    print('Мессенджер: клиентский модуль')
    #загрузка параметров командной строки
    server_address, server_port, client_name = arg_parser()
    #если имя пользователя не задано, нужно запросить
    if not client_name:
        client_name = input('Введите Ваше имя: ')
    else:
        print(f'Клиентский модуль запущен под именем {client_name}')
    logger.info(f'Запущен клиент {client_name} с адреса сервера: {server_address} и порта {server_port}')
    #инициализация сокета и сообщение серверу о появлении клиента
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_msg(transport, create_presence(client_name))
        answer = answer_process(get_msg(transport))
        logger.info(f'Установлено соединение с сервером. Ответ: {answer}')
        print(f'Соединение с сервером установлено')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную JSON строку')
        exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует обязательное поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}. Компьютер отклонил запрос')
        exit(1)
    else:
        #если все ok и соединение установлено запуск процесса приема сообщений
        mode_receiver = ClientReader(client_name, transport)
        mode_receiver.daemon = True
        mode_receiver.start()
        #запуск отправки сообщений и коммуникация с пользователем
        mode_sender = ClientSender(client_name, transport)
        mode_sender.daemon = True
        mode_sender.start()
        logger.debug('Процессы запущены')

        #основной цикл. Если один из потоков завершен - или потеряно соединение или пользователь ввел exit
        #так как события обрабатываются в потоках, достаточно завершить цикл
        while True:
            time.sleep(1)
            if mode_receiver.is_alive() and mode_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
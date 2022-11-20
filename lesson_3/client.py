import json
import sys
import socket
import time
import logging

import namespace as namespace

import log.client_log_config
import time
from variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, ACCOUNT_NAME, RESPONSE, MESSAGE, MESSAGE_TXT, TIME, SENDER, MSG_LENGTH, MAX_CONNECTION,\
    PRESENCE, TIME, USER, ERROR
from utils import get_msg, send_msg
from wrapper import log
from errors import ReqFieldMissingError, ServerError

CLIENT_LOG = logging.getLogger('client_log')


@log
def msg_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TXT in message:
        print(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TXT]}')
    else:
        CLIENT_LOG.error(f'Получено некорректное сообщение с сервера {message}')

@log
def create_msg(sock, account_name='Guest'):
    message = input('Введите сообщение или команду \'!@#\' для завершения работы: ')
    if message == '!@#':
        sock.close()
        CLIENT_LOG.info('Завершение работы по желанию пользователя')
        print('До свидания')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TXT: message
    }
    CLIENT_LOG.debug(f'Сформирован словарь сообщения {message_dict}')
    return message_dict


@log
def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOG.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def answer_process(message):
    CLIENT_LOG.debug(f'Проверка сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    raise ValueError


@log
def main():
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        client_mode = namespace.mode
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT

    except ValueError:
        CLIENT_LOG.critical(f'Попытка запуска клиента с неподходящим номером порта {server_port}')
        sys.exit(1)


    CLIENT_LOG.info(f'Запущен клиент: сервер {server_address} и порт {server_port}')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_address, server_port))
    send_msg(s, create_presence())
    answer = answer_process(get_msg(s))
    msg_to_server = create_presence()
    send_msg(s, msg_to_server)
    try:
        answer = answer_process(get_msg(s))
        CLIENT_LOG.info(f'Принят ответ от сервера {answer}')
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOG.error(f'Не удалось декодировать сообщение сервера')

    except ServerError as error:
        CLIENT_LOG.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)

    except ConnectionRefusedError:
        CLIENT_LOG.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отклонил запрос на подключение')
        sys.exit(1)

    else:
        if client_mode == 'send':
            print('Включен режим отправки сообщений')
        else:
            print('Включен режим приема сообщений')

        while True:
            if client_mode == 'send':
                try:
                    send_msg(s, create_msg(s))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOG.error(f'Соединение с сервером {server_address} потеряно')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    msg_from_server(get_msg(s))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOG.error(f'Соединение с сервером {server_address} потеряно')
                    sys.exit(1)

if __name__ == '__main__':
    main()
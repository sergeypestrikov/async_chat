import socket
import json
import sys
import logging
import log.client_log_config
import time
from variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, ACCOUNT_NAME, RESPONSE, MSG_LENGTH, MAX_CONNECTION,\
    PRESENCE, TIME, USER, ERROR
from utils import get_msg, send_msg

CLIENT_LOG = logging.getLogger('client_log')

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


def answer_process(message):
    CLIENT_LOG.debug(f'Проверка сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    raise ValueError


def main():
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
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
    msg_to_server = create_presence()
    send_msg(s, msg_to_server)
    try:
        answer = answer_process(get_msg(s))
        CLIENT_LOG.info(f'Принят ответ от сервера {answer}')
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOG.error(f'Не удалось декодировать сообщение сервера')


if __name__ == '__main__':
    main()
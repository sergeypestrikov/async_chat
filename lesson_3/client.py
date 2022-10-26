import socket
import json
import sys
import time
from variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, ACCOUNT_NAME, RESPONSE, MSG_LENGTH, MAX_CONNECTION,\
    PRESENCE, TIME, USER, ERROR
from utils import get_msg, send_msg


def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


def answer_process(message):
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
        print('Укажите номер порта в диапазоне 1024 - 65535')
        sys.exit(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_address, server_port))
    msg_to_server = create_presence()
    send_msg(s, msg_to_server)
    try:
        answer = answer_process(get_msg(s))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера')


if __name__ == '__main__':
    main()
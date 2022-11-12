import socket
import sys
import json
import logging
import log.server_log_config
from variables import DEFAULT_PORT, ACTION, ACCOUNT_NAME, RESPONSE, MSG_LENGTH, MAX_CONNECTION, PRESENCE, TIME, USER, ERROR
from utils import get_msg, send_msg

SERVER_LOG = logging.getLogger('server_log')

def get_client_msg(message):

    SERVER_LOG.debug(f'Проверка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('Укажите номер порта после параметра -p')
        sys.exit(1)
    except ValueError:
        SERVER_LOG.critical(f'Номер порта {listen_port} указан некорректно. Нужно указать в диапазоне 1024 - 65535')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print('Укажите адрес после параметра -a')
        sys.exit(1)
    SERVER_LOG.info(f'Сервер запущен. порт: {listen_port}')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((listen_address, listen_port))

    s.listen(MAX_CONNECTION)

    while True:
        client, client_address = s.accept()
        SERVER_LOG.info(f'соединение установлено c {client_address}')
        try:
            message_from_client = get_msg(client)
            SERVER_LOG.debug(f'Получено сообщение {message_from_client}')
            print(message_from_client)
            response = get_client_msg(message_from_client)
            SERVER_LOG.info(f'Сформирован ответ {response}')
            send_msg(client, response)
            SERVER_LOG.debug(f'Соединение с клиентом {client_address} закрывается')
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOG.error(f'От клиента {client_address} принято некорректное сообщение')
            print('Принято некорректное сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()
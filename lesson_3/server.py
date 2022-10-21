import socket
import sys
import json
from variables import DEFAULT_PORT, ACTION, ACCOUNT_NAME, RESPONSE, MSG_LENGTH, MAX_CONNECTION, PRESENCE, TIME, USER, ERROR
from utils import get_msg, send_msg


def get_client_msg(message):
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
        print('Укажите номер порта в диапазоне 1024 - 65535')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print('Укажите адрес после параметра -a')
        sys.exit(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((listen_address, listen_port))

    s.listen(MAX_CONNECTION)

    while True:
        client, client_address = s.accept()
        try:
            message_from_client = get_msg(client)
            print(message_from_client)
            response = get_client_msg(message_from_client)
            send_msg(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорректное сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()
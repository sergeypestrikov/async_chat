import socket
import sys
import json
import logging
import select
import time
import log.server_log_config
from variables import DEFAULT_PORT, ACTION, ACCOUNT_NAME, RESPONSE, MSG_LENGTH, SENDER, MESSAGE, MESSAGE_TXT, MAX_CONNECTION, PRESENCE, TIME, USER, ERROR
from utils import get_msg, send_msg
from wrapper import log


SERVER_LOG = logging.getLogger('server_log')


@log
def get_client_msg(message):

    SERVER_LOG.debug(f'Проверка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_msg(client, {RESPONSE: 200})
        return
    else:
        send_msg(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
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
    s.settimeout(0.2)

    clients = []
    messages = []

    s.listen(MAX_CONNECTION)

    while True:
        try:
            client, client_address = s.accept()
            SERVER_LOG.info(f'соединение установлено c {client_address}')
        except OSError:
            pass

        else:
            SERVER_LOG.info(f'Установлено соединение с {client_address}')
            clients.append(client)

        recv_data_list = []
        send_data_list = []
        error_list = []

        try:
            if clients:
                recv_data_list, send_data_list, error_list = select.select(clients, clients, [], 0)
        except OSError:
            pass
        if recv_data_list:
            for client_with_msg in recv_data_list:
                try:
                    process_client_msg(get_msg(client_with_msg), messages, client_with_msg)
                except:
                    SERVER_LOG.info(f'Клиент {client_with_msg.getpeername()} отключился от сервера')
                    clients.remove(client_with_msg)

        if messages and send_data_list:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_list:
                try:
                    send_msg(waiting_client, message)
                except:
                    SERVER_LOG.info(f'Клиент {waiting_client.getpeername()} отключился от сервера')
                    clients.remove(waiting_client)

        #     message_from_client = get_msg(client)
        #     SERVER_LOG.debug(f'Получено сообщение {message_from_client}')
        #     print(message_from_client)
        #     response = get_client_msg(message_from_client)
        #     SERVER_LOG.info(f'Сформирован ответ {response}')
        #     send_msg(client, response)
        #     SERVER_LOG.debug(f'Соединение с клиентом {client_address} закрывается')
        #     client.close()
        # except (ValueError, json.JSONDecodeError):
        #     SERVER_LOG.error(f'От клиента {client_address} принято некорректное сообщение')
        #     print('Принято некорректное сообщение от клиента')
        #     client.close()


if __name__ == '__main__':
    main()
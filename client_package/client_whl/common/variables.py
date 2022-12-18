import datetime
import logging

# Порт по умолчания для сетевого взаимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключения
MAX_CONNECTION = 5
# Максимальная длина сообщения а байтах
MSG_LENGTH = 1024
# Кодировка проекта
ENCODING = 'UTF-8'
# Текущий уровень логирования
LOG_LEVEL = logging.DEBUG
# БД для хранения данных сервера
SERVER_CONFIG = 'server.ini'

# Основные ключи для протокола JIM
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'to'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

# Прочие ключи из протокола
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TXT = 'message_txt'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'pubkey_need'

# Словари - ответы
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
RESPONSE_202 = {
    RESPONSE: 202,
    LIST_INFO: None
}
RESPONSE_205 = {
    RESPONSE: 205
}
RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}
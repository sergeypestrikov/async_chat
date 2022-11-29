import datetime
import logging

DEFAULT_PORT = 8888
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTION = 5
MSG_LENGTH = 1024
ENCODING = 'UTF-8'
LOG_LEVEL = logging.DEBUG

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'to'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TXT = 'message_txt'
EXIT = 'exit'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
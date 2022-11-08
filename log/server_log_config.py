import sys
import os
import logging
import logging.handlers
from lesson_3.variables import LOG_LEVEL

logging.basicConfig(
    filename='server_log.log',
    format='%(levelname)s %(asctime)s %(filename)s %(message)s',
    level=logging.DEBUG,
)

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler('server_log.log', encoding='UTF-8', interval=2, when='midnight')

LOG = logging.getLogger('server_log')
LOG.addHandler(STREAM_HANDLER)
LOG.addHandler(LOG_FILE)
LOG.setLevel(LOG_LEVEL)


if __name__ == '__main__':
    LOG.critical('Alarm! Критично!')
    LOG.error('Just ошибка')
    LOG.debug('Отладка')
    LOG.info('Для информации')
import sys
import os
import logging
import logging.handlers
from lesson_3.variables import LOG_LEVEL

logging.basicConfig(
    filename='client_log.log',
    format='%(levelname)s %(asctime)s %(filename)s %(message)s',
    level=logging.DEBUG,
)

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG = logging.getLogger('client_log')
LOG.addHandler(STREAM_HANDLER)


if __name__ == '__main__':
    LOG.critical('Alarm! Критично!')
    LOG.error('Just ошибка')
    LOG.debug('Отладка')
    LOG.info('Для информации')
import sys
import logging
import sys

logger = logging.getLogger('server')


class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(f'Номер порта {value} указан некорректно. Нужно указать в диапазоне 1024 - 65535')
            sys.exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
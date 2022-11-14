import sys
import logging

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):
        def wrapper(*args, **kwargs):
            LOGGER.debug(f'Вызвана функция {func.__name__} с аргументами {args} {kwargs}')
            r = func(*args, **kwargs)
            print(f'Функция {func.__name__} вернула {r}')
            return r
        return wrapper
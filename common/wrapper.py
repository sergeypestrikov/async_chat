import sys
import logging
import socket

import log.server_log_config
import log.client_log_config

# Метод определения модуля, источника запуска
if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):
    '''
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию о имени вызываемой функции, параметры с которыми
    вызывается функция, и модуль, вызывающий функцию.
    '''
    def wrapper(*args, **kwargs):
        LOGGER.debug(f'Вызвана функция {func.__name__} с аргументами {args} {kwargs}')
        r = func(*args, **kwargs)
        print(f'Функция {func.__name__} вернула {r}')
        return r
    return wrapper


def login_required(func):
    '''
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    '''
    def checker(*args, **kwargs):
        # Проверка, что первый аргумент - экземпляр ProcessorMSG
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта
        from server.core import ProcessorMSG
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], ProcessorMSG):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверка, что данный сокет есть в списке names класса ProcessorMSG
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True
            # Теперь проверка, что передаваемые аргументы не presence сообщение. Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не авторизован и не сообщение начала авторизации, то вызов исключения
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
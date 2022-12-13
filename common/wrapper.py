import sys
import logging
import log.server_log_config
import log.client_log_config
import socket

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')

'''
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию о имени вызываемой функиции, параметры с которыми
    вызывается функция, и модуль, вызывающий функцию.
    '''

def log(func):
        def wrapper(*args, **kwargs):
            LOGGER.debug(f'Вызвана функция {func.__name__} с аргументами {args} {kwargs}')
            r = func(*args, **kwargs)
            print(f'Функция {func.__name__} вернула {r}')
            return r
        return wrapper

'''
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    '''

def login_required(func):

    def checker(*args, **kwargs):
        #проверяем, что первый аргумент - экземпляр ProcessorMSG
        #импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from server.core import ProcessorMSG
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], ProcessorMSG):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    #проверяем, что данный сокет есть в списке names класса ProcessorMSG
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True
            #теперь надо проверить, что передаваемые аргументы не presence сообщение. Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            #если не не авторизован и не сообщение начала авторизации, то вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
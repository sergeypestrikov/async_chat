import dis

# метакласс выполняющий базовую проверку класса «Клиент»
class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                returning = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in returning:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('Обнаружен запрещенный метод')
        if 'get_msg' in methods or 'send_msg' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций работающих с сокетами')
        super().__init__(clsname, bases, clsdict)

# метакласс выполняющий базовую проверку класса «Сервер»
class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attributes = []
        for func in clsdict:
            try:
                returning = dis.get_instructions((clsdict[func]))
            except TypeError:
                pass
            else:
                for i in returning:
                    print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)

        print(methods)
        if 'connect' in methods:
            raise TypeError('Метод connect недопустим')
        if not ('SOCK_STREAM' in attributes and 'AF_INET' in attributes):
            raise TypeError('Некорректная инициализация сокета')
        super().__init__(clsname, bases, clsdict)

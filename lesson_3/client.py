import json
import sys
import socket
import threading
import dis
import argparse
import logging
from threading import Thread
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
import namespace as namespace
import log.client_log_config
import time
from variables import *
from utils import get_msg, send_msg
from wrapper import log
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from lesson_10.metaclasses import ClientVerifier
from lesson_12.client_data_base import ClientDataBase

# CLIENT_LOG = logging.getLogger('client_log')
logger = logging.getLogger('client')

#объект блокировки сокета и работы с БД
sock_lock = threading.Lock()
database_lock = threading.Lock()

#отправка сообщений на сервер и возаимодействие с пользователем
class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    #создание словаря с сообщением о выходе
    def create_msg_exit(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    #формирование сообщения и кому его отправлять + отправка данных на сервер
    @log
    def create_msg(self):
        to = input('Получатель сообщения: ')
        message = input('Введите сообщение: ')
        #проверка существования получателя
        with database_lock:
            if not self.database.check_user(to):
                logger.error(f'Попытка отправить сообщение незарегистрированому получателю: {to}')
                return
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TXT: message
        }
        logger.debug(f'Сформирован словарь сообщения {message_dict}')
        #сохранение сообщений для истории
        with database_lock:
            self.database.save_message(self.account_name, to, message)
        with sock_lock:
            try:
                send_msg(self.sock, message_dict)
                logger.info(f'Сообщение отправлено пользователю {to}')
            except OSError as err:
                if err.errno:
                    logger.critical('Соединение потеряно')
                    exit(1)
                else:
                    logger.error('Не удалось передать сообщение. Таймаут соединения')

    #взаимодействие с пользователем
    def communicaton(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_msg()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                with sock_lock:
                    try:
                        send_msg(self.sock, self.create_msg_exit())
                    except:
                        pass
                    print('Завершение соединения')
                    logger.info('Завершение работы по команде пользователя')
                time.sleep(0.5) #что бы успейло уйти сообщение
                break
            #список контактов
            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)
            #редактирование контактов
            elif command == 'edit':
                self.edit_contacts()
            #история сообщений.
            elif command == 'history':
                self.print_history()
            else:
                print('Команда не распознана. Воспользуйтесь help и попробуйте снова')


    #функция выводящяя справку по использованию.
    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    #функция выводящяя историю сообщений
    def print_history(self):
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} от {message[3]}\n{message[2]}')

    #функция изменеия контактов
    def edit_contacts(self):
        ans = input('Для удаления введите del, для добавления add: ')
        if ans == 'del':
            edit = input('Введите имя удаляемого контакта: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    logger.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            # Проверка на возможность такого контакта
            edit = input('Введите имя создаваемого контакта: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        ADD_CONTACT(self.sock, self.account_name, edit)
                    except ServerError:
                        logger.error('Не удалось отправить информацию на сервер.')

#прием сообщений и вывод информации
class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    #прием сообщений и вывод информации
    def msg_from_server(self):
        while True:
            time.sleep(1) #если не сделать задержку, второй поток может ждать долго
            with sock_lock:
                try:
                    message = get_msg(self.sock)
                except IncorrectDataRecivedError:
                    logger.error(f'Не удалось декодировать полученное сообщение')
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Потеряно соединение с сервером')
                        break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TXT in message and message[DESTINATION] == self.account_name:
                        print(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TXT]}')
                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TXT])
                            except:
                                logger.error('Ошибка взаимодействия с БД')
                        logger.info(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TXT]}')
                    else:
                        logger.error(f'Получено некорректное сообщение с сервера: {message}')

#генерация запроса о присутствии клиента
@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out

#разбор ответа сервера о присутствии
@log
def answer_process(message):
    logger.debug(f'Проверка сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        elif message[RESPONSE] == 400:
            raise ServerError (f'400: {message[ERROR]}')
    raise ReqFieldMissingError

# Парсер аргументов коммандной строки
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

#проверка подходящий номера порта
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с некорректным номером порта: {server_port}. Допустимые адреса от 1024 до 65535. Клиент завершается')
        exit(1)
    return server_address, server_port, client_name

#запрос контакт листа
def contacts_list_request(sock, name):
    logger.debug(f'Запрос контакт листа для пользователя {name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    logger.debug(f'Сформирован запрос {req}')
    send_msg(sock, req)
    ans = get_msg(sock)
    logger.debug(f'Получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


#добавление пользователя в контакт лист
def add_contact(sock, username, contact):
    logger.debug(f'Создание контакта {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_msg(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка создания контакта')
    print('Удачное создание контакта.')


# Функция запроса списка известных пользователей
def user_list_request(sock, username):
    logger.debug(f'Запрос списка известных пользователей {username}')
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_msg(sock, req)
    ans = get_msg(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


#удаление пользователя из контактов
def remove_contact(sock, username, contact):
    logger.debug(f'Создание контакта {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_msg(sock, req)
    ans = get_msg(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка удаления клиента')
    print('Удачное удаление')


#инициализатор базы данных. Запускается при запуске, загружает данные в базу с сервера.
def database_load(sock, database, username):
    # Загружаем список известных пользователей
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        logger.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)
    #загрузка списка контактов
    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        logger.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)

def main():
    #сообщаем о запуске
    print('Мессенджер: клиентский модуль')
    #загрузка параметров командной строки
    server_address, server_port, client_name = arg_parser()
    #если имя пользователя не задано, нужно запросить
    if not client_name:
        client_name = input('Введите Ваше имя: ')
    else:
        print(f'Клиентский модуль запущен под именем {client_name}')
    logger.info(f'Запущен клиент {client_name} с адреса сервера: {server_address} и порта {server_port}')
    #инициализация сокета и сообщение серверу о появлении клиента
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_msg(transport, create_presence(client_name))
        answer = answer_process(get_msg(transport))
        logger.info(f'Установлено соединение с сервером. Ответ: {answer}')
        print(f'Соединение с сервером установлено')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную JSON строку')
        exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует обязательное поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}. Компьютер отклонил запрос')
        exit(1)
    else:
        #инициализация БД
        database = ClientDataBase(client_name)
        database_load(transport, database, client_name)
        #если соединение с сервером установлено корректно, запускаем поток взаимодействия с пользователем
        module_sender = ClientSender(client_name, transport, database)
        module_sender.daemon = True
        module_sender.start()
        logger.debug('Запущены процессы')
        #запуск потока - приёмник сообщений
        module_receiver = ClientReader(client_name, transport, database)
        module_receiver.daemon = True
        module_receiver.start()
        #Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение или пользователь
        #ввёл exit. Поскольку все события обработываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
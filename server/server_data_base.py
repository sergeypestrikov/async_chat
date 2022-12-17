from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, mapper
from common.variables import *


class ServerStorage:
    '''
    Класс - оболочка для работы с базой данных сервера.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется классический подход.
    '''
    class Client:
        '''Класс - отображение таблицы всех пользователей'''
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveClient:
        '''Класс - отображение таблицы активных пользователей'''
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        '''Класс - отображение таблицы истории входов'''
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    class UsersContacts:
        '''Класс - отображение таблицы контактов пользователей'''
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    class UsersHistory:
        '''Класс - отображение таблицы истории действий'''
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    # Движок базы данных
    def __init__(self, name):
        print(name)
        self.engine = create_engine(f'sqlite:///server_{name}.db3', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        # Объект метадата
        self.metadata = MetaData()

        # Таблица пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )
        # Таблица активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id'), unique=True),
                                    Column('ip_address', String),
                                    Column('port', Integer),
                                    Column('login_time', DateTime)
                                    )
        # Таблица истории входов
        users_login_history = Table('Login_history', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('name', ForeignKey('Users.id')),
                                    Column('date_time', DateTime),
                                    Column('ip', String),
                                    Column('port', String)
                                    )
        # Таблица контактов пользователя
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )
        # Таблица истории пользователей
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )
        # Создание таблиц
        self.metadata.create_all(self.engine)
        # Создание отображений
        mapper(self.Client, users_table)
        mapper(self.ActiveClient, active_users_table)
        mapper(self.LoginHistory, users_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)
        # Создание сессии
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Удаление записей (если они есть) в таблице активных пользователей
        self.session.query(self.ActiveClient).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        '''
        Метод выполняющийся при входе пользователя, записывает в базу факт входа
        Обновляет открытый ключ пользователя при его изменении.
        '''
        result = self.session.query(self.Client).filter_by(name=username) #запрос в табюлицу на ниличие такого пользователя
        if result.count():
            user = result.first()
            # Если имя пользователя уже присутствует в таблице,
            # обновляем время последнего входа
            user.last_login = datetime.datetime.now()
        # Если нет, создаем нового пользователя
        else:
            user = self.Client(username)
            self.session.add(user)
            # Сommit нужен для присвоения id
            self.session.commit()
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)

        # Создание записи для активных пользователей о факте входа
        new_active_user = self.ActiveClient(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        # Сохранение в историю входов
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    def add_user(self, name, passwd_hash):
        '''
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        '''
        user_row = self.Client(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        '''Метод удаляющий пользователя из базы'''
        user = self.session.query(self.Client).filter_by(name=name).first()
        self.session.query(self.ActiveClient).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(
            self.UsersContacts).filter_by(
            contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.Client).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        '''Метод получения хэша пароля пользователя'''
        user = self.session.query(self.Client).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        '''Метод получения публичного ключа пользователя'''
        user = self.session.query(self.Client).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        '''Метод проверяющий существование пользователя.'''
        if self.session.query(self.Client).filter_by(name=name).count():
            return True
        else:
            return False

    def user_logout(self, username):
        '''Метод фиксирующий отключения пользователя'''
        # Запрос пользователю
        user = self.session.query(self.Client).filter_by(name=username).first()
        # Удаление пользователя из таблицы активных
        self.session.query(self.ActiveClient).filter_by(user=user.id).delete()
        self.session.commit()

    def process_msg(self, sender, receiver):
        '''Метод записывающий в таблицу статистики факт передачи сообщения'''
        # Получение ID отправителя и получателя
        sender = self.session.query(self.Client).filter_by(name=sender).first().id
        receiver = self.session.query(self.Client).filter_by(name=receiver).first().id
        # Запрос строк из истории + увеличение счетчика
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        receiver_row = self.session.query(self.UsersHistory).filter_by(user=receiver).first()
        receiver_row.accepted += 1
        self.session.commit()

    def add_contact(self, user, contact):
        '''Метод добавления контакта для пользователя'''
        # Получение id
        user = self.session.query(self.Client).filter_by(name=user).first()
        contact = self.session.query(self.Client).filter_by(name=contact).first()
        # Проверка, что контакт не дублируется и может существовать
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return
        # Создание объекта с записью в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        '''Метод удаления контакта пользователя'''
        # Получение ID
        user = self.session.query(self.Client).filter_by(name=user).first()
        contact = self.session.query(self.Client).filter_by(name=contact).first()
        # Проверка на возможность существоаания контакта
        if not contact:
            return
        # Удаляем требуемое
        print(self.session.query(self.UsersContacts). filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()

    def users_list(self):
        '''Метод возвращающий список известных пользователей со временем последнего входа'''
        # Запрос строк из таблицы
        query = self.session.query(self.Client.name, self.Client.last_login)
        return query.all()

    def active_users_list(self):
        '''Метод возвращающий список активных пользователей'''
        query = self.session.query(
            self.Client.name,
            self.ActiveClient.ip_address,
            self.ActiveClient.port,
            self.ActiveClient.login_time
        ).join(self.Client)
        return query.all()

    def login_history(self, username=None):
        '''Метод возвращающий историю входов'''
        # Запрос истории входа
        query = self.session.query(self.Client.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port,
                                   ).join(self.Client)
        # Если имя было указано то фильтрация по нему
        if username:
            query = query.filter(self.Client.name == username)
        return query.all()

    def get_contacts(self, username):
        '''Метод возвращающий список контактов пользователя'''
        user = self.session.query(self.Client).filter_by(name=username).one() #Запрашиваем указанного пользователя
        query = self.session.query(self.UserContacts, self.Client.name).filter_by(user=user.id).join(self.Client, self.UserContacts.contact == self.Client.id) #Запрашиваем его список контактов
        return [contact[1] for contact in query.all()]

    def msg_history(self):
        '''Метод возвращающий статистику сообщений'''
        query = self.session.query(
            self.Client.name,
            self.Client.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted,
        ).join(self.Client)
        return query.all()

# Отладка
if __name__ == '__main__':
    test_db = ServerStorage('server_storage_db')
    test_db.user_login('7777', '127.0.0.1', 8088)
    print(test_db.users_list())

    test_db.process_msg('7777', '1111')
    print(test_db.msg_history())

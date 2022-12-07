from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import relationship, sessionmaker, mapper
from lesson_3.variables import *

#серверная база данных
class ServerStorage:
    #таблица клиентов
    class Client:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    #таблица активных клиентов
    class ActiveClient:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    #таблица истории входов
    class LoginHistory:
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    #таблица контактов пользователей
    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    #таблица истории действий
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    #движок базы данных
    def __init__(self, name):
        print(name)
        self.engine = create_engine(f'sqlite:///server_{name}.db3', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        #объект метадата
        self.metadata = MetaData()

        #таблица пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )
        #таблица активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id'), unique=True),
                                    Column('ip_address', String),
                                    Column('port', Integer),
                                    Column('login_time', DateTime)
                                    )
        #таблица истории входов
        users_login_history = Table('Login_history', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('name', ForeignKey('Users.id')),
                                    Column('date_time', DateTime),
                                    Column('ip', String),
                                    Column('port', String)
                                    )
        #таблица контактов пользователя
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )
        #таблица истории пользователей
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )
        #создание таблиц
        self.metadata.create_all(self.engine)
        #создание отображений
        mapper(self.Client, users_table)
        mapper(self.ActiveClient, active_users_table)
        mapper(self.LoginHistory, users_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)
        #создание сессии
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        #удаление записей (если они есть) в таблице активных пользователей
        self.session.query(self.ActiveClient).delete()
        self.session.commit()

    #запись в базу факт входа пользователя
    def user_login(self, username, ip_address, port):
        result = self.session.query(self.Client).filter_by(name=username) #запрос в табюлицу на ниличие такого пользователя
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now() # eсли имя пользователя уже присутствует в таблице, обновляем время последнего входа
        # если нет, создаем нового пользователя
        else:
            user = self.Client(username)
            self.session.add(user)
            self.session.commit() #commit нужен для присвоения id
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)

        #создание записи для активных пользователей о факте входа
        new_active_user = self.ActiveClient(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        #сохранение в историю входов
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    #фиксация отключения пользователей
    def user_logout(self, username):
        #запрос пользователю
        user = self.session.query(self.Client).filter_by(name=username).first()
        #удаление пользователя из таблицы активных
        self.session.query(self.ActiveClient).filter_by(user=user.id).delete()
        self.session.commit()

    #фиксация передачи сообщений и отметки в БД
    def process_msg(self, sender, receiver):
        #получение ID отправителя и получателя
        sender = self.session.query(self.Client).filter_by(name=sender).first().id
        receiver = self.session.query(self.Client).filter_by(name=receiver).first().id
        #запрос строк из истории + увеличение счетчика
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        receiver_row = self.session.query(self.UsersHistory).filter_by(user=receiver).first()
        receiver_row.accepted += 1
        self.session.commit()

    #добавление контакта для пользователя
    def add_contact(self, user, contact):
        #получение id
        user = self.session.query(self.Client).filter_by(name=user).first()
        contact = self.session.query(self.Client).filter_by(name=contact).first()
        #проверка, что контакт не дублируется и может существовать
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return
        #создание объекта с записью в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    #удаление контакта из БД
    def remove_contact(self, user, contact):
        #получение ID
        user = self.session.query(self.Client).filter_by(name=user).first()
        contact = self.session.query(self.Client).filter_by(name=contact).first()
        #проверка на возможность существоаания контакта
        if not contact:
            return
        #удаляем требуемое
        print(self.session.query(self.UsersContacts). filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()

    #функция возврата списка пользователей с известными данными о последнем входе
    def users_list(self):
        #запрос строк из таблицы
        query = self.session.query(self.Client.name, self.Client.last_login)
        return query.all()

    #список активных пользователей
    def active_users_list(self):
        query = self.session.query(
            self.Client.name,
            self.ActiveClient.ip_address,
            self.ActiveClient.port,
            self.ActiveClient.login_time
        ).join(self.Client)
        return query.all()
    #возвращение истории входов по пользователю
    def login_history(self, username=None):
        #запрос истории входа
        query = self.session.query(self.Client.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port,
                                   ).join(self.Client)
        #если имя было указано то фильтрация по нему
        if username:
            query = query.filter(self.Client.name == username)
        return query.all()

    #возврат списка контактов пользователя
    def get_contacts(self, username):
        user = self.session.query(self.Client).filter_by(name=username).one() #Запрашиваем указанного пользователя
        query = self.session.query(self.UserContacts, self.Client.name).filter_by(user=user.id).join(self.Client, self.UserContacts.contact == self.Client.id) #Запрашиваем его список контактов
        return [contact[1] for contact in query.all()]

    #возврат переданных и полученных сообщений
    def msg_history(self):
        query = self.session.query(
            self.Client.name,
            self.Client.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted,
        ).join(self.Client)
        return query.all()

#отладка
if __name__ == '__main__':
    test_db = ServerStorage('server_storage_db')
    test_db.user_login('1111', '127.0.0.1', 8080)
    test_db.user_login('7777', '127.0.0.1', 8088)
    print(test_db.users_list())

    test_db.process_msg('7777', '1111')
    print(test_db.msg_history())

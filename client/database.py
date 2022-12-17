import datetime
import os

from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ClientDataBase:
    '''
    Класс - оболочка для работы с базой данных клиента.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется классический подход.
    '''
    class KnownUsers:
        '''Класс - отображение для таблицы всех пользователей'''
        def __init__(self, user):
            self.id = None
            self.username = user


    class MessageHistory:
        ''' Класс для отображения таблицы истории сообщений'''
        def __init__(self, from_user, to_user, message):
            self.id = None
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        '''Класс - отображение для таблицы контактов'''
        def __init__(self, contact):
            self.id =None
            self.name = contact

    # Конструктор класса. создание движка.
    # Поскольку разрешено несколько клиентов одновременно, каждый должен иметь свою БД.
    # Поскольку клиент мультипоточный необходимо отключить проверки на подключения с разных потоков
    def __init__(self, name):
        self.engine = create_engine(f'sqlite:///client_{name}.db3', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        # Создание объекта метадата
        self.metadata = MetaData()
        # Таблица известных пользователей
        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String)
                      )
        # Таблица истории сообщений
        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('from_user', String),
                        Column('to_user', String),
                        Column('message', Text),
                        Column('date', DateTime)
                        )
        # Таблица контактов
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True)
                         )
        # Создание таблиц
        self.metadata.create_all(self.engine)
        # Создание отображений
        mapper(self.KnownUsers, users)
        mapper(self.MessageHistory, history)
        mapper(self.Contacts, contacts)
        # Создание сессии
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Чистка таблицы контактов, которые при запуске они подгружаются с сервера
        self.session.query(self.Contacts).delete()
        self.session.commit()


    def add_contact(self, contact):
        '''Метод добавляющий контакт в базу данных'''
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact):
        '''Метод удаляющий определённый контакт'''
        self.session.query(self.Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list):
        '''Метод заполняющий таблицу известных пользователей'''
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_msg(self, from_user, to_user, message):
        '''Метод сохраняющий сообщение в базе данных'''
        message_row = self.MessageHistory(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        '''Метод возвращающий список всех контактов'''
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        '''Метод возвращающий список всех известных пользователей'''
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        '''Метод проверяющий существует ли пользователь'''
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        '''Метод проверяющий существует ли контакт'''
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        '''Метод возвращающий историю сообщений с определённым пользователем'''
        query = self.session.query(self.MessageHistory).filter_by(contact=contact)
        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in query.all()]

# Отладка
if __name__ == '__main__':
    test_db = ClientDataBase('Test_Base')
    print(test_db.get_contacts())
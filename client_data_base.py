from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import datetime

#клиентская база данных
class ClientDataBase:
    #таблица с известными пользователями
    class KnownUsers:
        def __init__(self, user):
            self.id = None
            self.username = user

    #отображение таблицы истории сообщений
    class MessageHistory:
        def __init__(self, from_user, to_user, message):
            self.id = None
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.datetime.now()
    #отображение списка контактов
    class Contacts:
        def __init__(self, contact):
            self.id =None
            self.name = contact

    #конструктор класса. создание движка.
    #поскольку разрешено несколько клиентов одновременно, каждый должен иметь свою БД.
    #поскольку клиент мультипоточный необходимо отключить проверки на подключения с разных потоков
    def __init__(self, name):
        self.engine = create_engine(f'sqlite:///client_{name}.db3', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        #создание объекта метадата
        self.metadata = MetaData()
        #таблица известных пользователей
        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String)
                      )
        #таблица истории сообщений
        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('from_user', String),
                        Column('to_user', String),
                        Column('message', Text),
                        Column('date', DateTime)
                        )
        #таблица контактов
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True)
                         )
        #создание таблиц
        self.metadata.create_all(self.engine)
        #создание отображений
        mapper(self.KnownUsers, users)
        mapper(self.MessageHistory, history)
        mapper(self.Contacts, contacts)
        #создание сессии
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        #чистка таблицы контактов, которые при запуске они подгружаются с сервера.
        self.session.query(self.Contacts).delete()
        self.session.commit()

        #добавление контактов
    def add_contact(self, contact):
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    #удаление контактов
    def del_contact(self, contact):
        self.session.query(self.Contacts).filter_by(name=contact).delete()

    #добавление известных пользователей
    def add_users(self, users_list):
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    #сохранение сообщений
    def save_msg(self, from_user, to_user, message):
        message_row = self.MessageHistory(from_user, to_user, message)
        self.session,add(message_row)
        self.session.commit()

    #возврат контакты
    def get_contacts(self):
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    #возврат списка известных пользователей
    def get_users(self):
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    #проверка наличия пользователя в известных
    def check_user(self, user):
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    #проверка наличие пользователя контактах
    def check_contact(self, contact):
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    #возвращение истории переписки
    def get_history(self, from_who=None, to_who=None):
        query = self.session.query(self.MessageHistory)
        if from_who:
            query = query.filter_by(from_user=from_who)
        if to_who:
            query = query.filter_by(to_user=to_who)
        return [(history_row.from_user, history_row.to_user, history_row.message, history_row.date)
                for history_row in query.all()]

# отладка
if __name__ == '__main__':
    test_db = ClientDataBase('client_storage_db')
    for i in ['client_storage_db']:
        test_db.add_contact(i)

    print(test_db.get_contacts())
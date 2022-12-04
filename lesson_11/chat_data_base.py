import ipaddress

import sqlalchemy
from sqlalchemy import create_engine, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime



from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import relationship

meta = MetaData()

Base = declarative_base()

engine = create_engine('sqlite:///:memory:storage.db')


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    login = Column(String(20), unique=True)
    info = Column(String(100))
    relation = relationship('ClientHistory', backref='clients', lazy='dynamic')

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return "<Client('%s', '%s')>" % (self.login, self.info)


class ClientHistory(Base):
    __tablename__ = 'client_history'
    created_on = Column(DateTime(), ForeignKey('Client.id'), default=datetime.now())
    ip = Column(ipaddress)

    def __init__(self, created_on):
        self.created_on = created_on
        self.ip = ip

    def __repr__(self):
        return "<Client('%d')>" % (self.created_on)


class ContactList(Base):
    __tablename__ = 'contact_list'
    user_id = Column(Integer)
    client_id = Column(Integer)

    def __init__(self, user_id, cliend_id):
        self.user_id = user_id
        self.client_id = cliend_id

    def __repr__(self):
        return "<Client('%s', '%s')>" % (self.user_id, self.client_id)


meta.create_all(engine)
"""Модуль, описывающий логику базы данных на стороне клиента."""

import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import default_comparator
from datetime import datetime


class ClientStorage:
    """Класс, описывающий данные на стороне клиента."""
    Base = declarative_base()

    class Users(Base):
        """Класс, описывающий всех зарегистрированных пользователей."""
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        user_name = Column(String)

        def __init__(self, user_name):
            self.user_name = user_name

    class Contacts(Base):
        """Класс, описывающий контакты клиента."""
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        contact_name = Column(String, unique=True)

        def __init__(self, contact_name):
            self.contact_name = contact_name

    class Posts(Base):
        """Класс, описывающий сообщения пользователей."""
        __tablename__ = 'posts'
        id = Column(Integer, primary_key=True)
        user_from = Column(String)
        user_to = Column(String)
        post = Column(Text)
        created_at = Column(DateTime)

        def __init__(self, user_from, user_to, post):
            self.user_from = user_from
            self.user_to = user_to
            self.post = post
            self.created_at = datetime.now()

    def __init__(self, client_name: str):
        db_path = os.getcwd()
        db_name = f'db_{client_name}.db3'
        self.db_engine = create_engine(
            f'sqlite:///{os.path.join(db_path, db_name)}',
            echo=False,
            pool_recycle=7200,
            connect_args={
                'check_same_thread': False})
        self.Base.metadata.create_all(self.db_engine)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

    def add_contact(self, contact_name: str):
        """Записывает имя контакта в базу клиента."""
        contact = self.session.query(
            self.Contacts).filter_by(
            contact_name=contact_name)
        # Если нет среди контактов:
        if not contact.count():
            new_contact = self.Contacts(contact_name)
            self.session.add(new_contact)
            self.session.commit()

    def remove_contact(self, contact_name: str):
        """Удаляет контакт пользователя."""
        contact = self.session.query(
            self.Contacts).filter_by(
            contact_name=contact_name)
        if contact.count():
            contact.delete()
        self.session.commit()

    def get_contacts(self):
        """Возвращает список контактов."""
        response = self.session.query(self.Contacts.contact_name).all()
        contacts = []
        for contact in response:
            contacts.append(contact[0])
        return contacts

    def get_users(self):
        """Возвращает список всех пользователей."""
        response = self.session.query(self.Users.user_name).all()
        users = []
        for user in response:
            users.append(user[0])
        return users

    def get_message_history(self, contact_name: str = None):
        """Возвращает историю переписки."""
        response = self.session.query(self.Posts)
        if contact_name:
            response = response.filter(
                or_(self.Posts.user_from == contact_name, self.Posts.user_to == contact_name))
        messages = []
        for message in response.all():
            messages.append(
                (message.user_from,
                 message.user_to,
                 message.post,
                 message.created_at))
        return messages

    def save_message(self, user_from: str, user_to: str, post: str):
        """Сохраняет в базе историю сообщений."""
        message = self.Posts(user_from, user_to, post)
        self.session.add(message)
        self.session.commit()

    def add_users(self, users_list):
        """Заполняет таблицу зарегистрированных пользователей."""
        self.session.query(self.Users).delete()
        for user in users_list:
            new_user = self.Users(user)
            self.session.add(new_user)
        self.session.commit()

    def clear_contacts(self):
        """Очищает таблицу контактов."""
        self.session.query(self.Contacts).delete()

    def check_contact(self, contact_name):
        """Проверяет, существует ли контакт."""
        return self.session.query(self.Contacts).filter_by(contact_name=contact_name).count()

    def check_user(self, user_name):
        """Проверяет, существует ли пользователь."""
        return self.session.query(self.Users).filter_by(user_name=user_name).count()


if __name__ == '__main__':
    client_name = 'client1'
    test_db = ClientStorage(client_name)

    test_db.add_contact('client2')
    test_db.add_contact('client3')
    test_db.add_contact('client4')
    print(test_db.get_contacts())

    test_db.add_contact('client4')
    print(test_db.get_contacts())

    test_db.save_message('client1', 'client2', 'Hi, client2')
    test_db.save_message('client2', 'client1', 'Hello, client1')
    test_db.save_message('client1', 'client3', 'Hi, client3')
    print(test_db.get_message_history())
    print(test_db.get_message_history('client2'))

    test_db.remove_contact('client4')
    print(test_db.get_contacts())

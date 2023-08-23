#!/usr/bin/python3
from models import storage
from models.user import User

def get_user_by_email(email):
    session = storage.get_session()
    user = session.query(User).filter(User.Email == email).first()
    session.close()
    return user

def get_user_by_username(username):
    session = storage.get_session()
    user = session.query(User).filter(User.UserName == username).first()
    session.close()
    return user
from app import db, models
from models import User
from flask import request


def user_exists(username):
    q = db.session.query(User).filter(User.name == username)
    return db.session.query(q.exists()).scalar()


def get_user_id(username):
    user = get_user_by_username(username)
    return user.id


def get_user_by_username(username):
    user = models.User.query.filter(User.name == username).first()
    return user


def get_message_repr_as_dict(message):
    return {'id': message.id,
            'from': get_username(message.sender_id),
            'to': get_username(message.receiver_id),
            'message': message.message,
            'timestamp': message.timestamp
            }


def get_username(user_id):
    user = models.User.query.get(user_id)
    return user.name

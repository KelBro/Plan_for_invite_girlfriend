from flask import session

from app.models.user import User


SESSION_KEY = "user_uuid"


def save_user(user):
    session[SESSION_KEY] = user.uuid


def get_user():
    uuid = session.get(SESSION_KEY)
    if uuid is None:
        return None
    return User.query.filter_by(uuid=uuid).first()

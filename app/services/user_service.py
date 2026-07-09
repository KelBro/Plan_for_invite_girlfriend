from flask import request

from app.extensions import db
from app.models.answer import Answer
from app.models.user import User


def create_user():
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")

    user = User(ip=ip, user_agent=user_agent)
    db.session.add(user)
    db.session.commit()

    answer = Answer(user_id=user.id)
    db.session.add(answer)
    db.session.commit()

    return user

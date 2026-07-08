import random
import string

from app.extensions import db
from app.models.tg_code import TelegramCode


def _generate_code():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=8))


def create_code_for_user(user_id):
    code_value = _generate_code()
    while TelegramCode.query.filter_by(code=code_value).first():
        code_value = _generate_code()
    tc = TelegramCode(code=code_value, user_id=user_id, active=True)
    db.session.add(tc)
    db.session.commit()
    return tc


def validate_code(code_value):
    tc = TelegramCode.query.filter_by(code=code_value, active=True).first()
    return tc


def activate_code(code_value, telegram_id):
    tc = TelegramCode.query.filter_by(code=code_value).first()
    if not tc:
        return None
    tc.telegram_id = telegram_id
    tc.active = False
    db.session.commit()
    return tc


def get_code_by_user_id(user_id):
    return TelegramCode.query.filter_by(user_id=user_id).first()

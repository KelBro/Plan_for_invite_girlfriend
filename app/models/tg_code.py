from datetime import datetime

from app.extensions import db


class TelegramCode(db.Model):

    __tablename__ = "telegram_codes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    code = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    telegram_id = db.Column(
        db.BigInteger,
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return self.code
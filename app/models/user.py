import uuid

from datetime import datetime

from app.extensions import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    uuid = db.Column(
        db.String(36),
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False
    )

    telegram_id = db.Column(
        db.BigInteger,
        nullable=True
    )

    ip = db.Column(
        db.String(100)
    )

    user_agent = db.Column(
        db.Text
    )

    finished = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    answer = db.relationship(
        "Answer",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.uuid}>"
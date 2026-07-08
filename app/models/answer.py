from datetime import datetime

from app.extensions import db


class Answer(db.Model):

    __tablename__ = "answers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    meeting_date = db.Column(
        db.Date,
        nullable=True
    )

    meeting_time = db.Column(
        db.Time,
        nullable=True
    )

    meeting_place = db.Column(
        db.String(255),
        nullable=True
    )

    food_id = db.Column(
        db.Integer,
        db.ForeignKey("foods.id")
    )

    answer6 = db.Column(
        db.Boolean
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="answer"
    )

    food = db.relationship(
        "Food",
        back_populates="answers"
    )
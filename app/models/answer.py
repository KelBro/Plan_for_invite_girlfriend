from datetime import datetime

from app.extensions import db


answer_foods = db.Table(
    "answer_foods",
    db.Column(
        "answer_id",
        db.Integer,
        db.ForeignKey("answers.id"),
        primary_key=True,
    ),
    db.Column(
        "food_id",
        db.Integer,
        db.ForeignKey("foods.id"),
        primary_key=True,
    ),
)


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

    foods = db.relationship(
        "Food",
        secondary=answer_foods,
        back_populates="answers"
    )

from app.extensions import db
from app.models.answer import answer_foods


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    emoji = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)

    answers = db.relationship("Answer", secondary=answer_foods, back_populates="foods")

    def __repr__(self):
        return self.name

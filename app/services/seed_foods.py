from app.extensions import db
from app.models.food import Food

foods = [

    ("Суши", "🍣"),
    ("Пицца", "🍕"),
    ("Паста", "🍝"),
    ("Бургер", "🍔"),
    ("Стейк", "🥩"),
    ("Роллы", "🍱"),
    ("Шашлык", "🍖"),
    ("Рамен", "🍜"),
    ("Салат", "🥗"),
    ("Десерт", "🍰"),
    ("Мороженое", "🍨"),
    ("Кофе", "☕"),
    ("Чай", "🫖"),
    ("Блины", "🥞"),
    ("Тако", "🌮")

]


def seed():

    if Food.query.count():

        return

    for name, emoji in foods:

        db.session.add(
            Food(
                name=name,
                emoji=emoji
            )
        )

    db.session.commit()

    print("Foods added.")
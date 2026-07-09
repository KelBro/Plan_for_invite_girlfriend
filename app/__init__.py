from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import User, Food, Answer
    from app.routes.main import main_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        from app.services.seed_foods import seed
        seed()
        _migrate_food_to_many_to_many(app)

    return app


def _migrate_food_to_many_to_many(app):
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    if "answer_foods" not in inspector.get_table_names():
        return

    try:
        answer_columns = {col["name"] for col in inspector.get_columns("answers")}
    except Exception:
        return

    if "food_id" not in answer_columns:
        return

    count = db.session.execute(text("SELECT COUNT(*) FROM answer_foods")).scalar()
    if count:
        return

    rows = db.session.execute(
        text("SELECT id, food_id FROM answers WHERE food_id IS NOT NULL")
    ).fetchall()

    for answer_id, food_id in rows:
        db.session.execute(
            text("INSERT INTO answer_foods (answer_id, food_id) VALUES (:answer_id, :food_id)"),
            {"answer_id": answer_id, "food_id": food_id},
        )

    db.session.commit()
    app.logger.info("Migrated %s food selections to answer_foods", len(rows))

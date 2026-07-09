import os
import random
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.models.food import Food
from app.models.user import User
from app.services.session_service import get_user, save_user
from app.services.user_service import create_user

main_bp = Blueprint("main", __name__)


def _petals():
    glyphs = ["🌸", "🌷", "💗", "🌺", "✿", "❀"]
    arr = []
    for i in range(10):
        arr.append({
            "glyph": glyphs[i % len(glyphs)],
            "left": str(round((i * 9.5 + 4) % 96)) + "%",
            "size": str(16 + (i % 4) * 6) + "px",
            "dur": str(9 + (i % 5) * 2) + "s",
            "delay": "-" + str(round(i * 1.7, 1)) + "s",
        })
    return arr


def _audio_url():
    audio_dir = os.path.join(
        current_app.static_folder or "app/static",
        "audio"
    )
    if not os.path.isdir(audio_dir):
        return ""
    files = [
        f for f in os.listdir(audio_dir)
        if os.path.isfile(os.path.join(audio_dir, f)) and not f.startswith(".")
    ]
    if not files:
        return ""
    return url_for("static", filename=f"audio/{files[0]}")


def _ensure_user():
    user = get_user()
    if user is None:
        user = create_user()
        save_user(user)
    return user


def _fmt_date(d):
    if not d:
        return "—"
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    return f"{d.day} {months[d.month - 1]} {d.year}"


@main_bp.route("/")
def index():
    return redirect(url_for("main.step1"))


@main_bp.route("/step/1", methods=["GET", "POST"])
def step1():
    if request.method == "POST":
        _ensure_user()
        return redirect(url_for("main.step2"))
    return render_template("step1.html", petals=_petals())


@main_bp.route("/step/2")
def step2():
    _ensure_user()
    return render_template("step2.html", petals=_petals(), audio_url=_audio_url())


@main_bp.route("/step/3", methods=["GET", "POST"])
def step3():
    user = _ensure_user()
    answer = user.answer

    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        time_str = request.form.get("time", "").strip()
        place = request.form.get("place", "").strip()

        if not date_str or not time_str or not place:
            return render_template(
                "step3.html",
                petals=_petals(),
                date=date_str,
                time=time_str,
                place=place,
                error="Пожалуйста, заполни все поля 🌸",
            )

        try:
            answer.meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            answer.meeting_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return render_template(
                "step3.html",
                petals=_petals(),
                date=date_str,
                time=time_str,
                place=place,
                error="Неверный формат даты или времени",
            )

        answer.meeting_place = place
        db.session.commit()
        return redirect(url_for("main.step4"))

    return render_template(
        "step3.html",
        petals=_petals(),
        date=answer.meeting_date.isoformat() if answer.meeting_date else "",
        time=answer.meeting_time.strftime("%H:%M") if answer.meeting_time else "",
        place=answer.meeting_place or "",
    )


@main_bp.route("/step/4", methods=["GET", "POST"])
def step4():
    user = _ensure_user()
    answer = user.answer

    if not answer.meeting_date or not answer.meeting_time or not answer.meeting_place:
        return redirect(url_for("main.step3"))

    if request.method == "POST":
        food_id = request.form.get("food_id", "").strip()
        if food_id:
            answer.food_id = int(food_id)
            db.session.commit()
        return redirect(url_for("main.step5"))

    foods = Food.query.filter_by(active=True).order_by(Food.id).all()
    return render_template(
        "step4.html",
        petals=_petals(),
        foods=foods,
        selected_food_id=answer.food_id,
    )


@main_bp.route("/step/5")
def step5():
    user = _ensure_user()
    answer = user.answer

    if not answer.food_id:
        return redirect(url_for("main.step4"))

    return render_template(
        "step5.html",
        petals=_petals(),
        phrase=current_app.config.get("PHRASE5"),
    )


@main_bp.route("/step/6", methods=["GET", "POST"])
def step6():
    user = _ensure_user()
    answer = user.answer

    if not answer.food_id:
        return redirect(url_for("main.step4"))

    if request.method == "POST":
        value = request.form.get("answer", "").strip()
        if value == "yes":
            answer.answer6 = True
        elif value == "no":
            answer.answer6 = False
        db.session.commit()
        return redirect(url_for("main.step7"))

    return render_template(
        "step6.html",
        petals=_petals(),
        phrase=current_app.config.get("PHRASE6"),
        answer6=answer.answer6,
    )


@main_bp.route("/step/7")
def step7():
    user = _ensure_user()
    answer = user.answer

    if answer.answer6 is None:
        return redirect(url_for("main.step6"))

    if answer.food_id:
        food = Food.query.get(answer.food_id)
    else:
        food = None

    if not user.finished:
        user.finished = True
        db.session.commit()

    # Финальный commit, чтобы гарантировать сохранение всех ответов
    db.session.commit()

    return render_template(
        "step7.html",
        petals=_petals(),
        final_phrase=current_app.config.get("FINAL_PHRASE"),
        date_out=_fmt_date(answer.meeting_date),
        time_out=answer.meeting_time.strftime("%H:%M") if answer.meeting_time else "—",
        place_out=answer.meeting_place or "—",
        food_out=f"{food.emoji} {food.name}" if food else "на твой вкус",
        answer_out="Да 💗" if answer.answer6 is True else "Неа 🙈",
        code=None,
    )

from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.food import Food
from app.models.user import User
from app.services.session_service import get_user, save_user
from app.services.user_service import create_user

api_bp = Blueprint("api", __name__)


@api_bp.post("/start")
def start():
    user = get_user()
    if user is None:
        user = create_user()
        save_user(user)
    return jsonify({"success": True, "uuid": user.uuid})


@api_bp.get("/me")
def me():
    user = get_user()
    if user is None:
        return jsonify({"success": False}), 401
    ans = user.answer
    food = None
    if ans and ans.food_id:
        f = Food.query.get(ans.food_id)
        if f:
            food = {"id": f.id, "name": f.name, "emoji": f.emoji}
    return jsonify({
        "success": True,
        "date": ans.meeting_date.isoformat() if ans and ans.meeting_date else None,
        "time": ans.meeting_time.strftime("%H:%M") if ans and ans.meeting_time else None,
        "place": ans.meeting_place or "",
        "food": food,
        "answer6": ans.answer6,
        "finished": user.finished,
    })


@api_bp.get("/foods")
def foods():
    foods_list = Food.query.filter_by(active=True).all()
    result = [{"id": f.id, "name": f.name, "emoji": f.emoji} for f in foods_list]
    return jsonify(result)


@api_bp.post("/meeting")
def meeting():
    user = get_user()
    if user is None:
        return jsonify({"success": False, "message": "Session expired"}), 401
    data = request.json or {}
    date = data.get("date")
    time = data.get("time")
    place = data.get("place")
    if not date or not time or not place:
        return jsonify({"success": False, "message": "Заполните все поля"}), 400
    answer = user.answer
    try:
        answer.meeting_date = datetime.strptime(date, "%Y-%m-%d").date()
        answer.meeting_time = datetime.strptime(time, "%H:%M").time()
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Неверный формат даты или времени"}), 400
    answer.meeting_place = place.strip()
    db.session.commit()
    return jsonify({"success": True})


@api_bp.post("/food")
def choose_food():
    user = get_user()
    if user is None:
        return jsonify({"success": False}), 401
    data = request.json or {}
    food_id = data.get("food_id")
    answer = user.answer
    answer.food_id = food_id
    db.session.commit()
    return jsonify({"success": True})


@api_bp.post("/question")
def question():
    user = get_user()
    if user is None:
        return jsonify({"success": False}), 401
    data = request.json or {}
    answer6 = data.get("answer")
    user.answer.answer6 = answer6
    db.session.commit()
    return jsonify({"success": True})


@api_bp.post("/finish")
def finish():
    user = get_user()
    if user is None:
        return jsonify({"success": False}), 401
    user.finished = True
    db.session.commit()
    return jsonify({"success": True})




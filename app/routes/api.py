from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from app.extensions import db
from app.models.food import Food
from app.models.tg_code import TelegramCode
from app.models.user import User
from app.services.code_service import create_code_for_user, validate_code, activate_code
from app.services.meeting_service import get_meeting_summary_by_user
from app.services.session_service import get_user, save_user
from app.services.telegram_service import send_message
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
    tc = TelegramCode.query.filter_by(user_id=user.id).first()
    if not tc:
        tc = create_code_for_user(user.id)

    admin_id = current_app.config.get("ADMIN_CHAT_ID")
    if admin_id:
        try:
            summary = get_meeting_summary_by_user(user) or "Данные не найдены"
            text = (
                f"✅ Девушка завершила приглашение!\n\n"
                f"🔑 Код: <code>{tc.code}</code>\n\n"
                f"{summary}"
            )
            send_message(admin_id, text, parse_mode="HTML")
        except Exception:
            current_app.logger.exception("Failed to notify admin")

    return jsonify({"success": True, "code": tc.code})


@api_bp.post("/check-code")
def check_code():
    data = request.json or {}
    code_value = data.get("code", "").strip().upper()
    telegram_id = data.get("telegram_id")
    tc = validate_code(code_value)
    if not tc:
        return jsonify({"success": False, "message": "Код не найден или уже использован"}), 404
    user = User.query.get(tc.user_id)
    if not user:
        return jsonify({"success": False, "message": "Данные не найдены"}), 404
    summary = get_meeting_summary_by_user(user)
    if not summary:
        return jsonify({"success": False, "message": "Данные не найдены"}), 404
    if telegram_id:
        activate_code(code_value, telegram_id)
    return jsonify({"success": True, "summary": summary})


@api_bp.get("/code")
def get_code():
    user = get_user()
    if user is None:
        return jsonify({"success": False}), 401
    tc = TelegramCode.query.filter_by(user_id=user.id).first()
    if tc:
        return jsonify({"success": True, "code": tc.code})
    return jsonify({"success": False, "message": "Code not generated yet"}), 404

from app.models.user import User
from app.models.food import Food


def get_meeting_summary_by_user(user):
    if not user or not user.answer:
        return None
    ans = user.answer
    food_name = "не выбрано"
    if ans.food_id:
        food = Food.query.get(ans.food_id)
        if food:
            food_name = f"{food.emoji} {food.name}"
    date_str = ""
    if ans.meeting_date:
        date_str = ans.meeting_date.strftime("%d.%m.%Y") if hasattr(ans.meeting_date, "strftime") else str(ans.meeting_date)
    time_str = ""
    if ans.meeting_time:
        time_str = ans.meeting_time.strftime("%H:%M") if hasattr(ans.meeting_time, "strftime") else str(ans.meeting_time)
    answer6 = "Да 💗" if ans.answer6 else "Неа 🙈" if ans.answer6 is False else "не ответила"
    text = (
        f"📋 <b>Результаты приглашения</b>\n\n"
        f"📅 <b>Дата:</b> {date_str or '—'}\n"
        f"⏰ <b>Время:</b> {time_str or '—'}\n"
        f"📍 <b>Место:</b> {ans.meeting_place or '—'}\n"
        f"🍽️ <b>Еда:</b> {food_name}\n"
        f"💭 <b>Ответ:</b> {answer6}\n"
    )
    return text

from app.extensions import db
from app.models.answer import Answer
from app.models.user import User


def get_or_create_telegram_user(telegram_id, username=None, first_name=None, last_name=None):
    """
    Ищет пользователя по telegram_id. Если не находит — создаёт новую запись
    в таблице users.
    """
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if user:
        return user, False

    display_name = " ".join(
        part for part in [first_name, last_name] if part
    ) or (f"@{username}" if username else "Telegram пользователь")

    user = User(
        telegram_id=telegram_id,
        ip="telegram",
        user_agent=f"Telegram: {display_name}".strip(),
    )

    db.session.add(user)
    db.session.commit()

    return user, True


def get_answers_summary():
    """
    Возвращает отформатированный текст со всеми записями из таблицы answers.
    """
    answers = Answer.query.order_by(Answer.created_at.desc()).all()
    if not answers:
        return "Пока никто не заполнил опрос."

    lines = [f"📋 Результаты опроса ({len(answers)} записей):\n"]
    for ans in answers:
        user = ans.user
        user_label = (
            f"tg:{user.telegram_id}"
            if user.telegram_id
            else f"uuid:{user.uuid[:8]}..."
        )

        food_name = "не выбрано"
        if ans.foods:
            food_name = ", ".join(f"{f.emoji} {f.name}" for f in ans.foods)

        date_str = (
            ans.meeting_date.strftime("%d.%m.%Y")
            if ans.meeting_date
            else "—"
        )
        time_str = (
            ans.meeting_time.strftime("%H:%M")
            if ans.meeting_time
            else "—"
        )
        answer6 = (
            "Да 💗"
            if ans.answer6 is True
            else "Неа 🙈"
            if ans.answer6 is False
            else "—"
        )

        lines.append(
            f"👤 Пользователь: {user_label}\n"
            f"📅 Дата: {date_str}\n"
            f"⏰ Время: {time_str}\n"
            f"📍 Место: {ans.meeting_place or '—'}\n"
            f"🍽️ Еда: {food_name}\n"
            f"💭 Ответ: {answer6}"
        )

    return "\n---\n".join(lines)


def split_message(text, max_len=4000):
    """
    Разбивает длинное сообщение на части, чтобы не превысить лимит Telegram.
    """
    if len(text) <= max_len:
        return [text]

    parts = text.split("\n---\n")
    result = []
    current = ""

    for part in parts:
        separator = "\n---\n" if current else ""
        if len(current) + len(separator) + len(part) > max_len:
            if current:
                result.append(current)
            current = part
        else:
            current = current + separator + part

    if current:
        result.append(current)

    return result if result else [text[:max_len]]

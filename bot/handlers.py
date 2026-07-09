from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.config import ADMIN_CHAT_ID
from bot.services import get_or_create_telegram_user, get_answers_summary, split_message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    user, created = get_or_create_telegram_user(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )

    name = first_name or username or "друг"

    # Если это администратор — отправляем все ответы из таблицы answers
    if ADMIN_CHAT_ID and telegram_id == ADMIN_CHAT_ID:
        summary = get_answers_summary()
        for part in split_message(summary):
            await message.answer(part)
        return

    if created:
        await message.answer(
            f"Привет, {name}! 👋\n\n"
            f"Я бот для приглашения на свидание. "
            f"Ты сохранён(а) в базе под ID {telegram_id}."
        )
    else:
        await message.answer(
            f"С возвращением, {name}! 💫\n\n"
            f"Ты уже есть в базе под ID {telegram_id}."
        )

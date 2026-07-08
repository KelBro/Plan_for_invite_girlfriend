import logging

import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import DOMAIN
from bot.keyboards import get_start_keyboard, remove_keyboard
from bot.states import CodeStates

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "💌 <b>Привет!</b>\n\n"
        "Это бот для просмотра результатов приглашения на свидание.\n\n"
        "Введи код, который ты получил, чтобы узнать все детали встречи 💕",
        parse_mode="HTML",
        reply_markup=get_start_keyboard()
    )


@router.message(F.text == "🔑 Ввести код")
async def ask_code(message: Message, state: FSMContext):
    await state.set_state(CodeStates.waiting_for_code)
    await message.answer(
        "Введи код из 8 символов (буквы и цифры):",
        reply_markup=remove_keyboard
    )


@router.message(CodeStates.waiting_for_code)
async def process_code(message: Message, state: FSMContext, http_session: aiohttp.ClientSession):
    code = message.text.strip().upper()

    if len(code) != 8 or not code.isalnum():
        await message.answer(
            "❌ Неверный формат кода. Код состоит из 8 букв и цифр.\n"
            "Попробуй ещё раз:"
        )
        return

    try:
        async with http_session.post(
            f"{DOMAIN}/api/check-code",
            json={"code": code, "telegram_id": message.from_user.id},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            data = await resp.json()

        if resp.status == 200 and data.get("success"):
            text = data.get("summary", "Данные не найдены.")
            await message.answer(
                f"✅ <b>Код принят!</b>\n\n{text}",
                parse_mode="HTML"
            )
            await state.clear()
            await message.answer(
                "Чтобы проверить другой код, нажми /start",
                reply_markup=get_start_keyboard()
            )
        else:
            await message.answer(
                f"❌ {data.get('message', 'Код не найден или уже использован.')}\n"
                "Попробуй ещё раз или нажми /start"
            )
    except Exception:
        logger.exception("Failed to check code via API")
        await message.answer(
            "❌ Ошибка соединения с сервером. Попробуй позже.\n"
            "Нажми /start чтобы начать заново."
        )

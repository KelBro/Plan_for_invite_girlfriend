import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.handlers import router

logging.basicConfig(level=logging.INFO)


async def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN not set in .env")
        return

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    async with aiohttp.ClientSession() as http_session:
        dp = Dispatcher()
        dp["http_session"] = http_session
        dp.include_router(router)

        logging.info("Bot started")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

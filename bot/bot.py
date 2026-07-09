from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.handlers import router
from bot.middleware import AppContextMiddleware


def create_bot():
    return Bot(token=BOT_TOKEN)


def create_dispatcher(app):
    dp = Dispatcher()
    dp.update.middleware(AppContextMiddleware(app))
    dp.include_router(router)
    return dp

import asyncio

from app import create_app
from bot.bot import create_bot, create_dispatcher


async def main():
    app = create_app()
    bot = create_bot()
    dp = create_dispatcher(app)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

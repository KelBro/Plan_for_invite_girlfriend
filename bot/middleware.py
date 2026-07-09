from aiogram import BaseMiddleware


class AppContextMiddleware(BaseMiddleware):
    """
    Открывает Flask app context на время обработки каждого обновления от Telegram,
    чтобы хендлеры могли работать с SQLAlchemy.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, handler, event, data):
        with self.app.app_context():
            return await handler(event, data)

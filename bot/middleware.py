from aiogram import BaseMiddleware


class AppContextMiddleware(BaseMiddleware):
    def __init__(self, app):
        self.app = app

    async def __call__(self, handler, event, data):
        with self.app.app_context():
            return await handler(event, data)

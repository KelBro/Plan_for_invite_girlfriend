import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-key-change-me"

    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or "sqlite:///instance/invitation.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JSON_AS_ASCII = False

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")

    PHRASE5 = os.getenv("PHRASE5") or (
        "Кстати… ты даже не представляешь, как я рад(а), "
        "что дочитала до этого места 🥰"
    )

    PHRASE6 = os.getenv("PHRASE6") or (
        "Обещаю, это будет лучший вечер. Ты мне веришь?"
    )

    FINAL_PHRASE = os.getenv("FINAL_PHRASE") or (
        "Значит, всё решено. Я тебя жду!"
    )

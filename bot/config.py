import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv("BOT_TOKEN")

_raw_admin_id = os.getenv("ADMIN_CHAT_ID")
ADMIN_CHAT_ID = int(_raw_admin_id.strip()) if _raw_admin_id and _raw_admin_id.strip().isdigit() else None

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле")

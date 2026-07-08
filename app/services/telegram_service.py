import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, parse_mode="HTML"):
    import requests
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"Telegram send error: {e}")
        return None

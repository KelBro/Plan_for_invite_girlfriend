from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔑 Ввести код")]
        ],
        resize_keyboard=True
    )


remove_keyboard = ReplyKeyboardRemove()

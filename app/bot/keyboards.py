from typing import List
from telegram import ReplyKeyboardMarkup


def create_currencies_keyboard(currencies: List[str]) -> ReplyKeyboardMarkup:
    """Creates a keyboard with currency buttons."""
    keyboard = []

    for i in range(0, len(currencies), 2):
        row = currencies[i : i + 2]
        keyboard.append(row)

    keyboard.append(["Ввести свой код"])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

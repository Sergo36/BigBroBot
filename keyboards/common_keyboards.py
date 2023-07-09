from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_null_keyboard() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    return kb.as_markup()
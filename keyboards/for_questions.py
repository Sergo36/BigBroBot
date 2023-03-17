from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def getKeyboardFromNodes(nodes: list) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for node in nodes:
        kb.button(text=node)
    kb.button(text="Clear")
    kb.adjust(len(nodes), 1)
    return kb.as_markup(resize_keyboard=True)

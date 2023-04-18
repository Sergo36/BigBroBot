from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def getKeyboardFromNodes(nodes: list) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for node in nodes:
        kb.button(text=node)
    kb.button(text="Cancel")
    kb.adjust(len(nodes), 1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_from_id(id_list: list) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for id in id_list:
        kb.button(text=id)
    kb.button(text="Cancel")
    kb.adjust(len(id_list), 1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_node_instance() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Payment")
    kb.button(text="Cancel")
    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_node_type(type_list: list) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for type in type_list:
        kb.button(text=type)
    kb.button(text="Cancel")
    kb.adjust(len(type_list), 1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_accept() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Confirm")
    kb.button(text="Cancel")
    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True)

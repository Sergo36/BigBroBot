from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard_from_nodes(nodes: list) -> ReplyKeyboardMarkup:
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
    kb.button(text="Tasks")
    kb.button(text="Cancel")
    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_tasks() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Hash node task")
    kb.button(text="Restart node task")
    kb.button(text="Backup keys task")
    kb.button(text="Delete node task")
    kb.button(text="Restore node task")
    kb.button(text="Close port task")
    kb.button(text="Open port task")
    kb.button(text="Turning off container task")
    kb.button(text="Cancel")
    kb.adjust(3, 2, 2, 1, 1)
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


def get_keyboard_for_actions(actions_list: list) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for action in actions_list:
        kb.button(text=action)
    kb.button(text="Cancel")
    kb.adjust(len(actions_list), 1)
    return kb.as_markup(resize_keyboard=True)
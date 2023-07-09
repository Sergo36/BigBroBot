from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.account_callback_factory import AccountCallbackFactory
from callbacks.main_callback_factory import MainCallbackFactory


def get_keyboard_for_account_list(query) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    index = 1
    for row in query:
        kb.button(
            text=f"{index}) {row.name}",
            callback_data=AccountCallbackFactory(action="select_account", node_id=row.id))
        index = index + 1
    kb.adjust(2)
    mm_button = InlineKeyboardButton(
        text="Главное меню",
        callback_data=MainCallbackFactory(action="main_menu").pack())
    kb.row(mm_button)
    return kb.as_markup()


def get_keyboard_for_account_instance(account_id) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Пополнить", callback_data=AccountCallbackFactory(
        action="replenish_account", account_id=account_id))
    kb.button(text="Главное меню", callback_data=MainCallbackFactory(
        action="main_menu"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_replenish_account() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=AccountCallbackFactory(
        action="back_step_account"))
    kb.button(text="Главное меню", callback_data=MainCallbackFactory(
        action="main_menu"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

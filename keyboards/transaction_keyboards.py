from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.transactions_callback_factory import TransactionsCallbackFactory


def get_keyboard_for_transaction_fail(back_step: CallbackData) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Пробовать еще раз", callback_data=TransactionsCallbackFactory(
        action="try_again"))
    kb.button(text="Назад", callback_data=back_step)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_transaction_verify(back_step: CallbackData) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=back_step)
    kb.button(text="Главное меню", callback_data=MainCallbackFactory(
        action="main_menu"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
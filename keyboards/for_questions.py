from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.account_callback_factory import AccountCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.order_callback_factory import OrderCallbackFactory
from callbacks.main_callback_factory import MainCallbackFactory


def get_keyboard_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="\U0001F6D2 Новый заказ", callback_data=OrderCallbackFactory(action="new_order")
    )
    builder.button(
        text="🗂Мои ноды", callback_data=NodesCallbackFactory(action="nodes_list")
    )
    builder.button(
        text="\U0001F4B0 Мой счет", callback_data=AccountCallbackFactory(action="accounts_list")
    )
    builder.adjust(2)
    return builder.as_markup()


def get_keyboard_for_nodes_list(query) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    index = 1
    for row in query:
        kb.button(
            text=f"{index}) {row.name}",
            callback_data=NodesCallbackFactory(action="select_node", node_id=row.id))
        index = index + 1
    kb.adjust(2)
    mm_button = InlineKeyboardButton(
        text="Главное меню",
        callback_data=MainCallbackFactory(action="main_menu").pack())
    kb.row(mm_button)
    return kb.as_markup()


def get_keyboard_for_empty_nodes_list() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Новый заказ",
        callback_data=OrderCallbackFactory(action="new_order")
    )
    kb.button(
        text="Главное меню",
        callback_data=MainCallbackFactory(action="main_menu")
    )
    return kb.as_markup()


def get_keyboard_for_node_instance() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Оплатить со счета", callback_data=NodesCallbackFactory(
        action="account_payment"))
    kb.button(text="💸 Оплатить за валюту", callback_data=NodesCallbackFactory(
        action="cash_payment"))
    kb.button(text="📕 Расширенная информация", callback_data=NodesCallbackFactory(
        action="extended_information"))
    kb.button(text="🔄 Взаимодействия", callback_data=NodesCallbackFactory(
        action="interaction"))
    kb.button(text="🗑 Отменить заказ", callback_data=NodesCallbackFactory(
        action="confirm_obsolete"))
    kb.button(text="Назад к списку нод", callback_data=NodesCallbackFactory(
        action="nodes_list"))
    kb.adjust(2, 2, 1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_node_extended_information(node) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к выбранной ноде", callback_data=NodesCallbackFactory(
        action="select_node", node_id=node.id))
    kb.button(text="Назад к списку нод", callback_data=NodesCallbackFactory(
        action="nodes_list"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_account_node_payment(back_step: CallbackData) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=back_step)
    kb.button(text="Главное меню", callback_data=MainCallbackFactory(
        action="main_menu"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_obsolete_node(node):
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data=NodesCallbackFactory(
        action="obsolete_node",
        node_id=node.id))
    kb.button(text="Нет", callback_data=NodesCallbackFactory(
        action="select_node",
        node_id=node.id))
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_after_obsolete_node():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к списку нод", callback_data=NodesCallbackFactory(
        action="nodes_list"))
    kb.button(text="Главное меню", callback_data=MainCallbackFactory(
        action="main_menu"))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_node_type(query):
    kb = InlineKeyboardBuilder()
    for node_type in query:
        kb.button(
            text=node_type.name,
            callback_data=OrderCallbackFactory(action="select_type", node_type_id=node_type.id))
    kb.adjust(2)

    individual = InlineKeyboardButton(
        text="Индивидуальный заказ",
        callback_data=OrderCallbackFactory(action="individual_order").pack())
    kb.row(individual)

    mm_button = InlineKeyboardButton(
        text="Главное меню",
        callback_data=MainCallbackFactory(action="main_menu").pack())
    kb.row(mm_button)
    return kb.as_markup()


def get_keyboard_for_accept() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Подтвердить",
        callback_data=OrderCallbackFactory(action="confirm"))
    kb.button(
        text="Отмена",
        callback_data=OrderCallbackFactory(action="new_order"))
    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True)


def get_keyboard_for_order_confirm(node) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Оплатить заказ",
        callback_data=NodesCallbackFactory(action="select_node", node_id=node.id))
    kb.button(
        text="Главное меню",
        callback_data=MainCallbackFactory(action="main_menu"))
    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True)

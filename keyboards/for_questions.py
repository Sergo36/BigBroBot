from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.account_callback_factory import AccountCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.payments_callback_factory import PaymentsCallbackFactory
from callbacks.order_callback_factory import OrderCallbackFactory
from callbacks.main_callback_factory import MainCallbackFactory


def get_keyboard_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🖥 Ноды", callback_data=MainCallbackFactory(action="nodes_menu")
    ),
    builder.button(
        text="🌐 Прокси", callback_data=MainCallbackFactory(action="proxy_menu")
    )
    builder.adjust(2)
    return builder.as_markup()


def get_keyboard_for_nodes_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="\U0001F6D2 Новый заказ", callback_data=OrderCallbackFactory(action="new_order")
    )
    builder.button(
        text="🗂 Мои ноды", callback_data=NodesCallbackFactory(action="nodes_list")
    )
    builder.button(
        text="\U0001F4B0 Мой счет", callback_data=AccountCallbackFactory(action="accounts_list")
    )
    builder.button(
        text="💬 Чат \"Ноды\"", url="https://t.me/+Fbg3iiAgx1ViNTZi"
    )
    builder.adjust(2)
    return builder.as_markup()


def get_keyboard_for_nodes_list(query) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    add_node_buttons(query, kb)
    kb.adjust(2)
    add_archive_button(kb)
    add_main_menu_button(kb)
    return kb.as_markup()


def get_keyboard_for_nodes_list_archive(query) -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    add_node_buttons(query, kb)
    kb.adjust(2)
    add_main_menu_button(kb)
    return kb.as_markup()


def add_node_buttons(query, kb):
    for row in query:
        kb.button(
            text=f"({row.id}) {row.name}",
            callback_data=NodesCallbackFactory(action="select_node", node_id=row.id))


def get_keyboard_for_empty_nodes_list() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    add_new_order_button(kb)
    add_archive_button(kb)
    add_main_menu_button(kb)
    return kb.as_markup()


def get_keyboard_for_empty_nodes_list_archive() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    add_new_order_button(kb)
    add_main_menu_button(kb)
    return kb.as_markup()


def add_new_order_button(kb):
    archive_button = InlineKeyboardButton(
        text="Новый заказ",
        callback_data=OrderCallbackFactory(action="new_order").pack())
    kb.row(archive_button)


def add_archive_button(kb):
    archive_button = InlineKeyboardButton(
        text="Архив нод",
        callback_data=NodesCallbackFactory(action="archive").pack())
    kb.row(archive_button)


def add_main_menu_button(kb):
    mm_button = InlineKeyboardButton(
        text="Главное меню",
        callback_data=MainCallbackFactory(action="main_menu").pack())
    kb.row(mm_button)


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
    kb.button(text="История платежей", callback_data=NodesCallbackFactory(
        action="payments_history", node_id=node.id))
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
    for row in query:
        text = f'{row.type_name}(∞)' if row.limit < 0 else f'{row.type_name}({row.limit - row.node_count})'
        kb.button(
            text=text,
            callback_data=OrderCallbackFactory(action="select_type", node_type_id=row.id))
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


def get_default_keyboard_for_order():
    kb = InlineKeyboardBuilder()
    kb.button(text="Главное меню", callback_data=MainCallbackFactory(
        action="main_menu"))
    kb.adjust(1)
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


def get_keyboard_for_payments_type(payments, node):
    kb = InlineKeyboardBuilder()
    for pay in payments:
        kb.button(text=f"{pay.contract_name}", callback_data=PaymentsCallbackFactory(payment_id=pay.id))

    kb.button(text="Назад к выбранной ноде", callback_data=NodesCallbackFactory(
        action="select_node", node_id=node.id))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
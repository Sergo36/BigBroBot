from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.notification_callback_factory import NotificationCallbackFactory


def get_keyboard_main_notification():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Send notification", callback_data=NotificationCallbackFactory(action="send")
    )
    builder.adjust(1)
    return builder.as_markup()


def get_keyboard_for_node_type(query):
    kb = InlineKeyboardBuilder()
    for node_type in query:
        kb.button(
            text=node_type.name,
            callback_data=NotificationCallbackFactory(action="select_type", node_type_id=node_type.id))
    kb.adjust(len(query))
    return kb.as_markup()


def get_keyboard_for_payment_notification(node_id):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Payment",
        callback_data=NotificationCallbackFactory(
            action="payment_node",
            node_id=node_id))
    kb.button(
        text="Main menu",
        callback_data=MainCallbackFactory(action="main_menu"))
    return kb.as_markup()
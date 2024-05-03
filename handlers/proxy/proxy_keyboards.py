from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.report_callback_factory import ProxyNextActionCallbackFactory, ProxyDeviceListCallbackFactory


def get_keyboard_for_complete_action():
    builder = InlineKeyboardBuilder()
    builder.button(text="Далее", callback_data=ProxyNextActionCallbackFactory(action="next"))
    return builder.as_markup()


def get_keyboard_for_last_action():
    kb = InlineKeyboardBuilder()
    kb.button(text="Главное меню", callback_data=MainCallbackFactory(
        action="new_main_menu"))
    kb.adjust(1)
    return kb.as_markup()
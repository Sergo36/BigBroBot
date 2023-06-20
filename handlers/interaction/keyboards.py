from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory


def get_keyboard_for_interactions(interactions):
    kb = InlineKeyboardBuilder()
    for interaction in interactions:
        kb.button(
            text=interaction.name,
            callback_data=interaction.callback)
    kb.adjust(3)
    return kb.as_markup()


def get_keyboard_default_interaction():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Назак к списку взаимодействий",
        callback_data=NodesCallbackFactory(action="interaction")
    )
    kb.button(
        text="Главное меню",
        callback_data=MainCallbackFactory(action="main_menu")
    )
    return kb.as_markup()

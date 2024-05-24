from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory


def get_keyboard_for_interactions(q_common, q_node, node):
    kb = InlineKeyboardBuilder()
    for interaction in q_common:
        kb.button(
            text=interaction.name,
            callback_data=interaction.callback)
    for interaction in q_node:
        kb.button(
            text=interaction.name,
            callback_data=interaction.callback)
    kb.adjust(1)

    back_button = InlineKeyboardButton(
        text="Назад к выбранной ноде",
        callback_data=NodesCallbackFactory(action="select_node", node_id=node.id).pack())
    kb.row(back_button)

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

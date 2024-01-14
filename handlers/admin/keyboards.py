from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.nodes_callback_factory import NodesCallbackFactory


def get_keyboard_for_node_overview():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Node data",
        callback_data=NodesCallbackFactory(action="extended_information"))
    kb.button(
        text="Interaction",
        callback_data=NodesCallbackFactory(action="interaction"))
    kb.adjust(1)
    return kb.as_markup()

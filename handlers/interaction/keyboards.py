from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_keyboard_for_interactions(interactions):
    kb = InlineKeyboardBuilder()
    for interaction in interactions:
        kb.button(
            text=interaction.name,
            callback_data=interaction.callback)
    kb.adjust(3)
    return kb.as_markup()

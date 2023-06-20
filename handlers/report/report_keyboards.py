from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.report_callback_factory import ReportCallbackFactory


def get_keyboard_payments_report(query):
    builder = InlineKeyboardBuilder()
    for row in query:
        builder.button(
            text=row.name,
            callback_data=ReportCallbackFactory(action="get_report", node_type=row.id)
        )
    builder.adjust(3)
    all_button = InlineKeyboardButton(
        text="Все ноды",
        callback_data=ReportCallbackFactory(action="get_report", node_type=0).pack())
    builder.row(all_button)
    return builder.as_markup()

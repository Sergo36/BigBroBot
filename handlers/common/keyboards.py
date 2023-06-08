from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.report_callback_factory import ReportCallbackFactory


def get_keyboard_for_report():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Payments report", callback_data=ReportCallbackFactory(action="payments_report")
    )
    builder.adjust(1)
    return builder.as_markup()

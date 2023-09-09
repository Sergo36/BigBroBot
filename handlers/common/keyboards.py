from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.report_callback_factory import ReportCallbackFactory


def get_keyboard_for_report():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отчет по платежам", callback_data=ReportCallbackFactory(action="payments_report")
    )
    builder.button(
        text="Отчет по Subspace", callback_data=ReportCallbackFactory(action="subspace_report")
    )
    builder.adjust(1)
    return builder.as_markup()

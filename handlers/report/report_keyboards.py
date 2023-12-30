from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.report_callback_factory import ReportCallbackFactory, UserReportCallbackFactory, DbViewCallbackFactory


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


def get_user_action_report_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Список транзакций",
        callback_data=DbViewCallbackFactory(table="transactions"))
    builder.button(
        text="Список нод",
        callback_data=DbViewCallbackFactory(table="nodes"))

    builder.adjust(1)
    return builder.as_markup()


def get_nodes_action_report_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Список платежей",
        callback_data=DbViewCallbackFactory(table="payments"))

    builder.adjust(1)
    return builder.as_markup()


def get_db_view_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Список пользователей",
        callback_data=DbViewCallbackFactory(table="users"))
    builder.button(
        text="Данные нод",
        callback_data=DbViewCallbackFactory(table="nodes_data"))
    builder.adjust(1)

    return builder.as_markup()

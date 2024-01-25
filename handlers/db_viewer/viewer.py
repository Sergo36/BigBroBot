import math
from typing import Optional

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.mesage_formater import table_message


class TableMessageCallbackFactory(CallbackData, prefix="table_message"):
    action: str
    new_page: Optional[int] = None


router = Router()


@router.callback_query(
    TableMessageCallbackFactory.filter(F.action == "page_change"))
async def page_change(
        callback: types.CallbackQuery,
        callback_data: TableMessageCallbackFactory,
        state: FSMContext):
    await state.update_data(current_page=callback_data.new_page)
    await create_message(state, callback)


async def show_data(
        state: FSMContext,
        callback: types.CallbackQuery,
        back_step=None):
    await state.update_data(current_page=1)
    await create_message(state, callback, back_step)


async def create_message(state: FSMContext, callback: types.CallbackQuery, back_step=None):
    data = await state.get_data()
    current_page = data.get('current_page')
    db_table = data.get('db_table')
    data_count = 10
    last_page = math.trunc((len(db_table) - 1) / data_count) + 1

    if current_page <= 0 or current_page > last_page:
        await callback.answer()
        return

    await callback.message.edit_text(
        text=f"`{table_message(db_table, (current_page - 1) * data_count, current_page * data_count)}`",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_keyboard_for_table_message(current_page, last_page, back_step))


def get_keyboard_for_table_message(current_page: int, last_page: int, back_step=None):
    builder = InlineKeyboardBuilder()

    if last_page > 1:
        buttons = []
        buttons.append(
            InlineKeyboardButton(text="<--",
                                 callback_data=TableMessageCallbackFactory(action='page_change',
                                                                           new_page=current_page - 1).pack())
            if current_page != 1
            else InlineKeyboardButton(text="|",
                                      callback_data=TableMessageCallbackFactory(action='null',
                                                                                new_page=current_page).pack())
        )

        buttons.append(
            InlineKeyboardButton(text=f'{current_page} / {last_page}',
                                 callback_data=TableMessageCallbackFactory(action='null',
                                                                           new_page=current_page).pack())
        )

        buttons.append(
            InlineKeyboardButton(text="-->",
                                 callback_data=TableMessageCallbackFactory(action='page_change',
                                                                           new_page=current_page + 1).pack())
            if current_page != last_page
            else InlineKeyboardButton(text="|",
                                      callback_data=TableMessageCallbackFactory(action='null',
                                                                                new_page=current_page).pack())
        )
        builder.row(*buttons)
        callback_data = TableMessageCallbackFactory(action="exit")
        if back_step is not None:
            callback_data = back_step
        builder.row(InlineKeyboardButton(text="Назад",
                                         callback_data=callback_data.pack()))
    return builder.as_markup()

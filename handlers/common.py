from random import randint

from aiogram import Bot, Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.parse_mode import ParseMode

import config
from data.database import get_nodes
from botStates import States
from data.entity.node_type import NodeType
from keyboards.for_questions import get_keyboard_from_id, get_keyboard_for_node_type
from middleware.user import UsersMiddleware

router = Router()
router.message.middleware(UsersMiddleware())

from typing import Optional
from aiogram.filters.callback_data import CallbackData
from magic_filter import F
class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int]


user_data = {}


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        text="Choose a section from the list below:",
        reply_markup=get_keyboard_main_menu()
    )


@router.message(Command('nodes'))
@router.callback_query(Text(text="nodes_list"))
async def nodes(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')

    user_nodes = get_nodes(user.id)
    keyboard: None
    text = "Nodes list:\n\n"
    if len(user_nodes) > 0:
        kb_id = []
        text += "Сhoose node by ID\n\n"
        for node in user_nodes:
            text += f'ID: {node.id} -> type: {NodeType(node.type).name}\n'
            kb_id.append(node.id)
            keyboard = get_keyboard_from_id(kb_id)
    else:
        text += 'The list of nodes is empty. Create the first command /order'
        keyboard = ReplyKeyboardRemove()

    await message.answer(
        text=text,
        reply_markup=keyboard
    )
    await state.set_state(States.nodes)


@router.callback_query(Text(text="new_order"))
async def order(callback: types.CallbackQuery, state: FSMContext):
    text = "Сhoose node type\n"
    keyboard = get_keyboard_for_node_type([e.name for e in NodeType])
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )
    await state.set_state(States.order)


@router.message(Command(commands=["cancel"]))
@router.message(Text(text="cancel", ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Action canceled",
        reply_markup=ReplyKeyboardRemove()
    )


######################### examples ############################
async def update_num_text_fab(message: types.Message, new_value: int):
    await message.edit_text(
        f"Укажите число: {new_value}",
        reply_markup=get_keyboard_fab()
    )

@router.message(Command("numbers"))
async def cmd_numbers_fab(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard_fab())


@router.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    user_value = user_data.get(callback.from_user.id, 0)

    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value + callback_data.value)
    await callback.answer()


@router.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)

    await callback.message.edit_text(f"Итого: {user_value}")
    await callback.answer()



@router.message(Command(commands=["send"]))
async def send_message(message: Message):
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
    await bot.send_message(message.from_user.id, "Hello")


@router.message()
async def unauthorized(message: Message):
    await message.answer(
        text="Use command /start to start the bot ",
        reply_markup=ReplyKeyboardRemove()
    )



def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="-10", callback_data=NumbersCallbackFactory(action="change", value=-10)
    )
    builder.button(
        text="-2", callback_data=NumbersCallbackFactory(action="change", value=-2)
    )
    builder.button(
        text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1)
    )
    builder.button(
        text="+1", callback_data=NumbersCallbackFactory(action="change", value=1)
    )
    builder.button(
        text="+2", callback_data=NumbersCallbackFactory(action="change", value=2)
    )
    builder.button(
        text="+10", callback_data=NumbersCallbackFactory(action="change", value=10)
    )
    builder.button(
        text="Подтвердить", callback_data=NumbersCallbackFactory(action="finish")
    )
    builder.adjust(6)
    return builder.as_markup()

def get_keyboard_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="New order", callback_data="new_order"
    )
    builder.button(
        text="Nodes list", callback_data="nodes_list"
    )
    builder.adjust(2)
    return builder.as_markup()



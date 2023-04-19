from aiogram import Router, F
from data.entity.node_type import NodeType
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from botStates import States
from data.database import get_node_type, set_node
from keyboards.for_questions import get_keyboard_for_accept


router = Router()


@router.message(
    States.order,
    F.text.in_([e.name.__str__() for e in NodeType]))
async def order_type(message: Message, state: FSMContext):
    node_type = get_node_type(message.text)

    await state.update_data(node_type=node_type)

    keyboard = get_keyboard_for_accept()
    await message.answer(text=f'Order cost: {node_type.cost.__str__()}', reply_markup=keyboard)


@router.message(
    States.order,
    Text(text="Confirm", ignore_case=True))
async def confirm_order(message: Message, state: FSMContext):
    data = await state.get_data()
    node_type = data.get('node_type')
    user = data.get('user')

    set_node(node_type, user)
    await message.answer(text="Order approved ", reply_markup=ReplyKeyboardRemove)

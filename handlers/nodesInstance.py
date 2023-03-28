from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from botStates import States
from data.entity.node_type import NodeType
from data.database import get_nodes_info, get_user
from keyboards.for_questions import get_keyboard_from_id

router = Router()


@router.message(
    States.choosing_nodes_type,
    F.text.in_([e.name.__str__() for e in NodeType]))
async def node_type_selection(message: Message, state: FSMContext):
    await state.update_data(chosen_node_type=message.text)
    telegram_id = message.from_user.id
    user = get_user(telegram_id)
    nodes = get_nodes_info(NodeType[message.text].value, user.id)
    text = "Nodes information:\n\n"
    kb_id = []
    for node in nodes:
        text += f'ID: {node.id}' \
                f' Payments date: {node.payment_date.day} of every month' \
                f' Payment state: paid \n\n'
        kb_id.append(node.id)

    text += "Сhoose node by ID"
    keyboard = get_keyboard_from_id(kb_id)
    await message.answer(
        text=text,
        reply_markup=keyboard
    )

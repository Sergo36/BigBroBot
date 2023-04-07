from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from keyboards.for_questions import getKeyboardFromNodes
from botStates import States
from data.database import get_user, getNodes
from data.entity.node_type import NodeType

router = Router()


@router.message(Command('nodes'))
async def nodes(message: Message, state: FSMContext):
    message_id = message.from_user.id
    user = get_user(message_id)
    user_nodes = getNodes(user.id)
    kb_nodes = list(map(lambda n: NodeType(n.type).name, user_nodes))
    keyboard = getKeyboardFromNodes(kb_nodes)
    await message.answer("Choose node type", reply_markup=keyboard)
    await state.set_state(States.nodes)


@router.message(Text(text="Clear", ignore_case=True))
async def clear(message: Message, state: FSMContext):
    await message.answer(
        "Тут должны быть команды",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(States.active)

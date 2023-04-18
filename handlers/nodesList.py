from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from keyboards.for_questions import get_keyboard_from_id
from botStates import States
from data.database import get_user, getNodes
from data.entity.node_type import NodeType

router = Router()


@router.message(Command('nodes'))
async def nodes(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')

    user_nodes = getNodes(user.id)
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

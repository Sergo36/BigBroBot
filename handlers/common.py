from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from data.database import get_nodes
from botStates import States
from data.entity.node_type import NodeType
from keyboards.for_questions import get_keyboard_from_id, get_keyboard_for_node_type
from middleware.user import UsersMiddleware

router = Router()
router.message.middleware(UsersMiddleware())


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        text="Hi i'm a bot from BigBro team",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command('nodes'))
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


@router.message(Command('order'))
async def order(message: Message, state: FSMContext):
    text = "Сhoose node type\n"
    keyboard = get_keyboard_for_node_type([e.name for e in NodeType])
    await message.answer(
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

@router.message()
async def unauthorized(message: Message):
    await message.answer(
        text="Use command /start to start the bot ",
        reply_markup=ReplyKeyboardRemove()
    )

from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from data.database import get_user, getNodes
from botStates import States

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Choose actions:"
             "list nodes (/nodes)"
             "payments history (/payments)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(States.active)


@router.message(Command(commands=["cancel"]))
#@router.message(Text(text="cancel", text_ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Action canceled",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Command(commands=["id"]))
async def cmd_id(message: Message):
    await message.answer(text=message.from_user.username)
    await message.answer(text=message.from_user.id)

@router.message(Command(commands=["datatest"]))
async def cmd_id(message: Message):
    user = get_user(message.from_user.id)
    await message.answer(text=user.id)
    await message.answer(text=user.telegram_name)

@router.message(Command(commands=["nodestest"]))
async def cmd_id(message: Message):
    nodes = getNodes(1)
    c = 5
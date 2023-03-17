from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from keyboards.for_questions import getKeyboardFromNodes
from nodeOwner import owners
from botStates import States

router = Router()


@router.message(Command('nodes'))
async def nodes(message: Message, state: FSMContext):
    messageMention = message.from_user.username
    for owner in owners:
        if (owner.mention == messageMention):
            keyboard = getKeyboardFromNodes(owner.nodes)
            await message.answer("Выберите интересующую ноду", reply_markup=keyboard)
    await state.set_state(States.choosing_nodes)


@router.message(Text(text="Clear", ignore_case=True))
async def clear(message: Message):
    await message.answer(
        "Тут должны быть команды",
        reply_markup=ReplyKeyboardRemove()
    )

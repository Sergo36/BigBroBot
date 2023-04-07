from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from data.database import get_user, getNodes
from botStates import States
from data.database import get_user_by_tn

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user = get_user_by_tn(message.from_user.username)

    if user is None:
        await message.answer(text="User is not found\n\n Seek help from https://t.me/repinSS or https://t.me/sirvmasle")
        return

    await message.answer(
        text="Choose actions:"
             "muon verification (/muon) \n\n",
             #"list nodes (/nodes) \n\n"
             #"payments history (/payments) \n\n"
             #"transaction history (/transaction) \n\n",
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

@router.message(
    States.active,
    Command(commands=["muon"]))
async def muon_verification(message: Message, state: FSMContext):
    await message.answer(text="Введите значение DISCORD_VERIFICATION")
    await state.set_state(States.muonVerification)

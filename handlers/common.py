from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

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
from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import getKeyboardFromNodes
from nodeOwner import owners

router = Router()

@router.message(Text(text="Gravity Bridge", ignore_case=True))
async def gravityBridge(message: Message):
    messageMention = message.from_user.username
    await message.answer(
        "Тут будет информация о ноде Gravity Bridge для пользователя " + messageMention,
        reply_markup=ReplyKeyboardRemove()
    )

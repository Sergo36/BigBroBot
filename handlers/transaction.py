from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from data.database import get_user, get_transactions

router = Router()

@router.message(Command('transactions'))
async def transactions(message: Message, state: FSMContext):
    message_id = message.from_user.id
    user = get_user(message_id)
    user_transactions = get_transactions(user.id)




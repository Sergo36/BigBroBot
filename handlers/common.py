from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from data.database import get_user, getNodes
from botStates import States
from data.database import set_user
from keyboards.for_questions import get_keyboard_for_actions

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = get_user(message.from_user.id)

    if user is None:
        user = set_user(message.from_user.id, message.from_user.username)
        await state.update_data(user=user)
    else:
        await state.update_data(user=user)

    await message.answer(
        text="Hi i'm a bot from BigBro team",
        reply_markup=ReplyKeyboardRemove()
    )

    # keyboard = get_keyboard_for_actions(['Nodes', 'Order'])
    # await message.answer(
    #     text="Choose actions:"
    #          "List nodes (/nodes) \n"
    #          "Order node (/order) \n",
    #     reply_markup=keyboard
    # )
    await state.set_state(States.authorized)


@router.message(Command(commands=["cancel"]))
@router.message(Text(text="cancel", ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Action canceled",
        reply_markup=ReplyKeyboardRemove()
    )

#to do move node type handler
#@router.message(
 #   States.authorized,
  #  Command(commands=["muon"]))
#async def muon_verification(message: Message, state: FSMContext):
 #   await message.answer(text="Введите значение DISCORD_VERIFICATION")
  #  await state.set_state(States.muonVerification)

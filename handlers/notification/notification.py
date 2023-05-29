from aiogram import Router, types, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from magic_filter import F

import config
from botStates import States
from callbacks.notification_callback_factory import NotificationCallbackFactory
from data.models.node import Node
from data.models.node_type import NodeType
from data.models.user import User
from handlers.notification.keyboards import get_keyboard_for_node_type, get_keyboard_main_notification, \
    get_keyboard_for_payment_notification

router = Router()


@router.message(Command(commands=['send']))
async def send_message(message: Message, state: FSMContext):
    await state.set_state(States.notification)
    await message.answer(
        text="Choose a section from the list below:",
        reply_markup=get_keyboard_main_notification()
    )


@router.callback_query(
    States.notification,
    NotificationCallbackFactory.filter(F.action == "send"))
async def order_type(
        callback: types.CallbackQuery,
        state: FSMContext
):
    text = "Choose node type\n"
    query = NodeType.select(NodeType.id, NodeType.name)
    keyboard = get_keyboard_for_node_type(query)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(
    States.notification,
    NotificationCallbackFactory.filter(F.action == "select_type"))
async def notification_type(
        callback: types.CallbackQuery,
        callback_data: NotificationCallbackFactory
):
    query = (User
             .select(User.telegram_id, Node.id)
             .join(Node, on=(User.id == Node.owner))
             .where(Node.type == callback_data.node_type_id))

    bot = Bot(config.TOKEN, parse_mode=ParseMode.HTML)

    for user in query:
        await bot.send_message(
            chat_id=user.telegram_id,
            text="Ploti nologi",
            reply_markup=get_keyboard_for_payment_notification(user.node.id))
    await bot.session.close()

    await callback.answer()

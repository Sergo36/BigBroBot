import asyncio

from aiogram import Router, types, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

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
        text="Выберите действие из списка ниже:",
        reply_markup=get_keyboard_main_notification()
    )


@router.callback_query(
    States.notification,
    NotificationCallbackFactory.filter(F.action == "send"))
async def order_type(
        callback: types.CallbackQuery,
):
    text = "Выберите тип ноды\n"
    query = NodeType.select(NodeType.id, NodeType.name)
    keyboard = get_keyboard_for_node_type(query)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

@router.callback_query(
    States.notification,
    NotificationCallbackFactory.filter(F.action == "node_install")
)
async def install_notification(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Введите номер ноды")


@router.message(
    States.notification,
    F.text.regexp('^[0-9]+$'))
async  def send_notification(message: Message, bot: Bot):
    node = Node.get_or_none(Node.id == message.text)

    if node is None:
        await message.answer(
            text="Нода не найдена\n"
                 "Введите идентификационный номер ноды"
        )
    else:
        await bot.send_message(
            chat_id=node.owner.telegram_id,
            parse_mode=ParseMode.MARKDOWN_V2,
            text=f"Дорогой нодранер, Ваша нода ***{node.type.name}*** установлена\!\n"
                 f"Вся необходимая информация, связанная с нодой, находится в разделе Расширенная информация\n"
                 f"***Ноды \> Мои ноды \> {node.type.name} \> Рассширенная информация***")


@router.callback_query(
    States.notification,
    NotificationCallbackFactory.filter(F.action == "select_type"))
async def notification_type(
        callback: types.CallbackQuery,
        callback_data: NotificationCallbackFactory
):
    query = (User
             .select(User.telegram_id, Node.id, Node.payment_date, NodeType.name, Node.cost)
             .join(Node, on=(User.id == Node.owner))
             .join(NodeType, on=(Node.type == NodeType.id))
             .where(Node.type == callback_data.node_type_id)
             .namedtuples())

    bot = Bot(config.TOKEN, parse_mode=ParseMode.HTML)
    await send_message(query, bot)
    await bot.session.close()
    await callback.answer()


async def send_message(query: any, bot: Bot):
    for row in query:
        try:
            await bot.send_message(
                chat_id=row.telegram_id,
                parse_mode=ParseMode.MARKDOWN_V2,
                text=f"♻️ Дорогой нодранер\! Напоминаем о продлении ноды ***{row.name}***\.\n"
                     f"Стоимость проделния: {str(row.cost).replace('.', ',')} USDT\n"
                     f"Текущий период заканчивается {row.payment_date.day}\-го числа\! \n\n"
                     f"Для продления ноды нажми кнопку «***Payment***» ниже 👇",
                reply_markup=get_keyboard_for_payment_notification(row.id))
            await asyncio.sleep(5)
        except Exception as err:
            print(f"Не удалось отправить уведомление {row.telegram_id}")

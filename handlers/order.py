from datetime import datetime
from aiogram import Router, F, types, Bot
from aiogram.types import Message

from bot_logging.telegram_notifier import TelegramNotifier
from callbacks.order_callback_factory import OrderCallbackFactory
from data.models.node_data import NodeData
from data.models.node_interactions import NodeInteraction
from data.models.node_type import NodeType
from data.models.node import Node
from aiogram.fsm.context import FSMContext
from botStates import States
from keyboards.for_questions import get_keyboard_for_accept, get_keyboard_for_order_confirm, \
    get_default_keyboard_for_order

router = Router()


@router.callback_query(
    States.order,
    OrderCallbackFactory.filter(F.action == "select_type"))
async def order_type(
        callback: types.CallbackQuery,
        callback_data: OrderCallbackFactory,
        state: FSMContext
):
    node_type = NodeType.get(NodeType.id == callback_data.node_type_id)
    limit = node_type.limit
    if limit != -1:
        node_count = Node.select().where((Node.type == callback_data.node_type_id) & (Node.obsolete == False)).count()
        if node_count >= limit:
            await callback.message.edit_text(
                text=f'Превышено максимальное число заказов',
                reply_markup=get_default_keyboard_for_order())
            return

    await state.update_data(node_type=node_type)
    keyboard = get_keyboard_for_accept()
    await callback.message.edit_text(text=f'Стоимость заказа: {node_type.cost.__str__()} USDT', reply_markup=keyboard)


@router.callback_query(
    States.order,
    OrderCallbackFactory.filter(F.action == "confirm"))
async def confirm_order(
        callback: types.CallbackQuery,
        state: FSMContext,
        notifier: TelegramNotifier
):
    data = await state.get_data()
    node_type = data.get('node_type')
    user = data.get('user')

    date = datetime.now()
    node = Node.create(
        owner=user.id,
        type=node_type.id,
        payment_date=date,
        cost=node_type.cost,
        expiry_date=date,
        obsolete=False
    )

    add_information(node)
    add_interaction(node)

    await notifier.emit(callback.from_user.username, f"Заказ ноды {node_type.name} ({node.id})")

    await callback.answer(text="Заказ подтвержден", show_alert=True)
    keyboard = get_keyboard_for_order_confirm(node)
    await callback.message.edit_text(text="Выберете действие из списка ниже:", reply_markup=keyboard)


@router.callback_query(
    States.order,
    OrderCallbackFactory.filter(F.action == "individual_order"))
async def individual_order(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await state.set_state(States.identification_order)
    await callback.message.edit_text("Напишите название проекта в котором вы хотите принять участие.\n" \
                                     "Укажите любую ссылку на контактную информацию проекта (Web site/Docs/GitHub/Discord)")


@router.message(
    States.identification_order)
async def transaction_handler(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(States.order)

    await message.answer(
        text="Заказ принят мы свяжемся с вами для уточнения деталей",
        reply_markup=get_default_keyboard_for_order()
    )

    await bot.send_message(chat_id=-915512097, text=f"Username: @{message.from_user.username}\n" \
                                                    f"Telegram full name: {message.from_user.full_name}\n" \
                                                    f"Message text: {message.text}")


def add_information(node: Node):
    if node.type.id == 8:
        add_information_babylon(node)


def add_information_babylon(node):
    NodeData.create(node_id=node.id, name="Explorer", type=1, data="[babylonscan.io](https://babylonscan.io/validators)")


def add_interaction(node: Node):
    if node.type.id == 8:
        add_interaction_babylon(node)


def add_interaction_babylon(node: Node):
    NodeInteraction.create(node_id=node.id, node_interaction_id=4)

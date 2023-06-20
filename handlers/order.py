from datetime import datetime
from aiogram import Router, F, types
from callbacks.order_callback_factory import OrderCallbackFactory
from data.models.node_type import NodeType
from data.models.node import Node
from aiogram.fsm.context import FSMContext
from botStates import States
from keyboards.for_questions import get_keyboard_for_accept, get_keyboard_for_order_confirm

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
    await state.update_data(node_type=node_type)
    keyboard = get_keyboard_for_accept()
    await callback.message.edit_text(text=f'Стоимость заказа: {node_type.cost.__str__()}', reply_markup=keyboard)


@router.callback_query(
    States.order,
    OrderCallbackFactory.filter(F.action == "confirm"))
async def confirm_order(
        callback: types.CallbackQuery,
        state: FSMContext
):
    data = await state.get_data()
    node_type = data.get('node_type')
    user = data.get('user')
    keyboard = get_keyboard_for_order_confirm()

    date = datetime.now()
    Node.create(
        owner=user.id,
        type=node_type.id,
        payment_date=date,
        cost=node_type.cost,
        expiry_date=date
    )
    await callback.answer(text="Заказ подтвержден", show_alert=True)
    await callback.message.edit_text(text="Выберете действие из списка ниже:", reply_markup=keyboard)

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
    await callback.message.edit_text(text=f'Order cost: {node_type.cost.__str__()}', reply_markup=keyboard)


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

    Node.create(
        owner=user.id,
        type=node_type.id,
        payment_date=datetime.now(),
        cost=node_type.cost,
    )
    await callback.answer(text="Order approved", show_alert=True)
    await callback.message.edit_text(text="Choose a section from the list below:", reply_markup=keyboard)

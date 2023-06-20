from datetime import datetime

from aiogram import Router, F, types

from callbacks.report_callback_factory import ReportCallbackFactory
from data.models.node import Node
from data.models.node_type import NodeType
from data.models.user import User
from handlers.nodes import payment_state
from handlers.report.report_keyboards import get_keyboard_payments_report

router = Router()


@router.callback_query(ReportCallbackFactory.filter(F.action == "payments_report"))
async def callback_payments_report(callback: types.CallbackQuery):
    query = (NodeType
             .select(NodeType.id, NodeType.name)
             .namedtuples())
    await callback.message.edit_text(
        text="Выберете тип ноды из списка ниже:",
        reply_markup=get_keyboard_payments_report(query))


@router.callback_query(ReportCallbackFactory.filter(F.action == "get_report"))
async def callback_get_report(
        callback: types.CallbackQuery,
        callback_data: ReportCallbackFactory):

    if callback_data.node_type == 0:
        query = (Node
                 .select(Node.id, NodeType.name, User.telegram_name)
                 .join(NodeType, on=(Node.type == NodeType.id))
                 .join(User, on=(Node.owner == User.id))
                 .where(Node.expiry_date < datetime.now())
                 .order_by(Node.id)
                 .namedtuples())
    else:
        query = (Node
                 .select(Node.id, NodeType.name, User.telegram_name)
                 .join(NodeType, on=(Node.type == NodeType.id))
                 .join(User, on=(Node.owner == User.id))
                 .where(Node.expiry_date < datetime.now())
                 .where(NodeType.id == callback_data.node_type)
                 .order_by(Node.id)
                 .namedtuples())

    text = "|ID|\tType|\tDuty|\tOwner|\n"
    for row in query:
        node = Node.get(Node.id == row.id)
        duty = payment_state(node)
        temp = f"|{row.id}|\t{row.name}|\t{duty}|\t{row.telegram_name}|\n"
        text += temp
    await callback.message.edit_text(text=text)

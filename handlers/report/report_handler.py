import csv
import io
from datetime import datetime

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from peewee import fn, Field

from botStates import DbViewReportState
from callbacks.report_callback_factory import ReportCallbackFactory, UserReportCallbackFactory, DbViewCallbackFactory
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_data_type import NodeDataType
from data.models.node_payments import NodePayments
from data.models.node_type import NodeType
from data.models.transaction import Transaction
from data.models.user import User
from handlers.db_viewer.viewer import show_data
from handlers.nodes import payment_state
from handlers.report.report_keyboards import get_keyboard_payments_report, get_user_action_report_keyboard, \
    get_nodes_action_report_keyboard, get_db_view_keyboard
from handlers.report.user_report_data import UserReportData, NodeReportData
from services.mesage_formater import table_message

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
                 .where(Node.obsolete == False)
                 .where(Node.expiry_date < datetime.now())
                 .order_by(Node.id)
                 .namedtuples())
    else:
        query = (Node
                 .select(Node.id, NodeType.name, User.telegram_name)
                 .join(NodeType, on=(Node.type == NodeType.id))
                 .join(User, on=(Node.owner == User.id))
                 .where(Node.obsolete == False)
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


@router.callback_query(ReportCallbackFactory.filter(F.action == "subspace_report"))
async def callback_podprobel_report(callback: types.CallbackQuery):
    q = (Node
         .select(Node.id, NodeType.name, Node.expiry_date, User.telegram_name)
         .join(NodeType, on=(Node.type == NodeType.id))
         .join(User, on=(Node.owner == User.id))
         .where(NodeType.name == "Subspace", Node.obsolete == False)
         .order_by(Node.expiry_date, Node.id)
         .namedtuples())
    res = q.execute()
    mylist = [['ID', 'Type', 'Expiry date', 'User']]
    for row in res:
        sq = (NodeData
              .select(NodeData.name, NodeData.data)
              .where(NodeData.node_id == row.id))
        mylist.append([f'{row.id}', f'{row.name}', f'{row.expiry_date}', f'@{row.telegram_name}'])
        sq_res = sq.execute()
        for sq_row in sq_res:
            mylist.append(['', f'{sq_row.name}', f'{sq_row.data}'])
    f = io.StringIO()
    csv.writer(f).writerows(mylist)
    b = bytes(f.getvalue(), encoding='utf-8')

    await callback.message.answer_document(BufferedInputFile(b, "subspace_node.csv"))
    await callback.answer()


@router.callback_query(ReportCallbackFactory.filter(F.action == "db_view"))
async def db_viewer(callback: types.CallbackQuery,):
    await callback.message.edit_text(
        text="Выберите таблицу из списка ниже",
        reply_markup=get_db_view_keyboard())


@router.callback_query(DbViewCallbackFactory.filter(F.table == "users"))
async def callback_users_report(
        callback: types.CallbackQuery,
        state: FSMContext):

    await state.set_state(DbViewReportState.UserSelect)

    query = (User
             .select(User.id.alias("ID"), User.telegram_name.alias("Name"))
             .order_by(User.telegram_name)
             .namedtuples())

    res = query.execute()
    await state.update_data(db_table=res)
    await show_data(state, callback)
    await callback.message.answer(text="Введите идентификационный номер пользоателя")


@router.message(
    DbViewReportState.UserSelect,
    F.text.regexp('^[0-9]+$'))
async def user_select(
        message: Message,
        state: FSMContext):
    user = User.get_or_none(User.id == message.text)
    if user is None:
        await message.answer(
            text="Пользователь не найден\n"
                 "Введите идентификационный номер пользователя"
        )
    else:
        report_data = UserReportData()
        report_data.user = user
        await state.update_data(report_data=report_data)

        await message.answer(
            text=f'Выбран пользователь : {user.telegram_name}\n'
                 f'Выберете раздел из списка ниже',
            reply_markup=get_user_action_report_keyboard()
        )


@router.callback_query(DbViewCallbackFactory.filter(F.table == "transactions"))
async def user_report_transaction(
        callback: types.CallbackQuery,
        state: FSMContext):
    data = await state.get_data()
    report_data: UserReportData = data.get('report_data')

    query = (Transaction
             .select(Transaction.transaction_date.alias("Date"), Transaction.value.alias("Value"))
             .where(Transaction.owner == report_data.user.id)
             .order_by( Transaction.transaction_date.desc())
             .namedtuples())
    res = query.execute()

    await state.update_data(db_table=res)
    await show_data(state, callback)


@router.callback_query(DbViewCallbackFactory.filter(F.table == "nodes"))
async def user_report_transaction(
        callback: types.CallbackQuery,
        state: FSMContext):
    await state.set_state(DbViewReportState.NodeSelect)

    data = await state.get_data()
    report_data: UserReportData = data.get('report_data')

    query = (Node
             .select(Node.id.alias("ID"), NodeType.name.alias("Type"), Node.expiry_date.alias("Expiry"))
             .join(NodeType, on=(Node.type == NodeType.id))
             .where(Node.owner == report_data.user.id)
             .order_by(Node.id)
             .namedtuples())
    res = query.execute()

    await state.update_data(db_table=res)
    await show_data(state, callback)

    await callback.message.answer(
        text="Введите идентификационный номер ноды")


@router.message(
    DbViewReportState.NodeSelect,
    F.text.regexp('^[0-9]+$'))
async def node_select(
        message: Message,
        state: FSMContext):
    node = Node.get_or_none(Node.id == message.text)

    if node is None:
        await message.answer(
            text="Нода не найдена\n"
                 "Введите идентификационный номер ноды"
        )
    else:
        report_data = NodeReportData()
        report_data.node = node
        await state.update_data(report_data=report_data)

        await message.answer(
            text=f'Выбрана нода : {node.type.name} Пользователь : {node.owner.telegram_name}\n'
                 f'Выберете раздел из списка ниже',
            reply_markup=get_nodes_action_report_keyboard()
        )


@router.callback_query(DbViewCallbackFactory.filter(F.table == "payments"))
async def user_report_transaction(
        callback: types.CallbackQuery,
        state: FSMContext):
    data = await state.get_data()
    report_data: NodeReportData = data.get('report_data')

    query = (NodePayments
             .select(NodePayments.payment_date.alias("Date"), NodePayments.value.alias("Value"))
             .where(NodePayments.node_id == report_data.node.id)
             .order_by(NodePayments.payment_date)
             .namedtuples())
    res = query.execute()

    await state.update_data(db_table=res)
    await show_data(state, callback)


@router.callback_query(DbViewCallbackFactory.filter(F.table == "nodes_data"))
async def nodes_data(
    callback: types.CallbackQuery,
    state: FSMContext
):
    await state.set_state(DbViewReportState.NodeSelectForNodeData)
    await callback.message.answer(
        text="Введите идентификационный номер ноды")
    await callback.answer()


@router.message(
    DbViewReportState.NodeSelectForNodeData,
    F.text.regexp('^[0-9]+$'))
async def node_select_for_node_data(
        message: Message,
        state: FSMContext):
    node = Node.get_or_none(Node.id == message.text)
    await state.update_data(node=node)

    if node is None:
        await message.answer(
            text="Нода не найдена\n"
                 "Введите идентификационный номер ноды"
        )
    else:
        node_data = (
            NodeData.select(NodeData.name, NodeData.data)
            .join(NodeDataType, on=(NodeData.type == NodeDataType.id))
            .where(NodeData.node_id == node.id)
            .where(NodeDataType.name == "Obligatory")
            .namedtuples())
        text = "Расширенная информация\n"
        for data in node_data:
            data_text = data.data.replace('.', '\\.')
            text += f"\n*{data.name}*: {data_text}"

        await message.answer(
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2)


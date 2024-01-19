from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from peewee import fn

from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.order_callback_factory import OrderCallbackFactory

from data.models.node_type import NodeType
from data.models.node import Node
from handlers.common.keyboards import get_keyboard_for_report

from keyboards.for_questions import get_keyboard_for_node_type, \
    get_keyboard_for_nodes_list, get_keyboard_for_empty_nodes_list, get_keyboard_main_menu
from middleware.user import UsersMiddleware

from botStates import States
from magic_filter import F

router = Router()
router.message.middleware(UsersMiddleware())
router.callback_query.middleware(UsersMiddleware())


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        text="Выберете раздел из списка ниже:",
        reply_markup=get_keyboard_main_menu()
    )


@router.callback_query(MainCallbackFactory.filter(F.action == "main_menu"))
async def callback_start(
        callback: types.CallbackQuery
):
    await callback.message.edit_text(
        text="Выберете раздел из списка ниже:",
        reply_markup=get_keyboard_main_menu())


@router.callback_query(NodesCallbackFactory.filter(F.action == "nodes_list"))
async def nodes(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')

    user_nodes = (
        Node.select(Node.id, NodeType.name)
        .join(NodeType, on=(Node.type == NodeType.id))
        .where(Node.owner == user.id, Node.obsolete == False)
        .order_by(Node.id)
        .namedtuples())
    keyboard: None
    if len(user_nodes) > 0:
        text = "Выберете ноду из списка ниже:"
        keyboard = get_keyboard_for_nodes_list(user_nodes)
    else:
        text = 'Список нод пуст. Закажите первую!!!'
        keyboard = get_keyboard_for_empty_nodes_list()

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(OrderCallbackFactory.filter(F.action == "new_order"))
async def order(callback: types.CallbackQuery, state: FSMContext):
    text = "Выберете проект:\n"
    query = (
        NodeType.select(NodeType.id.alias('id'), NodeType.name.alias('type_name'), NodeType.limit.alias('limit'), fn.Count(Node.id).alias('node_count'))
        .left_outer_join(Node, on=((NodeType.id == Node.type) & (Node.obsolete == False)))
        .where(NodeType.obsolete == False)
        .group_by(NodeType.id, NodeType.name))

    keyboard = get_keyboard_for_node_type(query)
    await state.set_state(States.order)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.message(Command(commands=["report"]))
async def report(message: Message):
    await message.answer(
        text="Выберете тип отчета из списка ниже:",
        reply_markup=get_keyboard_for_report()
    )





from aiogram import Router, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import config
from botStates import States
from web3 import Web3
from data.entity.node_type import NodeType
from data.database import get_nodes_info, get_user, get_node, get_payment_data, get_last_not_paid_payment, \
    create_new_payment, set_transaction
from data.entity.transaction import Transaction
from keyboards.for_questions import get_keyboard_from_id, get_keyboard_for_node_instance

router = Router()


@router.message(
    States.nodes,
    F.text.in_([e.name.__str__() for e in NodeType]))
async def node_type_selection(message: Message, state: FSMContext):
    # await state.update_data(chosen_node_type=message.text)
    telegram_id = message.from_user.id
    user = get_user(telegram_id)
    nodes = get_nodes_info(NodeType[message.text].value, user.id)
    text = "Nodes information:\n\n"
    kb_id = []
    for node in nodes:
        text += f'ID: {node.id}' \
                f' Payments date: {node.payment_date.day} of every month' \
                f' Payment state: paid \n\n'
        kb_id.append(node.id)

    text += "Сhoose node by ID"
    keyboard = get_keyboard_from_id(kb_id)
    await message.answer(
        text=text,
        reply_markup=keyboard
    )


@router.message(
    States.nodes,
    F.text.regexp('^\d+$'))
async def select_node(message: Message, state: FSMContext):
    node = get_node(message.text)

    if node.id == 0:
        await message.answer(
            text="no such node exists",
            reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(node=node)

    text = "Node information:\n\n"
    text += f' Payments date: {node.payment_date.day} of every month' \
            f' Payment state: paid \n\n'

    keyboard = get_keyboard_for_node_instance()
    await message.answer(
        text=text,
        reply_markup=keyboard
    )


@router.message(
    States.nodes,
    Text(text="Payment", ignore_case=True))
async def payment(message: Message, state: FSMContext):
    wallet_address = get_payment_data()
    data = await state.get_data()
    node = data.get('node')

    # to do use state.get_data()
    telegram_id = message.from_user.id
    user = get_user(telegram_id)

    payment = get_last_not_paid_payment(user.id, node.id)
    if payment is None:
        payment = create_new_payment(user.id, node.id)

    await state.update_data(payment=payment)

    text = f'To pay, transfer {node.cost} USDT to {wallet_address}\n\n' \
           f'After confirming the transaction, send the hash of the transaction'
    await message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(
    States.nodes,
    F.text.regexp('0[x][0-9a-fA-F]{64}'))
async def check_hash(message: Message, state: FSMContext):
    transaction_hash = message.text
    rpc = config.RPC
    web3 = Web3(Web3.HTTPProvider(rpc))
    txn = web3.eth.get_transaction(transaction_hash)
    trn = Transaction(transaction_hash, txn)

    # to do use state.get_data()
    telegram_id = message.from_user.id
    user = get_user(telegram_id)

    data = await state.get_data()
    payment = data.get('payment')

    set_transaction(trn, user, payment)

    await message.answer(
        text=txn.value,
        reply_markup=ReplyKeyboardRemove()
    )

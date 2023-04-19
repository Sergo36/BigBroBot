import datetime
from dateutil.relativedelta import relativedelta
from eth_utils.units import units
from aiogram.enums.parse_mode import ParseMode

from aiogram.types.message import Message
import psycopg2
from aiogram import Router, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from hexbytes import HexBytes

import config
from botStates import States
from web3 import Web3
from web3.exceptions import TransactionNotFound
from data.entity.node import Node
from data.database import get_user, get_node, get_payment_data, set_transaction, get_transaction_for_node
from data.entity.transaction import Transaction
from keyboards.for_questions import get_keyboard_for_node_instance


router = Router()


@router.message(
    States.nodes,
    F.text.regexp('^\d+$'))
async def select_node(message: Message, state: FSMContext):
    node = get_node(message.text)

    if node.id == 0:
        await message.answer(
            text="No such node exists",
            reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(node=node)

    difference = payment_state(node)
    paid_text = ("Not paid", "Paid")[difference >= 0]
    text1 = (f"duty: {difference}", f"prepaid: {difference}")[difference >= 0]

    text = "Node information:\n\n"
    text += f'Payments date: {node.payment_date.day} of every month\n' \
            f'Payment state: {paid_text}, {text1}'\

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

    text = f"To pay, transfer `{node.cost}` USDT in BEP20 chain to `{wallet_address}`\n\n" \
            f"After confirming the transaction, send the hash of the transaction\n"
    await message.answer(
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(
    States.nodes,
    F.text.regexp('0[x][0-9a-fA-F]{64}'))
async def check_hash(message: Message, state: FSMContext):
    transaction_hash = message.text
    rpc = config.RPC
    web3 = Web3(Web3.HTTPProvider(rpc))
    try:
        txn = web3.eth.get_transaction_receipt(transaction_hash)
    except TransactionNotFound:
        await message.answer(
            text="Error: Transaction not found.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    except Exception:
        await message.answer(
            text="Error: Unexpected error.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    contract_address = txn.logs[0].address
    contract = web3.eth.contract(contract_address, abi=config.ERC20_ABI)
    token_decimals = contract.functions.decimals().call()

    trn = Transaction().initialisation_transaction(transaction_hash, token_decimals, txn)

    if not transaction_valid(trn):
        await message.answer(
            text="Error: Transaction not valid.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    data = await state.get_data()
    user = data.get('user')
    node = data.get('node')

    try:
        set_transaction(trn, user, node)
    except psycopg2.errors.UniqueViolation:
        await message.answer(
            text="Error: Transaction already exists.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    except Exception as err:
        await message.answer(
            text="Error: Unexpected error.",
            reply_markup=ReplyKeyboardRemove()
        )
        return


    await message.answer(
        text="Transaction approved",
        reply_markup=ReplyKeyboardRemove()
    )


def transaction_valid(transaction: Transaction) -> bool:
    wallet_address = HexBytes(get_payment_data())
    transction_to = HexBytes(transaction.transaction_to)
    return not (False in ([_a == _b for _a, _b in zip(reversed(wallet_address), reversed(transction_to))]))


def payment_state(node: Node) -> float:
    delta = relativedelta(datetime.datetime.now(), node.payment_date)
    duty = (delta.months + 1) * node.cost

    transactions = get_transaction_for_node(node)
    transactions_sum: float = 0
    for transaction in transactions:
        unit = (unit_name(transaction.decimal), "ether")[transaction.decimal == None]
        transactions_sum += float(Web3.from_wei(Web3.to_int(hexstr=transaction.value), unit))
    paid = transactions_sum
    return paid - duty


def unit_name(decimal) -> str:
    for name, places in units.items():
        if places == (10 ** decimal):
            return name
    return None
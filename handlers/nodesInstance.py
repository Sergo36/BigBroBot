import datetime
import os, zipfile

from dateutil.relativedelta import relativedelta
from eth_utils.units import units
from aiogram.enums.parse_mode import ParseMode

import psycopg2
from aiogram import Router, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from hexbytes import HexBytes

from paramiko import SSHClient
from scp import SCPClient

import config
from botStates import States
from web3 import Web3
from web3.exceptions import TransactionNotFound
from data.entity.node import Node
from data.database import get_user, get_node, get_payment_data, set_transaction, get_transaction_for_node
from data.entity.transaction import Transaction
from keyboards.for_questions import get_keyboard_for_node_instance, get_keyboard_for_tasks



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
            f'Payment state: {paid_text}, {text1}\n' \
            f'Server IP: {node.server_ip}'

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
    Text(text="Tasks", ignore_case=True))
async def payment(message: Message, state: FSMContext):
    text = f"Select task"
    keyboard = get_keyboard_for_tasks()
    await message.answer(
        text=text,
        reply_markup=keyboard
    )


@router.message(States.nodes,
                Text(text="Hash node task", ignore_case=True))
async def hash_node_task(message: Message, state: FSMContext):
    creation_hash = (await state.get_data()).get("node").hash
    text = f"`{creation_hash}`"
    await message.answer(
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(States.nodes,
                Text(text="Restart node task", ignore_case=True))
async def restart_node_task(message: Message, state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    screenshot_path = f"{config.FILE_BASE_PATH}/{telegram_id}/restart.png"

    if not os.path.exists(screenshot_path):
        text = "Not found"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await message.answer_photo(screenshot_file)


@router.message(States.nodes,
                Text(text="Backup keys task", ignore_case=True))
async def backup_keys_task(message: Message, state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    node = (await state.get_data()).get("node")

    directory = "backup"
    parent_dir = f"{config.FILE_BASE_PATH}/{telegram_id}/"
    if not os.path.isdir(parent_dir):
        os.mkdir(parent_dir)
    local_path = os.path.join(parent_dir, directory)
    if not os.path.isdir(local_path):
        os.mkdir(local_path)

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=node.server_ip, username='root')
    scp = SCPClient(ssh.get_transport())

    remote_path = '/app/.data/keys/'
    scp.get(remote_path=remote_path,
            local_path=local_path,
            recursive=True)
    scp.close()
    ssh.close()

    file_path = os.path.join(local_path, 'keys')
    file_dir = os.listdir(file_path)
    zip_path = os.path.join(local_path, 'keys.zip')

    with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file in file_dir:
            add_file = os.path.join(file_path, file)
            zf.write(add_file, file)

    backup_file = FSInputFile(zip_path)
    await message.answer_document(backup_file)


@router.message(States.nodes,
                Text(text="Delete node task", ignore_case=True))
async def delete_node_task(message: Message, state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    screenshot_path = f"{config.FILE_BASE_PATH}/{telegram_id}/delete.png"

    if not os.path.exists(screenshot_path):
        text = "Not found"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await message.answer_photo(screenshot_file)


@router.message(States.nodes,
                Text(text="Restore node task", ignore_case=True))
async def restore_node_task(message: Message, state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    screenshot_path = f"{config.FILE_BASE_PATH}/{telegram_id}/restore.png"

    if not os.path.exists(screenshot_path):
        text = "Not found"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await message.answer_photo(screenshot_file)

@router.message(States.nodes,
                Text(text="Close port task", ignore_case=True))
async def close_port_task(message: Message, state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    screenshot_path = f"{config.FILE_BASE_PATH}/{telegram_id}/close_port.png"

    if not os.path.exists(screenshot_path):
        text = "Not found"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await message.answer_photo(screenshot_file)

@router.message(States.nodes,
                Text(text="Open port task", ignore_case=True))
async def close_port_task(message: Message, state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    screenshot_path = f"{config.FILE_BASE_PATH}/{telegram_id}/open_port.png"

    if not os.path.exists(screenshot_path):
        text = "Not found"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await message.answer_photo(screenshot_file)

@router.message(States.nodes,
                Text(text="Turning off container task", ignore_case=True))
async def close_port_task(message: Message, state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    screenshot_path = f"{config.FILE_BASE_PATH}/{telegram_id}/turoff_container.png"

    if not os.path.exists(screenshot_path):
        text = "Not found"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await message.answer_photo(screenshot_file)

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

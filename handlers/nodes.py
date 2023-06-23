from datetime import datetime

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dateutil.relativedelta import relativedelta
from eth_utils.units import units
from peewee import IntegrityError
from web3 import Web3
from web3.exceptions import TransactionNotFound

from botStates import States
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.notification_callback_factory import NotificationCallbackFactory
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_data_type import NodeDataType
from data.models.node_fields import NodeFields
from data.models.payment_data import PaymentData
from data.models.transaction import Transaction
from keyboards.for_questions import get_keyboard_for_node_instance, \
    get_keyboard_null, get_keyboard_for_node_extended_information, get_keyboard_for_transaction_fail
from services.web3 import get_block_date
from middleware.user import UsersMiddleware
from services.web3 import get_transaction, transaction_valid

router = Router()
router.callback_query.middleware(UsersMiddleware())


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "select_node"))
async def select_node(
        callback: types.CallbackQuery,
        callback_data: NodesCallbackFactory,
        state: FSMContext
):
    node = Node.get(Node.id == callback_data.node_id)
    await state.update_data(node=node)

    difference = payment_state(node)
    paid_text = ("Не оплачено", "Оплачено")[difference >= 0]
    text1 = (f"долг: {difference}", f"предоплата: {difference}")[difference >= 0]

    text = "Информация о ноде:\n\n"
    text += f'Дата платежа: {node.payment_date.day} числа каждого месяца\n' \
            f'Статус оплаты: {paid_text}, {text1}'

    await callback.message.edit_text(
        text=text,
        reply_markup=get_keyboard_for_node_instance()
    )


@router.callback_query(
    NotificationCallbackFactory.filter(F.action == "payment_node"))
async def notification_payment(
        callback: types.CallbackQuery,
        callback_data: NotificationCallbackFactory,
        state: FSMContext):
    node = Node.get(Node.id == callback_data.node_id)
    await state.update_data(node=node)
    await state.set_state(States.nodes)
    await payment(callback, state)


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "payment_node"))
async def nodes_payment(callback: types.CallbackQuery, state: FSMContext):
    await payment(callback, state)


async def payment(callback: types.CallbackQuery, state: FSMContext):
    wallet_address = PaymentData.get(PaymentData.active == True).wallet_address
    data = await state.get_data()
    node = data.get('node')

    text = f"Для оплаты, переведите `{node.cost}` USDT в сети BEP20 на адрес `{wallet_address}`\n\n" \
           f"После подтверждения транзакции сетью, отправьте хеш транзакции ответным сообщением\n"
    await callback.message.edit_text(
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_keyboard_for_node_extended_information(node),
    )
    await state.update_data(callback=callback)


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "extended_information"))
async def information_node(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    node = data.get('node')

    node_data = (
        NodeData.select(NodeData.name, NodeData.data)
        .join(NodeFields, on=(NodeData.id == NodeFields.node_data_id))
        .join(NodeDataType, on=(NodeData.type == NodeDataType.id))
        .where(NodeFields.node_id == node.id)
        .where(NodeDataType.name == "Obligatory")
        .namedtuples())
    text = "Расширенная информация\n"
    for data in node_data:
        text += f"\n{data.name}: {data.data}"

    await callback.message.edit_text(text=text, reply_markup=get_keyboard_for_node_extended_information(node))


@router.message(
    States.nodes,
    F.text.regexp('0[x][0-9a-fA-F]{64}'))
async def check_hash(message: Message, state: FSMContext):
    transaction_hash = message.text
    await message.delete()
    data = await state.get_data()
    user = data.get('user')
    node = data.get('node')
    callback = data.get('callback')
    if callback is None:
        return

    await callback.message.edit_text(text="Проверка транзакции в блокчейне: ожидание", reply_markup=get_keyboard_null())
    trn, error_text = get_transaction_blockchain(transaction_hash)

    if trn is None:
        await callback.message.edit_text(
            text="Проверка транзакции в блокчейне: провал\n"
                 f"\t\t{error_text}",
            reply_markup=get_keyboard_for_transaction_fail(node))
        return

    await callback.message.edit_text(text="Проверка транзакции в блокчейне: OK\n"
                                          "Сохранение транзакции в базе данных: ожидание",
                                     reply_markup=get_keyboard_null())

    trn.owner = user.id
    trn.node_id = node.id

    ok, error_text = save_transaction(trn)

    if not ok:
        await callback.message.edit_text(text="Проверка транзакции в блокчейне: OK\n"
                                              "Сохранение транзакции в базе данных: провал\n"
                                              f"\t\t{error_text}",
                                         reply_markup=get_keyboard_for_transaction_fail(node))
        return

    node.expiry_date = get_expiry_date(node)
    node.save()
    await state.update_data(node=node)

    await callback.message.edit_text(text="Проверка транзакции в блокчейне: OK\n"
                                          "Сохранение транзакции в базе данных: OK\n"
                                          "Транзакция подтверждена\n\n"
                                          "Выберете действие из списка ниже:",
                                     reply_markup=get_keyboard_for_node_extended_information(node))
    await state.update_data(callback=None)


def get_transaction_blockchain(transaction_hash: str):
    try:
        trn = get_transaction(transaction_hash)
    except TransactionNotFound:
        text = "Ошибка: Транзакция не найдена в блокчейне."
        return None, text
    except Exception:
        text = "Ошибка: Непредвиденная ошибка."
        return None, text

    if not transaction_valid(trn):
        text = "Ошибка: Транзакция не валидна."
        return None, text

    try:
        t_data = get_block_date(trn.block_hash)
        trn.transaction_date = t_data
    except:
        text = "Ошибка: Дата транзакции не определена."
        return None, text

    return trn, ""


def save_transaction(trn: Transaction) -> bool:
    try:
        trn.save(force_insert=True)
    except IntegrityError:
        text = "Ошибка: Транзакция уже существует."
        return False, text
    except Exception as err:
        text = "Ошибка: Непредвиденная ошибка при сохранении."
        return False, text
    return True, ""


def payment_state(node: Node) -> float:
    delta = relativedelta(datetime.now(), node.payment_date)
    duty = (delta.months + 1) * node.cost
    paid = get_transaction_summ(node)
    return paid - duty


def get_expiry_date(node: Node):
    summ = get_transaction_summ(node)
    month = round(summ / node.cost)
    return node.payment_date + relativedelta(months=month)


def get_transaction_summ(node: Node) -> float:
    transactions = (Transaction
                    .select(Transaction.value, Transaction.decimals)
                    .where(Transaction.node_id == node.id)
                    .namedtuples())

    transactions_sum: float = 0
    for transaction in transactions:
        unit = (unit_name(transaction.decimals), "ether")[transaction.decimals == None]
        transactions_sum += float(
            Web3.from_wei(Web3.to_int(hexstr=transaction.value), unit))
    return transactions_sum


def unit_name(decimals) -> str:
    for name, places in units.items():
        if places == (10 ** decimals):
            return name
    return None
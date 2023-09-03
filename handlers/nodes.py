from datetime import datetime

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dateutil.relativedelta import relativedelta
from web3 import Web3

from botStates import States
from callbacks.account_callback_factory import AccountCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.notification_callback_factory import NotificationCallbackFactory
from data.models.account import Account
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_data_type import NodeDataType
from data.models.node_fields import NodeFields
from data.models.node_payments import NodePayments
from data.models.payment_data import PaymentData
from data.models.transaction import Transaction
from keyboards.common_keyboards import get_null_keyboard
from keyboards.for_questions import get_keyboard_for_node_instance, get_keyboard_for_node_extended_information, \
    get_keyboard_for_account_node_payment
from keyboards.transaction_keyboards import get_keyboard_for_transaction_verify
from middleware.user import UsersMiddleware
from services.transaction import check_hash, replenish_account, unit_name

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

    paid = node.expiry_date >= datetime.now().date()
    paid_text = ("Не оплачено", "Оплачено")[paid]

    text = 'Информация о ноде:\n\n' \
            f'Дата платежа: {node.payment_date.day} числа каждого месяца\n' \
            f'Статус оплаты: {paid_text}'

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
    NodesCallbackFactory.filter(F.action == "cash_payment"))
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


@router.message(
    States.nodes,
    F.text.regexp('0[x][0-9a-fA-F]{64}'))
async def transaction_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    node = data.get('node')
    account = data.get('account')
    back_step = NodesCallbackFactory(action="select_node", node_id=node.id)
    trn = await check_hash(message, state, back_step)
    if not (trn is None):
        replenish_account(account, trn)
        if make_payment(account, node):
            unit = (unit_name(trn.decimals), "ether")[trn.decimals == None]
            value = float(Web3.from_wei(Web3.to_int(hexstr=trn.value), unit))

            await message.answer(text=f"Хеш транзакции: {trn.transaction_hash}\n"
                                      f"Дата транзакции: {datetime.fromtimestamp(trn.transaction_date)}\n"
                                      f"Сумма в транзакции: {value}\n"
                                      f"Аккаунт пополнения: {account.id}\n"
                                      f"Назначение платежа: Нода {node.type.name} ({node.id})\n"
                                      f"Сумма платежа: {node.cost }")
        else:
            unit = (unit_name(trn.decimals), "ether")[trn.decimals == None]
            value = float(Web3.from_wei(Web3.to_int(hexstr=trn.value), unit))
            await message.answer(text=f"Хеш транзакции:   {trn.transaction_hash}\n"
                                      f"Дата транзакции: {datetime.fromtimestamp(trn.transaction_date)}\n"
                                      f"Сумма в транзакции: {value}\n"
                                      f"Аккаунт пополнения: {account.id}\n"
                                      f"Назначение платежа: Аккаунт ({account.id})\n"
                                      f"Сумма платежа:      {value}")
        await message.answer(
            text="Выберете действие из списка ниже:",
            reply_markup=get_keyboard_for_transaction_verify(back_step))


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


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "account_payment"))
async def account_payment(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')
    user_account = (
        Account.select(Account.id)
        .where(Account.user_id == user.id)
        .namedtuples())

    if len(user_account) == 1:
        callback_data = AccountCallbackFactory(
            action="select_account",
            account_id=user_account.get().id
        )
        await select_account(callback, callback_data, state)
        return
    else:
        text = "Выберете счет из списка ниже:"
        keyboard = get_null_keyboard()
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(
    States.account,
    AccountCallbackFactory.filter(F.action == "select_account"))
async def select_account(
        callback: types.CallbackQuery,
        callback_data: AccountCallbackFactory,
        state: FSMContext
):
    account = Account.get(Account.id == callback_data.account_id)
    await state.update_data(account=account)
    data = await state.get_data()
    node = data.get('node')
    back_step = NodesCallbackFactory(action="select_node", node_id=node.id)

    if account.funds >= node.cost:
        if make_payment(account, node):
            await callback.message.answer(
                text=f"Аккаунт списания:   {account.id}\n"
                     f"Назначение платежа: Нода {node.type.name} ({node.id})\n"
                     f"Сумма платежа:      {node.cost}\n")

        await callback.message.answer(
            text="Нода успешно оплачена",
            reply_markup=get_keyboard_for_account_node_payment(back_step))
    else:
        await callback.message.answer(
            text="На счете недостаточно средств",
            reply_markup=get_keyboard_for_account_node_payment(back_step))


def make_payment(account: Account, node: Node):
    if account.funds >= node.cost:
        node_payment = NodePayments()
        node_payment.account_id = account.id
        node_payment.node_id = node.id
        node_payment.value = node.cost
        node_payment.save()

        account.funds = account.funds - node.cost
        account.save()

        node.expiry_date = get_expiry_date(node)
        node.save()
        return True
    return False


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
    transactions = (NodePayments
                    .select(NodePayments.value)
                    .where(NodePayments.node_id == node.id)
                    .namedtuples())

    transactions_sum: float = 0
    for transaction in transactions:
        transactions_sum += transaction.value
    return transactions_sum


class Check:
    transaction: Transaction
    account: Account = None
    node: Node = None

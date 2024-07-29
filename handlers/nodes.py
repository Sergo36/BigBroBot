from datetime import datetime

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from dateutil.relativedelta import relativedelta

import config
import re
from botStates import States
from bot_logging.telegram_notifier import TelegramNotifier
from callbacks.account_callback_factory import AccountCallbackFactory
from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.notification_callback_factory import NotificationCallbackFactory
from data.models.account import Account
from data.models.common_node_data import CommonNodeData
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_payments import NodePayments
from data.models.node_type import NodeType
from data.models.payment_data import PaymentData
from data.models.server_configuration import ServerConfiguration
from handlers.db_viewer.viewer import show_data
from keyboards.common_keyboards import get_null_keyboard
from keyboards.for_questions import get_keyboard_for_node_instance, get_keyboard_for_node_extended_information, \
    get_keyboard_for_account_node_payment, get_keyboard_for_obsolete_node, get_keyboard_for_after_obsolete_node, \
    get_keyboard_for_nodes_menu
from keyboards.transaction_keyboards import get_keyboard_for_transaction_verify
from middleware.user import UsersMiddleware
from services.hostings.contabo import create_server as create_server_contabo
from services.hostings.hetzner import create_server as create_server_hetzner
from services.transaction import check_hash, replenish_account

router = Router()
router.callback_query.middleware(UsersMiddleware())

SPECIAL_CHARS = [
  '\\',
  '_',
  '*',
  '[',
  ']',
  '(',
  ')',
  '~',
  '`',
  '>',
  '<',
  '&',
  '#',
  '+',
  '-',
  '=',
  '|',
  '{',
  '}',
  '.',
  '!'
]


def escapeMarkdown(text: str):
    for char in SPECIAL_CHARS:
        text = text.replace(char, f'\\{char}')
    return text


@router.callback_query(
    MainCallbackFactory.filter(F.action == "nodes_menu"))
async def nodes_menu(
        callback: types.CallbackQuery
):
    await callback.message.edit_text(
        text="Выберете раздел из списка ниже:",
        reply_markup=get_keyboard_for_nodes_menu())



@router.callback_query(
    NodesCallbackFactory.filter(F.action == "select_node"))
async def select_node(
        callback: types.CallbackQuery,
        callback_data: NodesCallbackFactory,
        state: FSMContext):
    node = Node.get(Node.id == callback_data.node_id)
    await state.update_data(node=node)
    await state.set_state(States.nodes)

    paid = node.expiry_date > datetime.now().date()
    paid_text = ("Не оплачено", "Оплачено")[paid]

    text = 'Информация о ноде:\n\n'\
           f'Номер ноды: {node.id}\n'\
           f'Статус оплаты: {paid_text}\n' \
           f'Оплачено до: {node.expiry_date.strftime("%d-%m-%Y")}'

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


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "account_payment"))
async def account_payment(callback: types.CallbackQuery, state: FSMContext, notifier: TelegramNotifier):
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
        await select_account(callback, callback_data, state, notifier)
        return
    else:
        text = "Выберете счет из списка ниже:"
        keyboard = get_null_keyboard()
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


async def payment(callback: types.CallbackQuery, state: FSMContext):
    wallet_address = PaymentData.get(PaymentData.active == True).wallet_address
    data = await state.get_data()
    node = data.get('node')

    photo = FSInputFile(config.FILE_BASE_PATH + f'qr_codes/{wallet_address}.png')
    await callback.message.answer_photo(photo=photo)

    text = f"Для оплаты, переведите `{node.cost}` USDT в сети BEP20 на адрес `{wallet_address}`\n\n" \
           f"После подтверждения транзакции сетью, отправьте хеш транзакции ответным сообщением\n"
    await callback.message.answer(
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_keyboard_for_node_extended_information(node),
    )
    await state.update_data(callback=callback)
    await callback.answer()


@router.message(
    States.nodes,
    F.text.regexp('0[x][0-9a-fA-F]{64}'))
async def transaction_handler(message: Message, state: FSMContext, notifier: TelegramNotifier):
    data = await state.get_data()
    node = data.get('node')
    account = data.get('account')
    back_step = NodesCallbackFactory(action="select_node", node_id=node.id)
    trn = await check_hash(message, state, back_step)
    if not (trn is None):
        await replenish_account(account, trn, message)
        await make_payment(account, node, message)

        if NodePayments.select().where(NodePayments.node_id == node.id).count() == 1:
            await message.answer("Ваша нода будет установлена в течение трех дней\n"
                                 "После установки Вам придет уведомление")
            await after_first_pay_handler(node, message.from_user.username, notifier)

        await message.answer(
            text="Выберете действие из списка ниже:",
            reply_markup=get_keyboard_for_transaction_verify(back_step))


@router.callback_query(States.nodes,
                       NodesCallbackFactory.filter(F.action == "extended_information"))
async def information_node(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    node: Node = data.get('node')

    common_node_data = (
        CommonNodeData.select(CommonNodeData.name, CommonNodeData.data)
        .where(CommonNodeData.type == node.type)
    )

    node_data = (
        NodeData.select(NodeData.name, NodeData.data)
        .where(NodeData.node_id == node.id)
        .namedtuples())
    text = "Расширенная информация\n"
    for data in common_node_data + node_data:
        match = re.search(r'\[\S*\]\(\S*\)', data.data)
        if match:
            link_name = re.search(r'\[\S*\]', data.data)
            link_data = re.search(r'\(\S*\)', data.data)
            value = (f"[{escapeMarkdown(data.data[link_name.regs[0][0] +1 :link_name.regs[0][1] -1])}]"
                     f"({escapeMarkdown(data.data[link_data.regs[0][0] +1 :link_data.regs[0][1] -1])})")
        else:
            value = f"`{escapeMarkdown(data.data)}`"

        text += f"\n*{data.name}*: {value}"

    await callback.message.edit_text(text=text, parse_mode=ParseMode.MARKDOWN_V2,
                                     reply_markup=get_keyboard_for_node_extended_information(node))


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "confirm_obsolete"))
async def obsolete_node(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    node = data.get('node')

    await callback.message.edit_text(
        text="Отменить заказ?",
        reply_markup=get_keyboard_for_obsolete_node(node))


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "obsolete_node"))
async def obsolete_node_yes(
        callback: types.CallbackQuery,
        callback_data: NodesCallbackFactory,
        notifier: TelegramNotifier):
    q = (Node
         .update({Node.obsolete: True})
         .where(Node.id == callback_data.node_id))
    q.execute()

    await callback.message.edit_text(text=f"Заказ {callback_data.node_id} отменен")
    await callback.message.answer(text="Выберите действие из списка ниже",
                                  reply_markup=get_keyboard_for_after_obsolete_node())

    await notifier.emit(callback.from_user.username, f"Отмена заказа {callback_data.node_id}")


@router.callback_query(
    States.account,
    AccountCallbackFactory.filter(F.action == "select_account"))
async def select_account(
        callback: types.CallbackQuery,
        callback_data: AccountCallbackFactory,
        state: FSMContext,
        notifier: TelegramNotifier):
    account = Account.get(Account.id == callback_data.account_id)
    await state.update_data(account=account)
    data = await state.get_data()
    node = data.get('node')
    back_step = NodesCallbackFactory(action="select_node", node_id=node.id)

    if account.funds >= node.cost:
        await make_payment(account, node, callback.message)
        
        if NodePayments.select().where(NodePayments.node_id == node.id).count() == 1:
            await callback.message.answer("Ваша нода будет установлена в течение трех дней\n"
                                          "После установки Вам придет уведомление")
            await after_first_pay_handler(node, callback.from_user.username, notifier)

        await callback.message.answer(
            text="Нода успешно оплачена",
            reply_markup=get_keyboard_for_account_node_payment(back_step))
    else:
        await callback.message.answer(
            text="На счете недостаточно средств",
            reply_markup=get_keyboard_for_account_node_payment(back_step))


async def make_payment(account: Account, node: Node, message: types.Message):
    if account.funds >= node.cost:
        node_payment = NodePayments()
        node_payment.account_id = account.id
        node_payment.node_id = node.id
        node_payment.value = node.cost
        node_payment.payment_date = datetime.now()
        node_payment.save()

        account.funds = account.funds - node.cost
        account.save()

        node.expiry_date = get_expiry_date(node)
        node.save()

        await message.answer(
            text=f"Аккаунт списания: {account.id}\n"
                 f"Сумма платежа: {node.cost}\n"
                 f"Остаток средств: {account.funds}\n"
                 f"Назначение платежа: {node.type.name} ({node.id})\n"
                 f"Заказ оплачен до: {node.expiry_date.strftime('%d-%m-%Y')}")


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


@router.callback_query(
    States.nodes,
    NodesCallbackFactory.filter(F.action == "payments_history"))
async def payments_history(
        callback: types.CallbackQuery,
        callback_data: NodesCallbackFactory,
        state: FSMContext):
    query = (NodePayments
             .select(NodePayments.payment_date.alias("Date"), NodePayments.value.alias("Value"))
             .where(NodePayments.node_id == callback_data.node_id)
             .order_by(NodePayments.payment_date)
             .namedtuples())
    res = query.execute()
    back_step = NodesCallbackFactory(action="select_node", node_id=callback_data.node_id)

    await state.update_data(db_table=res)
    await show_data(state, callback, back_step)


async def after_first_pay_handler(node: Node, username: str, notifier: TelegramNotifier, ):
    if NodePayments.select().where(NodePayments.node_id == node.id).count() == 1:
        await notifier.emit(username, f"Оплата ноды {node.type.name}({node.id})")
        server = await order_server(node, notifier)
        if not (server is None):
            server.save()
            node.server = server.id
            node.save()


async def order_server(node: Node, notifier: TelegramNotifier):
    sc: ServerConfiguration = (ServerConfiguration
                               .select()
                               .join(NodeType, on=(NodeType.server_configuration_id == ServerConfiguration.id))
                               .where(NodeType.id == node.type)
                               .get_or_none())
    if sc is None:
        await notifier.emit("BigBroBot", "Не задана конфигурация")
        return

    if not sc.auto_order:
        await notifier.emit("BigBroBot", "Отключен автоматический заказ")
        return

    await notifier.emit("BigBroBot", f"Заказ сервера для ноды: {node.id}")

    server = await create_server(node, sc)
    if server is None:
        await notifier.emit("BigBroBot", f"Не найден хостинг из конфигурации")
        await notifier.emit("BigBroBot", f"Не удалось заказать сервер")
    else:
        await notifier.emit("BigBroBot", f"Заказан сервер {server.hosting_server_id}. Статус поставки {server.hosting_status}")

    return server


async def create_server(node, sc):
    # to do settable hosting id
    if sc.hosting_id.name == 'Hetzner':
        server = await create_server_hetzner(node, sc)
    elif sc.hosting_id.name == 'Contabo':
        server = await create_server_contabo(node, sc)
    else:
        return None
    return server

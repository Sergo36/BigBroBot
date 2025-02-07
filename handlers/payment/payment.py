import types

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from botStates import States, PaymentStates
from bot_logging.telegram_notifier import TelegramNotifier
from callbacks.payment_callback_factory import PaymentCallbackFactory
from data.models.payment_token import PaymentToken
from services.web3 import get_transaction_receipt

router = Router()


@router.message(
    PaymentStates.ChainSelect
)
async def chain_select_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="Выберете сеть",
        reply_markup=get_keyboard_for_chain_select())


def get_keyboard_for_chain_select() -> ReplyKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="1", callback_data=PaymentCallbackFactory(
        action="chain_select"))

    return kb.as_markup(resize_keyboard=True)


@router.message(
    States.nodes,
    F.text.regexp('0[x][0-9a-fA-F]{64}'))
async def transaction_handler(message: Message, state: FSMContext, notifier: TelegramNotifier):
    data = await state.get_data()
    node = data.get('node')
    account = data.get('account')
    back_step = NodesCallbackFactory(action="select_node", node_id=node.id)

    trn_data = {
        "user" : data.get('user'),
        "account" : data.get('account'),
        "rpc" : data.get('rpc'),
        "abi" : data.get('abi')
    }

    trn = await check_hash(message, trn_data, back_step)
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


def get_transaction_receipt(payment_token_id):
    token = PaymentToken.get(PaymentToken.id == payment_token_id)
    trn_receipt = get_transaction_receipt(token)







from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

import config
from botStates import States
from callbacks.account_callback_factory import AccountCallbackFactory
from callbacks.payments_callback_factory import PaymentsCallbackFactory
from callbacks.transactions_callback_factory import TransactionsCallbackFactory
from data.models.account import Account
from data.models.payment_data import PaymentData
from handlers.account.keyboards import get_keyboard_for_account_list, get_keyboard_for_account_instance, \
    get_keyboard_for_replenish_account, get_keyboard_for_chose_token
from services.transaction import check_hash, replenish_account

router = Router()


@router.callback_query(AccountCallbackFactory.filter(F.action == "accounts_list"))
async def accounts(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.account)
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
        keyboard = get_keyboard_for_account_list(user_account)
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
    await account_answer(account, callback)


@router.callback_query(
    States.account,
    AccountCallbackFactory.filter(F.action == "back_step_account"))
async def back_step_account(
        callback: types.CallbackQuery,
        state: FSMContext
):
    data = await state.get_data()
    account = data.get('account')
    await account_answer(account, callback)


async def account_answer(account: Account, callback: types.CallbackQuery):
    text = 'Информация о счете: \n\n' \
           f'На счете осталось: {account.funds} USDT'

    await callback.message.edit_text(
        text=text,
        reply_markup=get_keyboard_for_account_instance(account.id)
    )


@router.callback_query(
    States.account,
    AccountCallbackFactory.filter(F.action == "replenish_account"))
async def internal_replenish_account(
        callback: types.CallbackQuery,
        state: FSMContext):
    await chose_payment(callback, state)


@router.callback_query(
    States.account,
    TransactionsCallbackFactory.filter(F.action == "try_again"))
async def try_again_replenish(
        callback: types.CallbackQuery,
        state: FSMContext):
    await chose_payment(callback, state)


async def chose_payment(callback: types.CallbackQuery, state: FSMContext):
    active_payments = (PaymentData
                       .select(PaymentData.id,
                               PaymentData.contract_name)
                       .where(PaymentData.active == True))

    await callback.message.edit_text(
        text="Выберите токен для оплаты",
        reply_markup=get_keyboard_for_chose_token(active_payments))
    await callback.answer()


@router.callback_query(
    States.account,
    PaymentsCallbackFactory.filter()
)
async def payment(callback: types.CallbackQuery, callback_data: PaymentsCallbackFactory, state: FSMContext):
    payment_data = PaymentData.get(PaymentData.id == callback_data.payment_id)
    await state.update_data(payment_data=payment_data)

    photo = FSInputFile(config.FILE_BASE_PATH + f'qr_codes/{payment_data.wallet_address}.png')
    await callback.message.answer_photo(photo=photo)

    text = f"Для пополнения счета переведите {payment_data.contract_name} в сети BEP20 на адрес `{payment_data.wallet_address}`\n\n" \
           f"После подтверждения транзакции сетью, отправьте хеш транзакции ответным сообщением\n"

    await callback.message.answer(
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_keyboard_for_replenish_account(),
    )
    await state.update_data(callback=callback)
    await callback.answer()


@router.message(
    States.account,
    F.text.regexp('0[x][0-9a-fA-F]{64}'))
async def transaction_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    account = data.get('account')
    back_step = AccountCallbackFactory(action="back_step_account")
    trn = await check_hash(message, state, back_step)
    if not (trn is None):
        await replenish_account(account, trn, message)
        await message.answer(
            text="Выберите действие из списка ниже",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=get_keyboard_for_replenish_account(),
        )


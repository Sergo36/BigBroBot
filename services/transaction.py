from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from peewee import IntegrityError
from web3 import Web3
from web3.exceptions import TransactionNotFound

from data.models.account import Account
from data.models.transaction import Transaction
from keyboards.common_keyboards import get_null_keyboard
from keyboards.transaction_keyboards import get_keyboard_for_transaction_fail

from services.web3 import get_transaction, transaction_valid, get_block_date
from eth_utils.units import units


async def check_hash(message: Message, state: FSMContext, back_step: CallbackData):
    transaction_hash = message.text
    data = await state.get_data()
    user = data.get('user')
    account = data.get('account')

    bot_message = await message.answer(text="Проверка транзакции в блокчейне: ожидание", reply_markup=get_null_keyboard())
    trn, error_text = get_transaction_blockchain(transaction_hash)

    if trn is None:
        await bot_message.edit_text(
            text="Проверка транзакции в блокчейне: провал\n"
                 f"\t\t{error_text}",
            reply_markup=get_keyboard_for_transaction_fail(back_step))
        return None

    await bot_message.edit_text(text="Проверка транзакции в блокчейне: OK\n"
                                          "Сохранение транзакции в базе данных: ожидание",
                                     reply_markup=get_null_keyboard())

    trn.owner = user.id
    trn.account_id = account.id

    ok, error_text = save_transaction(trn)

    if not ok:
        await bot_message.edit_text(text="Проверка транзакции в блокчейне: OK\n"
                                              "Сохранение транзакции в базе данных: провал\n"
                                              f"\t\t{error_text}",
                                         reply_markup=get_keyboard_for_transaction_fail(back_step))
        return None

    await bot_message.edit_text(text="Проверка транзакции в блокчейне: OK\n"
                                          "Сохранение транзакции в базе данных: OK\n"
                                          "Транзакция подтверждена\n\n",
                                     reply_markup=get_null_keyboard())
    await state.update_data(callback=None)
    return trn


async def replenish_account(account: Account, transaction: Transaction, message: Message):
    unit = (unit_name(transaction.decimals), "ether")[transaction.decimals == None]
    value = float(Web3.from_wei(Web3.to_int(hexstr=transaction.value), unit))
    account.funds += value
    account.save()
    await message.answer(text=f"Хэш транзакции: {transaction.transaction_hash}\n"
                              f"Дата транзакции: {datetime.fromtimestamp(transaction.transaction_date)}\n"
                              f"Сумма в транзакции: {value}\n"
                              f"Аккаунт пополнения: {account.id}")


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
        #trn.node_id = 170 # to do debug: delete after 0005 migration
        trn.save(force_insert=True)
    except IntegrityError as err:
        print(err)
        text = "Ошибка: Транзакция уже существует."
        return False, text
    except Exception as err:
        text = "Ошибка: Непредвиденная ошибка при сохранении."
        return False, text
    return True, ""


def unit_name(decimals) -> str:
    for name, places in units.items():
        if places == (10 ** decimals):
            return name
    return None

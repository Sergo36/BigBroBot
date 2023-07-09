from typing import Optional

from aiogram.filters.callback_data import CallbackData


class TransactionsCallbackFactory(CallbackData, prefix="transactions"):
    action: str

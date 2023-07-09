from typing import Optional

from aiogram.filters.callback_data import CallbackData


class AccountCallbackFactory(CallbackData, prefix="account"):
    action: str
    account_id: Optional[int]

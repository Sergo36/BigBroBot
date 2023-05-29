from aiogram.filters.callback_data import CallbackData
from typing import Optional


class OrderCallbackFactory(CallbackData, prefix="order"):
    action: str
    node_type_id: Optional[int]

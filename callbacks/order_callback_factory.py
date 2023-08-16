from typing import Optional

from aiogram.filters.callback_data import CallbackData


class OrderCallbackFactory(CallbackData, prefix="order"):
    action: str
    node_type_id: Optional[int] = None

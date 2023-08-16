from typing import Optional

from aiogram.filters.callback_data import CallbackData


class NotificationCallbackFactory(CallbackData, prefix="notification"):
    action: str
    node_type_id: Optional[int] = None
    node_id: Optional[int] = None

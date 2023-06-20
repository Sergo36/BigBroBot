from typing import Optional

from aiogram.filters.callback_data import CallbackData


class NodesCallbackFactory(CallbackData, prefix="nodes"):
    action: str
    node_id: Optional[int]

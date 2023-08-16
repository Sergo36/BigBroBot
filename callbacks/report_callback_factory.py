from aiogram.filters.callback_data import CallbackData
from typing import Optional


class ReportCallbackFactory(CallbackData, prefix="report"):
    action: str
    node_type: Optional[int] = None

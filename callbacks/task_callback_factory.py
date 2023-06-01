from typing import Optional

from aiogram.filters.callback_data import CallbackData


class TaskCallbackFactory(CallbackData, prefix="task"):
    action: str
    data: Optional[str]

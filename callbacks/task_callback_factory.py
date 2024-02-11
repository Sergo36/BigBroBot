from typing import Optional

from aiogram.filters.callback_data import CallbackData


class TaskCallbackFactory(CallbackData, prefix="task"):
    action: str
    data: Optional[str] = None


class InteractionCallbackFactory(CallbackData, prefix="interaction"):
    action: str
    name: Optional[str] = None
    header: Optional[str] = None
    conditions: Optional[str] = None

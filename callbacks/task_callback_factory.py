from typing import Optional

from aiogram.filters.callback_data import CallbackData


class TaskCallbackFactory(CallbackData, prefix="task"):
    action: str
    data: Optional[str] = None


class NodeDataSetCallback(CallbackData, prefix="node_data_set"):
    action: str
    interaction_id: int

# class SetDataCallbackFactory(CallbackData, prefix="set_data"):
#     filter: str
#     name: str
#     request: str
#     response: str
#     error: str



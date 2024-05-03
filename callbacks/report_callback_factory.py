from aiogram.filters.callback_data import CallbackData
from typing import Optional


class ReportCallbackFactory(CallbackData, prefix="report"):
    action: str
    node_type: Optional[int] = None


class UserReportCallbackFactory(CallbackData, prefix="user_report"):
    action: str


class DbViewCallbackFactory(CallbackData, prefix="db_view"):
    table: str


class ProxyDeviceListCallbackFactory(CallbackData, prefix="proxy_device"):
    device_type: str


class ProxyNextActionCallbackFactory(CallbackData, prefix = "next_action"):
    action: str
    
from aiogram.filters.callback_data import CallbackData


class MainCallbackFactory(CallbackData, prefix="main"):
    action: str

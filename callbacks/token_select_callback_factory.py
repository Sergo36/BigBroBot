from aiogram.filters.callback_data import CallbackData


class TokenSelectCallbackFactory(CallbackData, prefix="token_select"):
    action: str
    token_id: int

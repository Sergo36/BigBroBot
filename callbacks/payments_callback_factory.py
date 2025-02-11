from aiogram.filters.callback_data import CallbackData


class PaymentsCallbackFactory(CallbackData, prefix="payments"):
    payment_id: int

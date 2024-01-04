from aiogram.filters.callback_data import CallbackData


class InstallationCallbackFactory(CallbackData, prefix="install"):
    node_id: int

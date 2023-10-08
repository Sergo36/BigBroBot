from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

import config
from bot_logging.telegram_notifier import TelegramNotifier


class NotifierForward(BaseMiddleware):

    telegram_notifier = None
    chat_id = config.LOGGING_CHAT

    def __init__(self, bot):
        super().__init__()
        if self.chat_id is None:
            return
        self.telegram_notifier = TelegramNotifier(bot, self.chat_id)

    async def __call__(self,
                       handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        data['notifier'] = self.telegram_notifier

        return await handler(event, data)

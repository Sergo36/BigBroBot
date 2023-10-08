from datetime import datetime

from aiogram import Bot, types
from aiogram.types import User


class TelegramNotifier:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    async def emit(self, from_user : User, record: str):
        text = f"DateTime: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n" \
               f"Username: @{from_user.username}\n" \
               f"Action: {record}"
        await self.bot.send_message(chat_id=self.chat_id, text=text)

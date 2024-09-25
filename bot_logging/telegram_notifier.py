from datetime import datetime


class TelegramNotifier:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    async def emit(self, username: str, record: str):
        text = f"DateTime: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n" \
               f"Username: @{username}\n" \
               f"Action: {record}"
        await self.bot.send_message(chat_id=self.chat_id, text=text)

from datetime import datetime


class TelegramNotifier:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    async def emit(self, username: str, record: str):
        text = f"DateTime: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n" \
               f"Username: @{username}\n" \
               f"Action: {record}"
        return await self.bot.send_message(chat_id=self.chat_id, text=text)


class ConsoleNotifier:
    async def emit(self, username: str, record: str):
        print(f"DateTime: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n" \
               f"Username: @{username}\n" \
               f"Action: {record}")
        return ConsoleMessage()


class ConsoleMessage:
    async def answer(self, text, reply_markup):
        print(text)
        return self

    async def edit_text(self, text):
        print(text)
        return self



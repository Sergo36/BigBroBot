import config
import logging
import asyncio

from aiogram import Bot, Dispatcher
from handlers import nodesList, nodesInstance, common
# log
logging.basicConfig(level=logging.INFO)

# Запуск бота
async def main():
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher()

    dp.include_routers(common.router)
    dp.include_routers(nodesList.router)
    dp.include_routers(nodesInstance.router)

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
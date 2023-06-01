import config
import logging
import asyncio

from aiogram import Bot, Dispatcher
from handlers import common, order, nodes
from  handlers.notification import notification
from handlers.interaction import interaction

# log
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher()

    dp.include_routers(notification.router)
    dp.include_routers(nodes.router)
    dp.include_routers(order.router)
    dp.include_routers(interaction.router)

    dp.include_routers(common.router)

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

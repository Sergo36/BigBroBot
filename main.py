import config
import logging
import asyncio

from aiogram import Bot, Dispatcher
from handlers import order, nodes
from handlers.notification import notification
from handlers.interaction import interaction
from handlers.common import common
from handlers.report import report_handler

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler.tasks import send_payment_handlers

from datetime import datetime, timedelta

# log
logging.basicConfig(level=logging.INFO)


async def main():

    bot = Bot(token=config.TOKEN)
    dp = Dispatcher()

    dp.include_routers(notification.router)
    dp.include_routers(nodes.router)
    dp.include_routers(order.router)
    dp.include_routers(interaction.router)
    dp.include_routers(report_handler.router)
    dp.include_routers(common.router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_payment_handlers, trigger='cron',
                      hour=20,
                      minute=0,
                      kwargs={'bot': bot})
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

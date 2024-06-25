import config
import logging
import asyncio

from aiogram import Bot, Dispatcher

from handlers import order, nodes
from handlers.account import account
from handlers.db_viewer import viewer
from handlers.notification import notification
from handlers.interaction import interaction
from handlers.common import common
from handlers.report import report_handler
from handlers.admin import admin_handlers
from handlers.proxy import proxy_handlers

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middleware.telegram_notifier_forward import NotifierForward
from scheduler.tasks import send_payment_handlers, everyday_report
from middleware.data_forward import DataForward

# log
logging.basicConfig(level=logging.DEBUG)


async def main():
    bot = Bot(token=config.TOKEN)
    notifier_forward = NotifierForward(bot)
    dp = Dispatcher()

    dp.message.middleware(DataForward(bot))

    order.router.callback_query.middleware(notifier_forward)
    nodes.router.callback_query.middleware(notifier_forward)
    nodes.router.message.middleware(notifier_forward)

    dp.include_routers(notification.router)
    dp.include_routers(nodes.router)
    dp.include_routers(order.router)
    dp.include_routers(account.router)
    dp.include_routers(interaction.router)
    dp.include_routers(report_handler.router)
    dp.include_routers(viewer.router)
    dp.include_routers(admin_handlers.router)
    dp.include_routers(proxy_handlers.router)
    dp.include_routers(common.router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_payment_handlers, trigger='cron',
                      hour=20,
                      minute=0,
                      kwargs={'bot': bot})
    scheduler.add_job(everyday_report, trigger='cron',
                      hour=21,
                      minute=0,
                      kwargs={'notifier': notifier_forward.telegram_notifier})
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

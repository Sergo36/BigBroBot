import config
import logging
import asyncio

from aiogram import Bot, Dispatcher

from bot_logging.telegram_notifier import ConsoleNotifier
from handlers import order, nodes
from handlers.account import account
from handlers.db_viewer import viewer
from handlers.notification import notification
from handlers.interaction import interaction
from handlers.common import common
from handlers.report import report_handler
from handlers.admin import admin_handlers
from handlers.proxy import proxy_handlers

from middleware.telegram_notifier_forward import NotifierForward
from scheduler.scheduler_utils import scheduler_setup
from middleware.data_forward import DataForward
from scheduler.tasks import install_for_status_wait_dependencies, install_for_status_wait_run

# log
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=config.TOKEN)
    notifier_forward = NotifierForward(bot)
    console_notifier = ConsoleNotifier()

    #await install_for_status_wait_dependencies(console_notifier)
    await install_for_status_wait_run(console_notifier)
    return
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

    scheduler_setup(bot, notifier_forward)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

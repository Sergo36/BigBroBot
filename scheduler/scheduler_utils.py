from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.tasks import send_payment_handlers, everyday_report, contabo_server_status_update


def scheduler_setup(bot=None, notifier_forward=None):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_payment_handlers, trigger='cron',
                      hour=20,
                      minute=0,
                      kwargs={'bot': bot})
    scheduler.add_job(everyday_report, trigger='cron',
                      hour=21,
                      minute=0,
                      kwargs={'notifier': notifier_forward.telegram_notifier})

    scheduler.add_job(contabo_server_status_update, trigger='interval',
                      hours=1,
                      kwargs={'notifier': notifier_forward.telegram_notifier})

    scheduler.start()
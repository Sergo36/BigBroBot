from aiogram import Bot

from bot_logging.telegram_notifier import TelegramNotifier
from data.models.node import Node
from data.models.node_type import NodeType
from data.models.user import User

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from handlers.notification.notification import send_message


async def send_payment_handlers(bot: Bot):
    query = (User
             .select(User.telegram_id, Node.id, Node.payment_date, NodeType.name, Node.cost)
             .join(Node, on=(User.id == Node.owner))
             .join(NodeType, on=(Node.type == NodeType.id))
             .where(Node.expiry_date <= datetime.now() + relativedelta(days=+5))
             .where(Node.obsolete == False)
             .namedtuples())
    await send_message(query, bot)


async def everyday_report(notifier: TelegramNotifier):
    query = (Node
             .select(
                Node.id.alias("node_id"),
                Node.expiry_date.alias("node_expiry_date"),
                User.telegram_name.alias("username"),
                NodeType.name.alias("node_type"))
             .join(User, on=(User.id == Node.owner))
             .join(NodeType, on=(NodeType.id == Node.type))
             .where((Node.obsolete == False) & (Node.expiry_date <= datetime.now().date() + timedelta(days=3)))
             .namedtuples())
    header = f'Expiry date <= {datetime.now().date() + timedelta(days=3)}\n\n' \
             f'NodeId|User|Type|Expiry date\n'
    data_len = 0
    row_text = header
    row_len = len(row_text)
    data_len = data_len + row_len

    report_header = row_text

    report_data = []
    for row in query:
        row_text = f"{row.node_id}|@{row.username}|{row.node_type}|{row.node_expiry_date}"
        row_len = len(row_text)
        data_len = data_len + row_len
        if data_len < 4000:
            report_data.append(row_text)
        else:
            report = report_header + '\n'.join(report_data)
            await notifier.emit("BigBroBot", report)
            data_len = 0
            row_text = header
            row_len = len(row_text)
            data_len = data_len + row_len
    report = report_header + '\n'.join(report_data)
    await notifier.emit("BigBroBot", report)

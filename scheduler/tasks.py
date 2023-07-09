from aiogram import Bot

from data.models.node import Node
from data.models.node_type import NodeType
from data.models.user import User

from datetime import datetime
from dateutil.relativedelta import relativedelta
from handlers.notification.notification import send_message


async def send_payment_handlers(bot: Bot):
    query = (User
             .select(User.telegram_id, Node.id, Node.payment_date, NodeType.name)
             .join(Node, on=(User.id == Node.owner))
             .join(NodeType, on=(Node.type == NodeType.id))
             .where(Node.expiry_date <= datetime.now() + relativedelta(days=+5))
             .where(Node.obsolete == False)
             .namedtuples())
    await send_message(query, bot)

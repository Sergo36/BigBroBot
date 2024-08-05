import logging

import aiogram.types
from aiogram import Bot

from bot_logging.telegram_notifier import TelegramNotifier
from data.models.node import Node
from data.models.node_type import NodeType
from data.models.server import Server
from data.models.server_configuration import ServerConfiguration
from data.models.user import User
from aiogram.types.user import User as UserAIOgram

from datetime import datetime
from dateutil.relativedelta import relativedelta
from handlers.notification.notification import send_message
from services.hostings.contabo import get_server_status, get_instances


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
             .select(Node.id.alias("node_id"), User.telegram_name.alias("username"), NodeType.name.alias("node_type"))
             .join(User, on=(User.id == Node.owner))
             .join(NodeType, on=(NodeType.id == Node.type))
             .where((Node.obsolete == False) & (Node.expiry_date <= datetime.now().date()))
             .namedtuples())
    data_len = 0
    row_text = "Expiry date >= now\n"
    row_len = len(row_text)
    data_len = data_len + row_len

    report_header = row_text

    report_data = []
    for row in query:
        row_text = f"User: @{row.username}, Node: {row.node_type}, NodeId:{row.node_id}"
        row_len = len(row_text)
        data_len = data_len + row_len
        if data_len < 4000:
            report_data.append(f"User: @{row.username}, Node: {row.node_type}, NodeId:{row.node_id}")
        else:
            report = report_header + '\n'.join(report_data)
            await notifier.emit("BigBroBot", report)
            data_len = 0
            row_text = "Expiry date >= now\n"
            row_len = len(row_text)
            data_len = data_len + row_len
    report = report_header + '\n'.join(report_data)
    await notifier.emit("BigBroBot", report)


async def contabo_server_status_update(notifier: TelegramNotifier):

    query = (Server
             .select()
             .where(((Server.hosting_status != 'running') | (Server.hosting_status == None)) & (Server.hosting_id == 2)))
    for server in query:
        new_status = await get_server_status(server)
        print(new_status)
        # await notifier.emit("BigBroBot", f'For server with hosting id {server.hosting_server_id}\n'
        #                                  f'old status: {server.hosting_status}'
        #                                  f'new status: {new_status}')
        server.hosting_status = new_status
        server.save()


async def contabo_instances_update():
    parameters = {
        'size': '100'
    }

    configurations = {}
    query = ServerConfiguration.select(ServerConfiguration.id, ServerConfiguration.server_type).namedtuples()
    for id, type in query:
        configurations[type] = id

    async for instances in get_instances(parameters):
        for instance in instances:
            try:
                server = Server.get(Server.hosting_server_id == instance['instanceId'])
            except Server.DoesNotExist:
                server = Server.create(
                    hosting_id=2,
                    # server_configuration_id=configurations[instance['productId']],
                    server_configuration_id=2,
                    hosting_server_id=instance['instanceId'],
                    hosting_status=None,
                    install_status=None,
                    obsolete=False)

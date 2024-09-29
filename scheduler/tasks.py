import logging
from asyncio import sleep

import aiogram.types
from aiogram import Bot
from peewee import fn

from bot_logging.telegram_notifier import TelegramNotifier
from data.models.install_operation import InstallOperation
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_type import NodeType
from data.models.server import Server, InstallStatus
from data.models.server_configuration import ServerConfiguration
from data.models.user import User
from aiogram.types.user import User as UserAIOgram

from datetime import datetime
from dateutil.relativedelta import relativedelta
from handlers.notification.notification import send_message
from services.hostings.contabo import get_server_status, get_instances, get_server_ip


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
             .select(Server.hosting_server_id, Server.id, Server.hosting_status, Node.id)
             .join(Node, on=Server.id == Node.server)
             .where(((Server.hosting_status != 'running') | (Server.hosting_status == None)) & (Server.hosting_id == 2)))
    for server in query:
        new_status = await get_server_status(server)
        await notifier.emit("BigBroBot", f'For server with hosting id {server.hosting_server_id}\n'
                                         f'Old status: {server.hosting_status}\n'
                                         f'New status: {new_status}\n'
                                         f'Node id: {server.node.id}')
        server.hosting_status = new_status
        server.save()


async def install_for_status_wait_run(notifier: TelegramNotifier):
    query = (Server
             .select(Server.hosting_server_id, Node.id)
             .join(Node, on=Server.id == Node.server)
             .where((Server.hosting_status == 'running') & (Server.install_status == InstallStatus.WaitRun.name)))

    for server in query:
        ip = await get_server_ip(server)
        if ip is None:
            await notifier.emit("BigBroBot", f'For server with hosting id {server.hosting_server_id}\n'
                                             f'Failed to get IP address')
            return

        data = NodeData()
        data.name = 'Server ip'
        data.data = ip
        data.node_id = server.node.id
        data.save()
        server.install_status = InstallStatus.WaitDependencies.name
        server.save()

        await notifier.emit("BigBroBot", f'For server with hosting id {server.hosting_server_id}\n'
                                         f'Write ip address: {ip}')


async def install_for_status_wait_run(notifier: TelegramNotifier):

    query = (Node
              .select(Node.id)
              .join(Server, on=Server.id == Node.server)
              .where((Server.hosting_status == 'running') & (Server.install_status == InstallStatus.WaitDependencies.name)))
    for node in query:
        argsList = (InstallOperation
                    .select(InstallOperation.args)
                    .join(NodeType, on=NodeType.install_configuration == InstallOperation.install_configuration)
                    .join(Node, on=Node.type == NodeType.id)
                    .where(Node.id == node.id))
        unicArgs = list(set(';'.join(argsList).split(';')))

        test = (NodeData
                .select()
                .count()
                .where(NodeData.node_id == node.id) & (NodeData.name.in_(unicArgs)))

        #for args in argsList:







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

from datetime import datetime, timedelta
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
                                         f'Set up ip address: {ip}')


async def install_for_status_wait_dependencies(notifier: TelegramNotifier):

    query = (Node
              .select(Node.id)
              .join(Server, on=Server.id == Node.server)
              .where((Server.hosting_status == 'running') & (Server.install_status == InstallStatus.WaitDependencies.name)))

    #to do check auto installing nedded
    for node in query:
        args_collection = (InstallOperation
                    .select(InstallOperation.args)
                    .join(NodeType, on=NodeType.install_configuration == InstallOperation.install_configuration)
                    .join(Node, on=Node.type == NodeType.id)
                    .where(Node.id == node.id))
        all_args = []
        for args in args_collection:
            all_args.append(args.args)

        unic_args_list = list(set(';'.join(all_args).split(';')))

        avaliable_args_count = (NodeData
                .select()
                .where((NodeData.node_id == node.id) & (NodeData.name.in_(unic_args_list)))
                .count())

        if (len(unic_args_list) != avaliable_args_count):
            avaliable_args = (NodeData
                                    .select(NodeData.name)
                                    .where((NodeData.node_id == node.id) & (NodeData.name.in_(unic_args_list))))
            avaliable_args_list = []
            for arg in avaliable_args:
                avaliable_args_list.append(arg)

            # text = f'Installation error\n'\
            #        f'For node with id {node.id}\n'\
            #        f'Install args: {";".join(unic_args_list)} \n'\
            #        f'Avaliable args: {";".join(avaliable_args_list)}'
            # print(text)

            await notifier.emit("BigBroBot", f'Installation error\n'
                                             f'For node with id {node.id}\n'
                                             f'Install args: {";".join(unic_args_list)} \n'
                                             f'Avaliable args {";".join(avaliable_args_list)}')
            return



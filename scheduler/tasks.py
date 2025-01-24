from aiogram import Bot

from bot_logging.telegram_notifier import TelegramNotifier
from data.models.install_configuration import InstallConfiguration
from data.models.install_operation import InstallOperation
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_type import NodeType
from data.models.server import Server, InstallStatus
from data.models.user import User

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from handlers.install.install import execute_installation
from handlers.notification.notification import send_message
from services.hostings.contabo import get_server_status, get_server_ip


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
             .select(Node.id.alias("node_id"),
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
             .where(((Server.hosting_status != 'running') | (Server.hosting_status is None)) & (Server.hosting_id == 2)))
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
             .select(
                    Server.id,
                    Server.hosting_id,
                    Server.server_configuration_id,
                    Server.hosting_server_id,
                    Server.obsolete,
                    Server.hosting_status,
                    Server.install_status,
                    Node.id)
             .join(Node, on=Server.id == Node.server)
             .where((Server.hosting_status == 'running') & (Server.install_status == InstallStatus.WaitRun.name)))

    for server in query:
        ip = '123.123.123.123'#await get_server_ip(server)
        if ip is None:
            await notifier.emit("BigBroBot", f'For node with id {server.node.id}'
                                             f'And server with hosting id {server.hosting_server_id}\n'
                                             f'Failed to get IP address')
            return
        data = NodeData.get_or_none(NodeData.node_id == server.node.id, NodeData.name == "Server ip")
        if data is None:
            data = NodeData()
            data.name = 'Server ip'
            data.data = ip
            data.node_id = server.node.id
            data.save()
            await notifier.emit("BigBroBot", f'For node with id {server.node.id}\n'
                                             f'And server with hosting id {server.hosting_server_id}\n'
                                             f'Set up ip address: {ip}')
        else:
            await notifier.emit("BigBroBot", f'For node with id {server.node.id}\n'
                                             f'And server with hosting id {server.hosting_server_id}\n'
                                             f'Already was set up ip address: {data.data}')
        server.install_status = InstallStatus.WaitDependencies.name
        server.save()




async def install_for_status_wait_dependencies(notifier: TelegramNotifier):
    nodes_query = await get_nodes_wait_dependencies()

    for node in nodes_query:
        if not node.auto_install:
            await notifier.emit("BigBroBot", f'Install cancel\n'
                                             f'For node with id {node.id} automatic install disabled')
            return

        requirements_args_list = await get_requirements_arguments(node)

        if not await requirements_arguments_available(requirements_args_list, node):
            available_args = (NodeData
                              .select(NodeData.name)
                              .where((NodeData.node_id == node.id) & (NodeData.name.in_(requirements_args_list))))
            available_args_list = []
            for arg in available_args:
                available_args_list.append(arg.name)

            await notifier.emit("BigBroBot", f'Installation error\n'
                                             f'For node with id {node.id}\n'
                                             f'Install args: {";".join(requirements_args_list)} \n'
                                             f'Available args {";".join(available_args_list)}')
            return
        message = await notifier.emit("BigBroBot", f'Run installation for node with id {node.id}\n')
        await execute_installation(node, message)


async def get_nodes_wait_dependencies():
    query = (Node
             .select(Node.id, Node.type, Node.server, InstallConfiguration.auto_install)
             .join(Server, on=Server.id == Node.server)
             .join(NodeType, on=NodeType.id == Node.type)
             .join(InstallConfiguration, on=InstallConfiguration.id == NodeType.install_configuration)
             .where(
                (Server.hosting_status == 'running') & (Server.install_status == InstallStatus.WaitDependencies.name))
             .namedtuples())
    return query


async def get_requirements_arguments(node):
    args_collection = (InstallOperation
                       .select(InstallOperation.args)
                       .join(NodeType, on=NodeType.install_configuration == InstallOperation.install_configuration)
                       .join(Node, on=Node.type == NodeType.id)
                       .where(Node.id == node.id))
    all_args = []
    for args in args_collection:
        all_args.append(args.args)
    unic_args_list = list(set(';'.join(all_args).split(';')))
    return unic_args_list


async def requirements_arguments_available(requirements_args_list, node):
    available_args_count = (NodeData
                            .select()
                            .where((NodeData.node_id == node.id) & (NodeData.name.in_(requirements_args_list)))
                            .count())

    return len(requirements_args_list) == available_args_count

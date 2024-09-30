import asyncio
import logging
import os

from aiogram.types import Message

import config
from data.models.install_operation import InstallOperation
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_type import NodeType


async def execute_installation(node: Node, message: Message):
    strings_message = [f"Execute installation for node {node.id}"]
    log_message = await message.answer(text='\n'.join(strings_message),reply_markup=None)

    node_type: NodeType = NodeType.get(NodeType.id == node.type)
    query = (InstallOperation
             .select()
             .where(InstallOperation.install_configuration == node_type.install_configuration)
             .order_by(InstallOperation.index))
    for operation in query:
        await log_data_info(f"Execute operation {operation.file_path} for node {node.id}", log_message, strings_message)
        args = [] if operation.args == '' else operation.args.split(';')
        args_string = []
        for arg in args:
            node_data: NodeData = NodeData.get_or_none(NodeData.node_id == node.id,
                                                       NodeData.name == arg)
            if node_data is None:
                await log_data_error(f"Arguments {arg} not found for node {node.id}", log_message, strings_message)
                return
            else:
                args_string.append(node_data.data)

        script_file_path = config.INSTALL_SCRIPT_PATH + operation.file_path
        logging.info(f"Execute script {script_file_path} {' '.join(args_string)}")

        if operation.type == 0:
            await get_operation(node, script_file_path, args_string, log_message, strings_message)
        elif operation.type == 1:
            await set_operation(node, script_file_path, args_string, log_message, strings_message)
        else:
            await log_data_error("Operation type not found", log_message, strings_message)
            return

    await log_data_info(f"Complete execute installation for node {node.id}", log_message, strings_message)


async def get_operation(node, file_path, args, log_message: Message, strings_message: []):
    if not os.path.exists(file_path):
        await log_data_error(f"File {file_path} does not exist", log_message, strings_message)
        return

    proc = await asyncio.create_subprocess_exec(
        file_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stdout:
        node_data = NodeData()
        node_data.node_id = node.id
        node_data.name = os.path.splitext(os.path.basename(file_path))[0]
        node_data.type = 1
        node_data.data = stdout.decode()
        node_data.save()
        await log_data_info(stdout.decode(), log_message, strings_message)
    if stderr:
        await log_data_error(stderr.decode(), log_message, strings_message)


async def set_operation(node, file_path, args, log_message: Message, strings_message: []):
    if not os.path.exists(file_path):
        await log_data_error(f"File {file_path} does not exist", log_message, strings_message)
        return

    proc = await asyncio.create_subprocess_exec(
        file_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stdout:
        await log_data_info(stdout.decode(), log_message, strings_message)
    if stderr:
        await log_data_error(stderr.decode(), log_message, strings_message)


async def log_data_info(text: str, message: Message, strings_message: []):
    logging.info(text)
    strings_message.append(text)
    await message.edit_text('\n'.join(strings_message))


async def log_data_error(text: str, message: Message, strings_message: []):
    logging.error(text)
    strings_message.append(text)
    await message.edit_text('\n'.join(strings_message))

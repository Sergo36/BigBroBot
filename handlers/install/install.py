import asyncio
import logging
import os

from aiogram.types import Message

import config
from data.models.install_operation import InstallOperation
from data.models.node import Node
from data.models.node_data import NodeData
from data.models.node_type import NodeType


async def execute_installation(node: Node, message: Message, callback_function):
    await log_data_info(f"Execute installation for node {node.id}", message, callback_function)
    node_type: NodeType = NodeType.get(NodeType.id == node.type)
    query = (InstallOperation
             .select()
             .where(InstallOperation.install_configuration == node_type.install_configuration)
             .order_by(InstallOperation.index))
    for operation in query:
        await log_data_info(f"Execute operation {operation.file_path} for node {node.id}", message, callback_function)
        args = [] if operation.args == '' else operation.args.split(';')
        args_string = []
        for arg in args:
            node_data: NodeData = NodeData.get_or_none(NodeData.node_id == node.id,
                                                       NodeData.name == arg)
            if node_data is None:
                await log_data_error(f"Arguments {arg} not found for node {node.id}", message, callback_function)
                return
            else:
                args_string.append(node_data.data)

        script_file_path = config.INSTALL_SCRIPT_PATH + operation.file_path
        await log_data_info(f"Execute script {script_file_path}", message, callback_function)

        if operation.type == 0:
            await get_operation(node, script_file_path, args_string, message)
        elif operation.type == 1:
            await set_operation(node, script_file_path, args_string, message)
        else:
            await log_data_error("Operation type not found", message, callback_function)
            return

    await log_data_info(f"Complete execute installation for node {node.id}", message, callback_function)


async def get_operation(node, file_path, args, message: Message):
    if not os.path.exists(file_path):
        await log_data_error(f"File {file_path} does not exist", message, None)
        return

    proc = await asyncio.create_subprocess_exec(
        file_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stdout:
        logging.debug(f'[stdout]\n{stdout.decode()}')
        node_data = NodeData()
        node_data.node_id = node.id
        node_data.name = os.path.splitext(os.path.basename(file_path))[0]
        node_data.type = 1
        node_data.data = stdout.decode()
        node_data.save()
        await message.answer(f"Complete operation {file_path} for {node.id}")
    if stderr:
        logging.debug(f'[stderr]\n{stderr.decode()}')
        await message.answer(f"Error operation {file_path} for {node.id}")


async def set_operation(node, file_path, args, message: Message):
    if not os.path.exists(file_path):
        await log_data_error(f"File {file_path} does not exist", message, None)
        return

    proc = await asyncio.create_subprocess_exec(
        file_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stdout:
        logging.debug(f'[stdout]\n{stdout.decode()}')
        await message.answer(f"Complete operation {file_path} for {node.id}")
    if stderr:
        logging.debug(f'[stderr]\n{stderr.decode()}')
        await message.answer(f"Error operation {file_path} for {node.id}")


async def log_data_info(text: str, message: Message, callback_function):
    logging.info(text)
    await log_data_callback(text, message, callback_function)


async def log_data_error(text: str, message: Message, callback_function):
    logging.error(text)
    await log_data_callback(text, message, callback_function)


async def log_data_callback(text: str, message: Message, callback_function):
    if callback_function is None:
        return
    await callback_function(text, message)

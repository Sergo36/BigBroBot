from aiogram import Router, F
from botStates import States
from aiogram.types import Message, ReplyKeyboardRemove

from data.database import get_server_ip, get_user_by_tn
from data.entity.node_type import NodeType

import os


router = Router()

@router.message(
    States.muonVerification,
    F.text.regexp('[0-9a-zA-Z]{10}'))
async def check_hash(message: Message):

    user = get_user_by_tn(message.from_user.username)
    server = get_server_ip(user.id, NodeType.Muon.value)

    os.system(f'/root/NodeRuner/muon/discordVerification.sh {server.server_ip} {message.text}')

    await message.answer(
        text=f"Set variable {message.text} in server {server.server_ip}",
        reply_markup=ReplyKeyboardRemove()
    )



from aiogram import Router, F
from botStates import States
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from data.database import get_server_ip, get_user_by_tn
from data.entity.node_type import NodeType

import os


router = Router()

@router.message(
    States.muonVerification,
    F.text.regexp('[0-9a-zA-Z]{10}'))
async def check_hash(message: Message, state: FSMContext):

    user = get_user_by_tn(message.from_user.username)

    server = get_server_ip(user.id, NodeType.Muon.value)
    await message.answer(
        text=f"Устанавливая переменную {message.text} на сервере {server.server_ip}",
        reply_markup=ReplyKeyboardRemove()
    )
    #stream = os.popen(f'/root/NodeRuner/muon/discordVerefication.sh <ip> {message.text}')
    #output = stream.read()


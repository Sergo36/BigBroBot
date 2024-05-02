import enum
import logging

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputFile, ReplyKeyboardMarkup
from magic_filter import F

import config
from botStates import ProxyStates
from callbacks.report_callback_factory import ProxyDeviceListCallbackFactory, ProxyNextActionCallbackFactory
from handlers.proxy.proxy_keyboards import get_keyboard_for_complete_action, get_keyboard_for_last_action


class MessageType(enum.Enum):
    answer = 1
    answer_photo = 2


class ActionMessage:
    message_type: MessageType
    text: str
    photo_path: str

    def __init__(self, message_type: MessageType, text: str, photo_path: str = None):
        self.message_type = message_type
        self.text = text
        if photo_path is None:
            self.photo_path = None
        else:
            self.photo_path = photo_path


router = Router()

iphone_instructions = [
    ActionMessage(
        MessageType.answer,
        "Устанавливаем [приложение](https://apps.apple.com/ru/app/spectre-vpn/id1508712998) для подключения"),
    ActionMessage(
        MessageType.answer_photo,
        "Открываем приложение, в разделе Add Server нажимаем сканировать QR Code",
        config.FILE_BASE_PATH + "proxy/iphone_add_server.jpg"
    ),
    ActionMessage(
        MessageType.answer_photo,
        "QR код для настроки",
        config.FILE_BASE_PATH + "proxy/qr_code_server.jpg"
    ),
    ActionMessage(
        MessageType.answer_photo,
        "Для подключений используем вот этот переключатель",
        config.FILE_BASE_PATH + "proxy/iphone_conect_server.jpg"
    )
]
#https://github.com/shadowsocks/shadowsocks-android/releases/download/v5.3.3/shadowsocks-universal-5.3.3.apk
#https://github.com/shadowsocks/shadowsocks-windows/releases/download/4.4.1.0/Shadowsocks-4.4.1.0.zip
#https://github.com/shadowsocks/ShadowsocksX-NG/releases/download/v1.10.2/ShadowsocksX-NG.dmg

@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "iphone"))
async def proxy_iphone_instruction(callback: types.CallbackQuery, state: FSMContext):

    await state.update_data(instruction_index=0)
    await state.set_state(ProxyStates.IPhoneActions)
    await proxy_iphone_next_action(callback, state)

    # text = "Устанавливаем [приложение](https://apps.apple.com/ru/app/spectre-vpn/id1508712998) для подключения"
    # await callback.message.answer(text=text, parse_mode=ParseMode.MARKDOWN_V2)
    #
    # text = "Открываем приложение, в разделе Add Server нажимаем сканировать QR Code"
    # photo = FSInputFile(config.FILE_BASE_PATH + "proxy/iphone_add_server.jpg")
    # await callback.message.answer_photo(photo=photo, caption=text)
    #
    # text = "QR код для настроки"
    # photo = FSInputFile(config.FILE_BASE_PATH + "proxy/qr_code_server.jpg")
    # await callback.message.answer_photo(photo=photo, caption=text)
    #
    # text = "Для подключений используем вот этот переключатель"
    # photo = FSInputFile(config.FILE_BASE_PATH + "proxy/iphone_conect_server.jpg")
    # await callback.message.answer_photo(photo=photo, caption=text)
    #



@router.callback_query(
    ProxyStates.IPhoneActions,
    ProxyNextActionCallbackFactory.filter(F.action == "next"))
async def proxy_iphone_next_action(callback: types.CallbackQuery, state: FSMContext):
    index = (await state.get_data()).get("instruction_index")
    await send_proxy_actions(iphone_instructions, index, callback)
    await state.update_data(instruction_index=index + 1)


@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "android"))
async def proxy_android_instruction(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Android instruction")
    await callback.answer()


@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "windows"))
async def proxy_android_instruction(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Windows instruction")
    await callback.answer()


@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "macbook"))
async def proxy_android_instruction(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("MacBook instruction")
    await callback.answer()


async def send_proxy_actions(action_messages: [], index, callback: types.CallbackQuery):
    action_message = action_messages[index]
    keyboard = None
    if len(action_messages) - 1 > index:
        keyboard = get_keyboard_for_complete_action()
    else:
        keyboard = get_keyboard_for_last_action()

    if action_message.message_type == MessageType.answer:
        await send_answer(action_message, keyboard, callback)
    elif action_message.message_type == MessageType.answer_photo:
        await send_answer_photo(action_message, keyboard, callback)
    else:
        logging.error("Неизветсный тип сообщения")


async def send_answer(action_message: ActionMessage, keyboard: ReplyKeyboardMarkup, callback: types.CallbackQuery):
    await callback.message.answer(text=action_message.text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)
    await callback.answer()


async def send_answer_photo(action_message: ActionMessage, keyboard: ReplyKeyboardMarkup, callback: types.CallbackQuery):
    photo = FSInputFile(action_message.photo_path)
    await callback.message.answer_photo(photo=photo, caption=action_message.text, reply_markup=keyboard)
    await callback.answer()
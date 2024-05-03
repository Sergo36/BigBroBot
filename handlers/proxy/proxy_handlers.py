import enum
import logging

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, ReplyKeyboardMarkup
from magic_filter import F

import config
from botStates import ProxyStates
from callbacks.main_callback_factory import MainCallbackFactory
from callbacks.report_callback_factory import ProxyDeviceListCallbackFactory, ProxyNextActionCallbackFactory
from handlers.common.keyboards import get_keyboard_for_proxy_device_list
from handlers.proxy.proxy_keyboards import get_keyboard_for_complete_action, get_keyboard_for_last_action


class MessageType(enum.Enum):
    answer = 1
    answer_photo = 2
    answer_file = 3


class ActionMessage:
    message_type: MessageType
    text: str
    file_path: str

    def __init__(self, message_type: MessageType, text: str, file_path: str = None):
        self.message_type = message_type
        self.text = text
        if file_path is None:
            self.file_path = None
        else:
            self.file_path = file_path


router = Router()

iphone_instructions = [
    ActionMessage(
        MessageType.answer,
        "Устанавливаем [приложение](https://apps.apple.com/ru/app/spectre-vpn/id1508712998) для прокси"),
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
        "Для включения/отключения прокси используем переключатель",
        config.FILE_BASE_PATH + "proxy/iphone_conect_server.jpg"
    )
]

android_instructions = [
    ActionMessage(
        MessageType.answer_file,
        "Устанавливаем приложение для прокси",
        config.FILE_BASE_PATH + "proxy/shadowsocks-universal-5.3.3.apk"),
    ActionMessage(
        MessageType.answer_photo,
        "Нажимаем добавить профиль",
        config.FILE_BASE_PATH + "proxy/android_add_profile.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "Выбираем сканировать QR-код",
        config.FILE_BASE_PATH + "proxy/android_scan_qr.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "QR код для настроки",
        config.FILE_BASE_PATH + "proxy/qr_code_server.jpg"),
    ActionMessage(
        MessageType.answer_photo,
        "Для включения/отключения прокси используем переключатель",
        config.FILE_BASE_PATH + "proxy/android_connect_server.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "Соглашаемся с запросом на подключение",
        config.FILE_BASE_PATH + "proxy/android_connection_question.jpeg")
]

mac_os_instructions = [
    ActionMessage(
        MessageType.answer_file,
        "Скачиваем образ приложения",
        config.FILE_BASE_PATH + "proxy/ShadowsocksX-NG.dmg"),
    ActionMessage(
        MessageType.answer_photo,
        "Открываем образ и перетягиваем приложение в папку",
        config.FILE_BASE_PATH + "proxy/mac_os_install.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "В Finder переходим к папке с программами",
        config.FILE_BASE_PATH + "proxy/mac_os_open_application_folder.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "Находим Shadowsocks и кликаем с зажатым Control. В меню нажимает открыть",
        config.FILE_BASE_PATH + "proxy/mac_os_open_shadowsocks.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "Соглашаемся с предупреждением",
        config.FILE_BASE_PATH + "proxy/mac_os_open_confirm.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "Кликаем по иконке Shadowsocks в статус баре и проверяем что выбран Global Mode",
        config.FILE_BASE_PATH + "proxy/mac_os_global_mode.jpeg"),
    ActionMessage(
        MessageType.answer,
        "Копируем адрес сервера `ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTp4Zm94N2R4YWQydTJ6dWNh@158.220.108.26:8000`"),
    ActionMessage(
        MessageType.answer_photo,
        "Нажимаем Import Server URL",
        config.FILE_BASE_PATH + "proxy/mac_os_import_server.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "Адрес сервера автоматически вставляется в окно, нажимаем Import",
        config.FILE_BASE_PATH + "proxy/mac_os_import_confirm.jpeg"),
    ActionMessage(
        MessageType.answer_photo,
        "Для включения/выключения прокси используем перключатель \"Turn Sadowsocks\"",
        config.FILE_BASE_PATH + "proxy/mac_os_on_off.jpeg"),
]

windows_instructions = [
    ActionMessage(
        MessageType.answer_file,
        "Скачиваем архив приложения",
        config.FILE_BASE_PATH + "proxy/Shadowsocks-4.4.1.0.zip"),
    ActionMessage(
        MessageType.answer_photo,
        "Распаковываем архив в удобное место. Нарпимер C://Program Files/Shadowsocks",
        config.FILE_BASE_PATH + "proxy/windows_unzip.png"),
    ActionMessage(
        MessageType.answer_photo,
        "Запускаем приложение двойным нажатием из папки куда распаковали",
        config.FILE_BASE_PATH + "proxy/windows_start.png"),
    ActionMessage(
        MessageType.answer_photo,
        "Сразу закрываем открывшияся раздел редактирования серверов",
        config.FILE_BASE_PATH + "proxy/windows_cancel.png"),
    ActionMessage(
        MessageType.answer,
        "Копируем адрес сервера `ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTp4Zm94N2R4YWQydTJ6dWNh@158.220.108.26:8000`"),
    ActionMessage(
        MessageType.answer_photo,
        "Импортируем адрес сервера (вызов меню правой кнопкой мыши)",
        config.FILE_BASE_PATH + "proxy/windows_import.png"),
    ActionMessage(
        MessageType.answer_photo,
        "Подтверждаем импорт",
        config.FILE_BASE_PATH + "proxy/windows_import_confirm.png"),
    ActionMessage(
        MessageType.answer_photo,
        "Соглашаемся с уведомлением об импорте",
        config.FILE_BASE_PATH + "proxy/windows_import_successes.png"),
    ActionMessage(
        MessageType.answer_photo,
        "Для включения/выключения прокси используем раздел \"Системный прокси сервер\"",
        config.FILE_BASE_PATH + "proxy/windows_on_off.png")
]


#https://github.com/shadowsocks/shadowsocks-android/releases/download/v5.3.3/shadowsocks-universal-5.3.3.apk
#https://github.com/shadowsocks/shadowsocks-windows/releases/download/4.4.1.0/Shadowsocks-4.4.1.0.zip
#https://github.com/shadowsocks/ShadowsocksX-NG/releases/download/v1.10.2/ShadowsocksX-NG.dmg


@router.callback_query(MainCallbackFactory.filter(F.action == "proxy_menu"))
async def proxy_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProxyStates.ProxyCommand)
    await callback.message.edit_text(
        text="Выберете тип устройства из списка ниже",
        reply_markup=get_keyboard_for_proxy_device_list()
    )


@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "iphone"))
async def proxy_iphone_instruction(callback: types.CallbackQuery, state: FSMContext):

    await state.update_data(instruction_index=0)
    await state.set_state(ProxyStates.IPhoneActions)
    await proxy_iphone_next_action(callback, state)


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
    await state.update_data(instruction_index=0)
    await state.set_state(ProxyStates.AndroidActions)
    await proxy_android_next_action(callback, state)


@router.callback_query(
    ProxyStates.AndroidActions,
    ProxyNextActionCallbackFactory.filter(F.action == "next"))
async def proxy_android_next_action(callback: types.CallbackQuery, state: FSMContext):
    index = (await state.get_data()).get("instruction_index")
    await send_proxy_actions(android_instructions, index, callback)
    await state.update_data(instruction_index=index + 1)


@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "windows"))
async def proxy_android_instruction(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(instruction_index=0)
    await state.set_state(ProxyStates.Windows)
    await proxy_windows_next_action(callback, state)


@router.callback_query(
    ProxyStates.Windows,
    ProxyNextActionCallbackFactory.filter(F.action == "next"))
async def proxy_windows_next_action(callback: types.CallbackQuery, state: FSMContext):
    index = (await state.get_data()).get("instruction_index")
    await send_proxy_actions(windows_instructions, index, callback)
    await state.update_data(instruction_index=index + 1)


@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "macbook"))
async def proxy_android_instruction(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(instruction_index=0)
    await state.set_state(ProxyStates.MacOsActions)
    await proxy_mac_os_next_action(callback, state)


@router.callback_query(
    ProxyStates.MacOsActions,
    ProxyNextActionCallbackFactory.filter(F.action == "next"))
async def proxy_mac_os_next_action(callback: types.CallbackQuery, state: FSMContext):
    index = (await state.get_data()).get("instruction_index")
    await send_proxy_actions(mac_os_instructions, index, callback)
    await state.update_data(instruction_index=index + 1)



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
    elif action_message.message_type == MessageType.answer_file:
        await send_answer_file(action_message, keyboard, callback)
    else:
        logging.error("Неизветсный тип сообщения")


async def send_answer(action_message: ActionMessage, keyboard: ReplyKeyboardMarkup, callback: types.CallbackQuery):
    await callback.message.answer(text=action_message.text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)
    await callback.answer()


async def send_answer_photo(action_message: ActionMessage, keyboard: ReplyKeyboardMarkup, callback: types.CallbackQuery):
    photo = FSInputFile(action_message.file_path)
    await callback.message.answer_photo(photo=photo, caption=action_message.text, reply_markup=keyboard)
    await callback.answer()


async def send_answer_file(action_message: ActionMessage, keyboard: ReplyKeyboardMarkup, callback: types.CallbackQuery):
    await callback.message.answer("Идет загрузка файла")
    file = FSInputFile(action_message.file_path)
    await callback.message.answer_document(document=file, caption=action_message.text, reply_markup=keyboard)
    await callback.answer()

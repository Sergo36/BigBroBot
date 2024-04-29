from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from magic_filter import F

import config
from botStates import ProxyStates
from callbacks.report_callback_factory import ProxyDeviceListCallbackFactory

router = Router()

#https://github.com/shadowsocks/shadowsocks-android/releases/download/v5.3.3/shadowsocks-universal-5.3.3.apk
#https://github.com/shadowsocks/shadowsocks-windows/releases/download/4.4.1.0/Shadowsocks-4.4.1.0.zip
#https://github.com/shadowsocks/ShadowsocksX-NG/releases/download/v1.10.2/ShadowsocksX-NG.dmg

@router.callback_query(
    ProxyStates.ProxyCommand,
    ProxyDeviceListCallbackFactory.filter(F.device_type == "iphone"))
async def proxy_iphone_instruction(callback: types.CallbackQuery, state: FSMContext):
    text = "Устанавливаем [приложение](https://apps.apple.com/ru/app/spectre-vpn/id1508712998) для подключения: "
    await callback.message.answer(text=text, parse_mode=ParseMode.MARKDOWN_V2)

    text = "Открываем приложение, в разделе Add Server нажимаем сканировать QR Code"
    photo = FSInputFile(config.FILE_BASE_PATH + "proxy/iphone_add_server.jpg")
    await callback.message.answer_photo(photo=photo, caption=text)

    text = "QR код для настроки"
    photo = FSInputFile(config.FILE_BASE_PATH + "proxy/qr_code_server.jpg")
    await callback.message.answer_photo(photo=photo, caption=text)

    text = "Для подключений используем вот этот переключатель"
    photo = FSInputFile(config.FILE_BASE_PATH + "proxy/iphone_conect_server.jpg")
    await callback.message.answer_photo(photo=photo, caption=text)

    await callback.answer()


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
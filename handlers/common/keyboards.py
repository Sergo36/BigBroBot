from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.report_callback_factory import ReportCallbackFactory, ProxyDeviceListCallbackFactory, \
    ProxyNextActionCallbackFactory


def get_keyboard_for_report():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Просмотр базы данных", callback_data=ReportCallbackFactory(action="db_view"))
    builder.button(
        text="Отчет по платежам", callback_data=ReportCallbackFactory(action="payments_report"))
    builder.button(
        text="Отчет по Subspace", callback_data=ReportCallbackFactory(action="subspace_report"))
    builder.adjust(1)
    return builder.as_markup()


def get_keyboard_for_proxy_device_list():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="IPhone", callback_data=ProxyDeviceListCallbackFactory(device_type="iphone"))
    builder.button(
        text="Android", callback_data=ProxyDeviceListCallbackFactory(device_type="android"))
    builder.button(
        text="Windows PC", callback_data=ProxyDeviceListCallbackFactory(device_type="windows"))
    builder.button(
        text="MacBook", callback_data=ProxyDeviceListCallbackFactory(device_type="macbook"))
    builder.adjust(2)
    return builder.as_markup()
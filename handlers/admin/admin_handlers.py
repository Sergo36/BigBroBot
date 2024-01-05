from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from botStates import States
from callbacks.installation_callback_factory import InstallationCallbackFactory
from data.models.node import Node
from handlers.install.install import execute_installation

router = Router()


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    Command(commands=["version"]))
async def version(message: Message):
    await message.answer("1.0.1")


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    Command(commands=["changelog"]))
async def changelog(message: Message):
    await message.answer(text="# Change Log\n"
                              "## [1.0.1] - 2024-01-06\n"
                              "### Changed\n"
                              " - Order notification contains node ID\n"
                              " - Show installation state\n"
                              "## [1.0.0] - 2024-01-04\n"
                              "### Added\n"
                              " - Babylon nodes order\n"
                              " - Hetzner api servers order\n"
                              " - Installation mechanism\n",
                         parse_mode=ParseMode.MARKDOWN)


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    Command(commands=["test"]))
async def test(message: Message, state: FSMContext):
    await state.set_state(States.install)
    kb = InlineKeyboardBuilder()

    test_button = InlineKeyboardButton(
        text="Test",
        callback_data=InstallationCallbackFactory(node="babylon", file_name="babylon_install.sh").pack())
    kb.row(test_button)
    buttons = kb.as_markup()
    await message.answer(text="test", reply_markup=buttons)


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    Command(commands=["install"]))
async def test(message: Message, state: FSMContext):
    await state.set_state(States.install)
    await message.answer("Введите идентификационный номер ноды")


@router.message(
    States.install,
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    F.text.regexp('^[0-9]+$'))
async def node_select_for_node_data(
        message: Message):
    node = Node.get(Node.id == message.text)
    await message.answer(f"Устанавливаю ноду {node.id}")
    await execute_installation(node, message)

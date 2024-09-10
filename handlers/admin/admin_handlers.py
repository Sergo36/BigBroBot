from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from botStates import States
from data.models.node import Node
from data.models.node_type import NodeType
from data.models.server_configuration import ServerConfiguration
from data.models.user import User
from handlers.admin.keyboards import get_keyboard_for_node_overview
from handlers.install.install import execute_installation
from handlers.nodes import create_server

router = Router()


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    Command(commands=["admin"]))
async def admin(message: Message):
    kb = [
        [types.KeyboardButton(text="/version")],
        [types.KeyboardButton(text="/changelog")],
        [types.KeyboardButton(text="/install")],
        [types.KeyboardButton(text="/order")],
        [types.KeyboardButton(text="/overview")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("Доступные комманды", reply_markup=keyboard)


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    Command(commands=["version"]))
async def version(message: Message):
    await message.answer("1.0.2")


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973, 147769504}),
    Command(commands=["changelog"]))
async def changelog(message: Message):
    await message.answer(text="# Change Log\n"
                              "## [1.0.2] - 2024-01-14\n"
                              "### Changed\n"
                              " - Admin panel\n"
                              " - Node overview from admin panel\n"
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
    F.from_user.id.in_({502691086, 250812500, 658498973, 147769504}),
    Command(commands=["install"]))
async def install(message: Message, state: FSMContext):
    await state.set_state(States.manual_install)
    await message.answer("Введите идентификационный номер ноды")


async def callback_function(text: str, message: Message):
    await message.answer(text)


@router.message(
    States.manual_install,
    F.from_user.id.in_({502691086, 250812500, 658498973, 147769504}),
    F.text.regexp('^[0-9]+$'))
async def node_select_for_install(
        message: Message):
    node = Node.get(Node.id == message.text)
    await execute_installation(node, message, callback_function)


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973, 147769504}),
    Command(commands=["order"]))
async def order(message: Message, state: FSMContext):
    await state.set_state(States.manual_order)
    await message.answer("Введите идентификационный номер ноды")


@router.message(
    States.manual_order,
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    F.text.regexp('^[0-9]+$'))
async def node_select_for_order(
        message: Message):
    node = Node.get(Node.id == message.text)

    sc: ServerConfiguration = (ServerConfiguration
                               .select()
                               .join(NodeType, on=(NodeType.server_configuration_id == ServerConfiguration.id))
                               .where(NodeType.id == node.type)
                               .get_or_none())
    if sc is None:
        await message.answer("Не задана конфигурация")
        return

    await message.answer(f"Заказываю сервер для ноды {node.id}")
    server = await create_server(node, sc)

    if server is None:
        await message.answer("Не удалось заказать сервер")
        return
    node.server = server.id
    node.save()
    await message.answer(f"Заказал сервер {server.id}")


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973, 147769504}),
    Command(commands=["overview"]))
async def install(message: Message, state: FSMContext):
    await state.set_state(States.manual_overview)
    await message.answer("Введите идентификационный номер ноды")


@router.message(
    States.manual_overview,
    F.from_user.id.in_({502691086, 250812500, 658498973}),
    F.text.regexp('^[0-9]+$'))
async def node_select_for_overview(
        message: Message,
        state: FSMContext):
    node = Node.get(Node.id == message.text)
    await state.update_data(node=node)
    await state.update_data(interaction_level=1)
    await state.set_state(States.nodes)

    await message.answer(
        text="Выберете действие из списка ниже",
        reply_markup=get_keyboard_for_node_overview())


@router.message(
    F.from_user.id.in_({502691086, 250812500, 658498973, 147769504}),
    Command(commands=["user"]))
async def install(message: Message, state: FSMContext):
    await state.set_state(States.node_list)
    await message.answer("Введите юзернейм")


@router.message(
    States.node_list,
    F.from_user.id.in_({502691086, 250812500, 658498973, 147769504}),
    F.text.regexp('@\w+$'))
async def show_user_nodes(
        message: Message):
    username = message.text[1:] if message.text[0] == '@' else message.text
    query = (User
            .select(Node.id.alias('node_id'), NodeType.name.alias('node_type_name'))
            .join(Node, on=(User.id == Node.owner))
            .join(NodeType, on=(Node.type == NodeType.id))
            .where(User.telegram_name == username)
            .namedtuples())
    res = query.execute()

    text = f'Ноды пользователя @{username}:\n'

    for row in res:
        text += f'{row.node_id} - {row.node_type_name} \n'

    await message.answer(text)

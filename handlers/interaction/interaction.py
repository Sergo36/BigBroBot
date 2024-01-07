import asyncio
import os

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

import config
from botStates import States, SubSpace, InteractionState
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.task_callback_factory import TaskCallbackFactory
from data.models.interaction import Interaction
from data.models.node_data import NodeData
from data.models.node_interactions import NodeInteraction
from handlers.interaction.keyboards import get_keyboard_for_interactions, get_keyboard_default_interaction

router = Router()


@router.callback_query(
    NodesCallbackFactory.filter(F.action == "interaction"))
async def interaction(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    node = data.get('node')

    interactions = (
        Interaction.select(Interaction.name, Interaction.callback)
        .join(NodeInteraction, on=(Interaction.id == NodeInteraction.node_interaction_id))
        .where(NodeInteraction.node_id == node.id)
        .namedtuples())
    keyboard = get_keyboard_for_interactions(interactions, node)
    await state.set_state(States.interaction)
    await callback.message.edit_text(text="Выберете взаимодействие из списка ниже:", reply_markup=keyboard)


@router.callback_query(
    States.interaction,
    TaskCallbackFactory.filter(F.action == "get_screenshot"))
async def new_version_restart_task(
        callback: types.CallbackQuery,
        callback_data: TaskCallbackFactory,
        state: FSMContext):
    telegram_id = (await state.get_data()).get("user").telegram_id
    screenshot_path = f"{config.FILE_BASE_PATH}/{telegram_id}/{callback_data.data}"

    if not os.path.exists(screenshot_path):
        text = "Не найдено"
        await callback.message.edit_text(
            text=text,
            reply_markup=get_keyboard_default_interaction()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await callback.message.answer_photo(screenshot_file)
    await callback.answer()


@router.callback_query(
    States.interaction,
    TaskCallbackFactory.filter(F.action == "add_wallet"))
async def add_wallet(
        callback: types.CallbackQuery,
        state: FSMContext):

    await state.set_state(InteractionState.wallet_set)
    await callback.message.edit_text(
        text="Пришлите адрес кошелька",
        reply_markup=get_keyboard_default_interaction())

@router.message(
    InteractionState.wallet_set,
    F.text.regexp('bbn[0-9a-zA-z]{39}') #bbn13rrkva7ejra0sfe9mava3lhuvr78qje5wezg7c
)
async def babylon_wallet(message: Message, state: FSMContext):
    await set_wallet_address(message, state)


@router.message(
    InteractionState.wallet_set,
    F.text.regexp('st[0-9a-zA-Z]{47}'))
async def subspace_wallet(message: Message, state: FSMContext):
    await set_wallet_address(message, state)


async def set_wallet_address(message: Message, state: FSMContext):
    node = (await state.get_data()).get("node")
    NodeData.get_or_create(
        data=message.text,
        name="Wallet address",
        node_id=node.id,
        defaults={
            'type': 1,
        })

    await message.answer(
        text=f"Адрес кошелька установлен",
        reply_markup=get_keyboard_default_interaction())


@router.message(
    InteractionState.wallet_set)
async def set_wallet_address_error(message: Message):
    await message.answer(
        text="Неверный адрес кошелька. Повторите попытку.",
        reply_markup=get_keyboard_default_interaction())


@router.callback_query(
    States.interaction,
    TaskCallbackFactory.filter(F.action == "set_validator_name"))
async def set_validator_name(
        callback: types.CallbackQuery,
        state: FSMContext):

    await state.set_state(InteractionState.validator_name_set)
    await callback.message.edit_text(
        text="Пришлите желаемое имя валидатора (Латинские буквы, цифры)",
        reply_markup=get_keyboard_default_interaction())


@router.message(
    InteractionState.validator_name_set,
    F.text.regexp('^[a-zA-Z0-9]+$'))
async def set_validator_name(message: Message, state: FSMContext):
    node = (await state.get_data()).get("node")
    NodeData.get_or_create(
        data=message.text,
        name="Validator name",
        node_id=node.id,
        defaults={
            'type': 1,
        })

    await message.answer(
        text=f"Имя валидатора установлено",
        reply_markup=get_keyboard_default_interaction())


@router.message(
    InteractionState.validator_name_set
)
async def set_validator_name_error(message: Message):
    await message.answer(
        text="Неверный формат имени допустимы только латинские буквы и цифры. Повторите попытку.",
        reply_markup=get_keyboard_default_interaction())


@router.callback_query(
    States.interaction,
    TaskCallbackFactory.filter(F.action == "create_validator_babylon"))
async def create_validator_babylon(
        callback: types.CallbackQuery,
        state: FSMContext):
    await state.set_state(InteractionState.create_validator_babylon)
    await callback.message.edit_text(
        text="Пришлите желаемое количество uBBN первоначального стейка",
        reply_markup=get_keyboard_default_interaction())


@router.message(
    InteractionState.create_validator_babylon,
    F.text.regexp('^[0-9]+$'))
async def create_validator_babylon_implement(message: Message, state: FSMContext):
    node = (await state.get_data()).get("node")

    server_ip = NodeData.get_or_none(NodeData.node_id == node.id, NodeData.name == "Server ip")
    if server_ip is None:
        await message.answer("Не задан адрес сервера обратитесь в поддержку")

    moniker = NodeData.get_or_none(NodeData.node_id == node.id, NodeData.name == "Validator name")
    if moniker is None:
        await message.answer("Не задано имя валидатора обратитесь в поддержку")

    script_file_path = config.INSTALL_SCRIPT_PATH + 'babylon/create_validator.sh'
    args = [server_ip.name, message.text, moniker.name]
    proc = await asyncio.create_subprocess_exec(
        script_file_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stdout:
        await message.answer(
            text=f"Транзакция создана `{stdout.decode()}`",
            reply_markup=get_keyboard_default_interaction(),
            parse_mode=ParseMode.MARKDOWN_V2)


@router.message(
    InteractionState.create_validator_babylon
)
async def create_validator_babylon_implement_error(message: Message):
    await message.answer(
        text="Неверный формат числа. Повторите попытку.",
        reply_markup=get_keyboard_default_interaction())


@router.callback_query(
    States.interaction,
    TaskCallbackFactory.filter(F.action == "add_stake_babylon"))
async def add_stake_babylon(
        callback: types.CallbackQuery,
        state: FSMContext):

    await state.set_state(InteractionState.add_stake_babylon)
    await callback.message.edit_text(
        text="Пришлите желаемое количество uBBN",
        reply_markup=get_keyboard_default_interaction())


@router.message(
    InteractionState.add_stake_babylon,
    F.text.regexp('^[0-9]+$'))
async def add_stake_babylon_implement(message: Message, state: FSMContext):
    node = (await state.get_data()).get("node")

    server_ip = NodeData.get_or_none(NodeData.node_id == node.id, NodeData.name == "Server ip")
    if server_ip is None:
        await message.answer("Не задан адрес сервера обратитесь в поддержку")

    moniker = NodeData.get_or_none(NodeData.node_id == node.id, NodeData.name == "Validator name")
    if moniker is None:
        await message.answer("Не задано имя валидатора обратитесь в поддержку")

    script_file_path = config.INSTALL_SCRIPT_PATH + 'babylon/add_stake.sh'
    args = [server_ip.data, message.text]
    proc = await asyncio.create_subprocess_exec(
        script_file_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stdout:
        await message.answer(
            text=f"Транзакция создана `{stdout.decode()}`",
            reply_markup=get_keyboard_default_interaction(),
            parse_mode=ParseMode.MARKDOWN_V2)


@router.message(
    InteractionState.add_stake_babylon
)
async def add_stake_babylon_implement_error(message: Message):
    await message.answer(
        text="Неверный формат числа. Повторите попытку.",
        reply_markup=get_keyboard_default_interaction())


@router.callback_query(
    States.interaction,
    TaskCallbackFactory.filter(F.action == "get_file"))
async def get_file_interaction(
        callback: types.CallbackQuery,
        callback_data: TaskCallbackFactory,
        state: FSMContext):
    node_id = (await state.get_data()).get("node").id
    file_path = f"{config.FILE_BASE_PATH}/{node_id}/{callback_data.data}"

    if not os.path.exists(file_path):
        text = "Файл не найден"
        await callback.message.edit_text(
            text=text,
            reply_markup=get_keyboard_default_interaction()
        )
        return

    file = FSInputFile(file_path)
    await callback.message.answer_document(file)
    await callback.answer()

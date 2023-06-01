import os

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from magic_filter import F

import config
from botStates import States
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.task_callback_factory import TaskCallbackFactory
from data.models.interaction import Interaction
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
    keyboard = get_keyboard_for_interactions(interactions)
    await state.set_state(States.interaction)
    await callback.message.edit_text(text="Chose interaction in list below:", reply_markup=keyboard)


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
        text = "Not found"
        await callback.message.edit_text(
            text=text,
            reply_markup=get_keyboard_default_interaction()
        )
        return

    screenshot_file = FSInputFile(screenshot_path)
    await callback.message.answer_photo(screenshot_file)
    await callback.answer()

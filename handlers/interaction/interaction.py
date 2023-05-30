from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from magic_filter import F

from botStates import States
from callbacks.nodes_callback_factory import NodesCallbackFactory
from callbacks.task_callback_factory import TaskCallbackFactory
from data.models.interaction import Interaction
from data.models.node_interactions import NodeInteraction
from handlers.interaction.keyboards import get_keyboard_for_interactions
from keyboards.for_questions import get_keyboard_null

router = Router()


@router.callback_query(
    States.nodes,
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
    TaskCallbackFactory.filter(F.action == "task_1"))
async def interaction(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Task 1", reply_markup=get_keyboard_null())

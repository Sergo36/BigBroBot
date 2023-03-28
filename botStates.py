from aiogram.filters.state import State, StatesGroup


class States(StatesGroup):
    active = State()
    choosing_nodes_type = State()
    implement_node = State()

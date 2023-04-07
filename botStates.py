from aiogram.filters.state import State, StatesGroup


class States(StatesGroup):
    active = State()
    nodes = State()
    muonVerification = State()
    choosing_nodes_type = State()
    implement_node = State()

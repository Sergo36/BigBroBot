from aiogram.filters.state import State, StatesGroup


class States(StatesGroup):
    authorized = State()
    nodes = State()
    order = State()
    muonVerification = State()
    choosing_nodes_type = State()
    implement_node = State()

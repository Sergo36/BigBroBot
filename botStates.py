from aiogram.filters.state import State, StatesGroup


class States(StatesGroup):
    nodes = State()
    order = State()
    notification = State()
    interaction = State()

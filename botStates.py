from aiogram.filters.state import State, StatesGroup

class States(StatesGroup):
    choosing_nodes = State()
    choosing_food_size = State()

from aiogram.filters.state import State, StatesGroup


class States(StatesGroup):
    nodes = State()
    order = State()
    identification_order = State()
    notification = State()
    interaction = State()
    account = State()


class SubSpace(StatesGroup):
    interaction_wallet = State()


class InteractionState(StatesGroup):
    wallet_set = State()
    validator_name_set = State()


class DbViewReportState(StatesGroup):
    UserSelect = State()
    NodeSelect = State()
    NodeSelectForNodeData = State()
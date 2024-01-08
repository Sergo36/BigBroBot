from aiogram.filters.state import State, StatesGroup


class States(StatesGroup):
    nodes = State()
    order = State()
    identification_order = State()
    notification = State()
    interaction = State()
    account = State()
    install = State()
    manual_order = State()


class SubSpace(StatesGroup):
    interaction_wallet = State()


class InteractionState(StatesGroup):
    wallet_set = State()
    validator_name_set = State()
    add_stake_babylon = State()
    create_validator_babylon = State()


class DbViewReportState(StatesGroup):
    UserSelect = State()
    NodeSelect = State()
    NodeSelectForNodeData = State()

from aiogram.filters.state import State, StatesGroup


class States(StatesGroup):
    nodes = State()
    order = State()
    identification_order = State()
    notification = State()
    interaction = State()
    account = State()
    manual_install = State()
    manual_order = State()
    manual_overview = State()


class SubSpace(StatesGroup):
    interaction_wallet = State()


class InteractionState(StatesGroup):
    wallet_set = State()
    validator_name_set = State()
    add_stake_cosmos = State()
    create_validator_cosmos = State()
    add_rpc = State()
    common_handler = State()


class DbViewReportState(StatesGroup):
    UserSelect = State()
    NodeSelect = State()
    NodeSelectForNodeData = State()


class ProxyStates(StatesGroup):
    ProxyCommand = State()
    IPhoneActions = State()
    AndroidActions = State()

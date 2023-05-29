import config
from hexbytes import HexBytes
from data.models.payment_data import PaymentData
from data.models.transaction import Transaction
from web3 import Web3


def get_transaction(transaction_hash: str) -> Transaction:
    rpc = config.RPC
    web3 = Web3(Web3.HTTPProvider(rpc))
    txn = web3.eth.get_transaction_receipt(transaction_hash)

    contract_address = txn.logs[0].address
    contract = web3.eth.contract(contract_address, abi=config.ERC20_ABI)
    token_decimals = contract.functions.decimals().call()

    return Transaction().initialisation_transaction(transaction_hash, token_decimals, txn)


def transaction_valid(transaction: Transaction) -> bool:
    wallet_address = HexBytes(PaymentData.get(PaymentData.active == True).wallet_address)
    transction_to = HexBytes(transaction.transaction_to)
    return not (False in ([_a == _b for _a, _b in zip(reversed(wallet_address), reversed(transction_to))]))

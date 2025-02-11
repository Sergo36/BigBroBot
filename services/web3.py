import config
from hexbytes import HexBytes
from data.models.payment_data import PaymentData
from data.models.transaction import Transaction
from web3 import Web3
from web3.middleware import geth_poa_middleware


def get_transaction(transaction_hash: str) -> Transaction:
    rpc = config.RPC
    web3 = Web3(Web3.HTTPProvider(rpc))
    txn = web3.eth.get_transaction_receipt(transaction_hash)

    contract_address = txn.logs[0].address
    contract = web3.eth.contract(contract_address, abi=config.ERC20_ABI)
    token_decimals = contract.functions.decimals().call()

    return Transaction().initialisation_transaction(txn, transaction_hash, token_decimals)


def get_block_date(block_hash: str):
    rpc = config.RPC
    web3 = Web3(Web3.HTTPProvider(rpc))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    block = web3.eth.get_block(block_hash)
    return block.timestamp


def hash_equal(first: str, second: str):
    first_hash = HexBytes(first)
    second_hash = HexBytes(second)
    res = True
    for _a, _b in zip(reversed(first_hash), reversed(second_hash)):
        if _a != _b:
            res = False
            break
    return res

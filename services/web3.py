import json

from web3.types import TxReceipt

import config
from hexbytes import HexBytes
from data.models.payment_data import PaymentData
from data.models.payment_token import PaymentToken
from data.models.transaction import Transaction
from web3 import Web3
from web3.middleware import geth_poa_middleware


def get_transaction(transaction_hash: str, rpc: str, abi: str) -> Transaction:
    web3 = Web3(Web3.HTTPProvider(rpc))
    txn: TxReceipt = web3.eth.get_transaction_receipt(transaction_hash)

    contract_address = txn.logs[0].address
    contract = web3.eth.contract(contract_address, abi=json.loads(abi))
    token_decimals = contract.functions.decimals().call()

    return Transaction().initialisation_transaction(transaction_hash, token_decimals, contract_address, txn)


def get_block_date(block_hash: str):
    rpc = config.RPC
    web3 = Web3(Web3.HTTPProvider(rpc))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    block = web3.eth.get_block(block_hash)
    return block.timestamp


def transaction_valid(transaction: Transaction) -> bool:
    wallet_address = HexBytes(PaymentData.get(PaymentData.active == True).wallet_address)
    transaction_to = HexBytes(transaction.transaction_to)
    return not (False in ([_a == _b for _a, _b in zip(reversed(wallet_address), reversed(transaction_to))]))


def equal_address(first: str, second:str) -> bool:
    hex_first = HexBytes(first)
    hex_second = HexBytes(second)
    return not (False in ([_a == _b for _a, _b in zip(reversed(hex_first), reversed(hex_second))]))


def get_transaction_receipt(transaction_hash: str, token: PaymentToken) -> TxReceipt:
    rpc = token.chain_id.rpc_address
    web3 = Web3(Web3.HTTPProvider(rpc))
    return web3.eth.get_transaction_receipt(transaction_hash)

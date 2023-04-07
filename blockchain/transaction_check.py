from web3 import Web3
from data.entity.transaction import Transaction

binance_testnet_rpc_url = "https://bsc-testnet.public.blastapi.io"
web3 = Web3(Web3.HTTPProvider(binance_testnet_rpc_url))
print(f"Is connected: {web3.is_connected()}")

print(f"gas price: {web3.eth.gas_price} BNB")
print(f"current block number: {web3.eth.block_number}")
print(f"number of current chain is {web3.eth.chain_id}")

wallet_address = "0x2F06b63C1259F74C17e231AFf99767ca398Cd124"
balance = web3.eth.get_balance(wallet_address)
print(f"balance of {wallet_address}={balance}")

txn_hash = '0x848e1601a19eb78550524a1210a776621f8056faa1450ef9f4dfbdd24d28cd51'
txn = web3.eth.get_transaction(txn_hash)
print(txn.value)
print(txn)


def check_transaction(transaction: Transaction) -> bool:
    return False

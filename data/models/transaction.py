from data.models.account import Account
from data.models.base_model import BaseModel
from data.models.user import User
from data.models.node import Node
from peewee import TextField, BooleanField, ForeignKeyField, IntegerField, TimestampField, Field


class TransactionValue(TextField):
    def python_value(self, value):
        return f'{(int(value, base=16) / 1000000000000000000):5.2f}'

class Transaction(BaseModel):
    transaction_hash = TextField(column_name='transaction_hash', primary_key=True)
    block_hash = TextField(column_name='block_hash')
    block_number = TextField(column_name='block_number')
    transaction_from = TextField(column_name='transaction_from')
    transaction_to = TextField(column_name='transaction_to')
    transaction_date = TimestampField(column_name='transaction_date')
    status = BooleanField(column_name='status')
    owner = ForeignKeyField(column_name='owner', model=User)
    account_id = ForeignKeyField(column_name='account_id', model=Account)
    value = TransactionValue(column_name='value')
    decimals = IntegerField(column_name='decimals')

    class Meta:
        table_name = 'transactions'

    def initialisation_transaction(self, transaction_hash, decimals, txn):
        self.transaction_hash = transaction_hash
        self.block_hash = txn['blockHash'].hex()
        self.block_number = txn['blockNumber']
        self.transaction_from = txn.logs[0].topics[1].hex()
        self.transaction_to = txn.logs[0].topics[2].hex()
        self.status = bool(txn['status'])
        self.decimals = decimals
        self.owner = 0
        self.value = txn.logs[0].data.hex()
        self.node_id = 0
        return self
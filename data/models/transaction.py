from data.models.base_model import BaseModel
from data.models.user import User
from data.models.node import Node
from peewee import TextField, BooleanField, ForeignKeyField, IntegerField


class Transaction(BaseModel):
    transaction_hash = TextField(column_name='transaction_hash', primary_key=True)
    block_hash = TextField(column_name='block_hash')
    block_number = TextField(column_name='block_number')
    transaction_from = TextField(column_name='transaction_from')
    transaction_to = TextField(column_name='transaction_to')
    status = BooleanField(column_name='status')
    owner = ForeignKeyField(column_name= 'owner', model=User)
    node_id = ForeignKeyField(column_name='node_id', model=Node)
    value = TextField(column_name='value')
    decimals = IntegerField(column_name='decimals')

    class Meta:
        table_name = 'transactions'

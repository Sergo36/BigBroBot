from peewee import AutoField, ForeignKeyField, DoubleField

from data.models.account import Account
from data.models.base_model import BaseModel
from data.models.node import Node


class NodePayments(BaseModel):
    id = AutoField(column_name='id')
    account_id = ForeignKeyField(column_name='account_id', model=Account)
    node_id = ForeignKeyField(column_name='node_id', model=Node)
    value = DoubleField(column_name='value')

    class Meta:
        table_name = 'node_payments'

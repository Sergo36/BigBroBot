# auto-generated snapshot
from peewee import *
import datetime
import peewee


snapshot = Snapshot()


@snapshot.append
class User(peewee.Model):
    telegram_id = IntegerField()
    telegram_name = TextField()
    class Meta:
        table_name = "users"


@snapshot.append
class NodeType(peewee.Model):
    name = TextField()
    description = TextField()
    cost = FloatField()
    class Meta:
        table_name = "node_types"


@snapshot.append
class Node(peewee.Model):
    owner = snapshot.ForeignKeyField(backref='nodes', index=True, model='user')
    type = snapshot.ForeignKeyField(index=True, model='nodetype')
    payment_date = DateField()
    cost = FloatField()
    server_ip = TextField()
    hash = TextField()
    class Meta:
        table_name = "nodes"


@snapshot.append
class Transaction(peewee.Model):
    transaction_hash = TextField(primary_key=True)
    block_hash = TextField()
    block_number = TextField()
    transaction_from = TextField()
    transaction_to = TextField()
    status = BooleanField()
    owner = snapshot.ForeignKeyField(column_name='owner', index=True, model='user')
    node_id = snapshot.ForeignKeyField(index=True, model='node')
    value = TextField()
    decimals = IntegerField()
    class Meta:
        table_name = "transactions"


def forward(old_orm, new_orm):
    old_user = old_orm['user']
    user = new_orm['user']
    return [
        # Convert datatype of the field user.telegram_id: TEXT -> INT,
        user.update({user.telegram_id: old_user.telegram_id.cast('INTEGER')}).where(old_user.telegram_id.is_null(False)),
    ]


def backward(old_orm, new_orm):
    old_user = old_orm['user']
    user = new_orm['user']
    return [
        # Don't know how to do the conversion correctly, use the naive,
        user.update({user.telegram_id: old_user.telegram_id}).where(old_user.telegram_id.is_null(False)),
    ]

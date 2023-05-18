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
class NodeDataType(peewee.Model):
    name = TextField()
    class Meta:
        table_name = "node_data_type"


@snapshot.append
class NodeData(peewee.Model):
    name = TextField()
    type = snapshot.ForeignKeyField(index=True, model='nodedatatype')
    data = TextField()
    class Meta:
        table_name = "node_data"


@snapshot.append
class NodeFields(peewee.Model):
    node_id = snapshot.ForeignKeyField(index=True, model='node')
    node_data_id = snapshot.ForeignKeyField(index=True, model='nodedata')
    class Meta:
        table_name = "node_fields"


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



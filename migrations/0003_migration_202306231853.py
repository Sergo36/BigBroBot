# auto-generated snapshot
from peewee import *
import datetime
import peewee


snapshot = Snapshot()


@snapshot.append
class Interaction(peewee.Model):
    name = TextField()
    callback = TextField()
    class Meta:
        table_name = "interactions"


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
    expiry_date = DateField()
    obsolete = BooleanField()
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
class NodeInteraction(peewee.Model):
    node_id = snapshot.ForeignKeyField(index=True, model='node')
    node_interaction_id = snapshot.ForeignKeyField(index=True, model='interaction')
    class Meta:
        table_name = "node_interactions"


@snapshot.append
class PaymentData(peewee.Model):
    wallet_address = TextField(primary_key=True)
    active = BooleanField()
    class Meta:
        table_name = "payment_data"


@snapshot.append
class Transaction(peewee.Model):
    transaction_hash = TextField(primary_key=True)
    block_hash = TextField()
    block_number = TextField()
    transaction_from = TextField()
    transaction_to = TextField()
    transaction_date = TimestampField(default=datetime.datetime.now)
    status = BooleanField()
    owner = snapshot.ForeignKeyField(column_name='owner', index=True, model='user')
    node_id = snapshot.ForeignKeyField(index=True, model='node')
    value = TextField()
    decimals = IntegerField()
    class Meta:
        table_name = "transactions"


def forward(old_orm, new_orm):
    node = new_orm['node']
    return [
        # Apply default value False to the field node.obsolete,
        node.update({node.obsolete: False}).where(node.obsolete.is_null(True)),
    ]


def backward(old_orm, new_orm):
    node = new_orm['node']
    return [
        # Apply default value datetime.date(2023, 6, 23) to the field node.expiry_date,
        node.update({node.expiry_date: datetime.date(2023, 6, 23)}).where(node.expiry_date.is_null(True)),
    ]

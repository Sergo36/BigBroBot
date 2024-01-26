# auto-generated snapshot
from peewee import *
import data.models.transaction
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
class Account(peewee.Model):
    user_id = snapshot.ForeignKeyField(backref='accounts', index=True, model='user')
    funds = DoubleField()
    class Meta:
        table_name = "accounts"


@snapshot.append
class Hosting(peewee.Model):
    name = TextField()
    class Meta:
        table_name = "hostings"


@snapshot.append
class ServerConfiguration(peewee.Model):
    hosting_id = snapshot.ForeignKeyField(index=True, model='hosting')
    token = TextField()
    location = TextField()
    image = TextField()
    server_type = TextField()
    ssh_key = TextField()
    auto_order = BooleanField()
    class Meta:
        table_name = "server_configurations"


@snapshot.append
class InstallConfiguration(peewee.Model):
    auto_install = BooleanField()
    class Meta:
        table_name = "install_configurations"


@snapshot.append
class NodeType(peewee.Model):
    name = TextField()
    cost = FloatField()
    limit = IntegerField(default=0)
    obsolete = BooleanField(default=False)
    server_configuration_id = snapshot.ForeignKeyField(index=True, model='serverconfiguration', null=True)
    install_configuration = snapshot.ForeignKeyField(index=True, model='installconfiguration', null=True)
    class Meta:
        table_name = "node_types"


@snapshot.append
class CommonNodeData(peewee.Model):
    name = TextField()
    type = snapshot.ForeignKeyField(index=True, model='nodetype')
    data = TextField()
    class Meta:
        table_name = "common_node_data"


@snapshot.append
class Interaction(peewee.Model):
    name = TextField()
    callback = TextField()
    interaction_level = IntegerField(default=0)
    class Meta:
        table_name = "interactions"


@snapshot.append
class CommonNodeInteraction(peewee.Model):
    node_type = snapshot.ForeignKeyField(index=True, model='nodetype')
    node_interaction_id = snapshot.ForeignKeyField(index=True, model='interaction')
    class Meta:
        table_name = "common_node_interaction"


@snapshot.append
class InstallOperation(peewee.Model):
    index = IntegerField()
    install_configuration = snapshot.ForeignKeyField(index=True, model='installconfiguration')
    type = IntegerField()
    file_path = TextField()
    args = TextField()
    class Meta:
        table_name = "install_operations"


@snapshot.append
class Server(peewee.Model):
    hosting_id = snapshot.ForeignKeyField(index=True, model='hosting')
    server_configuration_id = snapshot.ForeignKeyField(index=True, model='serverconfiguration')
    hosting_server_id = TextField()
    obsolete = BooleanField()
    class Meta:
        table_name = "servers"


@snapshot.append
class Node(peewee.Model):
    owner = snapshot.ForeignKeyField(backref='nodes', index=True, model='user')
    type = snapshot.ForeignKeyField(index=True, model='nodetype')
    payment_date = DateField()
    cost = FloatField()
    expiry_date = DateField()
    obsolete = BooleanField()
    server = snapshot.ForeignKeyField(index=True, model='server', null=True)
    class Meta:
        table_name = "nodes"


@snapshot.append
class NodeData(peewee.Model):
    node_id = snapshot.ForeignKeyField(index=True, model='node')
    name = TextField()
    data = TextField()
    class Meta:
        table_name = "node_data"


@snapshot.append
class NodeInteraction(peewee.Model):
    node_id = snapshot.ForeignKeyField(index=True, model='node')
    node_interaction_id = snapshot.ForeignKeyField(index=True, model='interaction')
    class Meta:
        table_name = "node_interactions"


@snapshot.append
class NodePayments(peewee.Model):
    account_id = snapshot.ForeignKeyField(index=True, model='account')
    node_id = snapshot.ForeignKeyField(index=True, model='node')
    value = DoubleField()
    payment_date = DateTimeField()
    class Meta:
        table_name = "node_payments"


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
    account_id = snapshot.ForeignKeyField(index=True, model='account')
    value = data.models.transaction.TransactionValue()
    decimals = IntegerField()
    class Meta:
        table_name = "transactions"



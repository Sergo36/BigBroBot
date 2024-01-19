from data.models.base_model import BaseModel
from peewee import AutoField, TextField, FloatField, ForeignKeyField, IntegerField, BooleanField

from data.models.install_configuration import InstallConfiguration
from data.models.server_configuration import ServerConfiguration


class NodeType(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name')
    cost = FloatField(column_name='cost')
    limit = IntegerField(column_name='limit', default=0)
    obsolete = BooleanField(column_name='obsolete', default=False)
    server_configuration_id = ForeignKeyField(model=ServerConfiguration, null=True)
    install_configuration = ForeignKeyField(model=InstallConfiguration, null=True)

    class Meta:
        table_name = 'node_types'
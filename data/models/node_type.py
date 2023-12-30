from data.models.base_model import BaseModel
from peewee import AutoField, TextField, FloatField, ForeignKeyField

from data.models.server_configuration import ServerConfiguration


class NodeType(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name')
    description = TextField(column_name='description')
    cost = FloatField(column_name='cost')
    server_configuration_id = ForeignKeyField(model=ServerConfiguration, null=True)

    class Meta:
        table_name = 'node_types'
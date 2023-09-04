from peewee import AutoField, TextField, ForeignKeyField

from data.models.base_model import BaseModel
from data.models.node import Node
from data.models.node_data_type import NodeDataType


class NodeData(BaseModel):
    id = AutoField(column_name='id')
    node_id = ForeignKeyField(model=Node, null=True)
    name = TextField(column_name='name')
    type = ForeignKeyField(model=NodeDataType)
    data = TextField(column_name='data')

    class Meta:
        table_name = 'node_data'

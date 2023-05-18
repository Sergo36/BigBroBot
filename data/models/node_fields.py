from peewee import AutoField, ForeignKeyField

from data.models.base_model import BaseModel
from data.models.node import Node
from data.models.node_data import NodeData


class NodeFields(BaseModel):
    id = AutoField(column_name='id')
    node_id = ForeignKeyField(model=Node)
    node_data_id = ForeignKeyField(model=NodeData)

    class Meta:
        table_name = 'node_fields'

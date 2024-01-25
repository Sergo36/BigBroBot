from peewee import AutoField, TextField, ForeignKeyField

from data.models.base_model import BaseModel
from data.models.node_type import NodeType


class CommonNodeData(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name')
    type = ForeignKeyField(model=NodeType)
    data = TextField(column_name='data')

    class Meta:
        table_name = 'common_node_data'

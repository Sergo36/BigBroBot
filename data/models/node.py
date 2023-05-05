from data.models.base_model import BaseModel
from data.models.user import User
from data.models.node_type import NodeType
from peewee import AutoField, TextField, FloatField, ForeignKeyField, DateField


class Node(BaseModel):
    id = AutoField(column_name='id')
    owner = ForeignKeyField(model=User, backref='nodes')
    type = ForeignKeyField(model=NodeType)
    payment_date = DateField(column_name='payment_date')
    cost = FloatField(column_name='cost')
    server_ip = TextField(column_name='server_ip')
    hash = TextField(column_name='hash')

    class Meta:
        table_name = 'nodes'

from peewee import AutoField, ForeignKeyField

from data.models.base_model import BaseModel
from data.models.interaction import Interaction
from data.models.node import Node


class NodeInteraction(BaseModel):
    id = AutoField(column_name='id')
    node_id = ForeignKeyField(model=Node)
    node_interaction_id = ForeignKeyField(model=Interaction)

    class Meta:
        table_name = 'node_interactions'

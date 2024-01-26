from peewee import AutoField, ForeignKeyField

from data.models.base_model import BaseModel
from data.models.interaction import Interaction
from data.models.node_type import NodeType


class CommonNodeInteraction(BaseModel):
    id = AutoField(column_name='id')
    node_type = ForeignKeyField(column_name='node_type_id', model=NodeType)
    node_interaction_id = ForeignKeyField(column_name='node_interaction_id', model=Interaction)

    class Meta:
        table_name = 'common_node_interaction'
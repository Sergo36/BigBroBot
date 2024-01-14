from peewee import AutoField, TextField, IntegerField

from data.models.base_model import BaseModel


class Interaction(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name')
    callback = TextField(column_name='callback')
    interaction_level = IntegerField(column_name='interaction_level',default=0)

    class Meta:
        table_name = 'interactions'

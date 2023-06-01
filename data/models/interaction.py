from peewee import AutoField, TextField

from data.models.base_model import BaseModel


class Interaction(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name')
    callback = TextField(column_name='callback')

    class Meta:
        table_name = 'interactions'

from peewee import AutoField, TextField

from data.models.base_model import BaseModel


class Hosting(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name')

    class Meta:
        table_name = 'hostings'

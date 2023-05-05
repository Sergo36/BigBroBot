from data.models.base_model import BaseModel
from peewee import AutoField, TextField


class User(BaseModel):
    id = AutoField(column_name='id')
    telegram_id = TextField(column_name='telegram_id')
    telegram_name = TextField(column_name='telegram_name')

    class Meta:
        table_name = 'users'

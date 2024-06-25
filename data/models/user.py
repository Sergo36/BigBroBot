from data.models.base_model import BaseModel
from peewee import AutoField, TextField, BigIntegerField


class User(BaseModel):
    id = AutoField(column_name='id')
    telegram_id = BigIntegerField(column_name='telegram_id')
    telegram_name = TextField(column_name='telegram_name')

    class Meta:
        table_name = 'users'

from peewee import AutoField, TextField, ForeignKeyField, BooleanField

from data.models.base_model import BaseModel
from data.models.hosting import Hosting


class ServerConfiguration(BaseModel):
    id = AutoField(column_name='id')
    hosting_id = ForeignKeyField(column_name='hosting_id', model=Hosting)
    token = TextField(column_name='token')
    location = TextField(column_name='location')
    image = TextField(column_name='image')
    server_type = TextField(column_name='server_type')
    ssh_key = TextField(column_name='ssh_key')
    auto_order = BooleanField(column_name='auto_order')

    class Meta:
        table_name = 'server_configurations'

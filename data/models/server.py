import enum

from peewee import AutoField, ForeignKeyField, TextField, BooleanField

from data.models.base_model import BaseModel
from data.models.hosting import Hosting
from data.models.server_configuration import ServerConfiguration


class Server(BaseModel):
    id = AutoField(column_name='id')
    hosting_id = ForeignKeyField(column_name='hosting_id', model=Hosting)
    server_configuration_id = ForeignKeyField(column_name='server_configuration_id', model=ServerConfiguration)
    hosting_server_id = TextField(column_name='hosting_server_id')
    hosting_status = TextField(column_name='hosting_status', null=True)
    install_status = TextField(column_name='install_status', null=True)
    obsolete = BooleanField(column_name='obsolete')

    class Meta:
        table_name = 'servers'


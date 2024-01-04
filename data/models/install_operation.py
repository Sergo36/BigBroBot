from peewee import AutoField, IntegerField, ForeignKeyField, TextField

from data.models.base_model import BaseModel
from data.models.install_configuration import InstallConfiguration


class InstallOperation(BaseModel):
    id = AutoField(column_name='id')
    index = IntegerField(column_name='index')
    install_configuration = ForeignKeyField(column_name='install_configuration_id', model=InstallConfiguration)
    type = IntegerField(column_name='type') # 0 - get, 1 - set
    file_path = TextField(column_name='file_path')
    args = TextField(column_name='args')

    class Meta:
        table_name = 'install_operations'

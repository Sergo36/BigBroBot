from peewee import AutoField, BooleanField

from data.models.base_model import BaseModel


class InstallConfiguration(BaseModel):
    id = AutoField(column_name='id')
    auto_install = BooleanField(column_name='auto_install')

    class Meta:
        table_name = 'install_configurations'

from peewee import AutoField, ForeignKeyField, FloatField, DoubleField

from data.models.base_model import BaseModel
from data.models.user import User


class Account(BaseModel):
    id = AutoField(column_name='id')
    user_id = ForeignKeyField(model=User, backref='accounts')
    funds = DoubleField(column_name='funds')

    class Meta:
        table_name = 'accounts'



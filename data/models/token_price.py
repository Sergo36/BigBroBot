from peewee import AutoField, TextField, ForeignKeyField

from data.models.base_model import BaseModel
from data.models.payment_token import PaymentToken


class TokenPrice(BaseModel):
    id = AutoField(column_name='id', primary_key=True)
    token_id = TextField(column_name="token_id")
    payment_token_id = ForeignKeyField(model=PaymentToken, backref='tokens_prices')

    class Meta:
        table_name = 'tokens_prices'

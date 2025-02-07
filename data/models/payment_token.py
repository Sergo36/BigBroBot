from peewee import AutoField, TextField, ForeignKeyField, BooleanField, FloatField

from data.models.base_model import BaseModel
from data.models.payment_chain import PaymentChain


class PaymentToken(BaseModel):
    id = AutoField(column_name='id', primary_key=True)
    token_name = TextField(column_name="token_name")
    chain_id = ForeignKeyField(model=PaymentChain, backref='payment_tokens')
    is_native_token = BooleanField(column_name='is_native_token')
    contract_address = TextField(column_name='contract_address')
    abi = TextField(column_name="abi")
    token_price = FloatField(column_name='token_price')
    obsolete = BooleanField(column_name='obsolete')

    class Meta:
        table_name = 'payment_tokens'



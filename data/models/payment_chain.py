from peewee import AutoField, TextField

from data.models.base_model import BaseModel


class PaymentChain(BaseModel):
    id = AutoField(column_name='id', primary_key=True)
    chain_name = TextField(column_name="chain_name")
    wallet_address = TextField(column_name="wallet_address")
    rpc_address = TextField(column_name="rpc_address")

    class Meta:
        table_name = 'payment_chains'

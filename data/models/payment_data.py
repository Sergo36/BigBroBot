from peewee import TextField, BooleanField, AutoField

from data.models.base_model import BaseModel


class PaymentData(BaseModel):
    id = AutoField(column_name='id', primary_key=True)
    wallet_address = TextField(column_name="wallet_address")
    active = BooleanField(column_name="active")
    contract_address = TextField(column_name="contract_address")
    contract_name = TextField(column_name="contract_name")

    class Meta:
        table_name = 'payment_data'

from peewee import TextField, BooleanField

from data.models.base_model import BaseModel


class PaymentData(BaseModel):
    wallet_address = TextField(column_name="wallet_address", primary_key=True)
    active = BooleanField(column_name="active")

    class Meta:
        table_name = 'payment_data'

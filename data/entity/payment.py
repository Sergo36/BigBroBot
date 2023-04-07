from datetime import datetime
from data.entity.payment_type import PaymentType


class Payment:
    id: int
    node_id: int
    user_id: int
    status: PaymentType
    date: datetime

    def __init__(self, sql_res):
        self.id = sql_res[0]
        self.node_id = sql_res[1]
        self.user_id = sql_res[2]
        self.status = PaymentType(sql_res[3])
        self.date = sql_res[4]

from datetime import datetime


class Node:
    id: int = 0
    owner: int = 0
    type: int = 0
    payment_date: datetime = datetime(1970, 1, 1)
    cost: float = 0
    server_ip: str = ""

    def initialisation_sql(self, sql_res):
        if not sql_res:
            return self

        self.id = sql_res[0]
        self.owner = sql_res[1]
        self.type = sql_res[2]
        self.payment_date = sql_res[3]
        self.cost = sql_res[4]
        self.server_ip = sql_res[5]

        return self

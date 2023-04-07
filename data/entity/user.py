class User:
    id = 0
    telegram_id = 0
    telegram_name = ""

    def __init__(self, sql_res):
        self.id = sql_res[0]
        self.telegram_id = sql_res[1]
        self.telegram_name = sql_res[2]
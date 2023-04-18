class Transaction:
    transaction_hash = ""
    block_hash = ""
    block_number = ""
    transaction_from = ""
    transaction_to = ""
    # status = ""
    owner = ""
    value = 0
    node_id = 0

    def initialisation_transaction(self, transaction_hash, txn):
        self.transaction_hash = transaction_hash
        self.block_hash = txn['blockHash']
        self.block_number = txn['blockNumber']
        self.transaction_from = txn['from']
        self.transaction_to = txn['to']
        # self.status = txn.
        self.owner = 0
        self.value = txn['value']
        self.node_id = 0
        return self

    def initialisation_sql(self, sql_res):
        self.transaction_hash = sql_res[0]
        self.block_hash = sql_res[1]
        self.block_number = sql_res[2]
        self.transaction_from = sql_res[3]
        self.transaction_to = sql_res[4]
        # self.status = sql_res[5]
        self.owner = sql_res[6]
        self.value = sql_res[7]
        self.node_id = sql_res[8]
        return self

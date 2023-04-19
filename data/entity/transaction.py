from hexbytes import HexBytes
class Transaction:
    transaction_hash = ""
    block_hash = ""
    block_number = ""
    transaction_from = ""
    transaction_to = ""
    status = False
    decimals = 0
    owner = ""
    value = 0
    node_id = 0

    def initialisation_transaction(self, transaction_hash, decimals, txn):
        self.transaction_hash = transaction_hash
        self.block_hash = txn['blockHash'].hex()
        self.block_number = txn['blockNumber']
        self.transaction_from = txn.logs[0].topics[1].hex()
        self.transaction_to = txn.logs[0].topics[2].hex()
        self.status = bool(txn['status'])
        self.decimals = decimals
        self.owner = 0
        self.value = txn.logs[0].data.hex()
        self.node_id = 0
        return self

    def initialisation_sql(self, sql_res):
        self.transaction_hash = sql_res[0]
        self.block_hash = sql_res[1]
        self.block_number = sql_res[2]
        self.transaction_from = sql_res[3]
        self.transaction_to = sql_res[4]
        self.status = sql_res[5]
        self.decimal = sql_res[6]
        self.owner = sql_res[7]
        self.value = sql_res[8]
        self.node_id = sql_res[9]
        return self

    @staticmethod
    def get_sql():
        return """
                SELECT transaction_hash, block_hash, block_number, transaction_from, transaction_to, status, decimals, owner, value, node_id
                FROM public.transaction
                """

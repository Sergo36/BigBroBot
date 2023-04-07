class Transaction:
    transaction_hash = ""
    block_hash = ""
    block_number = ""
    transaction_from = ""
    transaction_to = ""
    #status = ""
    owner = ""
    value = 0
    payment_id = 0

    def __init__(self, transaction_hash, txn):
        self.transaction_hash = transaction_hash
        self.block_hash = txn['blockHash']
        self.block_number = txn['blockNumber']
        #self.transaction_from = txn.from
        self.transaction_to = txn['to']
        #self.status = txn.
        self.owner = 0
        self.value = txn['value']
        self.payment_id = 0

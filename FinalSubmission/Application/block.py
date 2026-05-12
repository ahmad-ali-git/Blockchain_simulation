import hashlib
import time


class Block:
    def __init__(self, index, transactions, previous_hash, miner_id):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.miner_id = miner_id
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = (
            str(self.index)
            + str(self.timestamp)
            + str(self.transactions)
            + str(self.previous_hash)
            + str(self.miner_id)
            + str(self.nonce)
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

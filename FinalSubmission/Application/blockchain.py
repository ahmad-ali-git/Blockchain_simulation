from block import Block


class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.create_genesis_block()  

    def create_genesis_block(self):
        genesis = Block(
            index=0,
            transactions=["Genesis Block"],
            previous_hash="0" * 64,
            miner_id="system"
        )
        self.chain.append(genesis)

    def get_latest_block(self):
        return self.chain[-1]

    def mine_block(self, miner_id, transactions=None):
        if transactions is None:
            transactions = self.pending_transactions

        new_block = Block(
            index=len(self.chain),      #next position 
            transactions=transactions,
            previous_hash=self.get_latest_block().hash,
            miner_id=miner_id
        )

        # PoW - keep incrementing nonce until we get a valid hash
        target = "0" * self.difficulty
        while not new_block.hash.startswith(target):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def print_chain(self):
        for block in self.chain:
            print(f"Block {block.index} | Miner: {block.miner_id} | Hash: {block.hash[:15]}... | Prev: {block.previous_hash[:15]}...")
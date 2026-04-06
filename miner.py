
import copy


class Miner:
    def __init__(self, miner_id, hashrate, is_malicious=False):
        self.miner_id = miner_id
        self.hashrate = hashrate  # e.g 0.55 = 55% computing power
        self.is_malicious = is_malicious
        self.blocks_mined = 0


class HonestMiner(Miner):
    def __init__(self, miner_id, hashrate):
        super().__init__(miner_id, hashrate, is_malicious=False)

    def mine(self, blockchain, transactions):
        block = blockchain.mine_block(self.miner_id, transactions)
        self.blocks_mined += 1
        return block


class MaliciousMiner(Miner):
    def __init__(self, miner_id, hashrate):
        super().__init__(miner_id, hashrate, is_malicious=True)
        self.private_chain = None
        self.attack_started = False

    def start_private_chain(self, blockchain):
        self.private_chain = copy.deepcopy(blockchain)
        self.attack_started = True

    def mine_on_private_chain(self, transactions):
        if self.private_chain is None:
            return None
        block = self.private_chain.mine_block(self.miner_id, transactions)
        self.blocks_mined += 1
        return block

    def should_publish(self, honest_chain_length):
        if self.private_chain is None:
            return False
        return len(self.private_chain.chain) > honest_chain_length

    def publish_private_chain(self):
        chain = self.private_chain
        self.private_chain = None
        self.attack_started = False
        return chain
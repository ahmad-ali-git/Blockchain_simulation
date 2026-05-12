import copy


class Miner:
    def __init__(self, miner_id, num_nodes=1, is_malicious=False):
        self.miner_id = miner_id
        self.num_nodes = num_nodes
        self.is_malicious = is_malicious
        self.blocks_mined = 0
        self.hashrate = 0.0  # computed later by the Network based on total nodes

    def add_node(self, count=1):
        self.num_nodes += count

    def remove_node(self, count=1):
        self.num_nodes = max(0, self.num_nodes - count)


class HonestMiner(Miner):
    def __init__(self, miner_id, num_nodes=1):
        super().__init__(miner_id, num_nodes, is_malicious=False)

    def mine(self, blockchain, transactions):
        block = blockchain.mine_block(self.miner_id, transactions)
        self.blocks_mined += 1
        return block


class MaliciousMiner(Miner):
    def __init__(self, miner_id, num_nodes=1):
        super().__init__(miner_id, num_nodes, is_malicious=True)
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


class Network:
    """Computes per-miner hashrate from node counts across all miners."""

    def __init__(self, miners):
        self.miners = miners
        self.recalculate()

    def recalculate(self):
        total_nodes = sum(m.num_nodes for m in self.miners)
        if total_nodes == 0:
            for m in self.miners:
                m.hashrate = 0.0
            self.total_nodes = 0
            return
        for m in self.miners:
            m.hashrate = m.num_nodes / total_nodes
        self.total_nodes = total_nodes

    def attacker_hashrate(self):
        for m in self.miners:
            if m.is_malicious:
                return m.hashrate
        return 0.0

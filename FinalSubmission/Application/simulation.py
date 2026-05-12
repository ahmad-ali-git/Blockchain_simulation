import random
from blockchain import Blockchain
from transaction import Transaction, UTXOSet
from miner import HonestMiner, MaliciousMiner, Network
from lpc_defense import LPCDefense


class Simulation:
    """
    Node-based simulation engine.

    Hashrate for every miner is derived from the number of nodes they run
    relative to the total nodes on the network. Add more nodes -> larger
    share of block production chances.
    """

    def __init__(self, honest_nodes=None, attacker_nodes=12,
                 total_blocks=30, difficulty=2, max_consecutive=6,
                 attack_start_fraction=1 / 3, on_event=None):
        # honest_nodes: list of ints, one per honest miner, e.g. [2, 2, 2, 2, 2]
        if honest_nodes is None:
            honest_nodes = [2, 2, 2, 2, 2]
        self.honest_nodes = list(honest_nodes)
        self.attacker_nodes = attacker_nodes
        self.total_blocks = total_blocks
        self.difficulty = difficulty
        self.attack_start_fraction = attack_start_fraction
        self.lpc_defense = LPCDefense(max_consecutive=max_consecutive)
        self.event_log = []
        # on_event(event_dict) — optional callback for live GUI streaming
        self.on_event = on_event

    # ---------- event emission ----------
    def _emit(self, kind, message, **extra):
        event = {"kind": kind, "message": message, **extra}
        self.event_log.append(event)
        if self.on_event:
            self.on_event(event)
        # also print for CLI users
        print(message)

    # ---------- setup ----------
    def setup_miners(self):
        self.honest_miners = [
            HonestMiner(f"Honest_{i + 1}", num_nodes=n)
            for i, n in enumerate(self.honest_nodes)
        ]
        self.attacker = MaliciousMiner("Attacker", num_nodes=self.attacker_nodes)
        self.network = Network(self.honest_miners + [self.attacker])

    def setup_utxo(self):
        self.utxo = UTXOSet()
        self.utxo.initialize_balance("Alice", 1000)
        self.utxo.initialize_balance("Bob", 500)
        self.utxo.initialize_balance("Charlie", 300)
        self.utxo.initialize_balance("Attacker", 500)

    def select_miner(self):
        all_miners = self.honest_miners + [self.attacker]
        hashrates = [m.hashrate for m in all_miners]
        return random.choices(all_miners, weights=hashrates, k=1)[0]

    def generate_transaction(self):
        users = ["Alice", "Bob", "Charlie"]
        sender = random.choice(users)
        receiver = random.choice([u for u in users if u != sender])
        amount = random.randint(1, 10)
        return Transaction(sender, receiver, amount)

    # ---------- baseline run (no defense) ----------
    def run_baseline(self):
        self._emit("header", "=" * 60)
        self._emit("header", "BASELINE SIMULATION (No Defense)")
        self._emit("header", "=" * 60)

        self.setup_miners()
        self.setup_utxo()
        self._emit(
            "info",
            f"Network: {len(self.honest_miners)} honest miners, "
            f"attacker hashrate = {self.attacker.hashrate * 100:.1f}% "
            f"({self.attacker.num_nodes}/{self.network.total_nodes} nodes)",
            attacker_hashrate=self.attacker.hashrate,
            total_nodes=self.network.total_nodes,
        )

        blockchain = Blockchain(self.difficulty)
        self.lpc_defense.disable()

        attack_started = False
        attack_block = int(self.total_blocks * self.attack_start_fraction)

        for i in range(self.total_blocks):
            tx = self.generate_transaction()
            selected = self.select_miner()

            if i == attack_block and not attack_started:
                self.attacker.start_private_chain(blockchain)
                attack_started = True
                double_spend_tx = Transaction("Attacker", "Attacker_wallet2", 500)
                self.attacker.mine_on_private_chain([str(double_spend_tx)])
                self._emit(
                    "attack",
                    f"  [!] Block {i}: Attacker started secret private chain!",
                    block_index=i,
                )
                self._progress(i, blockchain, attack_started)
                continue

            if attack_started and selected == self.attacker:
                self.attacker.mine_on_private_chain([str(tx)])
                self._emit(
                    "attack",
                    f"  [!] Block {i}: Attacker mining secretly...",
                    block_index=i,
                )
                self._progress(i, blockchain, attack_started)
                continue

            blockchain.mine_block(selected.miner_id, [str(tx)])
            selected.blocks_mined += 1
            self._emit(
                "mined",
                f"  Block {i}: Mined by {selected.miner_id}",
                block_index=i,
                miner_id=selected.miner_id,
            )
            self._progress(i, blockchain, attack_started)

        attack_success = False
        if attack_started:
            if self.attacker.should_publish(len(blockchain.chain)):
                attacker_chain = self.attacker.publish_private_chain()
                self._emit(
                    "attack",
                    f"  [!!] Attacker published private chain! "
                    f"Honest={len(blockchain.chain)} vs Attacker={len(attacker_chain.chain)}",
                    honest_len=len(blockchain.chain),
                    attacker_len=len(attacker_chain.chain),
                )
                attack_success = True
                blockchain = attacker_chain
            else:
                self._emit(
                    "info",
                    f"  [X] Attacker's chain too short ({len(self.attacker.private_chain.chain)}), "
                    f"honest wins ({len(blockchain.chain)})",
                )
                self.attacker.publish_private_chain()

        self._emit(
            "result",
            f"Attack Success: {attack_success}",
            attack_success=attack_success,
        )
        return {
            "attack_success": attack_success,
            "chain": blockchain,
            "total_blocks": len(blockchain.chain),
            "blocks_rejected": 0,
            "attacker_hashrate": self.attacker.hashrate,
            "total_nodes": self.network.total_nodes,
        }

    # ---------- LPC chain-wide check ----------
    def check_chain_lpc_violation(self, chain):
        if len(chain) < self.lpc_defense.max_consecutive + 1:
            return False
        count = 1
        for i in range(2, len(chain)):
            if chain[i].miner_id == chain[i - 1].miner_id:
                count += 1
                if count >= self.lpc_defense.max_consecutive:
                    return True
            else:
                count = 1
        return False

    # ---------- protected run (with Safe Mode Detection) ----------
    def run_protected(self):
        self._emit("header", "=" * 60)
        self._emit("header", "PROTECTED SIMULATION (LPC + Safe Mode)")
        self._emit("header", "=" * 60)

        self.setup_miners()
        self.setup_utxo()
        self._emit(
            "info",
            f"Network: {len(self.honest_miners)} honest miners, "
            f"attacker hashrate = {self.attacker.hashrate * 100:.1f}% "
            f"({self.attacker.num_nodes}/{self.network.total_nodes} nodes)",
            attacker_hashrate=self.attacker.hashrate,
            total_nodes=self.network.total_nodes,
        )

        blockchain = Blockchain(self.difficulty)
        self.lpc_defense.enable()
        self.lpc_defense.rejected_blocks_count = 0
        self.lpc_defense.event_log = []

        attack_started = False
        attack_block = int(self.total_blocks * self.attack_start_fraction)
        attacker_utxo = None

        for i in range(self.total_blocks):
            tx = self.generate_transaction()
            selected = self.select_miner()

            if i == attack_block and not attack_started:
                self.attacker.start_private_chain(blockchain)
                attack_started = True

                attacker_utxo = UTXOSet()
                attacker_utxo.balances = self.utxo.get_snapshot()

                double_spend_tx = Transaction("Attacker", "Attacker_wallet2", 500)
                self.attacker.mine_on_private_chain([str(double_spend_tx)])
                attacker_utxo.apply_transaction(double_spend_tx)
                self._emit(
                    "attack",
                    f"  [!] Block {i}: Attacker started secret private chain!",
                    block_index=i,
                )
                self._progress(i, blockchain, attack_started)
                continue

            if attack_started and selected == self.attacker:
                self.attacker.mine_on_private_chain([str(tx)])
                if attacker_utxo.is_valid_transaction(tx):
                    attacker_utxo.apply_transaction(tx)
                self._emit(
                    "attack",
                    f"  [!] Block {i}: Attacker mining secretly...",
                    block_index=i,
                )
                self._progress(i, blockchain, attack_started)
                continue

            if self.lpc_defense.should_reject_block(blockchain.chain, selected.miner_id):
                self._emit(
                    "defense",
                    f"  [DEFENSE] Block {i}: LPC rejected block by {selected.miner_id}",
                    block_index=i,
                    miner_id=selected.miner_id,
                )
                self._progress(i, blockchain, attack_started)
                continue

            blockchain.mine_block(selected.miner_id, [str(tx)])
            selected.blocks_mined += 1
            if self.utxo.is_valid_transaction(tx):
                self.utxo.apply_transaction(tx)
            self._emit(
                "mined",
                f"  Block {i}: Mined by {selected.miner_id}",
                block_index=i,
                miner_id=selected.miner_id,
            )
            self._progress(i, blockchain, attack_started)

        attack_success = False
        if attack_started:
            if self.attacker.should_publish(len(blockchain.chain)):
                attacker_chain = self.attacker.publish_private_chain()
                self._emit(
                    "attack",
                    f"  [!!] Attacker trying to publish... "
                    f"Honest={len(blockchain.chain)} vs Attacker={len(attacker_chain.chain)}",
                )

                if self.check_chain_lpc_violation(attacker_chain.chain):
                    self.lpc_defense.rejected_blocks_count += 1
                    self._emit(
                        "defense",
                        f"  [DEFENSE] LPC: attacker's chain has "
                        f"{self.lpc_defense.max_consecutive}+ consecutive blocks by same miner! "
                        f"Chain REJECTED.",
                    )
                    attack_success = False
                else:
                    differences = self.utxo.compare_with(attacker_utxo)
                    if differences:
                        self._emit(
                            "defense",
                            f"  [SAFE MODE] Double-spend detected! Diffs={differences}. "
                            f"Chain REJECTED.",
                            differences=differences,
                        )
                        attack_success = False
                    else:
                        attack_success = True
                        blockchain = attacker_chain
            else:
                self._emit(
                    "info",
                    f"  [X] Attacker's chain too short "
                    f"({len(self.attacker.private_chain.chain)}), "
                    f"honest wins ({len(blockchain.chain)})",
                )
                self.attacker.publish_private_chain()

        self._emit(
            "result",
            f"Attack Success: {attack_success} | "
            f"Blocks rejected by LPC: {self.lpc_defense.rejected_blocks_count}",
            attack_success=attack_success,
            blocks_rejected=self.lpc_defense.rejected_blocks_count,
        )
        return {
            "attack_success": attack_success,
            "chain": blockchain,
            "total_blocks": len(blockchain.chain),
            "blocks_rejected": self.lpc_defense.rejected_blocks_count,
            "attacker_hashrate": self.attacker.hashrate,
            "total_nodes": self.network.total_nodes,
        }

    # ---------- progress helper for GUI live view ----------
    def _progress(self, i, blockchain, attack_started):
        if not self.on_event:
            return
        private_len = (
            len(self.attacker.private_chain.chain)
            if attack_started and self.attacker.private_chain is not None
            else 0
        )
        self.on_event({
            "kind": "progress",
            "step": i + 1,
            "total": self.total_blocks,
            "honest_len": len(blockchain.chain),
            "private_len": private_len,
        })

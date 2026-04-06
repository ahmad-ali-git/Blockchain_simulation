import random
from blockchain import Blockchain
from transaction import Transaction, UTXOSet
from miner import HonestMiner, MaliciousMiner
from lpc_defense import LPCDefense


class Simulation:
    def __init__(self, num_honest_miners=5, attacker_hashrate=0.55,
                 total_blocks=30, difficulty=2):
        self.num_honest_miners = num_honest_miners
        self.attacker_hashrate = attacker_hashrate
        self.total_blocks = total_blocks
        self.difficulty = difficulty
        self.lpc_defense = LPCDefense(max_consecutive=6)
        self.event_log = []

    def setup_miners(self):
        honest_hashrate = (1 - self.attacker_hashrate) / self.num_honest_miners
        self.honest_miners = []
        for i in range(self.num_honest_miners):
            miner = HonestMiner(f"Honest_{i+1}", honest_hashrate)
            self.honest_miners.append(miner)
        self.attacker = MaliciousMiner("Attacker", self.attacker_hashrate)

    def setup_utxo(self):
        self.utxo = UTXOSet()
        self.utxo.initialize_balance("Alice", 1000)
        self.utxo.initialize_balance("Bob", 500)
        self.utxo.initialize_balance("Charlie", 300)
        self.utxo.initialize_balance("Attacker", 500)

    def select_miner(self):
        # weighted random selection based on hashrate
        all_miners = self.honest_miners + [self.attacker]
        hashrates = [m.hashrate for m in all_miners]
        return random.choices(all_miners, weights=hashrates, k=1)[0]

    def generate_transaction(self):
        users = ["Alice", "Bob", "Charlie"]
        sender = random.choice(users)
        receiver = random.choice([u for u in users if u != sender])
        amount = random.randint(1, 10)
        return Transaction(sender, receiver, amount)

    def run_baseline(self):
        print("=" * 60)
        print("BASELINE SIMULATION (No Defense)")
        print("=" * 60)

        self.setup_miners()
        self.setup_utxo()
        blockchain = Blockchain(self.difficulty)
        self.lpc_defense.disable()

        attack_started = False
        attack_block = self.total_blocks // 3

        for i in range(self.total_blocks):
            tx = self.generate_transaction()
            selected = self.select_miner()

            if i == attack_block and not attack_started:
                self.attacker.start_private_chain(blockchain)
                attack_started = True
                double_spend_tx = Transaction("Attacker", "Attacker_wallet2", 500)
                self.attacker.mine_on_private_chain([str(double_spend_tx)])
                self.event_log.append(f"Block {i}: Attacker started private chain")
                print(f"  [!] Block {i}: Attacker started secret private chain!")
                continue

            if attack_started and selected == self.attacker:
                self.attacker.mine_on_private_chain([str(tx)])
                self.event_log.append(f"Block {i}: Attacker mined on private chain")
                print(f"  [!] Block {i}: Attacker mining secretly...")
                continue

            blockchain.mine_block(selected.miner_id, [str(tx)])
            print(f"  Block {i}: Mined by {selected.miner_id}")

        honest_snapshot = self.utxo.get_snapshot()

        attack_success = False
        if attack_started:
            if self.attacker.should_publish(len(blockchain.chain)):
                attacker_chain = self.attacker.publish_private_chain()
                print(f"\n  [!!] Attacker published private chain!")
                print(f"  Honest chain length: {len(blockchain.chain)}")
                print(f"  Attacker chain length: {len(attacker_chain.chain)}")
                attack_success = True
                blockchain = attacker_chain
            else:
                print(f"\n  Honest chain length: {len(blockchain.chain)}")
                print(f"  Attacker chain length: {len(self.attacker.private_chain.chain)}")
                print(f"  [X] Attacker's chain too short, attack failed")
                self.attacker.publish_private_chain()

        print(f"\n  Attack Success: {attack_success}")
        print(f"\n  Final Chain:")
        blockchain.print_chain()
        return {"attack_success": attack_success, "chain": blockchain,
                "total_blocks": len(blockchain.chain)}

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

    def run_protected(self):
        print("\n" + "=" * 60)
        print("PROTECTED SIMULATION (With LPC Defense)")
        print("=" * 60)

        self.setup_miners()
        self.setup_utxo()
        blockchain = Blockchain(self.difficulty)
        self.lpc_defense.enable()
        self.lpc_defense.rejected_blocks_count = 0
        self.lpc_defense.event_log = []

        attack_started = False
        attack_block = self.total_blocks // 3
        attacker_utxo = None

        for i in range(self.total_blocks):
            tx = self.generate_transaction()
            selected = self.select_miner()

            if i == attack_block and not attack_started:
                self.attacker.start_private_chain(blockchain)
                attack_started = True

                # fork utxo state here so we can compare later
                attacker_utxo = UTXOSet()
                attacker_utxo.balances = self.utxo.get_snapshot()

                double_spend_tx = Transaction("Attacker", "Attacker_wallet2", 500)
                self.attacker.mine_on_private_chain([str(double_spend_tx)])
                attacker_utxo.apply_transaction(double_spend_tx)
                self.event_log.append(f"Block {i}: Attacker started private chain")
                print(f"  [!] Block {i}: Attacker started secret private chain!")
                continue

            # attacker mines secretly, LPC cant see this
            if attack_started and selected == self.attacker:
                self.attacker.mine_on_private_chain([str(tx)])
                if attacker_utxo.is_valid_transaction(tx):
                    attacker_utxo.apply_transaction(tx)
                print(f"  [!] Block {i}: Attacker mining secretly...")
                continue

            if self.lpc_defense.should_reject_block(blockchain.chain, selected.miner_id):
                print(f"  [DEFENSE] Block {i}: LPC rejected block by {selected.miner_id}")
                continue

            blockchain.mine_block(selected.miner_id, [str(tx)])
            if self.utxo.is_valid_transaction(tx):
                self.utxo.apply_transaction(tx)
            print(f"  Block {i}: Mined by {selected.miner_id}")

        attack_success = False
        if attack_started:
            if self.attacker.should_publish(len(blockchain.chain)):
                attacker_chain = self.attacker.publish_private_chain()
                print(f"\n  [!!] Attacker trying to publish private chain...")
                print(f"  Honest chain: {len(blockchain.chain)} blocks")
                print(f"  Attacker chain: {len(attacker_chain.chain)} blocks")

                # check if published chain violates LPC
                if self.check_chain_lpc_violation(attacker_chain.chain):
                    self.lpc_defense.rejected_blocks_count += 1
                    print(f"\n  [DEFENSE] LPC: Attacker's chain has {self.lpc_defense.max_consecutive}+ consecutive blocks by same miner!")
                    print(f"  Attacker's chain REJECTED!")
                    attack_success = False

                # if LPC passes, check utxo for double spend
                else:
                    differences = self.utxo.compare_with(attacker_utxo)
                    if differences:
                        print(f"\n  [SAFE MODE] Double-spend detected!")
                        print(f"  UTXO differences: {differences}")
                        print(f"  Attacker's chain REJECTED!")
                        attack_success = False
                    else:
                        attack_success = True
                        blockchain = attacker_chain
            else:
                print(f"\n  Honest chain: {len(blockchain.chain)} blocks")
                print(f"  Attacker chain: {len(self.attacker.private_chain.chain)} blocks")
                print(f"  [X] Attacker's chain too short, attack failed")
                self.attacker.publish_private_chain()

        print(f"\n  Attack Success: {attack_success}")
        print(f"  Blocks rejected by LPC: {self.lpc_defense.rejected_blocks_count}")
        print(f"\n  Final Chain:")
        blockchain.print_chain()
        return {"attack_success": attack_success, "chain": blockchain,
                "total_blocks": len(blockchain.chain),
                "blocks_rejected": self.lpc_defense.rejected_blocks_count}
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __repr__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}"


# UTXO based balance tracking
class UTXOSet:
    def __init__(self):
        self.balances = {}

    def initialize_balance(self, address, amount):
        self.balances[address] = amount

    def get_balance(self, address):
        return self.balances.get(address, 0)

    def is_valid_transaction(self, transaction):
        if transaction.sender == "system":
            return True
        return self.get_balance(transaction.sender) >= transaction.amount

    def apply_transaction(self, transaction):
        if transaction.sender != "system":
            self.balances[transaction.sender] = self.get_balance(transaction.sender) - transaction.amount
        self.balances[transaction.receiver] = self.get_balance(transaction.receiver) + transaction.amount

    def get_snapshot(self):
        return self.balances.copy()

    def compare_with(self, other_utxo):
        differences = {}
        all_addresses = set(self.balances.keys()) | set(other_utxo.balances.keys())
        for addr in all_addresses:
            my_bal = self.get_balance(addr)
            other_bal = other_utxo.get_balance(addr)
            if my_bal != other_bal:
                differences[addr] = {"honest": my_bal, "competing": other_bal}
        return differences


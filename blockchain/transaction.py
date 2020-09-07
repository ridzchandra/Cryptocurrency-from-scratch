
class Transaction:
    def __init__(self, sender, recipient, signature, tx_amt):
        self.sender = sender
        self.recipient = recipient
        self.tx_amt = tx_amt
        self.signature = signature

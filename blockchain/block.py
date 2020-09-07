from time import time


class Block:
    def __init__(self, prev_hash, index, transactions, proof, timestamp=None):
        self.prev_hash = prev_hash
        self.index = index
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time() if timestamp is None else timestamp

    def deep_dict(self):
        transactions = [tx.__dict__ for tx in self.transactions]
        dict_block = {
            'prev_hash' : self.prev_hash,
            'index' : self.index,
            'transactions' : transactions,
            'proof' : self.proof,
            'timestamp' : self.timestamp
        }
        return dict_block
   
        

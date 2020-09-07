from blockchain.block import Block
from blockchain.transaction import Transaction
from copy import deepcopy
# from blockchain import blockchain, open_transactions

class Json_translator():
    @staticmethod
    def dict_to_block(dictionary):
        return Block(
            prev_hash=dictionary['prev_hash'],
            index=dictionary['index'],
            transactions=dictionary['transactions'],
            proof=dictionary['proof'],
            timestamp=dictionary['timestamp']
        )

    @staticmethod
    def dict_to_transaction(dictionary):
        return Transaction(
            sender=dictionary['sender'],
            recipient=dictionary['recipient'],
            signature=dictionary['signature'],
            tx_amt=dictionary['tx_amt']
        )

    @classmethod
    def undict_blockchain(cls, blockchain):
        blockchain = deepcopy(blockchain) # have to deepcopy it or else the function manipulates the actual chain
        for block_index, dict_block in enumerate(blockchain):
            for tx_index, dict_transaction in enumerate(dict_block['transactions']):
                dict_block['transactions'][tx_index] = cls.dict_to_transaction(
                    dict_transaction)
            blockchain[block_index] = cls.dict_to_block(dict_block)
        return blockchain

    @classmethod
    def undict_open_transactions(cls, open_transactions):
        open_transactions = deepcopy(open_transactions) # have to deepcopy it or else the function manipulates the actual list
        open_transactions = [cls.dict_to_transaction(
            dict_transaction) for dict_transaction in open_transactions]
        return open_transactions

    @staticmethod
    def dict_blockchain(blockchain): 
        blockchain = deepcopy(blockchain) # have to deepcopy it or else the function manipulates the actual chain 
        for block_index, block in enumerate(blockchain):
            for tx_index, transaction in enumerate(block.transactions):
                block.transactions[tx_index] = transaction.__dict__
            blockchain[block_index] = block.__dict__
        return blockchain

    @staticmethod
    def dict_open_transactions(open_transactions):
        open_transactions = deepcopy(open_transactions) # have to deepcopy it or else the function manipulates the actual list
        open_transactions = [
            transaction.__dict__ for transaction in open_transactions]
        return open_transactions


# Manipulationg the genesis block when no other blocks are present is not diagnosed   ------ Yet to be resolved
from functools import reduce
from copy import deepcopy
import hashlib as hlib
import json
from collections import OrderedDict
from .block import Block
from .transaction import Transaction
from utility.json_translator import Json_translator
from utility.verification import Verification
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:

    def __init__(self, hosting_node_id, dev_port):
        GENESIS_BLOCK = Block(prev_hash='', index=0,
                              transactions=[], proof=100)
        self.__chain = [GENESIS_BLOCK]  # both the blockchain & open_transactions are madde private so that they cant be manipulated outside the blockchain class and to access one's gotta use methods get_chain() and get_open_transactions() which would only return a copy of these but not the actual objects
        self.__open_transactions = []
        self.hosting_node_id = hosting_node_id
        self.dev_port = dev_port
        self.__peer_nodes = set()
        self.load_data()

    def get_chain(self):
        return deepcopy(self.__chain)

    def get_open_transactions(self):
        return deepcopy(self.__open_transactions)

    def load_data(self):
        try:
            with open(f'blockchain_{self.dev_port}.json', mode='r') as f:
                blockchain = json.load(f)
                # converting each block from dict to Block
                # print(blockchain)
                # print(type(blockchain[0]) is OrderedDict)
                blockchain = Json_translator.undict_blockchain(blockchain)
                self.__chain = blockchain
                # print(blockchain)

            with open(f'open_transactions_{self.dev_port}.json', mode='r') as f:
                # can use parameter object_pairs_hook = OrderedDict to load as OrderedDict # Instead stor them as dict for flexible memory usage and use sortkeys = True in json.dumps at both save_data() and valid_proof()
                open_transactions = json.load(f)
                # print(open_transactions)
                open_transactions = Json_translator.undict_open_transactions(
                    open_transactions)
                self.__open_transactions = open_transactions
            with open(f'peer_nodes_{self.dev_port}.json', mode='r') as f:
                peer_nodes =  json.load(f)
                self.__peer_nodes = set(peer_nodes)
        except (IOError, json.JSONDecodeError):
            print('FROM LOAD_DATA EXCEPT BLOCK : Nothing to load. Hence, the blockchain has been initiated with just the genesis block.')

    def save_data(self):
        try:
            with open(f'blockchain_{self.dev_port}.json', mode='w') as f:
                jsonable_blockchain = Json_translator.dict_blockchain(
                    self.__chain)
                json.dump(jsonable_blockchain, f, indent=4, sort_keys=True)
            with open(f'open_transactions_{self.dev_port}.json', mode='w') as f:
                jsonable_open_transactions = Json_translator.dict_open_transactions(
                    self.__open_transactions)
                json.dump(jsonable_open_transactions,
                          f, indent=4, sort_keys=True)
            with open(f'peer_nodes_{self.dev_port}.json', mode='w') as f:
                json.dump(list(self.__peer_nodes), f, indent=4)
        except (IOError):
            print("Saving blockchain and open transactions to the disk failed!")

    def get_prev_block(self, my_list):
        if len(my_list) == 0:
            return None
        return my_list[-1]

    def add_new_tx(self, recipient, sender, signature, tx_amt=1.0):
        # transaction = {
        #     'sender': sender,
        #     'recipient': recipient,
        #     'tx_amt': tx_amt
        # } order within a dictionary matters while calculating a hash but dictionaries are inherently unordered whereby we need OrderedDicts from collections
        if self.hosting_node_id is None:
            print("You don't have a wallet. Please create a wallet!")
            return None
        transaction = Transaction(
            sender=sender, recipient=recipient, signature=signature, tx_amt=tx_amt)
        if not Wallet.verify_signature(transaction=transaction):
            return None
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return transaction
        return None

    def hash_block(self, block):
        if (type(block) is not Block):
            return None  # if type of block parsed is not dict, this return statement tells the caller that the block is not hashable
        else:
            # return '-'.join([str(block[key]) for key in block])
            jsonable_block = deepcopy(block.deep_dict())
            return hlib.sha256(json.dumps(jsonable_block, sort_keys=True).encode()).hexdigest()
        # for key in prev_block:
        #     prev_hash = prev_hash + str(prev_block[key]) -------The same functionality as the for loop has been achieved through list comprehension above

    def proof_of_work(self):
        last_block = deepcopy(self.__chain[-1])
        last_hash = self.hash_block(last_block)
        nonce = 0

        while not Verification.valid_proof(self.__open_transactions, last_hash, nonce):

            # print('generating pow')
            nonce += 1
        return nonce

    def get_balance(self):
        if self.hosting_node_id == None:
            return None
        participant = self.hosting_node_id
        tx_sent = [[transaction.tx_amt for transaction in block.transactions if transaction.sender ==
                    participant] for block in self.__chain if len(block.transactions) > 0]
        open_tx_sent = [
            tx.tx_amt for tx in self.__open_transactions if tx.sender == participant]
        # adding sll the tx_amounts of the sender in open transactions in one list element as they all would go to the same new block if successful
        tx_sent.append(open_tx_sent)
        # using reduce function for sent balance and for loop to do the same in received balance to show both the alternatives
        # sum of empty list automatically returns 0, the ternary expression is added merely to show that inline if else statements could be added anywhere in python code.
        amt_sent = reduce(lambda tx_sum, tx_amt: tx_sum +
                          (sum(tx_amt) if len(tx_amt) > 0 else 0), tx_sent, 0)

        tx_received = [[transaction.tx_amt for transaction in block.transactions if transaction.recipient ==
                        participant] for block in self.__chain if len(block.transactions) > 0]
        amt_received = 0
        for set_of_tx_amts_within_a_block in tx_received:
            amt_received += sum(set_of_tx_amts_within_a_block)
        return amt_received-amt_sent

    def check_open_transactions(self):
        corrupt_transactions = []
        for index, tx in enumerate(self.__open_transactions):
            if not Wallet.verify_signature(tx):
                manipulated = self.__open_transactions.pop(index)
                corrupt_transactions.append(tx.__dict__)
                self.save_data()
                return corrupt_transactions


    def mine_block(self):
        if self.hosting_node_id is None:
            print("You don't have a wallet. Please create a wallet!")
            return None

        prev_block = deepcopy(self.__chain[-1])
        prev_hash = self.hash_block(prev_block)
        proof = self.proof_of_work()  # proof_of_work should be calculated before appending the reward transaction because reward should only realize if the node is successful in calculating a valid proof
        if not prev_hash:
            pass
        else:
            # reward_transaction = {
            #     'sender' : 'MINING',
            #     'recipient' : owner,
            #     'tx_amt' : MINING_REWARD
            # }
            reward_transaction = Transaction(
                sender='MINING', recipient=self.hosting_node_id, signature='', tx_amt=MINING_REWARD)  # we don't sign reward transaction as we have different means of verifying manipulation of reward amount as reward transaction won't be entered into open_transactions and can't be manipulated over there before it's mined unlike other transactions.
            # We make a local copy of it so that the global open_transactions stays intact if for any reason mining the block wasunsuccesful while working on node-network
            # for index, tx in enumerate(self.__open_transactions):
            #     if not Wallet.verify_signature(tx):
            #         manipulated = self.__open_transactions.pop(index)
            #         print(
            #             f"Couldn't mine a block as the following transaction has been manipulated:\n{json.dumps(tx.__dict__, indent=4)}\nThe above transaction has been removed from the open transactions!")
            #         self.save_data()
            #         return None
            open_transactions_copy = deepcopy(self.__open_transactions)
            open_transactions_copy.append(reward_transaction)
            block = Block(prev_hash=prev_hash, index=len(self.__chain),
                          transactions=open_transactions_copy, proof=proof)
            # block = {
            #     'prev_hash': prev_hash,
            #     'index': len(blockchain),
            #     'transactions': open_transactions_copy,
            #     'proof' : proof
            # }

            self.__chain.append(block)
            self.__open_transactions.clear()
            self.save_data()
            return block

    def add_peer_node(self, node):
        self.__peer_nodes.add(node)
        self.save_data()
    
    def remove_peer_node(self, node):
        #discard removes the element in set if exists and does nothing otherwise.
        self.__peer_nodes.discard(node)
        self.save_data()
    
    def get_peer_nodes(self):
        return deepcopy(list(self.__peer_nodes))

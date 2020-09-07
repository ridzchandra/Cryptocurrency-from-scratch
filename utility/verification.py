from copy import deepcopy
from .json_translator import Json_translator
import json
import hashlib as hlib
from wallet import Wallet

class Verification:
    @staticmethod
    def verify_transaction(transaction, get_balance):
        sender_balance = get_balance()
        return sender_balance >= transaction.tx_amt
    @staticmethod
    def valid_proof(transactions_to_be_mined, last_hash, nonce):
        jsonable_transactions_to_be_mined = deepcopy(
            Json_translator.dict_open_transactions(transactions_to_be_mined))
        string = (json.dumps(jsonable_transactions_to_be_mined,
                             sort_keys=True) + json.dumps(last_hash) + json.dumps(nonce))
        # print(string)
        guess = string.encode()
        guessed_hash = hlib.sha256(guess).hexdigest()
        # print(f"guessed hash: {guessed_hash}")
        return guessed_hash[:2] == "00"

    @classmethod
    def verify_chain(cls, hash_block, blockchain):
        # is_valid = True # have commented "is_valid" throughout the function to demonstrate that for-else can give the same result as using a flag to find something in a loop

        for block_index, block in enumerate(blockchain):
            if block_index == 0:
                continue
            else:
                prev_block = blockchain[block_index-1]
                # print(block_index)
                # print(block['prev_hash'])
                # print(hash_block(prev_block))
                # print(type(blockchain[block_index]), type(blockchain[block_index+1]))
                # print(f"{block.prev_hash} and {hash_block(prev_block)}")
                # if (type(block) is not Block) or
                if (block.prev_hash != hash_block(prev_block)):
                    # is_valid = False
                    break
                # print('verifying chain')
                if not cls.valid_proof(block.transactions[:-1], block.prev_hash, block.proof):
                    # print("Proof of work is invalid")
                    break
        else:
            return True  # The else block runs only after normal exiting of for loop and not after breaking the for loop

        return False
        # return is_valid
    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        return all([Wallet.verify_signature(tx) for tx in open_transactions])

import json
from uuid import uuid4
from blockchain.blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet

class Node:
    def __init__(self):
        # self.wallet_id = str(uuid4())
        self.wallet = Wallet() 
        self.wallet_id = None     
        self.blockchain = None
        
    def get_transaction_value(self):
        recipient = input("Please enter the name of the recipient: ")
        tx_amt = float(input("Please enter the transaction amount: "))
        return recipient, tx_amt

    def listen_for_input(self):
        while True:
            print("1: Print out the blocks of the chain")
            print("2: Add a new transaction")
            print("3: Mine a block")
            # print("4: Show the participants")
            print("4: Verify all the open transactions")
            print("5: Create a new wallet")
            print("6: Save the current wallet")
            print("7: Load the existing wallet")
            # print("h: Manipulate a block in the blockchain")
            print("q: Quit")
            if self.wallet_id is None:
                print("You don't have a wallet. Please create a wallet!")
            else:
                print(f"Node:{self.wallet_id} 's balance : {self.blockchain.get_balance():.2f}")
                
            user_choice = (
                input("Please enter your choice (just the option):"))

            if user_choice == '1':
                try:
                    if len(self.blockchain.get_chain()) == 0:
                        print("The blockchain is empty. No blocks added yet.\n\n\n\n\n")
                    else:
                        for block in self.blockchain.get_chain():
                            print(json.dumps(block.deep_dict(), indent=4))
                except AttributeError:
                    print("You don't have a wallet. Please create a wallet!")
                    continue
            elif user_choice == '2':
                try:
                    tx_data = self.get_transaction_value()
                    recipient, tx_amt = tx_data
                    signature = self.wallet.sign_transaction(sender = self.wallet.public_key, recipient = recipient, tx_amt = tx_amt)
                    if self.blockchain.add_new_tx(recipient=recipient, sender=self.wallet_id, signature=signature, tx_amt=tx_amt):
                        print('Transaction added to open transactions!')
                    else:
                        print("Transaction couldn't be added due to insufficient balance!!")
                except (AttributeError,TypeError):
                    print("You don't have a wallet. Please create a wallet!")
                    continue
            elif user_choice == '3':
                try:
                    if not Verification.verify_chain(hash_block=self.blockchain.hash_block, blockchain=self.blockchain.get_chain()):
                        print("Alert!!! Block-chain data compromised!!")
                        break
                    else:
                        if self.blockchain.mine_block():
                            print("A new block has been mined successfully!")

                            # elif user_choice == '4':
                            #     print(participants)
                except AttributeError:
                    print("You don't have a wallet. Please create a wallet!")
                    continue
            elif user_choice == '4':
                try:
                    if Verification.verify_transactions(open_transactions=self.blockchain.get_open_transactions(), get_balance=self.blockchain.get_balance):
                        print("All open transactions are valid!")
                    else:
                        print("There are invalid open transactions!")
                except AttributeError:
                    print("You don't have a wallet. Please create a wallet!")
                    continue
            # elif user_choice == 'h':
            #     if len(blockchain) == 0:
            #         print("The blockchain is empty. Nothing to manipulate yet.\n\n\n\n\n")
            #     else:
            #         blockchain[0] = {
            #             'prev_hash': '',
            #             'index': 0,
            #             'transactions': [
            #                 {
            #                     'sender': 'Chris',
            #                     'recipient': 'Max',
            #                     'tx_amt': 10
            #                 }
            #             ]
            #         }
            #         print("Manipulation Successful!")

            elif user_choice == '5':
                self.wallet.create_keys()
                self.wallet_id = self.wallet.public_key # it doesn't copy the reference to self.wallet.public_key. It just copies the value into it.
                self.blockchain = Blockchain(hosting_node_id= self.wallet_id)
                # print(self.wallet_id)

            elif user_choice == '6':
                self.wallet.save_keys()

            elif user_choice == '7':
                self.wallet.load_keys()
                self.wallet_id = self.wallet.public_key
                self.blockchain = Blockchain(hosting_node_id= self.wallet_id)

            elif user_choice == 'q':
                break

            else:
                print("Invalid input! Please enter a valid input.")
            
            try:
                if not Verification.verify_chain(hash_block=self.blockchain.hash_block, blockchain=self.blockchain.get_chain()):
                    print("Alert!!! Block-chain data compromised!!")
                    break
            except AttributeError:
                    print("You don't have a wallet. Please create a wallet!")
                    continue

            # print(f"{owner}'s balance : {get_balance(owner):.2f}")


if __name__ == '__main__': # __name__ is set to '__main__' only if we are executing it. Otherwise, it's set to the name of the module ('__node__') if it imported.
    node = Node()
    node.listen_for_input()

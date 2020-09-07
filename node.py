from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from blockchain.blockchain import Blockchain
from utility.verification import Verification
from copy import deepcopy
from utility.json_translator import Json_translator

from wallet import Wallet


# Flask object is an application i.e the server that listens to and responds with HTTP requests
# creating a server or an app
chandra_app = Flask(__name__)


# CORS object opens up our app's api's to external clients i.e our api's are not constrained to the HTML pages rendered by our application/server.
CORS(chandra_app)

def check_for_wallet():
    if blockchain.hosting_node_id is not None:
        return True
    return False



@chandra_app.route("/", methods=["GET"])
def get_ui():
    return send_from_directory("ui", "node.html")


@chandra_app.route("/balance", methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if balance is not None:
        response = {
            "Wallet_ID" : blockchain.hosting_node_id,
            "funds": blockchain.get_balance(),
            "message" : "Fetched balance successfully!"
        }
        return jsonify(response), 200
    else:
        response = {
            "message" : "Wallet keys have neither been created nor been loaded!"
        }
        return jsonify(response), 500

@chandra_app.route("/wallet", methods=["POST"])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(hosting_node_id=wallet.public_key, dev_port= dev_port)
        response = {
            "message": "New keys have been created and saved successfully!",
            "Public Key": wallet.public_key,
            "Private Key": wallet.private_key,
            "funds" : blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Saving Keys Failed!"
        }
        return jsonify(response), 500


@chandra_app.route("/wallet", methods=["GET"])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(hosting_node_id=wallet.public_key, dev_port=dev_port)
        response = {
            "message": "Yor keys have been loaded successfully!",
            "Public Key": wallet.public_key,
            "Private Key": wallet.private_key,
            "funds" : blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            "message": "Saving Keys Failed!"
        }
        return jsonify(response), 500
        



@chandra_app.route("/transaction", methods=["POST"])
def add_transaction():
    try:
        #request is an object imported from flask package which takes in json data passed in along with a POST request
        #request.get_json() only takes in JSON data and returns a python dict
        values = request.get_json()
        if not values:
            response = {
                "message" : "No valid data found!"
            }
            return jsonify(response), 400
        required_fields = ["recipient", "tx_amt"]
        if all(field in values for field in required_fields):
            recipient = values["recipient"]
            tx_amt = values["tx_amt"]

            if (type(recipient) is not str) and (type(tx_amt) is not float):
                response = {
                    "message" : "No valid data found!"
                }
                return jsonify(response), 400
            
            signature = wallet.sign_transaction(sender = wallet.public_key, recipient = recipient, tx_amt = tx_amt)
            transaction = blockchain.add_new_tx(recipient=recipient, sender=wallet.public_key, signature=signature, tx_amt=tx_amt)
            if transaction:
                response = {
                    "message" : "Successfully added transaction!",
                    "transaction" : transaction.__dict__,
                    "funds" : blockchain.get_balance()
                }
                return jsonify(response), 201
            else:
                response = {
                    "message" : "Unable to add the transaction due to insufficient balance!"
                }
                return jsonify(response), 400
        else:
             response = {
                 "message" :  "Not all of the required fields have been filled!"
             }    
             return jsonify(response), 400
    
    except (AttributeError, TypeError):
        response = {
            "message" :  "Wallet keys have neither been created nor been loaded!"
        }
        return jsonify(response), 400 
            



@chandra_app.route("/mine", methods=["POST"])
def mine():
    try:
        if not Verification.verify_chain(hash_block=blockchain.hash_block, blockchain=blockchain.get_chain()):
            response = {
                "message": "Alert!!! Block-chain data compromised!!"
            }
            return jsonify(response), 500

        # Verifying signatures to check if any tx in open_txs have been corrupted
        corrupt_transactions = blockchain.check_open_transactions()      
        
        if corrupt_transactions:
            response = {
                "message": "Couldn't mine a block as the following transactions have been manipulated, which are now removed from the open_transactions",
                "corrupt_open_transactions": corrupt_transactions
            }
            return jsonify(response), 500

        else:
            mined_block = deepcopy(blockchain.mine_block())
            print(mined_block)

            if mined_block:
                response = {
                    "message": "A new block has been mined successfully!",
                    "mined_block": mined_block.deep_dict(),
                    "funds" : blockchain.get_balance()
                }
                return jsonify(response), 201
        raise TypeError
                
    except (AttributeError, TypeError):
        response = {
            "message": "You don't have a wallet. Please create a wallet!",
            "wallet_setup_status": wallet.public_key != None
        }
        return jsonify(response), 400

@chandra_app.route("/transactions", methods=["GET"])
def get_open_transactions():
    open_transactions = blockchain.get_open_transactions()
    jsonable_open_transactions = Json_translator.dict_open_transactions(open_transactions = open_transactions)
    return jsonify(jsonable_open_transactions), 200 


@chandra_app.route("/chain", methods=["GET"])
def get_blockchain():
    try:
        # blockchain.get_chain() only returns a deepcopy of the chain but not the actual chain
        chain_snapshot = blockchain.get_chain()
        if len(chain_snapshot) == 0:
            response = {
                "message": "The blockchain is empty. No blocks added yet."
            }
            return jsonify(response), 500

        else:
            jsonable_blockchain = Json_translator.dict_blockchain(
                chain_snapshot)
            return jsonify(jsonable_blockchain), 200
    except AttributeError:
        response = {
            "message": "You don't have a wallet. Please create a wallet!"
        }
        return jsonify(response), 400
    
@chandra_app.route("/node", methods=["POST"])
def add_peer_node():
    if check_for_wallet():
        values = request.get_json()
        if not values:
            response = {
                "message" : "No valid data found!"
            }
            return jsonify(response), 400
        required_fields = ["node"]
        if all(field in values for field in required_fields):
            blockchain.add_peer_node(values["node"])
            response = {
                "message" : "Node added successfully!",
                "node added" : values["node"]
            }
            return jsonify(response), 200
        else:
            response = {
                "message" : "Not all required fields have been enterd!"
            }
            return jsonify(response), 400
    else:
        response = {
            "message" :  "Wallet keys have neither been created nor been loaded!"
        }
        return jsonify(response), 400 

@chandra_app.route("/node/<node_url>", methods=["DELETE"])
def remove_peer_node(node_url):
    if check_for_wallet():
        if node_url == "" or node_url is None:
            response = {
                "message" : "No node found to be removed from the network!"
            }
            return jsonify(response), 400
        else:
            blockchain.remove_peer_node(node_url)
            response = {
                "message" : "Node removed succesfully!",
                "node removed" : node_url
            }
            return jsonify(response), 200
    else:
        response = {
            "message" :  "Wallet keys have neither been created nor been loaded!"
        }
        return jsonify(response), 400 

@chandra_app.route("/nodes", methods=["GET"])
def get_peer_nodes():
    if check_for_wallet():
        all_nodes =  blockchain.get_peer_nodes()
        response = {
            "all_nodes" : all_nodes
        }
        return jsonify(response), 200
    else:
        response = {
            "message" :  "Wallet keys have neither been created nor been loaded!"
        }
        return jsonify(response), 400 



if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type= int, default=5000)
    args = parser.parse_args()
    dev_port = args.port
    wallet = Wallet(dev_port=dev_port)
    blockchain = Blockchain(hosting_node_id=wallet.public_key, dev_port=dev_port) 
    # spins up the server
    chandra_app.run(host='0.0.0.0', port=dev_port)

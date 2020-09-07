from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
import Crypto.Random
import binascii
import json


class Wallet:
    def __init__(self, dev_port):
        self.private_key = None
        self.public_key = None
        self.dev_port = dev_port

    def create_keys(self):
        # print("Executing create keys")
        str_private_key, str_public_key = self.generate_keys()
        self.private_key = str_private_key
        self.public_key = str_public_key
        # print(self.public_key)

    def save_keys(self):
        try:
            with open(f"keys_{self.dev_port}.txt", mode='w') as f:
                f.write(self.private_key)
                f.write('\n')
                f.write(self.public_key)
                return True
        except (IOError, IndexError):
            print("Saving keys failed!")
            return False

    def load_keys(self):
        try:
            with open(f"keys_{self.dev_port}.txt", mode='r') as f:
               keys = f.readlines()
               self.private_key = keys[0][:-1]
               self.public_key = keys[1]
               return True
        except (IOError, IndexError):
            print("Loading keys failed!")
            return False

        



    def generate_keys(self):
        # print("Executing generate keys")
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        str_private_key = binascii.hexlify(
            private_key.exportKey(format='DER')).decode('ascii')
        str_public_key = binascii.hexlify(
            public_key.exportKey(format='DER')).decode('ascii')
        return (str_private_key, str_public_key)

    def sign_transaction(self, sender, recipient, tx_amt):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        hashed_payload = SHA256.new((str(sender) + str(recipient) + str(tx_amt)).encode('utf8'))
        signature = signer.sign(hashed_payload)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_signature(transaction):
        if transaction.sender == "MINING":
            return True
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        hashed_payload = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.tx_amt)).encode('utf8'))
        return verifier.verify(hashed_payload,binascii.unhexlify(transaction.signature))
import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, transactions, nonce=0, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions  
        self.nonce = nonce
        self.timestamp = timestamp if timestamp is not None else time.time()
        
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "nonce": self.nonce,
            "timestamp": self.timestamp
        }
        
        # IMPORTANTE: Usar sort_keys=True no JSON! [cite: 157]
        encoded_data = json.dumps(block_data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(encoded_data).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(data):
        b = Block(
            data['index'], data['previous_hash'], data['transactions'],
            data['nonce'], data['timestamp']
        )
        b.hash = data['hash']
        return b
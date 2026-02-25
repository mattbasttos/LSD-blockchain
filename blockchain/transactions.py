import time
import uuid

class Transaction:
    def __init__(self, origem, destino, valor, timestamp=None, tx_id=None):
        self.id = tx_id if tx_id else str(uuid.uuid4()) # "string-uuid" 
        self.origem = origem                            # "string" 
        self.destino = destino                          # "string" 
        self.valor = float(valor)                       # float 
        self.timestamp = timestamp if timestamp is not None else time.time() # float 

    def is_valid_format(self):
        if self.valor <= 0:
            return False
        if not self.origem or not self.destino:
            return False
        return True

    def to_dict(self):
        return {
            "id": self.id,
            "origem": self.origem,
            "destino": self.destino,
            "valor": self.valor,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_dict(data):
        return Transaction(
            origem=data['origem'], 
            destino=data['destino'], 
            valor=data['valor'], 
            timestamp=data.get('timestamp'),
            tx_id=data.get('id')
        )
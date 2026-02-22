import time
import uuid

class Transaction:
    def __init__(self, origem, destino, valor, timestamp=None, tx_id=None):
        """
        Estrutura de dados exata conforme o PDF [cite: 121-127].
        """
        self.id = tx_id if tx_id else str(uuid.uuid4()) # "string-uuid" [cite: 123]
        self.origem = origem                            # "string" [cite: 124]
        self.destino = destino                          # "string" [cite: 125]
        self.valor = float(valor)                       # float [cite: 126]
        self.timestamp = timestamp if timestamp is not None else time.time() # float [cite: 127]

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
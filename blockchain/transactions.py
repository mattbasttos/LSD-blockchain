import time
import hashlib
import json

class Transaction:
    def __init__(self, sender, recipient, amount, timestamp=None):
        """
        Cria uma nova transação.
        Campos obrigatórios conforme especificação:
        - origem (sender) 
        - destino (recipient) 
        - valor (amount) 
        - timestamp 
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or time.time()
        
        # Gera o identificador único automaticamente no momento da criação
        self.id = self.calculate_hash() 

    def calculate_hash(self):
        """Gera um hash SHA-256 único baseado nos dados da transação."""
        # A string deve ser determinística para garantir que o ID seja sempre o mesmo para os mesmos dados
        payload = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def is_valid_format(self):
        """
        Valida regras internas da transação.
        Regra: Ter somente valores positivos.
        """
        if self.amount <= 0:
            return False
        if not self.sender or not self.recipient:
            return False
        return True

    def to_dict(self):
        """Serializa para envio via JSON/Socket."""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_dict(data):
        """Reconstrói o objeto a partir de um dicionário."""
        tx = Transaction(
            data['sender'], 
            data['recipient'], 
            data['amount'], 
            data['timestamp']
        )
        tx.id = data['id'] # Mantém o ID original
        return tx
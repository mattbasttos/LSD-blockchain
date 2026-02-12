import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, transactions, nonce=0, timestamp=None):
        """
        Inicializa um bloco da blockchain.
        Campos obrigatórios:
        - índice do bloco (index)
        - hash do bloco anterior (previous_hash)
        - lista de transações (transactions)
        - nonce
        - timestamp
        """
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions  # Lista de dicionários (dados das transações)
        self.nonce = nonce
        self.timestamp = timestamp or time.time()
        
        # Campo obrigatório: hash do bloco atual 
        # É calculado automaticamente na criação para garantir integridade inicial
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Gera o hash SHA-256 do bloco.
        Requisito: O hash deve ser gerado utilizando SHA-256.
        """
        # Serializa a lista de transações para uma string JSON.
        # sort_keys=True é CRUCIAL para garantir que a ordem dos campos não altere o hash.
        transactions_str = json.dumps(self.transactions, sort_keys=True)
        
        # Concatena todos os campos do bloco em uma única string
        block_string = f"{self.index}{self.previous_hash}{transactions_str}{self.nonce}{self.timestamp}"
        
        # Retorna o hash hexadecimal SHA-256
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        """Converte o objeto Bloco para um dicionário (para envio via rede/JSON)."""
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
        """
        Reconstrói um objeto Bloco a partir de um dicionário recebido da rede.
        Útil ao receber blocos via socket e convertê-los de volta para objetos.
        """
        block = Block(
            index=data['index'],
            previous_hash=data['previous_hash'],
            transactions=data['transactions'],
            nonce=data['nonce'],
            timestamp=data['timestamp']
        )
        # O hash original recebido deve ser mantido para validação posterior
        block.hash = data['hash']
        return block
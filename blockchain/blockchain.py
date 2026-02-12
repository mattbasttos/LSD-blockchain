# blockchain.py
from block import Block
from consensus import Consensus
from transactions import Transaction  
from protocol import DIFFICULTY, MINING_REWARD 
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0, 
            previous_hash="0", 
            transactions=[],
            nonce=0, 
            timestamp=1672531200.0
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def get_balance(self, address):
        balance = 0
        # Percorre toda a blockchain para somar entradas e saídas
        for block in self.chain:
            for tx in block.transactions:
                if tx['recipient'] == address:
                    balance += tx['amount']
                if tx['sender'] == address:
                    balance -= tx['amount']
        
        # Opcional: subtrair o que está pendente para não gastar duas vezes
        for tx in self.pending_transactions:
            if tx['sender'] == address:
                balance -= tx['amount']
                
        return balance

    def add_transaction(self, transaction):
        if not transaction.is_valid_format():
            return False

        # Verifica saldo (exceto se for transação de recompensa do sistema)
        if transaction.sender != "System" and transaction.sender != "0":
            if self.get_balance(transaction.sender) < transaction.amount:
                print(f"[Erro] Saldo insuficiente.")
                return False

        self.pending_transactions.append(transaction.to_dict())
        return True

    def mine_pending_transactions(self, miner_address):
        """
        Minera o bloco e inclui a Recompensa (Coinbase) para o minerador.
        """
        # --- CORREÇÃO AQUI: CRIAR A RECOMPENSA ---
        # Cria uma transação do sistema para o minerador
        reward_tx = Transaction("System", miner_address, MINING_REWARD)
        
        # Adiciona a recompensa na lista de transações DESTE bloco
        # Nota: Não usamos add_transaction para evitar checagem de saldo do "System"
        self.pending_transactions.append(reward_tx.to_dict())
        
        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.hash,
            transactions=self.pending_transactions
        )

        # Minera (Proof of Work)
        mined_block = Consensus.mine(new_block)
        
        self.chain.append(mined_block)
        self.pending_transactions = [] # Limpa a lista
        
        return mined_block

    def is_chain_valid(self, chain_to_validate):
        for i in range(1, len(chain_to_validate)):
            current = Block.from_dict(chain_to_validate[i])
            previous = Block.from_dict(chain_to_validate[i-1])

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
            if not current.hash.startswith(DIFFICULTY):
                return False
        return True

    def replace_chain(self, new_chain_data):
        if len(new_chain_data) > len(self.chain) and self.is_chain_valid(new_chain_data):
            self.chain = [Block.from_dict(b) for b in new_chain_data]
            return True
        return False
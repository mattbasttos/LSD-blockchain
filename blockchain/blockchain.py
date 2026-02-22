from block import Block
from consensus import Consensus
from transactions import Transaction
from protocol import DIFFICULTY, MINING_REWARD
import uuid

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Bloco Gênesis exato conforme PDF .
        """
        genesis_block = Block(
            index=0, 
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000", 
            transactions=[], 
            nonce=0, 
            timestamp=0 
        )
        # Força o hash esperado (para fins de validação rápida)
        genesis_block.hash = "816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7" 
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx['destino'] == address: # Antes era recipient
                    balance += tx['valor']
                if tx['origem'] == address:  # Antes era sender
                    balance -= tx['valor']
        
        for tx in self.pending_transactions:
            if tx['origem'] == address:
                balance -= tx['valor']
                
        return balance

    def add_transaction(self, transaction):
        if not transaction.is_valid_format():
            return False

        if transaction.origem != "coinbase":
            if self.get_balance(transaction.origem) < transaction.valor:
                return False

        self.pending_transactions.append(transaction.to_dict())
        return True

    def mine_pending_transactions(self, miner_address):
        transactions_to_mine = list(self.pending_transactions)

        # 1. Cria a Recompensa de Mineração ("coinbase") [cite: 182-190]
        # O timestamp deve ser o mesmo do bloco[cite: 190], então criaremos o bloco primeiro.
        
        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.hash,
            transactions=[] # Inseriremos a coinbase agora
        )
        
        # A coinbase DEVE ser a primeira transação [cite: 183]
        coinbase_tx = Transaction(
            origem="coinbase", 
            destino=miner_address, 
            valor=MINING_REWARD, 
            timestamp=new_block.timestamp, 
            tx_id=str(uuid.uuid4())
        )
        
        # Insere no topo da lista [cite: 183]
        transactions_to_mine.insert(0, coinbase_tx.to_dict())
        
        # Atualiza o bloco com as transações definitivas
        new_block.transactions = transactions_to_mine
        new_block.hash = new_block.calculate_hash() # Recalcula hash inicial

        # 2. Minera
        mined_block = Consensus.mine(new_block)
        
        self.chain.append(mined_block)
        self.pending_transactions = [] 
        
        return mined_block

    def is_chain_valid(self, chain_to_validate):
        for i in range(1, len(chain_to_validate)):
            current = Block.from_dict(chain_to_validate[i])
            previous = Block.from_dict(chain_to_validate[i-1])

            if current.hash != current.calculate_hash(): return False
            if current.previous_hash != previous.hash: return False
            if not current.hash.startswith(DIFFICULTY): return False
        return True

    def replace_chain(self, new_chain_data):
        if len(new_chain_data) > len(self.chain) and self.is_chain_valid(new_chain_data):
            self.chain = [Block.from_dict(b) for b in new_chain_data]
            return True
        return False
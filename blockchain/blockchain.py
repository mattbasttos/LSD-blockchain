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
        Bloco Gênesis exato. 
        O calculate_hash() natural usando as regras (sort_keys=True) 
        irá gerar exatamente o hash 0567c32b97c...
        """
        genesis_block = Block(
            index=0, 
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            transactions=[],
            nonce=0,
            timestamp=0
        )
        
        # Deixamos o Python calcular o hash autêntico com as regras estabelecidas
        genesis_block.hash = genesis_block.calculate_hash()
        
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
        # 1. Verifica se o bloco Gênesis do colega é igual ao nosso
        genesis_recebido = Block.from_dict(chain_to_validate[0])
        if genesis_recebido.hash != self.chain[0].hash:
            print(f"[Erro Consenso] Bloco Gênesis incompatível! \n  Nosso: {self.chain[0].hash[:15]}... \n  Deles: {genesis_recebido.hash[:15]}...")
            return False

        # 2. Verifica o resto da cadeia
        for i in range(1, len(chain_to_validate)):
            current = Block.from_dict(chain_to_validate[i])
            previous = Block.from_dict(chain_to_validate[i-1])

            recalculated = current.calculate_hash()
            
            # Valida Integridade
            if current.hash != recalculated:
                print(f"[Erro Consenso] Bloco {current.index} corrompido! Esperado: {recalculated[:15]}..., Recebido: {current.hash[:15]}...")
                return False
            
            # Valida Encadeamento
            if current.previous_hash != previous.hash:
                print(f"[Erro Consenso] Bloco {current.index} quebrou a corrente (previous_hash inválido).")
                return False
            
            # Valida Proof of Work
            if not current.hash.startswith(DIFFICULTY):
                print(f"[Erro Consenso] Bloco {current.index} não atingiu a dificuldade PoW.")
                return False
                
        return True

    def replace_chain(self, new_chain_data):
        # Se a cadeia que chegou não for maior que a nossa, descartamos
        if len(new_chain_data) <= len(self.chain):
            print(f"[Consenso] Cadeia ignorada. A recebida (Tamanho {len(new_chain_data)}) não é maior que a local (Tamanho {len(self.chain)}).")
            return False
            
        # Se for maior, passamos pelo pente fino da validação
        if not self.is_chain_valid(new_chain_data):
            print("[Consenso] Cadeia rejeitada: Falha nas regras de integridade.")
            return False
            
        # Tudo certo! Adotamos a nova cadeia
        self.chain = [Block.from_dict(b) for b in new_chain_data]
        return True
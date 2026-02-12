from block import Block
from consensus import Consensus
from protocol import DIFFICULTY
import json

class Blockchain:
    def __init__(self):
        """
        Inicializa a Blockchain.
        Mantém a cadeia de blocos e a lista de transações pendentes.
        """
        self.chain = []
        self.pending_transactions = []
        
        # Cria o bloco gênesis fixo na inicialização 
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Gera o bloco gênesis.
        Requisito: Existir um bloco gênesis fixo.
        Nota: Usamos timestamp e nonce fixos para garantir que todos os nós
        tenham EXATAMENTE o mesmo hash inicial.
        """
        genesis_transactions = [] # Lista vazia ou transação simbólica
        genesis_block = Block(
            index=0, 
            previous_hash="0", 
            transactions=genesis_transactions,
            nonce=0, 
            timestamp=1672531200.0 #  Para consistência global deve ser o mesmo para todos os peers
        )
        
        # Calcula o hash inicial (deve ser idêntico em todos os nós)
        genesis_block.hash = genesis_block.calculate_hash()
        
        self.chain.append(genesis_block)

    def get_last_block(self):
        """Retorna o último bloco da cadeia."""
        return self.chain[-1]

    def get_balance(self, address):
        """
        Calcula o saldo de um endereço percorrendo a cadeia.
        Essencial para validar transações e impedir saldo negativo.
        """
        balance = 0
        
        # 1. Percorre blocos confirmados
        for block in self.chain:
            for tx in block.transactions:
                # tx é um dicionário aqui
                if tx['recipient'] == address:
                    balance += tx['amount']
                if tx['sender'] == address:
                    balance -= tx['amount']
        
        # 2. Percorre mempool (pendentes) para evitar gasto duplo imediato
        for tx in self.pending_transactions:
            if tx['sender'] == address:
                balance -= tx['amount']
                
        return balance

    def add_transaction(self, transaction):
        """
        Adiciona uma transação à lista de pendentes.
        """
        # Validação de formato (valores positivos)
        if not transaction.is_valid_format():
            return False

        # Validação de Saldo (Não permitir saldo negativo)
        # Exceção para o remetente "0" (Rewards do sistema)
        if transaction.sender != "0":
            if self.get_balance(transaction.sender) < transaction.amount:
                print(f"[Erro] Saldo insuficiente para {transaction.sender}")
                return False

        self.pending_transactions.append(transaction.to_dict())
        return True

    def mine_pending_transactions(self, miner_address):
        """
        Empacota transações e minera um novo bloco.
        """
        last_block = self.get_last_block()
        
        # Cria o novo bloco
        new_block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.hash, # Referencia hash do anterior 
            transactions=self.pending_transactions
        )

        # Executa o Consenso (Proof of Work)
        # O nó deve encontrar um nonce tal que o hash comece com "000" 
        mined_block = Consensus.mine(new_block)
        
        # Adiciona à cadeia e limpa a lista de pendentes
        self.chain.append(mined_block)
        self.pending_transactions = []
        
        return mined_block

    def is_chain_valid(self, chain_to_validate):
        """
        Valida a integridade da blockchain.
        Requisito: A cadeia válida é aquela que possui todos os blocos válidos.
        """
        # O índice 0 é o Gênesis, começamos a validar do 1 em diante
        for i in range(1, len(chain_to_validate)):
            current_block_data = chain_to_validate[i]
            previous_block_data = chain_to_validate[i-1]

            # Reconstrói o objeto Block para recalcular o hash real
            current_block = Block.from_dict(current_block_data)
            
            # 1. Valida Hash do Bloco Atual
            # Verifica se o hash armazenado bate com o cálculo dos dados (integridade)
            if current_block.calculate_hash() != current_block_data['hash']:
                print(f"[Erro] Hash inválido no bloco {current_block.index}")
                return False
            
            # 2. Valida Referência Anterior (Encadeamento)
            # Cada bloco deve referenciar corretamente o hash do bloco anterior 
            if current_block.previous_hash != previous_block_data['hash']:
                print(f"[Erro] Quebra de encadeamento no bloco {current_block.index}")
                return False

            # 3. Valida Proof of Work
            # O hash deve começar com "000" (DIFFICULTY)
            if not current_block.hash.startswith(DIFFICULTY):
                print(f"[Erro] Bloco {current_block.index} sem Proof of Work válido")
                return False

        return True

    def replace_chain(self, new_chain_data):
        """
        Algoritmo de Consenso da Rede (Longest Chain Rule).
        Substitui a cadeia local se a recebida for maior e válida.
        """
        if len(new_chain_data) > len(self.chain) and self.is_chain_valid(new_chain_data):
            print("[Consenso] Cadeia substituída por uma mais longa e válida.")
            # Converte lista de dicts para lista de objetos Block
            self.chain = [Block.from_dict(b) for b in new_chain_data]
            return True
        return False
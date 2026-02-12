import time

# A dificuldade é fixa conforme requisito 
DIFFICULTY = "000"

class Consensus:
    """
    Módulo responsável pelo algoritmo de Consenso (Proof of Work).
    """

    @staticmethod
    def mine(block):
        """
        Realiza a mineração do bloco (Proof of Work).
        O nó deve encontrar um valor de nonce tal que o hash do bloco comece com "000". 
        """
        print(f"[Miner] Iniciando mineração do Bloco {block.index}...")
        start_time = time.time()
        
        block.nonce = 0
        # Calcula o hash inicial
        block.hash = block.calculate_hash()

        # Loop de força bruta até encontrar o hash que satisfaz a dificuldade
        while not block.hash.startswith(DIFFICULTY):
            block.nonce += 1
            # Recalcula o hash com o novo nonce
            block.hash = block.calculate_hash()

        end_time = time.time()
        print(f"[Miner] Sucesso! Nonce: {block.nonce} | Hash: {block.hash}")
        print(f"[Miner] Tempo decorrido: {end_time - start_time:.4f} segundos")
        
        return block

    @staticmethod
    def is_valid_pow(block):
        """
        Valida se um bloco atende aos requisitos do Consenso.
        Blocos recebidos devem ser validados antes de serem aceitos. 
        """
        # 1. Verifica se o hash satisfaz a dificuldade ("000")
        if not block.hash.startswith(DIFFICULTY):
            print(f"[Consenso] Falha: Hash {block.hash} não começa com '{DIFFICULTY}'.")
            return False

        # 2. Verifica a integridade (se o hash corresponde ao conteúdo)
        # Isso impede que alguém altere transações e mantenha um hash válido antigo
        recalculated_hash = block.calculate_hash()
        if block.hash != recalculated_hash:
            print(f"[Consenso] Falha: Hash inválido. Esperado: {recalculated_hash}, Recebido: {block.hash}")
            return False

        return True
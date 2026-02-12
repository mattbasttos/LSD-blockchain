import sys
import time
from blockchain import Blockchain
from node import Node
from transactions import Transaction
from protocol import *

def print_header(node_address, balance, peers_count):
    """Exibe o cabeçalho do menu com informações de estado do nó."""
    print("\n" + "="*50)
    print(f"   BLOCKCHAIN NODE | Endereço: {node_address}")
    print(f"   Saldo: {balance:.2f} | Peers Conectados: {peers_count}")
    print("="*50)

def main():
    # 1. Configuração Inicial via Linha de Comando [cite: 23]
    if len(sys.argv) < 3:
        print("Uso: python main.py <IP_LOCAL> <PORTA_LOCAL> [BOOTSTRAP_IP:BOOTSTRAP_PORT]")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    my_address = f"{host}:{port}"
    
    # 2. Inicialização dos Módulos [cite: 25-27]
    # Cria a blockchain local (com bloco gênesis fixo)
    blockchain = Blockchain()
    
    # Inicia o servidor P2P em processo independente
    node = Node(host, port, blockchain)

    # 3. Conexão com Bootstrap (Entrada na Rede) [cite: 24]
    if len(sys.argv) > 3:
        try:
            bs_address = sys.argv[3]
            bs_host, bs_port = bs_address.split(":")
            print(f"[*] Conectando ao nó bootstrap {bs_address}...")
            # Usa o método específico que registra e pede a chain
            node.connect_to_bootstrap(bs_host, int(bs_port))
        except ValueError:
            print("[!] Erro: Formato do bootstrap deve ser IP:PORTA")

    # 4. Loop Principal (Interface do Usuário)
    while True:
        # Atualiza o saldo local para exibição (Regra: Saldo não negativo)
        current_balance = blockchain.get_balance(my_address)
        print_header(my_address, current_balance, len(node.peers))
        
        print("1. Criar Transação (Enviar Moedas)")
        print("2. Minerar Bloco (Proof of Work)")
        print("3. Visualizar Blockchain")
        print("4. Listar Peers Conectados")
        print("5. Forçar Sincronização (Request Chain)")
        print("0. Sair")
        print("-" * 50)
        
        opt = input("Escolha uma opção: ")
        
        if opt == '1':
            # --- CRIAR TRANSAÇÃO [cite: 61] ---
            recipient = input("Destinatário (IP:PORTA): ")
            try:
                amount = float(input("Valor a enviar: "))
                
                # Cria o objeto transação
                tx = Transaction(my_address, recipient, amount)
                
                # Tenta adicionar localmente (Valida saldo e valores positivos)
                if blockchain.add_transaction(tx):
                    # Se válido, propaga para a rede
                    msg = {
                        "type": NEW_TRANSACTION, 
                        "data": tx.to_dict(),
                        "sender_host": host,
                        "sender_port": port
                    }
                    node.broadcast(msg)
                    print(f"[Sucesso] Transação {tx.id[:8]}... enviada e propagada.")
                else:
                    print("[Falha] Transação rejeitada (Saldo insuficiente ou valor inválido).")
            
            except ValueError:
                print("[Erro] Valor inválido digitado.")

        elif opt == '2':
            # --- MINERAÇÃO (PoW) [cite: 53-58] ---
            if not blockchain.pending_transactions:
                print("[Aviso] Nenhuma transação pendente. Minerando bloco vazio (apenas recompensa/checkpoint)...")
            
            print("[Miner] Iniciando trabalho de Proof of Work...")
            # A função mine_pending_transactions já executa o algoritmo de consenso
            new_block = blockchain.mine_pending_transactions(my_address)
            
            print(f"[Sucesso] Bloco {new_block.index} minerado!")
            print(f"         Hash: {new_block.hash}")
            print(f"         Nonce: {new_block.nonce}")
            
            # Propaga o bloco minerado para validação dos outros nós
            msg = {
                "type": NEW_BLOCK, 
                "data": new_block.to_dict(),
                "sender_host": host,
                "sender_port": port
            }
            node.broadcast(msg)

        elif opt == '3':
            # --- VISUALIZAÇÃO [cite: 26] ---
            print("\n--- BLOCKCHAIN LOCAL ---")
            for block in blockchain.chain:
                print(f"[Bloco {block.index}]")
                print(f"   Hash Atual: {block.hash}")
                print(f"   Hash Ant. : {block.previous_hash}")
                print(f"   Transações: {len(block.transactions)}")
                for tx in block.transactions:
                    print(f"     -> {tx['sender']} envia {tx['amount']} para {tx['recipient']}")
                print("-" * 30)

        elif opt == '4':
            # --- PEERS ---
            print("\n--- NÓS CONECTADOS ---")
            if not node.peers:
                print("Nenhum peer conectado (Modo Standalone).")
            for p in node.peers:
                print(f" - {p[0]}:{p[1]}")

        elif opt == '5':
            # --- SINCRONIZAÇÃO [cite: 63] ---
            print("[Sync] Solicitando blockchain atualizada aos peers...")
            msg = {
                "type": REQUEST_CHAIN,
                "sender_host": host,
                "sender_port": port
            }
            node.broadcast(msg)

        elif opt == '0':
            print("Encerrando nó...")
            node.running = False
            # Pequeno delay para encerrar threads do node
            time.sleep(0.5) 
            sys.exit(0)

        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
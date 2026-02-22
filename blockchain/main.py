import sys
import time
from blockchain import Blockchain
from node import Node
from transactions import Transaction
from protocol import *

def print_header(node_address, balance, peers_count):
    print("\n" + "="*50)
    print(f"   BLOCKCHAIN NODE | Endereço: {node_address}")
    print(f"   Saldo: {balance:.2f} | Peers Conectados: {peers_count}")
    print("="*50)

def main():
    if len(sys.argv) < 3:
        print("Uso: python main.py <IP_LOCAL> <PORTA_LOCAL> [BOOTSTRAP_IP:BOOTSTRAP_PORT]")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    my_address = f"{host}:{port}"
    
    blockchain = Blockchain()
    node = Node(host, port, blockchain)

    if len(sys.argv) > 3:
        try:
            bs_host, bs_port = sys.argv[3].split(":")
            node.connect_to_bootstrap(bs_host, int(bs_port))
        except ValueError:
            print("[!] Erro: Formato do bootstrap deve ser IP:PORTA")

    while True:
        current_balance = blockchain.get_balance(my_address)
        print_header(my_address, current_balance, len(node.peers))
        
        print("1. Criar Transação")
        print("2. Minerar Bloco")
        print("3. Ver Blockchain")
        print("4. Peers Conectados")
        print("5. Sincronizar")
        print("0. Sair")
        
        opt = input("Escolha: ")
        
        if opt == '1':
            destino = input("Destinatário (IP:PORTA): ")
            try:
                valor = float(input("Valor: "))
                tx = Transaction(my_address, destino, valor)
                
                if blockchain.add_transaction(tx):
                    # Payload: {"transaction": {...}} 
                    msg = build_message(NEW_TRANSACTION, {"transaction": tx.to_dict()}, my_address)
                    node.broadcast(msg)
                    print(f"[Sucesso] Transação enviada.")
                else:
                    print("[Falha] Saldo insuficiente ou valor inválido.")
            except ValueError:
                print("[Erro] Valor inválido.")

        elif opt == '2':
            print("[Miner] Minerando...")
            new_block = blockchain.mine_pending_transactions(my_address)
            print(f"[Sucesso] Bloco {new_block.index} minerado com Hash: {new_block.hash[:15]}...")
            
            # Payload: {"block": {...}} 
            msg = build_message(NEW_BLOCK, {"block": new_block.to_dict()}, my_address)
            node.broadcast(msg)

        elif opt == '3':
            for b in blockchain.chain:
                print(f"[Bloco {b.index}] Hash: {b.hash[:10]}... | Txs: {len(b.transactions)}")
                for tx in b.transactions:
                    print(f"   -> [{tx['origem']}] enviou {tx['valor']} para [{tx['destino']}]")

        elif opt == '4':
            for p in node.peers: print(p)

        elif opt == '5':
            msg = build_message(REQUEST_CHAIN, {}, my_address)
            node.broadcast(msg)

        elif opt == '0':
            node.running = False
            time.sleep(0.5)
            sys.exit(0)

if __name__ == "__main__":
    main()
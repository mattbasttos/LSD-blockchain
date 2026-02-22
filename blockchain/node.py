import socket
import threading
from protocol import *
from transactions import Transaction
from block import Block

class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.address = f"{host}:{port}"
        self.blockchain = blockchain
        self.peers = set()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        threading.Thread(target=self.listen_for_connections, daemon=True).start()
        print(f"[Node] Ouvindo em {self.address}")

    def listen_for_connections(self):
        while self.running:
            try:
                client_socket, _ = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except: pass

    def register_node(self, node_address):
        if node_address not in self.peers and node_address != self.address:
            self.peers.add(node_address)
            print(f"[Rede] Peer adicionado: {node_address}")
            return True
        return False

    def connect_to_bootstrap(self, bootstrap_ip, bootstrap_port):
        target = f"{bootstrap_ip}:{bootstrap_port}"
        if self.register_node(target):
            msg = build_message(REQUEST_CHAIN, {}, self.address)
            self.send_message_to(target, msg)

    def handle_client(self, client_socket):
        try:
            # Usa a nova função TCP segura com prefixo de tamanho [cite: 108-109]
            message = recv_tcp_message(client_socket)
            if message:
                self.process_message(message)
        except Exception as e:
            print(f"[Erro Rede] {e}")
        finally:
            client_socket.close()

    def process_message(self, data):
        msg_type = data.get("type")
        payload = data.get("payload", {}) 
        sender = data.get("sender")       

        if sender:
            self.register_node(sender)

        if msg_type == NEW_TRANSACTION:
            # Formato do payload: {"transaction": {...}} 
            tx_data = payload.get("transaction")
            if tx_data:
                tx = Transaction.from_dict(tx_data)
                if self.blockchain.add_transaction(tx):
                    print(f"[Tx] Transação {tx.id[:8]}... recebida.")

        elif msg_type == NEW_BLOCK:
            # Formato do payload: {"block": {...}} 
            block_data = payload.get("block")
            if block_data:
                last_block = self.blockchain.get_last_block()
                if block_data['index'] == last_block.index + 1:
                    new_block = Block.from_dict(block_data)
                    if new_block.previous_hash == last_block.hash and new_block.hash.startswith(DIFFICULTY):
                        self.blockchain.chain.append(new_block)
                        self.blockchain.pending_transactions = []
                        print(f"[Bloco] Bloco {new_block.index} aceito.")
                elif block_data['index'] > last_block.index + 1:
                    self.broadcast(build_message(REQUEST_CHAIN, {}, self.address))

        elif msg_type == REQUEST_CHAIN:
            # Formato de envio: {"blockchain": {"chain": [...], "pending_transactions": [...]}} [cite: 137-141]
            payload_data = {
                "blockchain": {
                    "chain": [b.to_dict() for b in self.blockchain.chain],
                    "pending_transactions": self.blockchain.pending_transactions
                }
            }
            response = build_message(RESPONSE_CHAIN, payload_data, self.address)
            if sender:
                self.send_message_to(sender, response)

        elif msg_type == RESPONSE_CHAIN:
            blockchain_data = payload.get("blockchain", {})
            chain_data = blockchain_data.get("chain", [])
            
            if self.blockchain.replace_chain(chain_data):
                # Se a cadeia for substituída, atualiza as pendentes também
                self.blockchain.pending_transactions = blockchain_data.get("pending_transactions", [])
                print("[Consenso] Blockchain sincronizada com sucesso.")

    def broadcast(self, message_dict):
        for peer in list(self.peers):
            self.send_message_to(peer, message_dict)

    def send_message_to(self, peer_address, message_dict):
        try:
            host, port = peer_address.split(":")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, int(port)))
            # Usa a nova função de envio seguro com os 4 bytes [cite: 108-109]
            send_tcp_message(s, message_dict)
            s.close()
        except:
            pass # Peer offline
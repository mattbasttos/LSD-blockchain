import socket
import threading
import json
import time
from protocol import *
from transactions import Transaction
from block import Block

class Node:
    def __init__(self, host, port, blockchain):
        """
        Inicializa o nó da rede.
        Requisito: Executar como um processo independente.
        Requisito: Utilizar uma porta configurável.
        Requisito: Manter localmente uma cópia da blockchain e transações.
        """
        self.host = host
        self.port = port
        self.blockchain = blockchain  # Cópia local da blockchain e mempool
        self.peers = set()            # Lista de nós conhecidos (Host, Port)
        
        # Configuração do Socket Servidor (P2P)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        
        # Thread para escutar conexões de entrada sem travar o processamento
        listen_thread = threading.Thread(target=self.listen_for_connections)
        listen_thread.daemon = True
        listen_thread.start()
        
        print(f"[Node] Nó iniciado em {self.host}:{self.port}")

    def listen_for_connections(self):
        """Loop principal que aceita conexões TCP de outros nós."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                # Trata cada conexão em uma nova thread para não bloquear
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except Exception as e:
                print(f"[Erro] Falha no listener: {e}")

    def register_node(self, node_address):
        """
        Adiciona um novo nó à lista de peers conhecidos.
        Requisito: Conhecer ao menos um nó inicial.
        """
        if node_address not in self.peers and node_address != (self.host, self.port):
            self.peers.add(node_address)
            print(f"[Rede] Novo peer registrado: {node_address}")
            return True
        return False

    def connect_to_bootstrap(self, bootstrap_ip, bootstrap_port):
        """
        Conecta-se ao nó inicial e solicita a entrada na rede.
        """
        target = (bootstrap_ip, bootstrap_port)
        if self.register_node(target):
            # Ao conectar, solicitamos a chain e enviamos nossa porta para que ele nos conheça
            # O protocolo exige REQUEST_CHAIN 
            message = {
                "type": REQUEST_CHAIN,
                "sender_host": self.host, # Metadados para o peer saber quem somos
                "sender_port": self.port
            }
            self.send_message(target, message)

    def handle_client(self, client_socket):
        """Recebe e processa mensagens brutas via socket."""
        try:
            buffer = ""
            while True:
                data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                buffer += data
                if not data or len(data) < BUFFER_SIZE: break
            
            if buffer:
                message = json.loads(buffer)
                self.process_message(message)
        except json.JSONDecodeError:
            print("[Erro] Mensagem inválida recebida.")
        except Exception as e:
            print(f"[Erro] Tratando cliente: {e}")
        finally:
            client_socket.close()

    def process_message(self, data):
        """
        Roteia a lógica baseada no tipo de mensagem do protocolo.
        Requisito: Implementar NEW_TRANSACTION, NEW_BLOCK, REQUEST_CHAIN, RESPONSE_CHAIN.
        """
        msg_type = data.get("type")
        
        # Lógica de descoberta de pares (Gossip implícito)
        # Se a mensagem tem metadados do remetente, adicionamos aos peers
        if "sender_host" in data and "sender_port" in data:
            sender_addr = (data["sender_host"], int(data["sender_port"]))
            self.register_node(sender_addr)

        if msg_type == NEW_TRANSACTION:
            tx_data = data.get("data")
            tx = Transaction.from_dict(tx_data)
            # Tenta adicionar à pool local
            if self.blockchain.add_transaction(tx):
                print(f"[Tx] Transação {tx.id[:8]}... recebida e adicionada.")
                # Opcional: Re-propagar para outros peers (Flooding)

        elif msg_type == NEW_BLOCK:
            block_data = data.get("data")
            # Validação básica antes de aceitar
            last_block = self.blockchain.get_last_block()
            
            if block_data['index'] == last_block.index + 1:
                # Reconstrói bloco para validar hash
                new_block = Block.from_dict(block_data)
                
                if new_block.previous_hash == last_block.hash and new_block.hash.startswith(DIFFICULTY):
                    self.blockchain.chain.append(new_block)
                    self.blockchain.pending_transactions = [] # Limpa transações já mineradas
                    print(f"[Bloco] Bloco {new_block.index} recebido e aceito.")
            
            elif block_data['index'] > last_block.index + 1:
                print("[Consenso] Cadeia local curta demais. Solicitando sincronização.")
                self.broadcast({"type": REQUEST_CHAIN, "sender_host": self.host, "sender_port": self.port})

        elif msg_type == REQUEST_CHAIN:
            # Envia a cópia local da blockchain
            chain_data = [b.to_dict() for b in self.blockchain.chain]
            response = {
                "type": RESPONSE_CHAIN,
                "data": chain_data,
                "sender_host": self.host,
                "sender_port": self.port
            }
            # Se soubermos quem pediu, respondemos direto (melhor performance)
            if "sender_host" in data:
                target = (data["sender_host"], int(data["sender_port"]))
                self.send_message(target, response)
            else:
                self.broadcast(response)

        elif msg_type == RESPONSE_CHAIN:
            new_chain_data = data.get("data")
            # Tenta substituir a cadeia local pela recebida (Regra da cadeia mais longa) 
            if self.blockchain.replace_chain(new_chain_data):
                print("[Consenso] Blockchain sincronizada com a rede (Cadeia substituída).")

    def broadcast(self, message_dict):
        """Envia uma mensagem para TODOS os nós conhecidos."""
        # Garante que metadados de origem vão em todas as mensagens
        if "sender_host" not in message_dict:
            message_dict["sender_host"] = self.host
            message_dict["sender_port"] = self.port

        for peer in self.peers:
            self.send_message(peer, message_dict)

    def send_message(self, peer, message_dict):
        """Envia mensagem para um nó específico."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2) # Timeout curto para não travar
            s.connect(peer)
            s.sendall(json.dumps(message_dict).encode('utf-8'))
            s.close()
        except ConnectionRefusedError:
            # Se falhar, podemos remover o peer da lista futuramente
            pass
        except Exception as e:
            print(f"[Erro Rede] Falha ao enviar para {peer}: {e}")
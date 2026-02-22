import json
import struct

NEW_TRANSACTION = "NEW_TRANSACTION"
NEW_BLOCK       = "NEW_BLOCK"
REQUEST_CHAIN   = "REQUEST_CHAIN"
RESPONSE_CHAIN  = "RESPONSE_CHAIN"

ENCODING    = 'utf-8'
DIFFICULTY  = "000"
MINING_REWARD = 50.0  # Novo valor da recompensa [cite: 189]

def build_message(msg_type, payload=None, sender_address=None):
    """
    Cria a estrutura base exigida pelo padrão [cite: 111-116].
    """
    if payload is None:
        payload = {}
        
    return {
        "type": msg_type,
        "payload": payload,
        "sender": sender_address # Formato "host:port"
    }

def send_tcp_message(sock, message_dict):
    """
    Formato de Transmissão (TCP): [4 bytes: tamanho big-endian] [N bytes: JSON UTF-8] [cite: 108-109]
    """
    msg_bytes = json.dumps(message_dict).encode(ENCODING)
    # '>I' significa Big-Endian, Unsigned Integer de 4 bytes
    size_prefix = struct.pack('>I', len(msg_bytes)) 
    sock.sendall(size_prefix + msg_bytes)

def recvall(sock, n):
    """Função auxiliar para garantir o recebimento de exatamente n bytes."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def recv_tcp_message(sock):
    """Lê o prefixo de tamanho e depois o JSON exato."""
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    
    # Desempacota os 4 bytes big-endian para descobrir o tamanho
    msglen = struct.unpack('>I', raw_msglen)[0]
    
    msg_bytes = recvall(sock, msglen)
    if not msg_bytes:
        return None
        
    return json.loads(msg_bytes.decode(ENCODING))
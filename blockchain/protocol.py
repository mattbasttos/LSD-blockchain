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
    if payload is None:
        payload = {}
        
    return {
        "type": msg_type,
        "payload": payload,
        "sender": sender_address # Formato "host:port"
    }

def send_tcp_message(sock, message_dict):
    msg_bytes = json.dumps(message_dict).encode(ENCODING)
    # '>I' significa Big-Endian, Unsigned Integer de 4 bytes
    size_prefix = struct.pack('>I', len(msg_bytes)) 
    sock.sendall(size_prefix + msg_bytes)

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def recv_tcp_message(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    
    msglen = struct.unpack('>I', raw_msglen)[0]
    
    msg_bytes = recvall(sock, msglen)
    if not msg_bytes:
        return None
        
    return json.loads(msg_bytes.decode(ENCODING))
import json

# TIPOS DE MENSAGENS
NEW_TRANSACTION = "NEW_TRANSACTION"  # Envio de uma nova transação
NEW_BLOCK       = "NEW_BLOCK"        # Envio de um bloco minerado
REQUEST_CHAIN   = "REQUEST_CHAIN"    # Solicitação da blockchain completa (ao entrar na rede)
RESPONSE_CHAIN  = "RESPONSE_CHAIN"   # Envio da blockchain para sincronização

# CONFIGURAÇÕES DA REDE
BUFFER_SIZE = 4096       # Tamanho do buffer de recebimento do socket
ENCODING    = 'utf-8'    # Codificação padrão das mensagens
DIFFICULTY  = "000"      # Dificuldade fixa do Proof of Work [cite: 55]

# UTILITÁRIOS DE PROTOCOLO

def build_message(msg_type, data=None, sender_host=None, sender_port=None):
    """
    Cria um dicionário padronizado para comunicação via socket.
    Isso garante que todos os nós (mesmo de outros grupos) recebam
    o JSON no formato esperado.
    
    Estrutura Padrão:
    {
        "type": "NEW_BLOCK",
        "data": { ...dados do bloco... },
        "sender_host": "192.168.1.10",
        "sender_port": 5000
    }
    """
    message = {
        "type": msg_type,
        "data": data,
        "timestamp": 0 # Pode ser útil para logs ou desempate
    }
    
    # Metadados opcionais para descoberta de peers (Gossip)
    if sender_host and sender_port:
        message["sender_host"] = sender_host
        message["sender_port"] = sender_port
        
    return message

def to_json(message_dict):
    """Serializa o dicionário para bytes prontos para envio no socket."""
    return json.dumps(message_dict).encode(ENCODING)

def from_json(bytes_data):
    """Deserializa bytes recebidos do socket para dicionário Python."""
    return json.loads(bytes_data.decode(ENCODING))
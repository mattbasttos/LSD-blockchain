# Blockchain LSD 2025 - Sistema Distribuído Simplificado

Este projeto é uma implementação de uma criptomoeda simplificada (baseada em Bitcoin) desenvolvida para a disciplina de **Sistemas Distribuídos** da UFPA. O sistema funciona sobre uma rede P2P estruturada com *sockets*, sem servidor central, implementando consenso via *Proof of Work* (PoW).

## 📋 Pré-requisitos

Para executar este projeto, você precisa apenas de:

* **Python 3.6 ou superior** instalado.
* Sistema Operacional: Windows, Linux ou macOS.
* **Não é necessário instalar bibliotecas externas** (o código utiliza apenas bibliotecas padrão do Python: `socket`, `threading`, `json`, `hashlib`, `sys`, `time`).

## 📂 Estrutura dos Arquivos

Certifique-se de que todos os arquivos abaixo estejam na mesma pasta:

* `main.py`: Ponto de entrada e interface CLI.
* `node.py`: Gerenciamento de rede P2P e Sockets.
* `blockchain.py`: Regras de negócio, validação da cadeia e saldo.
* `block.py`: Estrutura de dados do Bloco.
* `transactions.py`: Estrutura de dados da Transação.
* `consensus.py`: Algoritmo de Mineração (Proof of Work).
* `protocol.py`: Constantes e configurações de mensagens JSON.

---

## 🚀 Como Rodar

O sistema pode ser executado de duas formas: **Localmente** (simulação em um único PC) ou **Distribuído** (em vários PCs na mesma rede/laboratório).

A sintaxe padrão de execução no terminal é:

```bash
python main.py <IP_DESTE_NO> <PORTA_DESTE_NO> [IP_BOOTSTRAP:PORTA_BOOTSTRAP]

```

### Cenário 1: Simulação Local (Localhost)

Abra múltiplos terminais (cmd/powershell/bash) para simular nós diferentes.

**Terminal 1 (Nó Gênesis / Bootstrap):**
Este é o primeiro nó. Ele inicia a rede.

```bash
python main.py 127.0.0.1 5000

```

**Terminal 2 (Peer A):**
Conecta-se ao nó da porta 5000.

```bash
python main.py 127.0.0.1 5001 127.0.0.1:5000

```

**Terminal 3 (Peer B):**
Conecta-se ao nó da porta 5000 (ou 5001).

```bash
python main.py 127.0.0.1 5002 127.0.0.1:5000

```

---

### Cenário 2: Execução Distribuída (Laboratório/LAN)

Para rodar em computadores diferentes na mesma rede Wi-Fi ou cabeada.

1. **Descubra o IP** de cada máquina (comando `ipconfig` no Windows ou `hostname -I` no Linux).
2. **Firewall:** Certifique-se de que o firewall permite conexões na porta escolhida (ex: 5000).

**No Computador A (IP: 192.168.1.10):**

```bash
python main.py 192.168.1.10 5000

```

**No Computador B (IP: 192.168.1.11):**
Conectando-se ao Computador A:

```bash
python main.py 192.168.1.11 5000 192.168.1.10:5000

```

---

## 🎮 Guia de Uso (Menu)

Ao iniciar, você verá o seguinte menu interativo:

1. **Criar Transação:**
* Solicita o `IP:PORTA` do destinatário e o valor.
* O sistema verifica se você tem saldo positivo (regra: não permitir saldo negativo ).


* A transação é propagada para a rede via mensagem `NEW_TRANSACTION`.




2. **Minerar Bloco:**
* Executa o *Proof of Work* (encontrar hash iniciando com "000").


* Empacota as transações pendentes.
* Ao terminar, propaga o bloco (`NEW_BLOCK`) para todos os nós conectados.


3. **Visualizar Blockchain:**
* Mostra o estado atual da cadeia local, hashes e transações confirmadas.


4. **Listar Peers Conectados:**
* Mostra quais IPs estão conectados ao seu nó.


5. **Forçar Sincronização:**
* Envia uma mensagem `REQUEST_CHAIN` para os pares.
* Se um par tiver uma cadeia maior e válida, seu nó substituirá a cadeia local automaticamente (Regra da Cadeia Mais Longa).




6. **Sair:** Desliga o nó.

---

## 🛠️ Detalhes Técnicos e Protocolo

O sistema implementa estritamente os requisitos do trabalho:

* **Comunicação:** Sockets TCP/IP.
* **Serialização:** JSON.
* **Consenso:** Proof of Work com dificuldade fixa ("000").
* 
**Mensagens Implementadas** :


* `NEW_TRANSACTION`: Propagação de transferência de fundos.
* `NEW_BLOCK`: Propagação de bloco minerado.
* `REQUEST_CHAIN`: Pedido de sincronização (entrada na rede).
* `RESPONSE_CHAIN`: Envio da blockchain completa.



## ⚠️ Solução de Problemas Comuns

* **Erro "Address already in use":** Você está tentando abrir um nó numa porta que já está aberta. Mude a porta (ex: de 5000 para 5001) ou feche o terminal anterior.
* **Nós não se conectam (Distribuído):** Verifique se os computadores conseguem se "pingar". Desative temporariamente o Firewall do Windows para testar.
* **Transação Rejeitada:** Você tentou enviar mais dinheiro do que possui. Lembre-se: No início, ninguém tem saldo. Minere um bloco primeiro para ganhar recompensas ou crie uma transação vinda do sistema (modificando o código para testes).

---

**Autores:** Mateus Bastos, Matheus Azevedo e Alexandre Moraes

**Disciplina:** Laboratório de Sistemas Distribuídos - UFPA 2025
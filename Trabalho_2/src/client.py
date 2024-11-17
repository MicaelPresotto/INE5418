import socket

# Initial commit, I'm in doubt about who communicates with whom, idk if they communicate with de sequencer or with the server
# I had assumed that the client communicates with the server, but I'm not sure
# Probably the client communicates with the server, and the server communicates with the sequencer
# The sequencer communicates with the replicas, to broadcast the message
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 8080))

    # Conjunto de leitura e escrita
    rs = []
    ws = []

    # Realiza uma leitura
    client.send("READ item1".encode())
    response = client.recv(1024).decode()
    if response.startswith("VALUE"):
        _, key, value, version = response.split()
        rs.append((key, int(value), int(version)))
        print(f"Lido: {key} = {value}, versão {version}")

    # Adiciona uma escrita
    ws.append(("item1", 30))

    # Tenta confirmar a transação
    client.send(f"COMMIT {str((rs, ws))}".encode())
    response = client.recv(1024).decode()
    print(f"Resultado da transação: {response}")

    client.close()

start_client()

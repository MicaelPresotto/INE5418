import socket
import threading

# Difusão atômica simples
def atomic_broadcast(message, replicas):
    for replica in replicas:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(replica)
            client_socket.sendall(message.encode())

# Servidor sequenciador central
def sequencer_server(port, replicas):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print("Sequenciador iniciado...")

    while True:
        conn, _ = server.accept()
        with conn:
            message = conn.recv(1024).decode()
            print(f"Sequenciador recebeu: {message}")
            atomic_broadcast(message, replicas)

# Lista de réplicas
replicas = [("127.0.0.1", 9001), ("127.0.0.1", 9002)]
threading.Thread(target=sequencer_server, args=(8080, replicas), daemon=True).start()

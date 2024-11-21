import socket
import threading
import json

def atomic_broadcast(message, replicas):
    for replica in replicas:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(replica)
            client_socket.sendall(message.encode())

def sequencer_server(replicas):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 9000))
    server.listen(1)
    print("Sequencializer started")

    while True:
        conn, _ = server.accept()
        with conn:
            message = json.loads(conn.recv(1024).decode())
            print(f"Sequencializer received: {message}")
            atomic_broadcast(message, replicas)

replicas = [("127.0.0.1", 9001), ("127.0.0.1", 9002)]
threading.Thread(target=sequencer_server, args=(8080, replicas), daemon=True).start()

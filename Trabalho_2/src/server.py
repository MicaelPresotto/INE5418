import socket
import threading

# Banco de dados simples: key-value com versão
database = {
    "item1": {"value": 10, "version": 1},
    "item2": {"value": 20, "version": 1},
}

def handle_client(client_socket):
    while True:
        message = client_socket.recv(1024).decode()
        if not message:
            break
        
        if message.startswith("READ"):
            key = message.split()[1]
            if key in database:
                response = f"VALUE {key} {database[key]['value']} {database[key]['version']}"
            else:
                response = f"ERROR Key {key} not found"
            client_socket.send(response.encode())

        elif message.startswith("COMMIT"):
            rs, ws = eval(message.split(" ", 1)[1])  # Recebe rs e ws
            valid = True
            for item in rs:
                key, _, version = item
                if database[key]["version"] != version:
                    valid = False
                    break

            if valid:
                for item in ws:
                    key, value = item
                    database[key]["value"] = value
                    database[key]["version"] += 1
                client_socket.send("COMMITTED".encode())
            else:
                client_socket.send("ABORTED".encode())
    client_socket.close()

# Inicialização do servidor
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8080))
    server.listen(5)
    print("Servidor iniciado na porta 8080...")

    while True:
        client_socket, _ = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

start_server()

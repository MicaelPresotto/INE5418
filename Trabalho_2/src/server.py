import socket
import threading
from Item import Item
import json

class Server:
    def __init__(self):
        self.database = [
            Item(id=1, name="x", value=0, version=0),
            Item(id=2, name="y", value=0, version=0),
        ]
        self.last_committed = 0

    def get_item(self, item_name):
        for item in self.database:
            if item.name == item_name:
                return item
        return None

    def process_request(self, client_socket, request):
        request_type = request["type"]

        if request_type == "read":
            item_name = request["item"]
            item = self.get_item(item_name)
            if item:
                response = {"status": "success", "value": item.value, "version": item.version}
            else:
                response = {"status": "error", "message": "Item not found"}
            client_socket.sendall(json.dumps(response).encode())

        elif request_type == "commit":
            read_set = request["read_set"]
            write_set = request["write_set"]
            abort = False

            # Certification test
            for read_item in read_set:
                item_name = read_item["item"]
                client_version = read_item["version"]
                item = self.get_item(item_name)
                if not item or item.version > client_version:
                    response = {"status": "abort"}
                    client_socket.sendall(json.dumps(response).encode())
                    abort = True
                    break

            if not abort:
                self.last_committed += 1

                # Apply write operations
                for write_item in write_set:
                    item_name = write_item["item"]
                    value = write_item["value"]
                    item = self.get_item(item_name)
                    if item:
                        item.version = self.last_committed
                        item.value = value

                # Confirm the commit
                response = {"status": "commit"}
                client_socket.sendall(json.dumps(response).encode())

    def handle_client(self, client_socket):
        try:
            while True:
                # Receive data from the client
                request_data = json.loads(client_socket.recv(1024).decode())
                if not request_data:
                    break

                request = request_data
                self.process_request(client_socket, request)
        except Exception as e:
            print(f"Erro ao processar cliente: {e}")
        finally:
            client_socket.close()

def start_server():
    server_instance = Server()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 9001))
    server_socket.listen(5)
    print("Servidor iniciado na porta 9001...")

    while True:
        client_socket, _ = server_socket.accept()
        thread = threading.Thread(target=server_instance.handle_client, args=(client_socket,))
        thread.start()

start_server()

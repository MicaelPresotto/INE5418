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
            print(f"Sending response: {response}")
            client_socket.sendall(json.dumps(response).encode())

        elif request_type == "commit":
            read_set = request["read_set"]
            write_set = request["write_set"]
            abort = False

            # Certification test
            for read_item in read_set:
                item_name = read_item[0]
                client_version = read_item[2]
                if client_version == "local":
                    continue
                client_version = int(client_version)
                item = self.get_item(item_name)
                if not item or item.version > client_version:
                    print(f"Certification test failed for item {item_name}")
                    response = {"status": "abort"}
                    print(f"Sending response: {response}")
                    try:
                        client_socket.sendall(json.dumps(response).encode())
                    except Exception as e:
                        print(f"Error sending response: {e}")
                    abort = True
                    break

            if not abort:
                self.last_committed += 1

                # Apply write operations
                for write_item in write_set:
                    item_name = write_item[0]
                    value = write_item[1]
                    item = self.get_item(item_name)
                    if item:
                        item.version = self.last_committed
                        item.value = value

                # Confirm the commit
                response = {"status": "commit"}
                print(f"Sending response: {response}")
                client_socket.sendall(json.dumps(response).encode())
                print("New database state:", self.database)

    def handle_client(self, client_socket):
        try:
            while True:
                raw_data = client_socket.recv(1024).decode().strip()
                if not raw_data:
                    print("Client disconnected.")
                    break
                print("Data received: ", raw_data)
                request_data = json.loads(raw_data)
                self.process_request(client_socket, request_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}, raw data: '{raw_data}'")
        except Exception as e:
            print(f"Error processing client: {e}")
        finally:
            print("Closing client connection.")
            client_socket.close()



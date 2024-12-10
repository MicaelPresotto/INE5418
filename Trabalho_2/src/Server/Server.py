import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils.Item import Item

class Server:
    def __init__(self):
        self.database = [
            Item(id=1, name="x", value=0, version=0),
            Item(id=2, name="y", value=0, version=0),
        ]
        self.last_committed = 0
        self.message_queue = dict()
        self.sequence_numbers_received = 0

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
            sequence_number = request.get("sequence_number")
            if sequence_number is None:
                response = {"status": "error", "message": "Sequence number missing"}
                print(f"Sending response: {response}")
                client_socket.sendall(json.dumps(response).encode())
                return

            if sequence_number > self.sequence_numbers_received + 1:
                print(f"Sequence {sequence_number} out of order. Expected {self.sequence_numbers_received + 1}. Storing in queue.")
                self.message_queue[sequence_number].append((client_socket, request))
                return
            elif sequence_number < self.sequence_numbers_received + 1:
                print(f"Sequence {sequence_number} already processed. Ignoring.")
                return

            self.sequence_numbers_received+=1
            self._process_commit_request(client_socket, request)

            self.message_queue = dict(sorted(self.message_queue.items()))
            self._process_buffered_requests()

    def _process_commit_request(self, client_socket, request):
        read_set = request["read_set"]
        write_set = request["write_set"]
        abort = False

        # Certification Test
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

            for write_item in write_set:
                item_name = write_item[0]
                value = write_item[1]
                item = self.get_item(item_name)
                if item:
                    item.version = item.version + 1
                    item.value = value

            # Confirm commit
            response = {"status": "commit"}
            print(f"Sending response: {response}")
            client_socket.sendall(json.dumps(response).encode())
            print("New database state:", self.database)

    def _process_buffered_requests(self):
        for i in self.message_queue.keys():
            if i == self.sequence_numbers_received + 1:
                for sequence_number, requests in self.message_queue.items():
                    self._process_commit_request(requests[0], requests[1])
                    self.sequence_numbers_received+=1
                    del self.message_queue[sequence_number]


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



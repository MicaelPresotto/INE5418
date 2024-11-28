import socket
import random
import json
from time import sleep
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils.Transaction import Transaction

class Client:
    def __init__(self, client_id, sequencer, replica_servers):
        self.client_id = client_id
        self.sequencer = sequencer
        self.replica_servers = replica_servers

    def execute_transaction(self, transaction: Transaction):
        write_set = set()
        read_set = set()
        i = 0

        # Randomly choose one of the replica servers
        replica_server = random.choice(self.replica_servers)

        while transaction.get_op(i) not in ["commit", "abort"]:
            operation = transaction.get_op(i)
            if operation is None:
                return
            item = transaction.get_item(i)
            value = transaction.get_value(i)
            print(f"Operation: {operation}, Item: {item}, Value: {value}")

            if operation == "write":
                write_set.add((item, value))

            elif operation == "read":
                if item in {item for item, _ in write_set}:
                    value = next(value for item, value in write_set if item == item)
                    read_set.add((item, value, "local"))
                else:
                    # Handle read operation
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                        client.connect(replica_server)
                        message = {
                            "type": "read",
                            "client_id": self.client_id,
                            "transaction_id": transaction.id,
                            "item": item
                        }
                        self._send_message(client, message)
                        response = self._receive_response(client)

                        if response["status"] == "error":
                            print(response["message"])
                        else:
                            value, version = response["value"], response["version"]
                            read_set.add((item, value, version))

            sleep(transaction.sleep_time)
            i += 1

        if transaction.get_op(i) == "commit":
            self._commit_transaction(transaction, read_set, write_set)
        else:
            transaction.result = "abort"

    def _commit_transaction(self, transaction, read_set, write_set):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(self.sequencer)
            message = {
                "type": "commit",
                "client_id": self.client_id,
                "transaction_id": transaction.id,
                "read_set": list(read_set),
                "write_set": list(write_set)
            }
            self._send_message(client, message)
            response = self._receive_response(client)
            transaction.result = response['status']
            print("Transaction result: ", transaction.result)

    def _send_message(self, client, message):
        try:
            serialized_message = json.dumps(message).encode()
            client.sendall(serialized_message)
        except Exception as e:
            print(f"Error sending message: {e}")
            raise

    def _receive_response(self, client):
        response_data = client.recv(1024).decode()
        if not response_data.strip():  # Empty response
            raise ValueError("Empty response received from server")
        try:
            return json.loads(response_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            raise


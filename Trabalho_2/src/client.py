import socket
import random
from Transaction import Transaction
import json

replica_servers = [("127.0.0.1", 9001)]
sequencializer = ("127.0.0.1", 9000)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind(("127.0.0.1", 8000))


def T(client_id, transaction: Transaction):
    write_set = set()
    read_set = set()
    i = 0

    # Randomly choose one of the replica servers
    s = random.choice(replica_servers)

    while transaction.get_op(i) != "commit" and transaction.get_op(i) != "abort":
        if transaction.get_op(i) == "write":
            write_set.add((transaction.get_item(i), transaction.get_value(i)))

        elif transaction.get_op(i) == "read":
            # Check if the item is in the write set
            if transaction.get_item(i) in {item for item, _ in write_set}:
                return next(value for item, value in write_set if item == transaction.get_item(i))
            else:
                # Send the read request to the replica server
                client.connect(s)
                message = {
                    "com_req": "read",
                    "client_id": client_id,
                    "transaction_id": transaction.id,
                    "item": transaction.get_item(i)
                }
                client.sendall(message.encode())
                response = json.loads(client.recv(1024).decode())
                if response["status"] == "error":
                    print([response["message"]])
                else:            
                    value, version = response.split()[1:]
                    read_set.add((transaction.get_item(i), value, version))
                client.close()

        i += 1

    if transaction.get_op(i) == "commit":
        client.connect(sequencializer)
        message = {
            "com_req": "commit",
            "client_id": client_id,
            "transaction_id": transaction.id,
            "read_set": read_set,
            "write_set": write_set
        }
        client.sendall(message.encode())
        outcome = json.loads(client.recv(1024).decode())
        transaction.result = outcome['status']
        client.close()
    else:
        transaction.result = "abort"

transaction = Transaction(
    operations=["write", "read", "commit"],
    items=["x", "y"],
    values=[42, None],
    transaction_id="T1"
)

client_id = "client1"

T(client_id, transaction)
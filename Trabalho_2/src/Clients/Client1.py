import threading
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.Client import Client
from Utils.Transaction import Transaction

# Configuração do sistema
replica_servers = [("127.0.0.1", 9001), ("127.0.0.1", 9002)]
sequencializer = ("127.0.0.1", 9000)

# Função para executar uma transação
def execute_transaction(client_id, operations, items, values, sleep_time, transaction_id):
    client = Client(client_id=client_id, sequencializer=sequencializer, replica_servers=replica_servers)
    transaction = Transaction(
        operations=operations,
        items=items,
        values=values,
        transaction_id=transaction_id,
        sleep_time=sleep_time
    )
    client.execute_transaction(transaction)
    print(f"Client {client_id}: Transaction {transaction_id} result: {transaction.result}")

threads = (
    threading.Thread(
        target=execute_transaction,
        args=("client1", ["read", "write", "commit"], ["x", "x"], [None, 42], 2,"T1")
    ),
    threading.Thread(
        target=execute_transaction,
        args=("client2", ["read", "write", "commit"], ["x", "x"], [None, 99], 4, "T2")
    ),
    threading.Thread(
        target=execute_transaction,
        args=("client3", ["read", "commit"], ["y"], [None], 3, "T3")
    ),

)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()


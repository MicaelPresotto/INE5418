import threading
from Client import Client
from Transaction import Transaction

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

thread_1 = threading.Thread(
    target=execute_transaction,
    args=("client1", ["read", "write", "commit"], ["x", "x"], [None, 42], 2,"T1")
)

thread_2 = threading.Thread(
    target=execute_transaction,
    args=("client2", ["read", "write", "commit"], ["x", "x"], [None, 99], 2, "T2")
)

# Iniciar threads
thread_1.start()
thread_2.start()

# Aguardar finalização
thread_1.join()
thread_2.join()

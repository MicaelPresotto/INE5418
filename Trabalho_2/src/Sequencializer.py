import socket
import threading
import json

def atomic_broadcast(message, replicas):
    responses = []
    
    for replica in replicas:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(replica)
            client_socket.sendall(json.dumps(message).encode())
            try:
                response_data = client_socket.recv(1024).decode()
                if not response_data.strip():
                    raise ValueError("Empty response from replica")
                response = json.loads(response_data)
                responses.append(response)
            except Exception as e:
                print(f"Error communicating with replica: {e}")
                responses.append({"status": "error"})
    
    return responses

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
            
            responses = atomic_broadcast(message, replicas)
            
            if all(response.get("status") == "commit" for response in responses):
                response = {"status": "commit"}
            else:
                response = {"status": "abort"}
            
            conn.sendall(json.dumps(response).encode())


replicas = [("127.0.0.1", 9001), ("127.0.0.1", 9002)]

threading.Thread(target=sequencer_server, args=(replicas,)).start()

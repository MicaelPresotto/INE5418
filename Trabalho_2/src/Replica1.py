from Server import Server
import socket
import threading

def start_server():
    server_instance = Server()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 9001))
    server_socket.listen(5)
    print("Server started on port 9001...")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            thread = threading.Thread(target=server_instance.handle_client, args=(client_socket,))
            thread.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server_socket.close()
        print("Server socket closed.")

start_server()
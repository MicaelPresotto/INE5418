import socket
import threading
import json

class Sequencer:
    def __init__(self, host, port, replicas):
        self.host = host
        self.port = port
        self.replicas = replicas
        self.sequence_number = 0
        self.sequence_lock = threading.Lock()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        """Starts the Sequencer server."""
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Sequencer started on {self.host}:{self.port}")

        threading.Thread(target=self._listen_for_clients).start()

    def _listen_for_clients(self):
        """Waits for client connections and processes their requests."""
        while True:
            conn, addr = self.server.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=self._handle_client, args=(conn,)).start()

    def _handle_client(self, conn):
        """Processes messages from clients."""
        try:
            message = json.loads(conn.recv(1024).decode())
            print(f"Received message: {message}")

            # Add the sequence number in a thread-safe manner
            with self.sequence_lock:
                self.sequence_number += 1
                message["sequence_number"] = self.sequence_number

            # Broadcast the message to the replicas
            responses = self._atomic_broadcast(message)

            # Determine the status based on the responses from the replicas
            if all(response.get("status") == "commit" for response in responses):
                response = {"status": "commit"}
            else:
                response = {"status": "abort"}

            # Send the response back to the client
            conn.sendall(json.dumps(response).encode())
        except Exception as e:
            print(f"Error handling client: {e}")
            error_response = {"status": "error", "message": str(e)}
            conn.sendall(json.dumps(error_response).encode())
        finally:
            conn.close()

    def _atomic_broadcast(self, message):
        """Broadcasts a message to all replicas and collects responses."""
        responses = []

        for replica in self.replicas:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.connect(replica)
                    client_socket.sendall(json.dumps(message).encode())
                    response_data = client_socket.recv(1024).decode()

                    if not response_data.strip():
                        raise ValueError("Empty response from replica")
                    responses.append(json.loads(response_data))
            except Exception as e:
                print(f"Error communicating with replica {replica}: {e}")
                responses.append({"status": "error"})
        print(f"Responses from replicas: {responses}")
        return responses


if __name__ == "__main__":
    # Sequencer and replica configurations
    replicas = [("127.0.0.1", 9001), ("127.0.0.1", 9002)]
    sequencer = Sequencer(host="127.0.0.1", port=9000, replicas=replicas)

    # Start the Sequencer server
    sequencer.start()

    # Keep the program running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down Sequencer.")

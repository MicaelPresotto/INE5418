import socket
import threading
import json
import time
import os
from Peer import Peer

class P2PNetwork:
    def __init__(self, peer: Peer):
        self.peer = peer
        self.chunks_found = {}
        self.received_chunks = {}
        self.reconstructed_file = False

    def get_available_chunks(self, peer: Peer, file_name: str):
        peer_folder = f"../exemplo/{peer.id}/"
        if not os.path.exists(peer_folder):
            return []
        
        chunks = []
        for file in os.listdir(peer_folder):
            if file.startswith(file_name+ ".ch"):
                try:
                    chunk_number = int(file.split('.ch')[-1])
                    chunk_path = os.path.join(peer_folder, file)
                    chunk_size = os.path.getsize(chunk_path)  # Get the size of the chunk file
                    chunks.append((chunk_number, chunk_size))  # Append chunk number and size as a tuple
                except ValueError:
                    continue
        return chunks



    def udp_connection(self, peer: Peer):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.bind((peer.ip, peer.port))
            print(f"Peer {peer.id} listening on {peer.ip}:{peer.port}")
        except socket.error as e:
            print(f"Error binding peer {peer.id}: {e}")
            return

        # Start a thread for receiving messages
        threading.Thread(target=self.receive_messages, args=(sock, peer)).start()
        # Start a TCP server thread for sending chunks
        threading.Thread(target=self.tcp_server, args=(peer,)).start()

        while True:
            # Simulate sending messages at any time (for demo purposes)
            message = input()
            self.send_message(sock, message, peer)

    def receive_messages(self, sock, peer: Peer):
        while True:
            try:
                data, addr = sock.recvfrom(peer.bandwidth)
                try:
                    message = json.loads(data.decode())
                except json.JSONDecodeError:
                    print("Probably, your bandwidth is too low to receive the message.")
                    continue
                if (message['port_that_wants_file'] == peer.port) and 'chunks_list' in message.keys():
                    chunk, chunk_size = message['chunks_list'][0], message['chunks_list'][1]
                    if chunk not in self.chunks_found.keys():
                        self.chunks_found[chunk] = {'ip': peer.ip, 'port': message['peer_that_sent_port'], 'bandwidth': message['peer_band_width'], 'chunk_size': chunk_size}
                    elif self.chunks_found[chunk]['bandwidth'] < message['peer_band_width'] and self.chunks_found['port'] != peer.port:
                        self.chunks_found.pop(chunk)
                        self.chunks_found[chunk] = {'ip': peer.ip, 'port': message['peer_that_sent_port'], 'bandwidth': message['peer_band_width'], 'chunk_size': chunk_size}

                message["ttl"] -= 1
                ttl = message["ttl"]
                chunks_list = self.get_available_chunks(peer, message["file"])            

                if chunks_list:
                    if message['port_that_wants_file'] == peer.port:
                        for chunk, chunk_size in chunks_list:
                            if chunk not in self.chunks_found.keys():
                                self.chunks_found[chunk] = {'ip': peer.ip, 'port': peer.port, 'bandwidth': peer.bandwidth, 'chunk_size': chunk_size}
                                self.received_chunks[chunk] = True
                            else:
                                self.chunks_found.pop(chunk)
                                self.chunks_found[chunk] = {'ip': peer.ip, 'port': peer.port, 'bandwidth': peer.bandwidth, 'chunk_size': chunk_size}
                    else:
                        for chunk, chunk_size in chunks_list:
                            send_chunk = {"content": "I have a chunk", "ttl": 1, "chunks": message['chunks'], "chunks_list": (chunk, chunk_size), "port_that_wants_file": message['port_that_wants_file'], "peer_that_sent_port": peer.port, "file": message["file"], "peer_band_width": peer.bandwidth}
                            sock.sendto(json.dumps(send_chunk).encode(), (peer.ip, message["port_that_wants_file"]))
                if ttl > 0:
                    print(f"Peer {peer.id} received message from {addr}: {message['content']} with TTL {ttl}")

                    peer_that_sent = message["peer_that_sent_id"]
                    message["peer_that_sent_id"] = peer.id
                    message["peer_that_sent_port"] = peer.port
                        
                    for neighbour in peer.neighbours:
                        if neighbour.id == peer_that_sent: continue
                        sock.sendto(json.dumps(message).encode(), (peer.ip, neighbour.port))
                        print(f"Peer {peer.id} sent message to neighbour {neighbour.id} on port {neighbour.port}")
                else:
                    print(f"Peer {peer.id} dropped message with TTL expired from {addr}")
                    for i in os.listdir(f"../exemplo/{peer.id}/"):
                        if(message['file'] != i):
                            self.reconstructed_file = False
                        else:
                            self.reconstructed_file = True
                    if message["port_that_wants_file"] == peer.port:
                        self.download_chunks(peer)
                        if(not self.reconstructed_file):
                            if(self.reconstruct_file(peer.id, message["file"], message["chunks"])):
                                self.reconstructed_file = True
            except Exception as e:
                print(f"Error receiving message: {e}")

    def send_message(self, sock, message: str, peer: Peer):
        for neighbour in peer.neighbours:
            try:
                file, chunks, ttl = self.read_p2p_file('../exemplo/image.png.p2p')
                msg_with_ttl = {
                    "content": message, 
                    "ttl": ttl, 
                    "peer_that_sent_id": peer.id,
                    "peer_that_sent_port": peer.port,
                    "file": file, 
                    "chunks": chunks, 
                    "port_that_wants_file": peer.port,
                } 
                sock.sendto(json.dumps(msg_with_ttl).encode(), (peer.ip, neighbour.port))
                print(f"Peer {peer.id} sent message to neighbour {neighbour.id} on port {neighbour.port}")
            except Exception as e:
                print(f"Error sending message to neighbour {neighbour.id}: {e}")

    def tcp_server(self, peer: Peer):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((peer.ip, peer.port + 1000))  # Use a different port for TCP
        server_sock.listen(5)
        print(f"Peer {peer.id} TCP server listening on {peer.ip}:{peer.port + 1000}")

        while True:
            client_sock, addr = server_sock.accept()
            threading.Thread(target=self.handle_tcp_client, args=(client_sock, peer)).start()

    def handle_tcp_client(self, client_sock, peer: Peer):
        try:
            data = client_sock.recv(peer.bandwidth).decode()
            request = json.loads(data)
            file_name = request.get("file_name")
            chunk_number = request.get("chunk_number")
            
            # Locate the requested chunk
            file_path = f"../exemplo/{peer.id}/{file_name}.ch{chunk_number}"
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    client_sock.sendfile(f)
                print(f"Sent chunk {chunk_number} of {file_name} to {client_sock.getpeername()}")
            else:
                client_sock.send(b"Chunk not found")
        finally:
            client_sock.close()

    def request_chunk(self, peer: Peer, chunk_info):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((chunk_info["ip"], chunk_info["port"] + 1000))
            request_data = json.dumps({"file_name": "image.png", "chunk_number": chunk_info["chunk"]})
            sock.send(request_data.encode())
            received_data = 0

            with open(f"../exemplo/{peer.id}/image.png.ch{chunk_info['chunk']}", "wb") as f:
                while True:
                    data = sock.recv(chunk_info["bandwidth"])
                    if not data:
                        break
                    received_data += len(data)
                    print(f"Receving chunk {chunk_info['chunk']} from {chunk_info['ip']}:{chunk_info['port'] + 1000} the transfer is {received_data/chunk_info['chunk_size']*100:.2f}% completed")
                    time.sleep(1)
                    f.write(data)
            print(f"Received chunk {chunk_info['chunk']} from peer at {chunk_info['ip']}:{chunk_info['port'] + 1000}")
            if chunk_info["chunk"] not in self.received_chunks:
                self.received_chunks[chunk_info["chunk"]] = True

    def download_chunks(self, peer: Peer):
        for chunk, info in self.chunks_found.items():
            if chunk in self.received_chunks.keys() or info["port"] == peer.port:
                continue
            self.request_chunk(peer, {"ip": info["ip"], "port": info["port"], "chunk": chunk, "bandwidth": info["bandwidth"], "chunk_size": info["chunk_size"]})


    def read_p2p_file(self, filename: str) -> tuple[str, int, int]:
        with open(filename, 'r') as file:
            lines = file.readlines()
            return lines[0].replace('\n', ''), int(lines[1].replace('\n', '')), int(lines[2].replace('\n', ''))

    def reconstruct_file(self, peer_id: int, file_name: str, num_chunks: int):
        folder_path = f"../exemplo/{peer_id}/"
        output_file = f"{folder_path}{file_name}"

        if(len(os.listdir(folder_path)) < num_chunks):
            return False
        
        with open(output_file, 'wb') as final_file:
            for chunk_num in range(num_chunks):
                chunk_file = f"{folder_path}{file_name}.ch{chunk_num}"
                if os.path.exists(chunk_file):
                    with open(chunk_file, 'rb') as chunk:
                        final_file.write(chunk.read())
                else:
                    print(f"Chunk {chunk_num} do arquivo '{file_name}' não encontrado.")
                    return False

        print(f"Arquivo '{file_name}' reconstruído com sucesso em '{output_file}'")
        return True    
import socket
import time
import json
import sys
import threading
from dataclasses import dataclass, field
import os

@dataclass
class PeerNeighbour:
    id: int
    port: int = 0

@dataclass    
class Peer:
    id: int
    ip: str = ""
    port: int = 0
    bandwidth: int = 0
    neighbours: list[PeerNeighbour] = field(default_factory=list)

chunks_found = {}
received_chunks = {}

def get_available_chunks(peer: Peer, file_name: str):
    peer_folder = f"../exemplo/{peer.id}/"
    if not os.path.exists(peer_folder):
        return []
    
    chunks = []
    for file in os.listdir(peer_folder):
        if file.startswith(file_name):
            try:
                chunk_number = int(file.split('.ch')[-1])
                chunk_path = os.path.join(peer_folder, file)
                chunk_size = os.path.getsize(chunk_path)  # Get the size of the chunk file
                chunks.append((chunk_number, chunk_size))  # Append chunk number and size as a tuple
            except ValueError:
                continue
    return chunks



def udp_connection(peer: Peer):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((peer.ip, peer.port))
        print(f"Peer {peer.id} listening on {peer.ip}:{peer.port}")
    except socket.error as e:
        print(f"Error binding peer {peer.id}: {e}")
        return

    # Start a thread for receiving messages
    threading.Thread(target=receive_messages, args=(sock, peer)).start()
    # Start a TCP server thread for sending chunks
    threading.Thread(target=tcp_server, args=(peer,)).start()

    while True:
        # Simulate sending messages at any time (for demo purposes)
        message = input()
        send_message(sock, message, peer)

def receive_messages(sock, peer: Peer):
    reconstructed_file = False
    while True:
        try:
            data, addr = sock.recvfrom(peer.bandwidth)
            message = json.loads(data.decode())
            if (message['port_that_wants_file'] == peer.port) and 'chunks_list' in message.keys():
                for chunk, chunk_size in message['chunks_list']:
                    if chunk not in chunks_found.keys():
                        chunks_found[chunk] = {'ip': peer.ip, 'port': message['peer_that_sent_port'], 'bandwidth': message['peer_band_width'], 'chunk_size': chunk_size}
                    elif chunks_found[chunk]['bandwidth'] < message['peer_band_width']:
                        chunks_found.pop(chunk)
                        chunks_found[chunk] = {'ip': peer.ip, 'port': message['peer_that_sent_port'], 'bandwidth': message['peer_band_width'], 'chunk_size': chunk_size}

            message["ttl"] -= 1
            ttl = message["ttl"]
            chunks_list = get_available_chunks(peer, message["file"])            

            if chunks_list:
                if message['port_that_wants_file'] == peer.port:
                    for chunk, chunk_size in chunks_list:
                        if chunk not in chunks_found.keys():
                            chunks_found[chunk] = {'ip': peer.ip, 'port': peer.port, 'bandwidth': peer.bandwidth, 'chunk_size': chunk_size}
                            received_chunks[chunk] = True
                        elif chunks_found[chunk]['bandwidth'] < peer.bandwidth:
                            chunks_found.pop(chunk)
                            chunks_found[chunk] = {'ip': peer.ip, 'port': peer.port, 'bandwidth': peer.bandwidth, 'chunk_size': chunk_size}
                else:
                    send_chunk = {"content": "I have a chunk", "ttl": 1, "chunks": message['chunks'], "chunks_list": chunks_list, "port_that_wants_file": message['port_that_wants_file'], "peer_that_sent_port": peer.port, "file": message["file"], "peer_band_width": peer.bandwidth}
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
                if message["port_that_wants_file"] == peer.port:
                    download_chunks(peer)
                    if(len(chunks_found) == len(received_chunks) and not reconstructed_file):
                        reconstruct_file(peer.id, message["file"], message["chunks"])
                        reconstructed_file = True
        except Exception as e:
            print(f"Error receiving message: {e}")

def send_message(sock, message: str, peer: Peer):
    for neighbour in peer.neighbours:
        try:
            file, chunks, ttl = read_p2p_file('../exemplo/image.png.p2p')
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

def tcp_server(peer: Peer):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((peer.ip, peer.port + 1000))  # Use a different port for TCP
    server_sock.listen(5)
    print(f"Peer {peer.id} TCP server listening on {peer.ip}:{peer.port + 1000}")

    while True:
        client_sock, addr = server_sock.accept()
        threading.Thread(target=handle_tcp_client, args=(client_sock, peer)).start()

def handle_tcp_client(client_sock, peer: Peer):
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

def request_chunk(peer: Peer, chunk_info):
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
                print(f"Receving chunk {chunk_info['chunk']} from {chunk_info['ip']}:{chunk_info['port'] + 1000} the transfer is {received_data/chunk_info['chunk_size']*100:.2f}%  ")
                time.sleep(1)
                f.write(data)
        print(f"Received chunk {chunk_info['chunk']} from peer at {chunk_info['ip']}:{chunk_info['port'] + 1000}")
        if chunk_info["chunk"] not in received_chunks:
            received_chunks[chunk_info["chunk"]] = True

def download_chunks(peer: Peer):
    for chunk, info in chunks_found.items():
        if chunk in received_chunks.keys():
            continue
        request_chunk(peer, {"ip": info["ip"], "port": info["port"], "chunk": chunk, "bandwidth": info["bandwidth"], "chunk_size": info["chunk_size"]})

def load_peer_from_json(peer_id: int, filename: str) -> Peer:
    with open(filename, 'r') as json_file:
        peers_data = json.load(json_file)
        
    for peer_data in peers_data:
        if peer_data['id'] == peer_id:
            neighbours = [PeerNeighbour(id=neigh['id'], port=neigh['port']) for neigh in peer_data.get('neighbours', [])]
            return Peer(id=peer_data['id'], ip=peer_data['ip'], port=peer_data['port'], bandwidth=peer_data['bandwidth'], neighbours=neighbours)
    
    raise ValueError(f"Peer ID {peer_id} not found in the JSON file.")

def read_p2p_file(filename: str) -> tuple[str, int, int]:
    with open(filename, 'r') as file:
        lines = file.readlines()
        return lines[0].replace('\n', ''), int(lines[1].replace('\n', '')), int(lines[2].replace('\n', ''))

def reconstruct_file(peer_id: int, file_name: str, num_chunks: int):
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

def main():
    if len(sys.argv) != 2:
        print("Usage: python program.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])
    
    try:
        selected_peer = load_peer_from_json(peer_id, "truePeers.json")
    except ValueError as e:
        print(e)
        sys.exit(1)

    time.sleep(1) 
    udp_connection(selected_peer)

if __name__ == "__main__":
    main()

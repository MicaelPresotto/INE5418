import socket
import time
import json
import sys
import threading
from dataclasses import dataclass, field
import json

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

    while True:
        # Simulate sending messages at any time (for demo purposes)
        message = input(f"Peer {peer.id}, enter message to send: ")
        send_message(sock, message, peer)

def receive_messages(sock, peer: Peer):
    while True:
        try:
            data, addr = sock.recvfrom(peer.bandwidth)
            message = json.loads(data.decode())
            ttl = message.get("ttl", 0)
            
            if ttl > 0:
                print(f"Peer {peer.id} received message from {addr}: {message['content']} with TTL {ttl}")

                # Forward the message to all neighbors with decremented TTL
                message["ttl"] -= 1
                print(peer.neighbours)
                for neighbour in peer.neighbours:
                    sock.sendto(json.dumps(message).encode(), (peer.ip, neighbour.port))
                    print(f"Peer {peer.id} sent message to neighbour {neighbour.id} on port {neighbour.port}")
            else:
                print(f"Peer {peer.id} dropped message with TTL expired from {addr}")

        except Exception as e:
            print(f"Error receiving message: {e}")

def send_message(sock, message: str, peer: Peer):
    for neighbour in peer.neighbours:
        try:
            file, chunks, ttl = read_p2p_file('../exemplo/image.png.p2p')
            msg_with_ttl = {"content": message, "ttl": ttl, "peer_that_sent": peer.id, "file": file, "chunks": chunks} 
            sock.sendto(json.dumps(msg_with_ttl).encode(), (peer.ip, neighbour.port))
            print(f"Peer {peer.id} sent message to neighbour {neighbour.id} on port {neighbour.port}")
        except Exception as e:
            print(f"Error sending message to neighbour {neighbour.id}: {e}")

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

import socket
import time
import json
import sys
from dataclasses import dataclass, asdict, field

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

# def listen_udp(peer: Peer):
#     """ Function to listen for UDP messages on a peer """
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind((peer.ip, peer.port))

#     while True:
#         data, addr = sock.recvfrom(1024)  # Receive messages of up to 1024 bytes
#         print(f"Peer {peer.id} received message from {addr}: {data.decode()}")

def send_message_to_neighbors(peer: Peer, peers: list[Peer], message: str, ttl: int):
    """ Function to send discovery message to neighbors """
    if ttl <= 0:
        return  

    neighbors = peer.neighbours
    for neighbor in neighbors:
        neighbor = peers[neighbor.id]
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        msg_with_ttl = f"{message} (TTL: {ttl})"
        sock.sendto(msg_with_ttl.encode(), (neighbor.ip, neighbor.port))
        print(f"Peer {peer.id} sent message to Peer {neighbor.id}: {msg_with_ttl}")
        sock.close()

def load_peer_from_json(peer_id: int, filename: str) -> Peer:
    """ Load a specific peer from a JSON file """
    with open(filename, 'r') as json_file:
        peers_data = json.load(json_file)
        
    for peer_data in peers_data:
        if peer_data['id'] == peer_id:
            neighbours = [PeerNeighbour(id=neigh['id'], port=neigh['port']) for neigh in peer_data.get('neighbours', [])]
            return Peer(id=peer_data['id'], ip=peer_data['ip'], port=peer_data['port'], bandwidth=peer_data['bandwidth'], neighbours=neighbours)
    
    raise ValueError(f"Peer ID {peer_id} not found in the JSON file.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python program.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])
    
    try:
        selected_peer = load_peer_from_json(peer_id, "peers.json")
        print(selected_peer)
    except ValueError as e:
        print(e)
        sys.exit(1)

    time.sleep(1) 
    # send_message_to_neighbors(selected_peer, [selected_peer], "Searching for file 'example.txt'", ttl=3)

if __name__ == "__main__":
    main()

import socket
import time
from dataclasses import dataclass

@dataclass
class PeerNeighbour:
    id: int
    port: int = 0
@dataclass    
class Peer:
    id: int
    ip: str = ""
    porta: int = 0
    banda: int = 0
    neighbours: list[PeerNeighbour] = None
    

def listen_udp(peer: Peer):
    """ Função para escutar mensagens UDP em um peer """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((peer.ip, peer.porta))

    while True:
        data, addr = sock.recvfrom(1024)  # Recebe mensagens de até 1024 bytes
        print(f"Peer {peer.id} recebeu mensagem de {addr}: {data.decode()}")
        
        # Lógica para processar a mensagem recebida, uma solicitação de arquivo ou a retransmissão da mensagem para os vizinhos


def send_message_to_neighbors(peer: Peer, peers: list[Peer], message: str, ttl: int):
    """ Função para enviar mensagem de descoberta para os vizinhos """
    if ttl <= 0:
        return  

    neighbors = peer.neighbours
    for neighbor in neighbors:
        neighbor = peers[neighbor.id]
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        msg_with_ttl = f"{message} (TTL: {ttl})"
        sock.sendto(msg_with_ttl.encode(), (neighbor.ip, neighbor.porta))
        print(f"Peer {peer.id} enviou mensagem para Peer {neighbor.id}: {msg_with_ttl}")
        sock.close()

def main():
    file = open("exemplo/topologia.txt", "r")
    peers = []
    for line in file:
        new_line = line.strip().split(':')
        peer_id = int(new_line[0].strip())
        neighbours = new_line[1].strip().split(',')
        peer = Peer(peer_id)
        peer.neighbours = [PeerNeighbour(int(i.strip())) for i in neighbours]
        peers.append(peer)
    file.close()
    config = open("exemplo/config.txt", "r")
    for line in config:
        new_line = line.strip().split(':')
        peer_id = int(new_line[0].strip())
        peer = peers[peer_id]
        data = new_line[1].strip().split(',')
        peer.ip = data[0].strip()
        peer.porta = int(data[1].strip())
        peer.banda = int(data[2].strip())
    for peer in peers:
        for neighbour in peer.neighbours:
            neighbour.port = peers[neighbour.id].porta
    config.close()
    time.sleep(1) 
    peer_zero = peers[0]
    send_message_to_neighbors(peer_zero, peers, "Buscando arquivo 'example.txt'", ttl=3)
if __name__ == "__main__":
    main()

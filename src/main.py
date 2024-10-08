import socket
import threading
import time
from dataclasses import dataclass

@dataclass
class Vertex:
    id: int
    ip: str = ""
    porta: int = 0
    banda: int = 0

class Graph:
    def __init__(self):
        self._adjacency_list = {}
        self._vertices = {}

    def add_vertex(self, vertex: Vertex):
        if vertex.id not in self._adjacency_list:
            self._adjacency_list[vertex.id] = []
            self._vertices[vertex.id] = vertex

    def add_edge(self, u_id: int, v_id: int):
        if v_id not in self._adjacency_list[u_id]:
            self._adjacency_list[u_id].append(v_id)
        if u_id not in self._adjacency_list[v_id]:
            self._adjacency_list[v_id].append(u_id)

    def get_vertex(self, id: int):
        return self._vertices.get(id, None)

    def get_neighbors(self, id: int):
        return self._adjacency_list.get(id, [])

    def __str__(self):
        graph_str = ""
        for vertex_id, neighbors in self._adjacency_list.items():
            vertex_info = self._vertices[vertex_id]
            neighbors_info = [self._vertices[n] for n in neighbors]
            graph_str += f"{vertex_info} -> {neighbors_info}\n"
        return graph_str

def listen_udp(vertex: Vertex, graph: Graph):
    """ Função para escutar mensagens UDP em um peer """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((vertex.ip, vertex.porta))

    while True:
        data, addr = sock.recvfrom(1024)  # Recebe mensagens de até 1024 bytes
        print(f"Peer {vertex.id} recebeu mensagem de {addr}: {data.decode()}")
        
        # Lógica para processar a mensagem recebida, uma solicitação de arquivo ou a retransmissão da mensagem para os vizinhos


def send_message_to_neighbors(graph: Graph, vertex: Vertex, message: str, ttl: int):
    """ Função para enviar mensagem de descoberta para os vizinhos """
    if ttl <= 0:
        return  

    neighbors = graph.get_neighbors(vertex.id)
    for neighbor_id in neighbors:
        neighbor = graph.get_vertex(neighbor_id)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        msg_with_ttl = f"{message} (TTL: {ttl})"
        sock.sendto(msg_with_ttl.encode(), (neighbor.ip, neighbor.porta))
        print(f"Peer {vertex.id} enviou mensagem para Peer {neighbor.id}: {msg_with_ttl}")
        sock.close()

def main():
    graph = Graph()

    # Configuração dos Peers
    file = open("exemplo/topologia.txt", "r")
    for line in file:
        new_line = line.strip().split(':')
        vertex_id = int(new_line[0].strip())
        edges = new_line[1].strip().split(',')

        if vertex_id not in graph._vertices:
            vertex = Vertex(id=vertex_id)
            graph.add_vertex(vertex)

        for edge in edges:
            neighbor_id = int(edge.strip())
            if neighbor_id not in graph._vertices:
                neighbor_vertex = Vertex(id=neighbor_id)
                graph.add_vertex(neighbor_vertex)
            graph.add_edge(vertex_id, neighbor_id)
    file.close()

    # Carregar IPs e Portas
    config = open("exemplo/config.txt", "r")
    for line in config:
        new_line = line.strip().split(' ')
        vertex_id = int(new_line[0].replace(":", ""))
        vertex = graph.get_vertex(vertex_id)
        vertex.ip = new_line[1].replace(",", "")
        vertex.porta = int(new_line[2].replace(",", ""))
        vertex.banda = int(new_line[3].replace(",", ""))
    config.close()

    print(graph)

    for vertex in graph._vertices.values():
        listen_thread = threading.Thread(target=listen_udp, args=(vertex, graph))
        listen_thread.daemon = True  # Permitir que a thread termine quando o programa terminar
        listen_thread.start()

    # Exemplo: enviar mensagem de descoberta de arquivo do peer 0
    time.sleep(1) 
    peer_zero = graph.get_vertex(0)
    send_message_to_neighbors(graph, peer_zero, "Buscando arquivo 'example.txt'", ttl=3)

if __name__ == "__main__":
    main()

from dataclasses import dataclass

@dataclass
class Vertex:
    id: int
    ip: str = ""
    porta: int = 0
    banda: int = 0

class Graph:
    def __init__(self):
        self.adjacency_list = {}
        self.vertices = {}

    def add_vertex(self, vertex: Vertex):
        if vertex.id not in self.adjacency_list:
            self.adjacency_list[vertex.id] = []
            self.vertices[vertex.id] = vertex

    def add_edge(self, u_id: int, v_id: int):
        # Verifica se a aresta já existe antes de adicionar
        if v_id not in self.adjacency_list[u_id]:
            self.adjacency_list[u_id].append(v_id)
        if u_id not in self.adjacency_list[v_id]:
            self.adjacency_list[v_id].append(u_id)

    def get_vertex(self, id: int):
        return self.vertices.get(id, None)

    def __str__(self):
        graph_str = ""
        for vertex_id, neighbors in self.adjacency_list.items():
            vertex_info = self.vertices[vertex_id]
            neighbors_info = [self.vertices[n] for n in neighbors]
            graph_str += f"{vertex_info} -> {neighbors_info}\n"
        return graph_str

if __name__ == "__main__":
    file = open("exemplo/topologia.txt", "r")
    graph = Graph()
    
    for line in file:
        new_line = line.strip().split(':')  # Separar pelo ':'
        vertex_id = int(new_line[0].strip())  # Capturar o ID do vértice
        edges = new_line[1].strip().split(',')  # Capturar as conexões e remover espaços
        
        # Criar o vértice (se não existir)
        if vertex_id not in graph.vertices:
            vertex = Vertex(id=vertex_id)
            graph.add_vertex(vertex)
        
        # Adicionar as arestas (conexões)
        for edge in edges:
            neighbor_id = int(edge.strip())  # Remover espaços e converter em int
            if neighbor_id not in graph.vertices:
                neighbor_vertex = Vertex(id=neighbor_id)
                graph.add_vertex(neighbor_vertex)
            graph.add_edge(vertex_id, neighbor_id)
    
    file.close()
    print(graph)
    print(graph.adjacency_list)

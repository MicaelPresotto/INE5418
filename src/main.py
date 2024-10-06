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

    def __str__(self):
        graph_str = ""
        for vertex_id, neighbors in self._adjacency_list.items():
            vertex_info = self._vertices[vertex_id]
            neighbors_info = [self._vertices[n] for n in neighbors]
            graph_str += f"{vertex_info} -> {neighbors_info}\n"
        return graph_str

if __name__ == "__main__":
    file = open("exemplo/topologia.txt", "r")
    graph = Graph()
    
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

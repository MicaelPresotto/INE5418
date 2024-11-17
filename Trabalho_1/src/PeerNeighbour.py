from dataclasses import dataclass

@dataclass
class PeerNeighbour:
    id: int
    port: int = 0
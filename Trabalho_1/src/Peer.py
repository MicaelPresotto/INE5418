from dataclasses import dataclass, field
from PeerNeighbour import PeerNeighbour

@dataclass    
class Peer:
    id: int
    ip: str = ""
    port: int = 0
    bandwidth: int = 0
    neighbours: list[PeerNeighbour] = field(default_factory=list)
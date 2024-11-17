import json
from Peer import Peer
from PeerNeighbour import PeerNeighbour


def load_peer_from_json(peer_id: int, filename: str) -> Peer:
    with open(filename, 'r') as json_file:
        peers_data = json.load(json_file)
        
    for peer_data in peers_data:
        if peer_data['id'] == peer_id:
            neighbours = [PeerNeighbour(id=neigh['id'], port=neigh['port']) for neigh in peer_data.get('neighbours', [])]
            return Peer(id=peer_data['id'], ip=peer_data['ip'], port=peer_data['port'], bandwidth=peer_data['bandwidth'], neighbours=neighbours)
    
    raise ValueError(f"Peer ID {peer_id} not found in the JSON file.")
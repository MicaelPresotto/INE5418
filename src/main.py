import time
import sys
from P2PNetwork import P2PNetwork
from utils import load_peer_from_json

def main():
    if len(sys.argv) != 2:
        print("Usage: python program.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])
    
    try:
        selected_peer = load_peer_from_json(peer_id, "peers.json")
    except ValueError as e:
        print(e)
        sys.exit(1)

    time.sleep(1)
    p2pNetwork = P2PNetwork(selected_peer)
    p2pNetwork.udp_connection(selected_peer)

if __name__ == "__main__":
    main()

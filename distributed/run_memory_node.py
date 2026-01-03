"""
Entry point for running a Memory Node
"""
import logging
import sys
from distributed.memory_node import MemoryNode
from distributed.node_discovery import NodeDiscovery

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("memory_node.log"),
            logging.StreamHandler()
        ]
    )

def main():
    configure_logging()
    
    # Parse arguments
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    orchestrator_addr = sys.argv[2] if len(sys.argv) > 2 else "localhost:8000"
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   Kamil v2 - Memory Node              ║
    ║   Persistent Cognition                ║
    ╚═══════════════════════════════════════╝
    
    Port: {port}
    """)
    
    # Start memory node
    memory_node = MemoryNode(port=port)
    
    # Register with orchestrator
    discovery = NodeDiscovery(orchestrator_addr)
    local_ip = NodeDiscovery.get_local_ip()
    discovery.register_node(
        node_type=memory_node.node_type,
        address=f"{local_ip}:{port}"
    )
    
    # Start server
    memory_node.start(threaded=False)

if __name__ == "__main__":
    main()


"""
Entry point for running a Tool Node
"""
import logging
import sys
from distributed.tool_node import ToolNode
from distributed.node_discovery import NodeDiscovery

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("tool_node.log"),
            logging.StreamHandler()
        ]
    )

def main():
    configure_logging()
    
    # Parse arguments
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    orchestrator_addr = sys.argv[2] if len(sys.argv) > 2 else "localhost:8000"
    available_tools = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   Kamil v2 - Tool Node               ║
    ║   Execution Layer                    ║
    ╚═══════════════════════════════════════╝
    
    Port: {port}
    Tools: {', '.join(available_tools) if available_tools else 'all'}
    """)
    
    # Start tool node
    tool_node = ToolNode(port=port, available_tools=available_tools)
    
    # Register with orchestrator
    discovery = NodeDiscovery(orchestrator_addr)
    local_ip = NodeDiscovery.get_local_ip()
    discovery.register_node(
        node_type=tool_node.node_type,
        address=f"{local_ip}:{port}",
        metadata={"available_tools": available_tools or "all"}
    )
    
    # Start server
    tool_node.start(threaded=False)

if __name__ == "__main__":
    main()


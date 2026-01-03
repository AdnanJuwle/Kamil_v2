"""
Entry point for running an LLM Node
"""
import logging
import sys
from distributed.llm_node import LLMNode
from distributed.node_discovery import NodeDiscovery

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("llm_node.log"),
            logging.StreamHandler()
        ]
    )

def main():
    configure_logging()
    
    # Parse arguments
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    model = sys.argv[2] if len(sys.argv) > 2 else "mistral:latest"
    orchestrator_addr = sys.argv[3] if len(sys.argv) > 3 else "localhost:8000"
    specializations = sys.argv[4].split(",") if len(sys.argv) > 4 else ["general"]
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   Kamil v2 - LLM Node                ║
    ║   Reasoning Engine                   ║
    ╚═══════════════════════════════════════╝
    
    Model: {model}
    Port: {port}
    Specializations: {', '.join(specializations)}
    """)
    
    # Start LLM node
    llm_node = LLMNode(port=port, model_name=model, specializations=specializations)
    
    # Register with orchestrator
    discovery = NodeDiscovery(orchestrator_addr)
    local_ip = NodeDiscovery.get_local_ip()
    discovery.register_node(
        node_type=llm_node.node_type,
        address=f"{local_ip}:{port}",
        specializations=specializations,
        metadata={"model": model}
    )
    
    # Start server
    llm_node.start(threaded=False)

if __name__ == "__main__":
    main()


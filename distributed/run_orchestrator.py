"""
Entry point for running the Orchestrator Node
"""
import logging
import sys
from distributed.orchestrator_node import OrchestratorNode

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("orchestrator.log"),
            logging.StreamHandler()
        ]
    )

def main():
    configure_logging()
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   Kamil v2 - Orchestrator Node       ║
    ║   Central Brain / Task Scheduler      ║
    ╚═══════════════════════════════════════╝
    
    Starting orchestrator on port {port}...
    """)
    
    orchestrator = OrchestratorNode(port=port)
    orchestrator.start(threaded=False)  # Run in main thread

if __name__ == "__main__":
    main()


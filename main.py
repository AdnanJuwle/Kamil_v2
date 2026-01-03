import logging
import sys
import time
from core.agent import KamilAgent
from interfaces.voice_interface import VoiceInterface
from interfaces.cli import CommandLineInterface

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("kamil_debug.log"),
            logging.StreamHandler()
        ]
    )

def main():
    print("""
    ██╗  ██╗ █████╗ ███╗   ███╗██╗██╗     
    ██║ ██╔╝██╔══██╗████╗ ████║██║██║     
    █████╔╝ ███████║██╔████╔██║██║██║     
    ██╔═██╗ ██╔══██║██║╚██╔╝██║██║██║     
    ██║  ██╗██║  ██║██║ ╚═╝ ██║██║███████╗
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚══════╝
    """)
    
    configure_logging()
    
    # Check for distributed mode
    mode = sys.argv[1] if len(sys.argv) > 1 else "monolithic"
    
    if mode == "distributed":
        # Distributed mode - connect to orchestrator
        orchestrator_addr = sys.argv[2] if len(sys.argv) > 2 else "localhost:8000"
        print(f"Distributed mode - connecting to orchestrator at {orchestrator_addr}")
        try:
            from distributed.distributed_agent import DistributedAgent
            agent = DistributedAgent(orchestrator_address=orchestrator_addr)
        except Exception as e:
            print(f"Error connecting to orchestrator: {e}")
            print("Make sure the orchestrator is running:")
            print("  python distributed/run_orchestrator.py")
            return
    else:
        # Monolithic mode (default)
        print("Monolithic mode - all components in single process")
        agent = KamilAgent()
    
    interface_type = input("Choose interface (voice/cli/web): ").strip().lower()
    
    if interface_type == "voice":
        voice = VoiceInterface()
        voice.voice_loop(agent)
    elif interface_type == "cli":
        cli = CommandLineInterface()
        cli.start(agent)
    elif interface_type == "web":
        from interfaces.web_ui import start_web_server
        server_thread = start_web_server(agent)
        
        # Keep main thread alive
        print("Web server running at http://localhost:5000")
        print("Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
    else:
        print("Invalid interface selected")

if __name__ == "__main__":
    main()

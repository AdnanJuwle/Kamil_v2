"""
Node Discovery and Registration System
Handles automatic discovery and registration of nodes on the local network.
"""
import logging
import socket
import uuid
from typing import Dict, Optional
from distributed.network import NodeClient
from distributed.protocol import NodeRegistration, NodeType, HardwareCapabilities


class NodeDiscovery:
    """
    Handles discovery and registration of nodes.
    Supports both manual registration and automatic discovery (future).
    """
    
    def __init__(self, orchestrator_address: str):
        self.orchestrator_address = orchestrator_address
        self.orchestrator_client = NodeClient(orchestrator_address)
        self.logger = logging.getLogger("NodeDiscovery")
    
    def register_node(self, node_type: NodeType, address: str,
                     specializations: list = None,
                     metadata: dict = None) -> bool:
        """
        Register a node with the orchestrator.
        
        Args:
            node_type: Type of node (LLM, Tool, Memory, etc.)
            address: Network address (host:port)
            specializations: List of specializations (e.g., ["coding", "math"])
            metadata: Additional metadata
        
        Returns:
            True if registration successful
        """
        node_id = str(uuid.uuid4())
        
        # Get hardware capabilities
        capabilities = self._detect_capabilities()
        
        registration = NodeRegistration(
            node_id=node_id,
            node_type=node_type,
            address=address,
            capabilities=capabilities,
            specializations=specializations or [],
            metadata=metadata or {}
        )
        
        success = self.orchestrator_client.register(registration)
        
        if success:
            self.logger.info(f"Successfully registered {node_type.value} node at {address}")
        else:
            self.logger.error(f"Failed to register {node_type.value} node at {address}")
        
        return success
    
    def _detect_capabilities(self) -> HardwareCapabilities:
        """Detect hardware capabilities of current machine"""
        import psutil
        
        cpu_cores = psutil.cpu_count()
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        # Try to detect GPU
        vram_gb = None
        accelerator_type = "cpu"
        
        try:
            import torch
            if torch.cuda.is_available():
                accelerator_type = "cuda"
                vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                accelerator_type = "mps"
        except ImportError:
            pass
        
        return HardwareCapabilities(
            cpu_cores=cpu_cores,
            ram_gb=ram_gb,
            vram_gb=vram_gb,
            accelerator_type=accelerator_type,
            current_load=psutil.cpu_percent() / 100.0,
            available=True
        )
    
    @staticmethod
    def get_local_ip() -> str:
        """Get local IP address"""
        try:
            # Connect to external address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


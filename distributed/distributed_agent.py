"""
Distributed Agent - Client interface for UI
Connects to orchestrator and provides same interface as monolithic agent
"""
import logging
from typing import Optional, List, Dict
from distributed.network import NodeClient
from distributed.protocol import TaskRequest


class DistributedAgent:
    """
    Client interface that connects to the distributed Kamil v2 system.
    Provides the same interface as the monolithic KamilAgent for backward compatibility.
    """
    
    def __init__(self, orchestrator_address: str = "localhost:8000"):
        self.orchestrator_address = orchestrator_address
        self.orchestrator_client = NodeClient(orchestrator_address)
        self.logger = logging.getLogger("DistributedAgent")
        
        # Verify connection
        if not self.orchestrator_client.health_check():
            raise ConnectionError(f"Cannot connect to orchestrator at {orchestrator_address}")
        
        self.logger.info(f"Connected to orchestrator at {orchestrator_address}")
    
    def process_request(self, user_input: str, context: Optional[List] = None, 
                       history: Optional[List] = None) -> str:
        """
        Process user request through the distributed system.
        Same interface as monolithic KamilAgent.
        """
        self.logger.info(f"Processing request: {user_input[:50]}...")
        
        try:
            # Send request directly to orchestrator (simpler format)
            import requests
            response = requests.post(
                f"http://{self.orchestrator_address}/task",
                json={
                    "user_input": user_input,
                    "context": context or [],
                    "history": history or []
                },
                timeout=300
            )
            response = response.json()
            
            # Handle response - response is now a dict from orchestrator
            if isinstance(response, dict):
                if response.get("status") == "completed":
                    result = response.get("result", {})
                    if isinstance(result, dict):
                        # Extract the final response
                        return result.get("response", str(result))
                    return str(result)
                else:
                    error_msg = response.get("error", "Unknown error")
                    return f"Error processing request: {error_msg}"
            else:
                # Fallback for TaskResponse format
                if hasattr(response, 'status') and response.status.value == "completed":
                    result = response.result
                    if isinstance(result, dict):
                        return result.get("response", str(result))
                    return str(result)
                else:
                    error_msg = getattr(response, 'error', None) or "Unknown error"
                    return f"Error processing request: {error_msg}"
        
        except Exception as e:
            self.logger.error(f"Request processing error: {e}")
            return f"Error: {str(e)}"
    
    def handle_file_command(self, user_input: str) -> str:
        """Handle file commands (for backward compatibility)"""
        # File commands are now handled through the orchestrator
        return self.process_request(user_input)
    
    def handle_safety_concern(self, user_input: str) -> str:
        """Handle safety concerns"""
        safety_resources = {
            "US": "National Suicide Prevention Lifeline: 1-800-273-8255",
            "UK": "Samaritans: 116 123",
            "Global": "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
        }
        
        resources = "\n".join([f"{k}: {v}" for k, v in safety_resources.items()])
        return f"I'm concerned about your safety. Please reach out for help:\n\n{resources}"


"""
Network communication layer for Kamil v2 distributed nodes.
Provides REST API for inter-node communication.
"""
import logging
import requests
import json
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify
from threading import Thread
from distributed.protocol import (
    NodeRegistration, TaskRequest, TaskResponse, 
    ReasoningRequest, ToolExecutionRequest, MemoryRequest,
    TaskStatus, NodeType
)


class NodeClient:
    """Client for communicating with remote nodes"""
    
    def __init__(self, node_address: str):
        self.address = node_address
        self.base_url = f"http://{node_address}"
        self.logger = logging.getLogger(f"NodeClient({node_address})")
    
    def health_check(self) -> bool:
        """Check if node is alive"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False
    
    def register(self, registration: NodeRegistration) -> bool:
        """Register this node with another node"""
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json=registration.to_dict(),
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
            return False
    
    def execute_task(self, task: TaskRequest) -> TaskResponse:
        """Send task execution request"""
        try:
            response = requests.post(
                f"{self.base_url}/task",
                json=task.to_dict(),
                timeout=300
            )
            data = response.json()
            return TaskResponse(
                task_id=data["task_id"],
                status=TaskStatus(data["status"]),
                result=data.get("result"),
                error=data.get("error"),
                metadata=data.get("metadata", {})
            )
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return TaskResponse(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    def reason(self, req: ReasoningRequest) -> str:
        """Request reasoning from LLM node"""
        try:
            response = requests.post(
                f"{self.base_url}/reason",
                json=req.to_dict(),
                timeout=300
            )
            data = response.json()
            if response.status_code == 200:
                return data.get("response", "")
            else:
                return f"Error: {data.get('error', 'Unknown error')}"
        except Exception as e:
            self.logger.error(f"Reasoning request failed: {e}")
            return f"Error: {str(e)}"
    
    def execute_tool(self, req: ToolExecutionRequest) -> Any:
        """Request tool execution from tool node"""
        try:
            response = requests.post(
                f"{self.base_url}/execute",
                json=req.to_dict(),
                timeout=60
            )
            data = response.json()
            if response.status_code == 200:
                return data.get("result")
            else:
                raise Exception(data.get("error", "Unknown error"))
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            raise
    
    def memory_operation(self, req: MemoryRequest) -> Any:
        """Request memory operation from memory node"""
        try:
            response = requests.post(
                f"{self.base_url}/memory",
                json=req.to_dict(),
                timeout=30
            )
            data = response.json()
            if response.status_code == 200:
                return data.get("result")
            else:
                raise Exception(data.get("error", "Unknown error"))
        except Exception as e:
            self.logger.error(f"Memory operation failed: {e}")
            raise


class NodeServer:
    """Base server for all node types"""
    
    def __init__(self, node_type: NodeType, port: int, host: str = "0.0.0.0"):
        self.node_type = node_type
        self.port = port
        self.host = host
        self.app = Flask(f"{node_type.value}_server")
        self.logger = logging.getLogger(f"NodeServer({node_type.value})")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup common routes for all nodes"""
        self.app.route("/health", methods=["GET"])(self.health)
        self.app.route("/register", methods=["POST"])(self.register)
        self.app.route("/capabilities", methods=["GET"])(self.get_capabilities)
    
    def health(self):
        """Health check endpoint"""
        return jsonify({"status": "healthy", "node_type": self.node_type.value})
    
    def register(self):
        """Handle node registration"""
        data = request.json
        # Subclasses should implement registration logic
        return jsonify({"status": "registered"})
    
    def get_capabilities(self):
        """Get node capabilities"""
        # Subclasses should implement
        return jsonify({"capabilities": {}})
    
    def start(self, threaded: bool = True):
        """Start the server"""
        if threaded:
            thread = Thread(target=self._run_server, daemon=True)
            thread.start()
            self.logger.info(f"{self.node_type.value} server started on {self.host}:{self.port}")
        else:
            self._run_server()
    
    def _run_server(self):
        """Run the Flask server"""
        self.app.run(host=self.host, port=self.port, debug=False)


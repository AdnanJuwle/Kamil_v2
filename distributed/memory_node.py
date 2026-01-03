"""
Memory Node - Persistent Cognition
Stores and retrieves memory. Read-only for LLMs, write-controlled by orchestrator.
"""
import logging
from typing import List, Dict, Any, Optional
from distributed.network import NodeServer
from distributed.protocol import NodeType, MemoryRequest, HardwareCapabilities
from flask import request, jsonify
from core.memory import VectorMemory


class MemoryNode(NodeServer):
    """
    Specialized node for persistent memory storage and retrieval.
    Uses tiered memory model: vector DB, knowledge graph, episodic logs.
    """
    
    def __init__(self, port: int = 8003, host: str = "0.0.0.0"):
        super().__init__(NodeType.MEMORY_NODE, port, host)
        
        # Initialize memory systems
        self.memory = VectorMemory()
        
        self.logger = logging.getLogger("MemoryNode")
        self._setup_memory_routes()
    
    def _setup_memory_routes(self):
        """Setup memory node routes"""
        self.app.route("/memory", methods=["POST"])(self.memory_operation)
        self.app.route("/memory/stats", methods=["GET"])(self.get_stats)
    
    def memory_operation(self):
        """Handle memory operation request"""
        data = request.json
        try:
            req = MemoryRequest(
                operation=data["operation"],
                key=data.get("key"),
                value=data.get("value"),
                query=data.get("query"),
                top_k=data.get("top_k", 5)
            )
            
            result = None
            
            if req.operation == "store":
                # Store interaction
                if isinstance(req.value, dict):
                    user_input = req.value.get("input", "")
                    output = req.value.get("output", "")
                else:
                    user_input = str(req.value)
                    output = ""
                
                self.memory.store_interaction(user_input, output)
                result = {"status": "stored", "key": req.key}
            
            elif req.operation == "retrieve":
                # Retrieve relevant memories
                if not req.query:
                    return jsonify({"error": "Query required for retrieve operation"}), 400
                
                memories = self.memory.retrieve_relevant(req.query, top_k=req.top_k)
                result = memories
            
            elif req.operation == "query":
                # Semantic query
                if not req.query:
                    return jsonify({"error": "Query required for query operation"}), 400
                
                memories = self.memory.retrieve_relevant(req.query, top_k=req.top_k)
                result = memories
            
            elif req.operation == "update":
                # Update existing memory (if key-based storage implemented)
                # For now, this is a placeholder
                result = {"status": "updated", "key": req.key}
            
            else:
                return jsonify({"error": f"Unknown operation: {req.operation}"}), 400
            
            self.logger.info(f"Memory operation '{req.operation}' completed")
            
            return jsonify({
                "result": result,
                "operation": req.operation
            })
        except Exception as e:
            self.logger.error(f"Memory operation error: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_stats(self):
        """Get memory node statistics"""
        # TODO: Implement actual stats from vector DB and knowledge graph
        return jsonify({
            "memory_items": 0,  # Placeholder
            "vector_db_size": 0,
            "knowledge_graph_nodes": 0
        })
    
    def get_capabilities(self):
        """Get memory node capabilities"""
        import psutil
        
        capabilities = HardwareCapabilities(
            cpu_cores=psutil.cpu_count(),
            ram_gb=psutil.virtual_memory().total / (1024**3),
            accelerator_type="cpu",  # Memory operations typically CPU-bound
            current_load=0.0,
            available=True
        )
        
        return jsonify({
            "node_type": "memory_node",
            "capabilities": capabilities.to_dict(),
            "memory_types": ["vector", "knowledge_graph", "episodic"]
        })


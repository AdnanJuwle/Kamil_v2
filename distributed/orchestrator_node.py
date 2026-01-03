"""
Orchestrator Node (Coordinator) - Central Brain
Responsible for task decomposition, routing, and scheduling.
Does NOT perform inference or store large memory blobs.
"""
import logging
import uuid
from typing import Dict, List, Optional, Any
from collections import defaultdict
from distributed.network import NodeServer, NodeClient
from distributed.protocol import (
    NodeType, NodeRegistration, TaskRequest, TaskResponse,
    ReasoningRequest, ToolExecutionRequest, MemoryRequest,
    TaskStatus, HardwareCapabilities
)
from flask import request, jsonify


class OrchestratorNode(NodeServer):
    """
    Central orchestrator that decomposes tasks and routes them to capability nodes.
    Think of it as a kernel scheduler for intelligence.
    """
    
    def __init__(self, port: int = 8000, host: str = "0.0.0.0"):
        super().__init__(NodeType.ORCHESTRATOR, port, host)
        self.registered_nodes: Dict[str, NodeRegistration] = {}
        self.node_clients: Dict[str, NodeClient] = {}
        self.active_tasks: Dict[str, TaskRequest] = {}
        self.task_results: Dict[str, TaskResponse] = {}
        self.logger = logging.getLogger("OrchestratorNode")
        self._setup_orchestrator_routes()
    
    def _setup_orchestrator_routes(self):
        """Setup orchestrator-specific routes"""
        self.app.route("/task", methods=["POST"])(self.handle_task)
        self.app.route("/nodes", methods=["GET"])(self.list_nodes)
        self.app.route("/task/<task_id>", methods=["GET"])(self.get_task_status)
    
    def register(self):
        """Register a capability node"""
        data = request.json
        try:
            registration = NodeRegistration(
                node_id=data["node_id"],
                node_type=NodeType(data["node_type"]),
                address=data["address"],
                capabilities=HardwareCapabilities(**data["capabilities"]),
                specializations=data.get("specializations", []),
                metadata=data.get("metadata", {})
            )
            
            self.registered_nodes[registration.node_id] = registration
            self.node_clients[registration.node_id] = NodeClient(registration.address)
            self.logger.info(f"Registered {registration.node_type.value} node: {registration.node_id} at {registration.address}")
            
            return jsonify({"status": "registered", "node_id": registration.node_id})
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return jsonify({"error": str(e)}), 400
    
    def list_nodes(self):
        """List all registered nodes"""
        nodes = [reg.to_dict() for reg in self.registered_nodes.values()]
        return jsonify({"nodes": nodes})
    
    def handle_task(self):
        """Handle incoming task request from UI or other nodes"""
        data = request.json
        
        # Support both direct requests and TaskRequest format
        if "payload" in data:
            # TaskRequest format
            payload = data.get("payload", {})
            user_input = payload.get("user_input", "")
            context = payload.get("context", [])
        else:
            # Direct format (for backward compatibility)
            user_input = data.get("user_input", "")
            context = data.get("context", [])
        
        # Generate task ID
        task_id = data.get("task_id") or str(uuid.uuid4())
        
        # Decompose task
        plan = self.decompose_task(user_input, context)
        
        # Execute plan
        result = self.execute_plan(plan, task_id)
        
        # Store result
        self.task_results[task_id] = TaskResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            result=result
        )
        
        return jsonify({
            "task_id": task_id,
            "status": "completed",
            "result": result
        })
    
    def decompose_task(self, user_input: str, context: List[Dict]) -> Dict[str, Any]:
        """
        Decompose user request into a dependency graph of sub-tasks.
        This is the core intelligence of the orchestrator.
        """
        # Step 1: Intent parsing
        intent = self._parse_intent(user_input)
        
        # Step 2: Determine required capabilities
        required_capabilities = self._determine_capabilities(intent)
        
        # Step 3: Create dependency graph
        steps = []
        
        # Memory retrieval step (if context needed)
        if not context:
            steps.append({
                "step_id": "memory_retrieve",
                "type": "memory_read",
                "node_type": NodeType.MEMORY_NODE,
                "payload": {"query": user_input, "top_k": 5}
            })
        
        # Reasoning step
        steps.append({
            "step_id": "reasoning",
            "type": "reasoning",
            "node_type": NodeType.LLM_NODE,
            "payload": {
                "prompt": user_input,
                "context": context
            },
            "depends_on": ["memory_retrieve"] if not context else []
        })
        
        # Tool execution steps (if needed)
        if self._requires_tools(intent):
            steps.append({
                "step_id": "tool_execution",
                "type": "execution",
                "node_type": NodeType.TOOL_NODE,
                "payload": {"intent": intent},
                "depends_on": ["reasoning"]
            })
        
        # Memory storage step
        steps.append({
            "step_id": "memory_store",
            "type": "memory_write",
            "node_type": NodeType.MEMORY_NODE,
            "payload": {"input": user_input},
            "depends_on": ["reasoning"]
        })
        
        return {
            "intent": intent,
            "steps": steps,
            "required_capabilities": required_capabilities
        }
    
    def _parse_intent(self, user_input: str) -> str:
        """Parse user intent to determine task type"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["code", "write", "create", "build", "script", "function"]):
            return "coding"
        elif any(word in user_input_lower for word in ["search", "find", "research", "look up", "what is"]):
            return "research"
        elif any(word in user_input_lower for word in ["file", "read", "write", "delete", "list"]):
            return "file_operation"
        elif any(word in user_input_lower for word in ["train", "model", "ml", "machine learning"]):
            return "ml_training"
        else:
            return "general"
    
    def _determine_capabilities(self, intent: str) -> List[str]:
        """Determine required hardware capabilities for intent"""
        capabilities = []
        
        if intent == "ml_training":
            capabilities.extend(["gpu", "high_memory"])
        elif intent == "coding":
            capabilities.extend(["cpu", "medium_memory"])
        elif intent == "research":
            capabilities.extend(["cpu", "network"])
        
        return capabilities
    
    def _requires_tools(self, intent: str) -> bool:
        """Check if intent requires tool execution"""
        return intent in ["coding", "file_operation", "ml_training", "automation"]
    
    def execute_plan(self, plan: Dict[str, Any], task_id: str) -> Any:
        """
        Execute the decomposed plan by routing tasks to appropriate nodes.
        Handles dependency resolution and parallelization.
        """
        steps = plan["steps"]
        step_results = {}
        
        # Build dependency graph
        step_dependencies = {step["step_id"]: step.get("depends_on", []) for step in steps}
        
        # Execute steps in dependency order
        completed_steps = set()
        
        while len(completed_steps) < len(steps):
            # Find steps ready to execute (dependencies satisfied)
            ready_steps = [
                step for step in steps
                if step["step_id"] not in completed_steps
                and all(dep in completed_steps for dep in step.get("depends_on", []))
            ]
            
            if not ready_steps:
                self.logger.error("Circular dependency or missing dependencies detected")
                break
            
            # Execute ready steps (can be parallelized)
            for step in ready_steps:
                result = self._execute_step(step, step_results)
                step_results[step["step_id"]] = result
                completed_steps.add(step["step_id"])
        
        # Return final result (usually from reasoning step)
        final_result = step_results.get("reasoning", "")
        if not final_result:
            # Fallback to any available result
            final_result = next(iter(step_results.values()), "Task completed")
        
        return {
            "response": final_result,
            "steps_completed": len(completed_steps),
            "step_results": step_results
        }
    
    def _execute_step(self, step: Dict[str, Any], previous_results: Dict[str, Any]) -> Any:
        """Execute a single step by routing to appropriate node"""
        node_type = step["node_type"]
        payload = step["payload"]
        
        # Select best node for this step
        node_id = self._select_node(node_type, step.get("specialization"))
        
        if not node_id:
            raise Exception(f"No available {node_type.value} node")
        
        client = self.node_clients[node_id]
        
        # Route based on step type
        if step["type"] == "reasoning":
            req = ReasoningRequest(**payload)
            return client.reason(req)
        
        elif step["type"] == "execution":
            # Extract tool info from reasoning result if available
            tool_req = ToolExecutionRequest(
                tool_name=payload.get("tool_name", "unknown"),
                action=payload.get("action", "execute"),
                parameters=payload.get("parameters", {})
            )
            return client.execute_tool(tool_req)
        
        elif step["type"] == "memory_read":
            req = MemoryRequest(
                operation="retrieve",
                query=payload.get("query"),
                top_k=payload.get("top_k", 5)
            )
            return client.memory_operation(req)
        
        elif step["type"] == "memory_write":
            req = MemoryRequest(
                operation="store",
                value=payload
            )
            return client.memory_operation(req)
        
        else:
            raise Exception(f"Unknown step type: {step['type']}")
    
    def _select_node(self, node_type: NodeType, specialization: Optional[str] = None) -> Optional[str]:
        """
        Select the best node for a task based on:
        - Hardware capabilities
        - Current load
        - Specialization match
        - Availability
        """
        candidates = [
            (node_id, reg) for node_id, reg in self.registered_nodes.items()
            if reg.node_type == node_type and reg.capabilities.available
        ]
        
        if not candidates:
            return None
        
        # Filter by specialization if specified
        if specialization:
            candidates = [
                (node_id, reg) for node_id, reg in candidates
                if specialization in reg.specializations
            ]
        
        # Select node with lowest load
        best_node = min(candidates, key=lambda x: x[1].capabilities.current_load)
        return best_node[0]
    
    def get_task_status(self, task_id: str):
        """Get status of a task"""
        if task_id in self.task_results:
            return jsonify(self.task_results[task_id].to_dict())
        elif task_id in self.active_tasks:
            return jsonify({"status": "in_progress"})
        else:
            return jsonify({"error": "Task not found"}), 404
    
    def get_capabilities(self):
        """Orchestrator capabilities (minimal - it's just a scheduler)"""
        return jsonify({
            "node_type": "orchestrator",
            "capabilities": {
                "task_decomposition": True,
                "routing": True,
                "scheduling": True,
                "hardware_aware": True
            }
        })


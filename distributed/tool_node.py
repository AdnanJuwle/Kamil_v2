"""
Tool Node - Execution Layer
Executes actions with validation, sandboxing, and permission checks.
LLMs never execute tools directly - all actions go through tool nodes.
"""
import logging
from typing import Dict, Any, List
from distributed.network import NodeServer
from distributed.protocol import NodeType, ToolExecutionRequest, HardwareCapabilities
from flask import request, jsonify
from tools.tool_registry import ToolRegistry
from core.security import SecurityManager


class ToolNode(NodeServer):
    """
    Specialized node for tool execution.
    Provides validation, sandboxing, and permission checks.
    """
    
    def __init__(self, port: int = 8002, host: str = "0.0.0.0",
                 available_tools: List[str] = None):
        super().__init__(NodeType.TOOL_NODE, port, host)
        self.available_tools = available_tools or ["file_ops", "code_tools", "web_tools", "automation"]
        
        # Initialize tool registry (no LLM engine needed - tools are stateless executors)
        self.tool_registry = ToolRegistry(llm_engine=None)
        
        # Security manager for validation
        self.security = SecurityManager()
        
        self.logger = logging.getLogger("ToolNode")
        self._setup_tool_routes()
    
    def _setup_tool_routes(self):
        """Setup tool node routes"""
        self.app.route("/execute", methods=["POST"])(self.execute)
        self.app.route("/tools", methods=["GET"])(self.list_tools)
    
    def execute(self):
        """Handle tool execution request"""
        data = request.json
        try:
            req = ToolExecutionRequest(
                tool_name=data["tool_name"],
                action=data["action"],
                parameters=data.get("parameters", {}),
                validation_required=data.get("validation_required", True),
                sandboxed=data.get("sandboxed", True)
            )
            
            # Validate request
            if req.validation_required:
                self._validate_request(req)
            
            # Get tool
            tool = self.tool_registry.get_tool(req.tool_name)
            if not tool:
                raise Exception(f"Tool '{req.tool_name}' not available")
            
            # Execute with sandboxing if required
            if req.sandboxed:
                result = self._execute_sandboxed(tool, req.action, req.parameters)
            else:
                result = tool.execute(req.action, **req.parameters)
            
            self.logger.info(f"Executed {req.tool_name}.{req.action}")
            
            return jsonify({
                "result": result,
                "tool": req.tool_name,
                "action": req.action
            })
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}")
            return jsonify({"error": str(e)}), 500
    
    def _validate_request(self, req: ToolExecutionRequest):
        """Validate tool execution request"""
        # Check if tool is available
        if req.tool_name not in self.available_tools:
            raise Exception(f"Tool '{req.tool_name}' not available on this node")
        
        # Validate parameters based on tool type
        if req.tool_name == "file_ops":
            if "filename" in req.parameters:
                # Sanitize filename
                req.parameters["filename"] = self.security.sanitize_filename(
                    req.parameters["filename"]
                )
        
        # Additional validation can be added here
        # (e.g., path traversal checks, permission checks, etc.)
    
    def _execute_sandboxed(self, tool, action: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute tool in a sandboxed environment.
        For now, this is a placeholder - full sandboxing would require
        containerization or process isolation.
        """
        # TODO: Implement actual sandboxing (Docker, chroot, etc.)
        # For now, just execute normally but log for audit
        self.logger.info(f"Sandboxed execution: {tool.__class__.__name__}.{action}")
        return tool.execute(action, **parameters)
    
    def list_tools(self):
        """List available tools on this node"""
        return jsonify({
            "available_tools": self.available_tools,
            "tools": list(self.tool_registry.tools.keys())
        })
    
    def get_capabilities(self):
        """Get tool node capabilities"""
        import psutil
        
        capabilities = HardwareCapabilities(
            cpu_cores=psutil.cpu_count(),
            ram_gb=psutil.virtual_memory().total / (1024**3),
            accelerator_type="cpu",  # Tools typically don't need GPU
            current_load=0.0,
            available=True
        )
        
        return jsonify({
            "node_type": "tool_node",
            "available_tools": self.available_tools,
            "capabilities": capabilities.to_dict()
        })


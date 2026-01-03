"""
LLM Node - Stateless Reasoning Engine
Performs inference but does NOT execute tools or write memory directly.
"""
import logging
from typing import Optional, List, Dict
from distributed.network import NodeServer, NodeClient
from distributed.protocol import NodeType, ReasoningRequest, HardwareCapabilities
from flask import request, jsonify
from core.llm_engine import LLMEngine


class LLMNode(NodeServer):
    """
    Specialized node for LLM reasoning.
    Stateless by default - receives task slice, produces output, returns.
    """
    
    def __init__(self, port: int = 8001, host: str = "0.0.0.0", 
                 model_name: str = "mistral:latest",
                 specializations: List[str] = None):
        super().__init__(NodeType.LLM_NODE, port, host)
        self.model_name = model_name
        self.specializations = specializations or ["general"]
        
        # LLM engine (stateless - no memory or tools)
        self.llm_engine = LLMEngine(memory=None, tools={})
        # Don't start background processing for distributed node
        # (requests come via HTTP, not queue)
        
        self.logger = logging.getLogger(f"LLMNode({model_name})")
        self._setup_llm_routes()
    
    def _setup_llm_routes(self):
        """Setup LLM node routes"""
        self.app.route("/reason", methods=["POST"])(self.reason)
    
    def reason(self):
        """Handle reasoning request"""
        data = request.json
        try:
            req = ReasoningRequest(
                prompt=data["prompt"],
                context=data.get("context", []),
                max_tokens=data.get("max_tokens", 1024),
                model_preference=data.get("model_preference"),
                temperature=data.get("temperature", 0.7)
            )
            
            # Build prompt with context
            full_prompt = self._build_prompt(req.prompt, req.context)
            
            # Generate response
            response = self.llm_engine.generate(
                full_prompt,
                context=req.context,
                max_tokens=req.max_tokens
            )
            
            self.logger.info(f"Generated response for prompt: {req.prompt[:50]}...")
            
            return jsonify({
                "response": response,
                "model": self.model_name,
                "specializations": self.specializations
            })
        except Exception as e:
            self.logger.error(f"Reasoning error: {e}")
            return jsonify({"error": str(e)}), 500
    
    def _build_prompt(self, prompt: str, context: List[Dict]) -> str:
        """Build prompt with context"""
        if not context:
            return prompt
        
        context_str = "\n".join([
            f"Input: {c.get('input', '')}\nOutput: {c.get('output', '')}"
            for c in context if isinstance(c, dict)
        ])
        
        if not context_str:
            return prompt
        
        return f"""Context from memory:
{context_str}

User request:
{prompt}

Please provide a helpful response based on the context and request above."""
    
    def get_capabilities(self):
        """Get LLM node capabilities"""
        import psutil
        
        # Detect hardware
        cpu_cores = psutil.cpu_count()
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        # Try to detect GPU/accelerator
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
        
        capabilities = HardwareCapabilities(
            cpu_cores=cpu_cores,
            ram_gb=ram_gb,
            vram_gb=vram_gb,
            accelerator_type=accelerator_type,
            current_load=0.0,  # TODO: Implement actual load tracking
            available=True
        )
        
        return jsonify({
            "node_type": "llm_node",
            "model": self.model_name,
            "specializations": self.specializations,
            "capabilities": capabilities.to_dict()
        })


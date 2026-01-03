"""
Communication protocol definitions for Kamil v2 distributed nodes.
Defines schemas for all inter-node communication.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class NodeType(Enum):
    """Types of nodes in the distributed system"""
    ORCHESTRATOR = "orchestrator"
    LLM_NODE = "llm_node"
    TOOL_NODE = "tool_node"
    MEMORY_NODE = "memory_node"
    UI_NODE = "ui_node"


class TaskStatus(Enum):
    """Status of a task execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class HardwareCapabilities:
    """Hardware capabilities advertised by a node"""
    cpu_cores: int
    ram_gb: float
    vram_gb: Optional[float] = None
    accelerator_type: Optional[str] = None  # "cuda", "mps", "cpu", etc.
    current_load: float = 0.0  # 0.0 to 1.0
    available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "vram_gb": self.vram_gb,
            "accelerator_type": self.accelerator_type,
            "current_load": self.current_load,
            "available": self.available
        }


@dataclass
class NodeRegistration:
    """Registration information for a node"""
    node_id: str
    node_type: NodeType
    address: str  # IP:port or hostname:port
    capabilities: HardwareCapabilities
    specializations: List[str]  # e.g., ["coding", "general", "math"]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "address": self.address,
            "capabilities": self.capabilities.to_dict(),
            "specializations": self.specializations,
            "metadata": self.metadata
        }


@dataclass
class TaskRequest:
    """Request for task execution"""
    task_id: str
    task_type: str  # "reasoning", "execution", "memory_read", "memory_write"
    payload: Dict[str, Any]
    dependencies: List[str] = None  # Task IDs this depends on
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "dependencies": self.dependencies or [],
            "priority": self.priority
        }


@dataclass
class TaskResponse:
    """Response from task execution"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata or {}
        }


@dataclass
class ReasoningRequest:
    """Request for LLM reasoning"""
    prompt: str
    context: Optional[List[Dict[str, str]]] = None
    max_tokens: int = 1024
    model_preference: Optional[str] = None
    temperature: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "context": self.context or [],
            "max_tokens": self.max_tokens,
            "model_preference": self.model_preference,
            "temperature": self.temperature
        }


@dataclass
class ToolExecutionRequest:
    """Request for tool execution"""
    tool_name: str
    action: str
    parameters: Dict[str, Any]
    validation_required: bool = True
    sandboxed: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "action": self.action,
            "parameters": self.parameters,
            "validation_required": self.validation_required,
            "sandboxed": self.sandboxed
        }


@dataclass
class MemoryRequest:
    """Request for memory operations"""
    operation: str  # "store", "retrieve", "query", "update"
    key: Optional[str] = None
    value: Optional[Any] = None
    query: Optional[str] = None
    top_k: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "key": self.key,
            "value": self.value,
            "query": self.query,
            "top_k": self.top_k
        }


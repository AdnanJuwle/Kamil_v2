import logging
from core.memory import VectorMemory
from core.model_manager import ModelPool
from core.task_orchestrator import TaskOrchestrator
from core.llm_engine import LLMEngine
from tools.tool_registry import ToolRegistry

SAFETY_KEYWORDS = [
    "kill myself", "suicide", "self-harm", 
    "end my life", "want to die"
]

class KamilAgent:
    def __init__(self):
        # Phase 1: Create basic components without dependencies
        self.memory = VectorMemory()
        self.logger = logging.getLogger("KamilAgent")
        
        # Phase 2: Create LLM engine (needs memory and will get tools later)
        self.llm_engine = LLMEngine(self.memory, {})
        
        # Phase 3: Create tool registry with reference to LLM engine
        self.tool_registry = ToolRegistry(self.llm_engine)
        
        # Phase 4: Update LLM engine with actual tools
        self.llm_engine.tools = self.tool_registry.tools
        
        # Phase 5: Create model pool with all dependencies
        self.model_pool = ModelPool(self.memory, self.tool_registry.tools)
        
        # Phase 6: Create task orchestrator
        self.task_orchestrator = TaskOrchestrator(self)
        
        # Set safety resources
        self.safety_resources = {
            "US": "National Suicide Prevention Lifeline: 1-800-273-8255",
            "UK": "Samaritans: 116 123",
            "Global": "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
        }
        
        # Start services
        self.llm_engine.start()
        self.logger.info("Agent initialized")

    def process_request(self, user_input, context=None, history=None):
        # Safety check
        if any(keyword in user_input.lower() for keyword in SAFETY_KEYWORDS):
            return self.handle_safety_concern(user_input)
        
        self.logger.info(f"Processing request: {user_input}")
        
        # Determine processing mode
        if self._is_conversational(user_input):
            return self.llm_engine.chat(user_input, history)
        else:
            return self.llm_engine.execute_task(user_input)
    
    def _is_conversational(self, user_input):
        """Determine if input is conversational or task-oriented"""
        conversational_keywords = [
            "hello", "hi", "hey", "how are you", "good morning", "good afternoon",
            "thank you", "thanks", "please", "tell me about", "what is"
        ]
        return any(keyword in user_input.lower() for keyword in conversational_keywords)
    
    def handle_safety_concern(self, user_input):
        self.logger.warning(f"Safety concern detected: {user_input}")
        return (
            "I'm really sorry you're feeling this way. "
            "Please reach out to a mental health professional: "
            f"{self.safety_resources['US']}, {self.safety_resources['UK']}, "
            f"or {self.safety_resources['Global']}. You're not alone."
        )

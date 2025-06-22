import logging
import re
from core.memory import VectorMemory
from core.model_manager import ModelPool
from core.task_orchestrator import TaskOrchestrator
from core.llm_engine import LLMEngine
from tools.tool_registry import ToolRegistry
SAFETY_KEYWORDS = [
    "kill myself", "suicide", "self-harm", 
    "end my life", "want to die"
]

FILE_COMMANDS = [
    "create file", "read file", "open file", "edit file", "modify file",
    "delete file", "execute file", "run file", "list files", "show files"
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
    def is_smalltalk(self, text):
        greetings = ["hello", "hi", "hey", "how are you", "what's up", "yo", "sup", "good morning", "good evening"]
        text = text.lower()
        return any(greet in text for greet in greetings) or len(text.split()) <= 3

    def process_request(self, user_input, context=None, history=None):
        # Handle file commands directly
        if any(cmd in user_input.lower() for cmd in FILE_COMMANDS):
            return self.handle_file_command(user_input)
        
        # Safety check
        if any(keyword in user_input.lower() for keyword in SAFETY_KEYWORDS):
            return self.handle_safety_concern(user_input)
        
        self.logger.info(f"Processing request: {user_input}")
        
        # Retrieve relevant memory
        context = self.memory.retrieve_relevant(user_input, top_k=3)
        
                # Decide if this is just a casual chat
        if self.is_smalltalk(user_input):
            return self.llm_engine.chat(user_input, history)

        # Otherwise, it's a task
        task_type = self.task_orchestrator.classify_task(user_input)
        specialist = self.model_pool.get_specialist(task_type)
        plan = specialist.generate_plan(user_input, context)
        self.logger.info(f"Generated plan: {plan}")
        results = self.task_orchestrator.execute_plan(plan, user_input)

        
        # Update memory
        self.memory.store_interaction(user_input, results)
        
        # Format final response
        if task_type == "research":
            return self.format_search_results(results.get('web_search', 'No results found'))
        elif task_type == "coding":
            return results.get('show_code', 'Code generated successfully')
        else:
            return "\n".join([f"{k}: {v}" for k, v in results.items()])
    
    def format_search_results(self, raw_results):
        """Convert raw search results to readable format"""
        if not raw_results:
            return "No results found"
        
        # Format as bullet points
        formatted = []
        results = raw_results.split('\n\n')
        
        for i, result in enumerate(results[:3]):  # Show top 3 results
            if result.strip():
                formatted.append(f"{i+1}. {result.strip()}")
        
        return "\n\n".join(formatted)
    
    def handle_file_command(self, user_input):
        self.logger.info(f"Processing file command: {user_input}")
        
        # Extract filename and command
        command = None
        filename = None
        
        # Try to extract filename from command
        match = re.search(r'(\bcreate|\bread|\bopen|\bedit|\bmodify|\bdelete|\bexecute|\brun)\s+file\s+(.+)', user_input, re.IGNORECASE)
        if match:
            command = match.group(1).lower()
            filename = match.group(2).strip()
        else:
            # Fallback to listing files
            file_ops = self.tool_registry.get_tool('file_ops')
            files = file_ops.execute('list_files')
            file_list = "\n".join([f"- {f['name']} ({f['type']})" for f in files])
            return f"Available files:\n{file_list}"
        
        # Execute the command
        try:
            file_ops = self.tool_registry.get_tool('file_ops')
            if command in ['create', 'edit', 'modify']:
                # For create/edit, return a message to use the web UI
                return f"Please use the file editor in the web UI to {command} '{filename}'"
            elif command in ['read', 'open']:
                content = file_ops.execute('read_file', filename=filename)
                return f"Contents of {filename}:\n```\n{content}\n```"
            elif command in ['delete', 'remove']:
                return file_ops.execute('delete_file', filename=filename)
            elif command in ['execute', 'run']:
                result = file_ops.execute('execute_file', filename=filename)
                return f"Execution result for {filename}:\n```\n{result}\n```"
        except Exception as e:
            return f"Error processing file command: {str(e)}"

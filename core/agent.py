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
        # ... existing initialization ...
    
    def process_request(self, user_input, context=None, history=None):
        # Handle file commands directly
        if any(cmd in user_input.lower() for cmd in FILE_COMMANDS):
            return self.handle_file_command(user_input)
        
        # ... existing processing logic ...
    
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

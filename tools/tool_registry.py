import logging
from tools.file_ops import FileOperationsTool
from tools.code_tools import CodeTools
from tools.automation import AutomationEngine
from tools.web_tools import WebTools

class ToolRegistry:
    def __init__(self, llm_engine=None):
        self.tools = {}
        self.logger = logging.getLogger("ToolRegistry")
        self.llm_engine = llm_engine
        self._initialize_tools()
        
    def _initialize_tools(self):
        self.tools = {
            "file_ops": FileOperationsTool(),
            "code_tools": CodeTools(self.llm_engine),
            "automation": AutomationEngine(),
            "web_tools": WebTools(self.llm_engine)
        }
        self.logger.info("Tool registry initialized")

    def get_tool(self, tool_name):
        return self.tools.get(tool_name)

    def register_tool(self, name, tool):
        self.tools[name] = tool
        self.logger.info(f"Registered new tool: {name}")

import logging
import re

class TaskOrchestrator:
    def __init__(self, agent):
        self.agent = agent
        self.logger = logging.getLogger("TaskOrchestrator")

    def classify_task(self, user_input):
        user_input = user_input.lower()
        if any(w in user_input for w in ["how to", "tutorial", "what is", "explain", "research"]):
            return "research"
        elif any(w in user_input for w in ["create", "build", "make", "write", "generate", 
                                          "code", "script", "function", "program", "calculator"]):
            return "coding"
        elif any(w in user_input for w in ["automate", "schedule", "workflow", "routine"]):
            return "automation"
        return "research"

    def execute_plan(self, plan, user_input):
        results = {}
        self.logger.info(f"Executing plan with {len(plan['steps'])} steps")
        
        for step in plan['steps']:
            tool_name = step['tool']
            action = step['action']
            
            tool = self.agent.tool_registry.get_tool(tool_name)
            if tool:
                try:
                    # Determine parameters based on action
                    params = {}
                    if action == "web_search":
                        params = {'query': user_input}
                    elif action == "fetch_url":
                        params = {'url': 'https://example.com'}
                    elif action == "generate_code":
                        params = {'specification': user_input}
                    elif action == "show_code":
                        # Use generated code from previous step
                        params = {'code': results.get('generate_code', '')}
                    
                    # Execute the tool with parameters
                    result = tool.execute(action, **params)
                    results[action] = result
                    self.logger.info(f"Step '{action}' completed")
                except Exception as e:
                    self.logger.error(f"Error in step {action}: {str(e)}")
                    results[action] = f"Error: {str(e)}"
            else:
                self.logger.warning(f"Tool not found: {tool_name}")
                results[action] = "Tool not available"
        
        return results

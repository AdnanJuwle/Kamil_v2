import subprocess
import logging

class CodeTools:
    def __init__(self, llm_engine=None):
        self.logger = logging.getLogger("CodeTools")
        self.llm_engine = llm_engine
        self.logger.info("Code tools initialized" + (" with LLM engine" if llm_engine else ""))
    def execute(self, action, **kwargs):
        if action == "generate_code":
            return self.generate_code(kwargs['specification'])
        elif action == "execute_script":
            return self.execute_script(kwargs['filename'])
        elif action == "debug_code":
            return self.debug_code(kwargs['code'], kwargs['error'])
        elif action == "show_code":
            return self.format_code(kwargs['code'])
        else:
            raise ValueError(f"Unknown action: {action}")

    def generate_code(self, specification):
        self.logger.info(f"Generating code for: {specification[:50]}...")
        
        prompt = f"""<|system|>
You are an expert Python developer. Create code for: "{specification}"

Requirements:
1. Include complete, runnable code
2. Add comments for complex sections
3. Include example usage
4. Handle common errors
</s>
<|assistant|>
```python
"""
        
        return self.llm_engine.generate(prompt)

    def execute_script(self, filename):
        try:
            result = subprocess.run(
                ["python", filename],
                capture_output=True,
                text=True,
                timeout=30
            )
            self.logger.info(f"Executed script: {filename}")
            output = result.stdout or result.stderr or "No output"
            
            # Analyze output with LLM
            prompt = f"""<|system|>
Explain the output of the program:
{output}
</s>
<|assistant|>
Explanation:"""
            
            return self.llm_engine.generate(prompt)
        except Exception as e:
            return f"Error: {str(e)}"

    def debug_code(self, code, error):
        self.logger.info(f"Debugging code with error: {error[:50]}...")
        
        prompt = f"""<|system|>
Debug this Python code that produces the error: "{error}"

Code:
{code}

Provide:
1. Explanation of the error
2. Fixed code
</s>
<|assistant|>
"""
        return self.llm_engine.generate(prompt)

    def format_code(self, code):
        return f"```python\n{code}\n```"

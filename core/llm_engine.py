import logging
import subprocess
import json
import threading
import time
from queue import Queue
from config import MODEL_NAME, TIMEOUT_SECONDS
from utils.helpers import clean_code

class LLMEngine:
    def __init__(self, memory, tools):
        self.memory = memory
        self.tools = tools
        self.logger = logging.getLogger("LLMEngine")
        self.model_name = MODEL_NAME
        self.fast_model = "mistral:7b-instruct"  # Faster model for simple queries
        self.timeout = TIMEOUT_SECONDS
        self.response_queue = Queue()
        self.is_running = False
        self.logger.info(f"LLM Engine initialized with model: {MODEL_NAME}")
        
        if not tools:
            self.logger.warning("Tools registry not provided at initialization")

    def start(self):
        self.is_running = True
        threading.Thread(target=self._process_requests, daemon=True).start()
        self.logger.info("LLM Engine started")

    def stop(self):
        self.is_running = False
        self.logger.info("LLM Engine stopped")

    def generate(self, prompt, context=None, max_tokens=1024):
        """Generate response from LLM with optimizations"""
        full_prompt = self._build_prompt(prompt, context)
        self.logger.debug(f"Sending prompt: {full_prompt[:100]}...")
        
        # Optimize model selection
        model_to_use = self._select_model(full_prompt)
        
        # Truncate very long prompts
        if len(full_prompt) > 4000:
            full_prompt = full_prompt[:2000] + " [...] " + full_prompt[-2000:]
            self.logger.info("Truncated long prompt")
        
        try:
            result = subprocess.run(
                ["ollama", "run", model_to_use, full_prompt],
                capture_output=True,
                text=True,
                timeout=15 if model_to_use == self.fast_model else self.timeout
            )
            output = clean_code(result.stdout.strip())
            self.logger.debug(f"Received response: {output[:100]}...")
            return output
        except subprocess.TimeoutExpired:
            self.logger.warning("LLM generation timed out")
            return "I need more time to think about that. Could you clarify?"
        except Exception as e:
            self.logger.error(f"LLM generation error: {str(e)}")
            return "I encountered an error processing your request."

    def _select_model(self, prompt):
        """Choose the appropriate model based on prompt complexity"""
        # Use fast model for short, simple prompts
        if len(prompt) < 150 and "?" not in prompt:
            self.logger.info("Using fast model for simple query")
            return self.fast_model
        return self.model_name

    def chat(self, user_input, history=None):
        """Generate conversational response"""
        context = self._build_chat_context(user_input, history)
        prompt = f"""<|system|>
You are Kamil, an advanced AI assistant. Respond helpfully and concisely.
Use available tools when appropriate. Maintain natural conversation flow.
Current time: {time.strftime("%Y-%m-%d %H:%M")}
Context: {context}
</s>
<|user|>
{user_input}
</s>
<|assistant|>"""
        return self.generate(prompt, max_tokens=512)

    def execute_task(self, user_input):
        """Generate and execute task-based response"""
        context = self.memory.retrieve_relevant(user_input, top_k=3)
        context_str = "\n".join([f"- {c['input']}: {c['output']}" for c in context])
        
        prompt = f"""<|system|>
You are a task execution AI. Given the user request and context, generate a plan and execute it.
Available tools: {", ".join(self.tools.keys())}
Context:
{context_str}
</s>
<|user|>
{user_input}
</s>
<|assistant|>
Plan:"""
        
        plan = self.generate(prompt, max_tokens=256)
        self.logger.info(f"Generated plan: {plan}")
        return self._execute_plan(plan, user_input)

    def _build_prompt(self, prompt, context=None):
        """Build enhanced prompt with context"""
        base_prompt = f"""<|system|>
You are Kamil, an advanced AI assistant. You have access to tools and memory.
Current time: {time.strftime("%Y-%m-%d %H:%M")}
</s>"""
        
        if context:
            context_str = "\n".join([f"- {c['input']}: {c['output']}" for c in context])
            base_prompt += f"\n<|context|>\n{context_str}\n</s>"
        
        base_prompt += f"\n<|user|>\n{prompt}\n</s>\n<|assistant|>"
        return base_prompt

    def _build_chat_context(self, user_input, history):
        """Build context for conversational responses"""
        context = self.memory.retrieve_relevant(user_input, top_k=3)
        context_str = "\n".join([f"- {c['input']}: {c['output']}" for c in context])
        
        history_str = ""
        if history:
            for i, (user, assistant) in enumerate(history[-3:]):
                history_str += f"Turn {i+1}:\nUser: {user}\nAssistant: {assistant}\n"
        
        return f"Recent history:\n{history_str}\nRelevant memories:\n{context_str}"

    def _execute_plan(self, plan, user_input):
        """Parse and execute the generated plan"""
        try:
            # Extract tool calls from plan
            if "Tool:" in plan:
                tool_section = plan.split("Tool:")[1].split("\n")[0].strip()
                tool_name, action = tool_section.split("->")
                tool = self.tools.get(tool_name.strip())
                
                if tool:
                    # Execute tool
                    result = tool.execute(action.strip(), **{"query": user_input})
                    self.logger.info(f"Tool executed: {tool_name}->{action}")
                    return result
            
            # If no tool specified, use conversational response
            return self.chat(user_input)
        except Exception as e:
            self.logger.error(f"Plan execution error: {str(e)}")
            return self.chat(user_input)

    def _process_requests(self):
        """Background processing of queued requests"""
        while self.is_running:
            if not self.response_queue.empty():
                request = self.response_queue.get()
                response = self.generate(request['prompt'], request.get('context'))
                if request.get('callback'):
                    request['callback'](response)
            time.sleep(0.1)

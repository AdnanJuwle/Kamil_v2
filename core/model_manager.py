import logging
from core.llm_engine import LLMEngine

class ModelPool:
    def __init__(self, memory, tools):
        self.llm_engine = LLMEngine(memory, tools)
        self.specialists = {
            "coding": CodingSpecialist(self.llm_engine),
            "research": ResearchSpecialist(self.llm_engine),
            "automation": AutomationSpecialist(self.llm_engine),
            "chat": ChatSpecialist(self.llm_engine)
        }
        self.logger = logging.getLogger("ModelPool")
        self.logger.info("Model pool initialized with specialists")

    def get_specialist(self, task_type):
        return self.specialists.get(task_type, self.specialists["chat"])

class SpecialistBase:
    def __init__(self, llm_engine):
        self.llm_engine = llm_engine

    def generate_plan(self, user_input, context):
        raise NotImplementedError

class CodingSpecialist(SpecialistBase):
    def generate_plan(self, user_input, context):
        prompt = f"""<|system|>
You are a coding specialist AI. Given the user request:
"{user_input}"

Generate a plan to create the requested code solution.
</s>
<|assistant|>
Plan:"""
        
        plan = self.llm_engine.generate(prompt)
        return {
            "task": "coding",
            "steps": [
                {"action": "generate_code", "tool": "code_tools"},
                {"action": "show_code", "tool": "code_tools"}
            ]
        }

class ResearchSpecialist(SpecialistBase):
    def generate_plan(self, user_input, context):
        prompt = f"""<|system|>
You are a research specialist AI. Given the user query:
"{user_input}"

Generate a plan to research this topic.
</s>
<|assistant|>
Plan:"""
        
        plan = self.llm_engine.generate(prompt)
        return {
            "task": "research",
            "steps": [
                {"action": "web_search", "tool": "web_tools"},
                {"action": "fetch_url", "tool": "web_tools"}
            ]
        }

class AutomationSpecialist(SpecialistBase):
    def generate_plan(self, user_input, context):
        prompt = f"""<|system|>
You are an automation specialist AI. Given the user request:
"{user_input}"

Generate a plan to automate this task.
</s>
<|assistant|>
Plan:"""
        
        plan = self.llm_engine.generate(prompt)
        return {
            "task": "automation",
            "steps": [
                {"action": "system_status", "tool": "automation"},
                {"action": "create_workflow", "tool": "automation"}
            ]
        }

class ChatSpecialist(SpecialistBase):
    def generate_plan(self, user_input, context):
        return {
            "task": "chat",
            "steps": [
                {"action": "generate_response", "tool": "llm_engine"}
            ]
        }

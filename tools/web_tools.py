import requests
import logging

class WebTools:
    def __init__(self, llm_engine=None):
        self.logger = logging.getLogger("WebTools")
        self.llm_engine = llm_engine
        self.logger.info("Web tools initialized" + (" with LLM engine" if llm_engine else ""))

    def execute(self, action, **kwargs):
        if action == "web_search":
            query = kwargs.get('query', '')
            return self.web_search(query)
        elif action == "fetch_url":
            url = kwargs.get('url', '')
            return self.fetch_url(url)
        else:
            raise ValueError(f"Unknown action: {action}")

    def web_search(self, query):
        self.logger.info(f"Searching web for: {query}")
        
        # Use LLM to generate a simulated search result
        prompt = f"""<|system|>
You are a web search expert. Generate a realistic search result for: "{query}"
Include 3 relevant results with titles and brief descriptions.
</s>
<|assistant|>"""
        
        return self.llm_engine.generate(prompt)

    def fetch_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            content = response.text[:2000]
            
            # Use LLM to summarize content
            prompt = f"""<|system|>
Summarize the key information from this webpage content:
{content}
</s>
<|assistant|>
Summary:"""
            
            return self.llm_engine.generate(prompt)
        except Exception as e:
            return f"Error: {str(e)}"

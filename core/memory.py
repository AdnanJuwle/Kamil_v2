import logging
from memory_store.vector_db import VectorDatabase
from memory_store.knowledge_graph import KnowledgeGraph

class VectorMemory:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.knowledge_graph = KnowledgeGraph()
        self.logger = logging.getLogger("VectorMemory")
        self.logger.info("Memory system initialized")

    def store_interaction(self, user_input: str, output: any):
        # Create text representation for embedding
        if isinstance(output, dict):
            output_str = "\n".join([f"{k}: {v}" for k, v in output.items()])
        else:
            output_str = str(output)
            
        text = f"{user_input}\n{output_str}"
        
        # Generate embedding from the combined text
        embedding = self._generate_embedding(text)
        
        # Store in vector DB
        self.vector_db.add(embedding, metadata={
            "input": user_input,
            "output": output
        })
        
        # Extract entities from both input and output
        input_entities = self._extract_entities(user_input)
        output_entities = self._extract_entities(output_str)
        all_entities = list(set(input_entities + output_entities))
        
        self.knowledge_graph.add_entities(all_entities)
        
        self.logger.info(f"Stored interaction: {user_input[:50]}...")

    def retrieve_relevant(self, query: str, top_k: int = 5) -> list:
        """Retrieve relevant memories based on query similarity"""
        embedding = self._generate_embedding(query)
        results = self.vector_db.search(embedding, top_k)
        return [item['metadata'] for item in results]

    def _generate_embedding(self, text: str) -> list:
        # Simplified embedding generation - should be replaced with real model
        return [0.0] * 512  # Return a dummy embedding

    def _extract_entities(self, text: str) -> list:
        # Simple entity extraction - split on whitespace
        return [word for word in text.split() if len(word) > 4]

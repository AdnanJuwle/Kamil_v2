import logging

class KnowledgeGraph:
    def __init__(self):
        self.graph = {}
        self.logger = logging.getLogger("KnowledgeGraph")
        self.logger.info("Knowledge graph initialized")

    def add_entities(self, entities: list):
        if not entities:
            return
            
        self.logger.info(f"Adding {len(entities)} entities to graph")
        
        # Create connections between all entities in the list
        for i, entity in enumerate(entities):
            # Add the entity if not present
            if entity not in self.graph:
                self.graph[entity] = set()
            
            # Connect to all other entities
            for other in entities[i+1:]:
                self.graph[entity].add(other)
                # Ensure the other entity exists in the graph
                if other not in self.graph:
                    self.graph[other] = set()
                self.graph[other].add(entity)

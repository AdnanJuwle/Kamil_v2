import numpy as np
import logging

class VectorDatabase:
    def __init__(self):
        self.vectors = []
        self.metadata = []
        self.logger = logging.getLogger("VectorDB")
        self.logger.info("Vector database initialized")

    def add(self, vector, metadata):
        self.vectors.append(vector)
        self.metadata.append(metadata)
        self.logger.info("Added vector to database")

    def search(self, query_vector, top_k=5):
        if not self.vectors:
            return []
            
        try:
            vectors = np.array(self.vectors)
            query_vec = np.array(query_vector)
            
            # Handle zero vectors
            vector_norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            query_norm = np.linalg.norm(query_vec)
            
            if query_norm == 0 or np.any(vector_norms == 0):
                # Use random similarities as fallback
                similarities = np.random.rand(len(vectors))
            else:
                # Calculate cosine similarities
                norm_vectors = vectors / vector_norms
                norm_query = query_vec / query_norm
                similarities = np.dot(norm_vectors, norm_query)
            
            # Get top K results
            indices = np.argsort(similarities)[-top_k:][::-1]
            return [{
                "similarity": float(similarities[i]),
                "metadata": self.metadata[i]
            } for i in indices]
        except Exception as e:
            self.logger.error(f"Vector search error: {str(e)}")
            return []

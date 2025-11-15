"""
Embeddings module using SentenceTransformers for generating dense vector embeddings.
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL


class EmbeddingGenerator:
    """Generates embeddings using SentenceTransformers."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding model."""
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the SentenceTransformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise Exception(f"Error loading embedding model: {str(e)}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text string."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of texts."""
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty texts
        valid_texts = [text if text and text.strip() else " " for text in texts]
        
        embeddings = self.model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        if self.model is None:
            self._load_model()
        # Use a dummy text to get dimension
        dummy_embedding = self.generate_embedding("test")
        return len(dummy_embedding)


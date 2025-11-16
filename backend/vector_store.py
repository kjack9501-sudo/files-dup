"""
Vector store module using FAISS for efficient similarity search.
"""

import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from backend.config import VECTOR_STORE_INDEX_FILE, VECTOR_STORE_METADATA_FILE


class VectorStore:
    """Manages FAISS vector store for document embeddings."""
    
    def __init__(self, dimension: int = 384):
        """Initialize the vector store with embedding dimension."""
        self.dimension = dimension
        self.index = None
        self.metadata = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load FAISS index."""
        if VECTOR_STORE_INDEX_FILE.exists() and VECTOR_STORE_METADATA_FILE.exists():
            self.load()
        else:
            # Create new index using L2 distance (Euclidean)
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict]):
        """Add vectors and their metadata to the index."""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}")
        
        if len(metadata) != vectors.shape[0]:
            raise ValueError("Number of vectors and metadata entries must match")
        
        # Normalize vectors for cosine similarity (optional, but improves results)
        faiss.normalize_L2(vectors)
        
        # Add vectors to index
        self.index.add(vectors.astype('float32'))
        
        # Add metadata
        self.metadata.extend(metadata)
    
    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Search for similar vectors and return top-k results with metadata."""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Normalize query vector
        query_vector = query_vector.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # Search
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                # Convert L2 distance to similarity score (lower distance = higher similarity)
                # Convert numpy float32 to Python float for JSON serialization
                similarity = float(1 / (1 + float(distance)))
                results.append((self.metadata[idx], similarity))
        
        return results
    
    def save(self):
        """Save the FAISS index and metadata to disk."""
        if self.index is None:
            return
        
        # Save FAISS index
        faiss.write_index(self.index, str(VECTOR_STORE_INDEX_FILE))
        
        # Save metadata
        with open(VECTOR_STORE_METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def load(self):
        """Load the FAISS index and metadata from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(VECTOR_STORE_INDEX_FILE))
            
            # Load metadata
            with open(VECTOR_STORE_METADATA_FILE, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            # Update dimension from loaded index
            self.dimension = self.index.d
        except Exception as e:
            raise Exception(f"Error loading vector store: {str(e)}")
    
    def get_size(self) -> int:
        """Get the number of vectors in the index."""
        if self.index is None:
            return 0
        return self.index.ntotal
    
    def clear(self):
        """Clear all vectors and metadata."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self.save()
    
    def get_all_metadata(self) -> List[Dict]:
        """Get all metadata entries."""
        return self.metadata.copy()


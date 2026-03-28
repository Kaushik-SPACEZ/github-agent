"""
Vector Store Module
===================
Manages FAISS vector database for storing and retrieving code embeddings.
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[RAG] FAISS not installed. RAG features will be disabled.")


class VectorStore:
    """
    FAISS-based vector store for code embeddings.
    
    Stores code chunks with their embeddings and metadata for similarity search.
    """
    
    def __init__(self, store_path: str = "./rag/vector_db"):
        """
        Initialize vector store.
        
        Args:
            store_path: Directory to store FAISS index and metadata
        """
        self.store_path = store_path
        self.index_path = os.path.join(store_path, "faiss.index")
        self.metadata_path = os.path.join(store_path, "metadata.pkl")
        
        os.makedirs(store_path, exist_ok=True)
        
        self.index = None
        self.metadata = []
        self.dimension = 384  # Default embedding dimension
        
        # Load existing index if available
        self.load()
    
    def initialize_index(self, dimension: int = 384):
        """
        Initialize a new FAISS index.
        
        Args:
            dimension: Embedding vector dimension
        """
        if not FAISS_AVAILABLE:
            return
        
        self.dimension = dimension
        # Use IndexFlatL2 for exact search (good for small datasets)
        self.index = faiss.IndexFlatL2(dimension)
        print(f"[RAG] Initialized FAISS index with dimension {dimension}")
    
    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict]):
        """
        Add embeddings to the vector store.
        
        Args:
            embeddings: Numpy array of shape (n, dimension)
            metadata: List of metadata dicts for each embedding
        """
        if not FAISS_AVAILABLE or self.index is None:
            return
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.metadata.extend(metadata)
        
        print(f"[RAG] Added {len(embeddings)} embeddings to vector store")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Search for similar code chunks.
        
        Args:
            query_embedding: Query vector of shape (1, dimension)
            k: Number of results to return
        
        Returns:
            List of metadata dicts for top-k similar chunks
        """
        if not FAISS_AVAILABLE or self.index is None or self.index.ntotal == 0:
            return []
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Retrieve metadata for results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['distance'] = float(distances[0][i])
                results.append(result)
        
        return results
    
    def save(self):
        """Save FAISS index and metadata to disk."""
        if not FAISS_AVAILABLE or self.index is None:
            return
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'dimension': self.dimension
                }, f)
            
            print(f"[RAG] Saved vector store with {self.index.ntotal} embeddings")
        except Exception as e:
            print(f"[RAG] Error saving vector store: {e}")
    
    def load(self):
        """Load FAISS index and metadata from disk."""
        if not FAISS_AVAILABLE:
            return
        
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Load FAISS index
                self.index = faiss.read_index(self.index_path)
                
                # Load metadata
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data['metadata']
                    self.dimension = data['dimension']
                
                print(f"[RAG] Loaded vector store with {self.index.ntotal} embeddings")
        except Exception as e:
            print(f"[RAG] Error loading vector store: {e}")
            self.initialize_index()
    
    def clear(self):
        """Clear all embeddings from the vector store."""
        self.initialize_index(self.dimension)
        self.metadata = []
        print("[RAG] Cleared vector store")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        if not FAISS_AVAILABLE or self.index is None:
            return {
                'total_embeddings': 0,
                'dimension': 0,
                'faiss_available': False
            }
        
        return {
            'total_embeddings': self.index.ntotal,
            'dimension': self.dimension,
            'faiss_available': True,
            'metadata_count': len(self.metadata)
        }
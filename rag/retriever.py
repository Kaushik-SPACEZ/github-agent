"""
RAG Retriever Module
====================
Orchestrates the RAG pipeline for code analysis.
"""

from typing import List, Dict, Optional
from .vector_store import VectorStore
from .embeddings import CodeEmbedder


class RAGRetriever:
    """
    RAG retriever for contextual code analysis.
    
    Combines vector store and embeddings to provide relevant context
    for code quality analysis.
    """
    
    def __init__(self, store_path: str = "./rag/vector_db"):
        """
        Initialize RAG retriever.
        
        Args:
            store_path: Path to vector database
        """
        self.vector_store = VectorStore(store_path)
        self.embedder = CodeEmbedder()
        
        # Initialize vector store if empty
        if self.vector_store.index is None:
            self.vector_store.initialize_index(self.embedder.dimension)
    
    def index_repository(self, python_files: List[Dict]):
        """
        Index a repository's code for RAG retrieval.
        
        Args:
            python_files: List of dicts with 'filename' and 'content'
        """
        print(f"[RAG] Indexing {len(python_files)} Python files...")
        
        # Generate embeddings
        embeddings, metadata = self.embedder.process_repository(python_files)
        
        if len(embeddings) == 0:
            print("[RAG] No code chunks to index")
            return
        
        # Add to vector store
        self.vector_store.add_embeddings(embeddings, metadata)
        
        # Save to disk
        self.vector_store.save()
        
        print(f"[RAG] Successfully indexed {len(embeddings)} code chunks")
    
    def retrieve_context(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve relevant code context for a query.
        
        Args:
            query: Query string (e.g., "security vulnerabilities")
            k: Number of relevant chunks to retrieve
        
        Returns:
            List of relevant code chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, k=k)
        
        return results
    
    def get_context_for_file(self, filename: str, issue_type: str = "code quality") -> str:
        """
        Get relevant context for analyzing a specific file.
        
        Args:
            filename: Name of the file being analyzed
            issue_type: Type of issue to look for
        
        Returns:
            Context string to add to LLM prompt
        """
        # Build query
        query = f"{issue_type} issues in {filename}"
        
        # Retrieve relevant chunks
        results = self.retrieve_context(query, k=3)
        
        if not results:
            return ""
        
        # Format context
        context_parts = ["## Similar Code Patterns (RAG Context)\n"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"### Pattern {i} (from {result['filename']})")
            context_parts.append(f"```python\n{result['text']}\n```\n")
        
        return "\n".join(context_parts)
    
    def clear_index(self):
        """Clear the vector store index."""
        self.vector_store.clear()
        self.vector_store.save()
        print("[RAG] Cleared vector store index")
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics."""
        stats = self.vector_store.get_stats()
        stats['embedder_model'] = self.embedder.model_name
        stats['embedder_dimension'] = self.embedder.dimension
        return stats
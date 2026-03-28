"""
RAG (Retrieval Augmented Generation) Module
============================================
Provides contextual code analysis using vector embeddings and similarity search.

This module enhances the code scanner by:
1. Storing code patterns in a vector database (FAISS)
2. Retrieving similar code patterns during analysis
3. Providing better context to the LLM for issue detection
"""

from .vector_store import VectorStore
from .embeddings import CodeEmbedder
from .retriever import RAGRetriever

__all__ = ['VectorStore', 'CodeEmbedder', 'RAGRetriever']
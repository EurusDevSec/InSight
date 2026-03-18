"""
InSight Knowledge Base Module — Task 3.1
=========================================

Provides document chunking, embedding generation, and hybrid search
for the medical knowledge base used by the RAG agent.

Components:
    - chunking: Split documents into overlapping chunks with metadata
    - embedding: Generate 384-dim vectors using sentence-transformers
    - search: Hybrid vector + keyword search with re-ranking
"""

from knowledge_base.chunking import ChunkingService
from knowledge_base.embedding import EmbeddingService
from knowledge_base.search import SearchService

__all__ = ["ChunkingService", "EmbeddingService", "SearchService"]

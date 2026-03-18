"""
Pydantic schemas for the knowledge base pipeline.

Task 3.1 — Knowledge Base Setup
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Source Document ────────────────────────────────────────────────

class MedicalDocument(BaseModel):
    """A single medical guideline document loaded from guidelines.json."""

    doc_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    source: str = Field(..., description="Citation source (e.g. ADA, MOH)")
    category: str = Field(..., description="Category tag for filtering")
    tags: list[str] = Field(default_factory=list, description="Keyword tags")
    content: str = Field(..., description="Full text content")
    language: str = Field(default="en", description="Content language code")


# ── Chunk ──────────────────────────────────────────────────────────

class DocumentChunk(BaseModel):
    """A text chunk produced by the chunking service."""

    chunk_id: str = Field(..., description="Unique chunk ID: {doc_id}__chunk_{idx}")
    doc_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk text content")
    source: str = Field(..., description="Inherited from parent document")
    category: str = Field(..., description="Inherited from parent document")
    chunk_index: int = Field(..., description="0-based position within parent doc")
    total_chunks: int = Field(..., description="Total chunks from parent doc")


# ── Embedding Record ──────────────────────────────────────────────

class EmbeddingRecord(BaseModel):
    """A chunk with its embedding vector, ready for Milvus insertion."""

    chunk_id: str = Field(..., description="Chunk identifier")
    content: str = Field(..., description="Chunk text content")
    source: str = Field(..., description="Citation source")
    category: str = Field(..., description="Category tag")
    embedding: list[float] = Field(..., description="384-dim float vector")


# ── Search ─────────────────────────────────────────────────────────

class SearchQuery(BaseModel):
    """Input for hybrid search."""

    query: str = Field(..., description="Natural language query text")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results")
    category_filter: str | None = Field(
        default=None, description="Optional category filter"
    )


class SearchResult(BaseModel):
    """A single search result with combined score."""

    chunk_id: str = Field(..., description="Matched chunk ID")
    content: str = Field(..., description="Chunk text")
    source: str = Field(..., description="Citation source")
    category: str = Field(..., description="Category")
    vector_score: float = Field(..., description="Cosine similarity score (0-1)")
    keyword_score: float = Field(
        default=0.0, description="BM25-like keyword relevance score"
    )
    combined_score: float = Field(..., description="Weighted combined score")


class SearchResponse(BaseModel):
    """Full search response."""

    query: str = Field(..., description="Original query text")
    results: list[SearchResult] = Field(default_factory=list)
    total_found: int = Field(default=0, description="Number of results returned")

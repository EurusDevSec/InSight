"""
Hybrid search service: vector similarity + keyword scoring + re-ranking.

Task 3.1.4 — Implement hybrid search over the ``medical_knowledge`` Milvus
collection.

Strategy:
    1. Encode the query with the same embedding model.
    2. Milvus ANN search (cosine similarity) → top ``top_k * 2`` candidates.
    3. Compute BM25-like keyword score for each candidate.
    4. Combine: ``combined = α * vector_score + (1 − α) * keyword_score``
    5. Re-rank by combined score, return top ``top_k``.
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field

from knowledge_base.embedding import EmbeddingService
from knowledge_base.schemas import SearchQuery, SearchResponse, SearchResult

logger = logging.getLogger(__name__)

# ── Defaults ───────────────────────────────────────────────────────

DEFAULT_ALPHA = 0.7  # weight for vector score
MILVUS_COLLECTION = "medical_knowledge"
MILVUS_SEARCH_PARAMS = {"metric_type": "COSINE", "params": {"ef": 128}}


@dataclass
class SearchService:
    """Hybrid search over the medical_knowledge Milvus collection."""

    embedding_service: EmbeddingService
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    alpha: float = DEFAULT_ALPHA
    _collection: object | None = field(default=None, init=False, repr=False)

    def connect(self) -> None:
        """Connect to Milvus and load the collection."""
        from pymilvus import Collection, connections

        connections.connect("default", host=self.milvus_host, port=self.milvus_port)
        self._collection = Collection(MILVUS_COLLECTION)
        self._collection.load()
        logger.info(
            "Connected to Milvus (%s:%d), collection '%s' loaded.",
            self.milvus_host,
            self.milvus_port,
            MILVUS_COLLECTION,
        )

    def search(self, query: SearchQuery) -> SearchResponse:
        """Execute hybrid search: vector ANN + keyword re-ranking.

        Args:
            query: Search query with text, top_k, and optional category filter.

        Returns:
            SearchResponse with ranked results.

        Raises:
            RuntimeError: If not connected to Milvus.
        """
        if self._collection is None:
            raise RuntimeError("Not connected. Call connect() first.")

        # 1. Encode query
        query_vector = self.embedding_service.encode_single(query.query)

        # 2. Build Milvus expression filter
        expr = ""
        if query.category_filter:
            safe_category = query.category_filter.replace('"', "")
            expr = f'category == "{safe_category}"'

        # 3. ANN search — fetch 2× candidates for re-ranking headroom
        ann_limit = min(query.top_k * 2, 50)
        hits = self._collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=MILVUS_SEARCH_PARAMS,
            limit=ann_limit,
            expr=expr or None,
            output_fields=["content", "source", "category"],
        )

        # 4. Score, combine, re-rank
        candidates: list[SearchResult] = []
        for hit in hits[0]:
            content = hit.entity.get("content", "")
            vector_score = float(hit.score)
            keyword_score = _keyword_score(query.query, content)
            combined = self.alpha * vector_score + (1 - self.alpha) * keyword_score

            candidates.append(
                SearchResult(
                    chunk_id=str(hit.id),
                    content=content,
                    source=hit.entity.get("source", ""),
                    category=hit.entity.get("category", ""),
                    vector_score=vector_score,
                    keyword_score=keyword_score,
                    combined_score=combined,
                )
            )

        # 5. Re-rank by combined score
        candidates.sort(key=lambda r: r.combined_score, reverse=True)
        top_results = candidates[: query.top_k]

        return SearchResponse(
            query=query.query,
            results=top_results,
            total_found=len(top_results),
        )


# ── Keyword scoring ───────────────────────────────────────────────


def _keyword_score(query: str, document: str) -> float:
    """Simple BM25-inspired term-frequency keyword score normalised to [0, 1].

    Not a full BM25 implementation (no IDF across corpus), but effective
    for re-ranking a small candidate set returned by vector search.
    """
    query_terms = _tokenise(query)
    if not query_terms:
        return 0.0

    doc_terms = _tokenise(document)
    if not doc_terms:
        return 0.0

    doc_len = len(doc_terms)
    avg_dl = 200.0  # approximate average doc length in tokens
    k1 = 1.5
    b = 0.75

    score = 0.0
    for qt in set(query_terms):
        tf = doc_terms.count(qt)
        if tf == 0:
            continue
        # BM25 TF saturation
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * doc_len / avg_dl)
        score += numerator / denominator

    # Normalise by number of query terms to keep score in [0, ~1]
    max_possible = len(set(query_terms)) * (k1 + 1)
    return min(score / max_possible, 1.0) if max_possible > 0 else 0.0


def _tokenise(text: str) -> list[str]:
    """Lowercase word tokeniser."""
    return re.findall(r"[a-z0-9]+", text.lower())

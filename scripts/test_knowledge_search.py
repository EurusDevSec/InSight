"""
End-to-end search verification against a live Milvus instance.

Task 3.1.4 — Verify hybrid search returns relevant results.

Usage (requires Docker Compose Milvus + data ingested):
    cd src/rag-service
    python -m scripts.test_knowledge_search

Or from project root:
    python scripts/test_knowledge_search.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_RAG_ROOT = Path(__file__).resolve().parent.parent / "src" / "rag-service"
if _RAG_ROOT.exists():
    sys.path.insert(0, str(_RAG_ROOT))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from knowledge_base.embedding import EmbeddingService
from knowledge_base.schemas import SearchQuery
from knowledge_base.search import SearchService


def main() -> None:
    # Prepare services
    embedder = EmbeddingService()
    embedder.load()

    searcher = SearchService(embedding_service=embedder)
    searcher.connect()

    # ── Test queries ───────────────────────────────────────────────
    test_queries = [
        SearchQuery(
            query="liều insulin cho 60g Carb",
            top_k=5,
        ),
        SearchQuery(
            query="how to calculate bolus insulin from carbohydrate",
            top_k=3,
        ),
        SearchQuery(
            query="hypoglycemia emergency treatment rule of 15",
            top_k=3,
            category_filter="emergency_protocol",
        ),
        SearchQuery(
            query="Vietnamese pho noodle carbohydrate content",
            top_k=3,
            category_filter="vn_food_guidance",
        ),
        SearchQuery(
            query="glycemic load calculation formula",
            top_k=3,
        ),
    ]

    all_passed = True
    for q in test_queries:
        response = searcher.search(q)
        print(f"\n{'='*60}")
        print(f"Query: {q.query}")
        print(f"Filter: {q.category_filter or 'none'}")
        print(f"Results: {response.total_found}")

        if response.total_found == 0:
            print("  ⚠ NO RESULTS — FAIL")
            all_passed = False
            continue

        for i, r in enumerate(response.results):
            print(
                f"  [{i+1}] score={r.combined_score:.4f} "
                f"(vec={r.vector_score:.4f} kw={r.keyword_score:.4f}) "
                f"| {r.source} | {r.category}"
            )
            # Show first 120 chars of content
            snippet = r.content[:120].replace("\n", " ")
            print(f"      {snippet}…")

    print(f"\n{'='*60}")
    if all_passed:
        print("✅ All search queries returned results.")
    else:
        print("❌ Some queries returned no results — check ingestion.")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

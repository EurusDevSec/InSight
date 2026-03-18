"""
Batch ingestion: Read guidelines.json → chunk → embed → insert into Milvus.

Task 3.1.3 — Embedding & nhập vào Milvus.

Usage (requires Docker Compose Milvus running):
    cd src/rag-service
    python -m scripts.ingest_knowledge_base

Or from project root:
    python scripts/ingest_knowledge_base.py
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

# ── Resolve imports ────────────────────────────────────────────────
# Support running from both project root and src/rag-service/

_SCRIPT_DIR = Path(__file__).resolve().parent
_RAG_ROOT = _SCRIPT_DIR.parent / "src" / "rag-service"
if _RAG_ROOT.exists():
    sys.path.insert(0, str(_RAG_ROOT))
else:
    # Running from inside src/rag-service/
    sys.path.insert(0, str(_SCRIPT_DIR.parent))

from knowledge_base.chunking import ChunkingService
from knowledge_base.embedding import EmbeddingService
from knowledge_base.schemas import MedicalDocument

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger("ingest")

# ── Constants ──────────────────────────────────────────────────────

GUIDELINES_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "rag-service"
    / "knowledge"
    / "medical"
    / "guidelines.json"
)
# Fallback when running from src/rag-service
if not GUIDELINES_PATH.exists():
    GUIDELINES_PATH = (
        Path(__file__).resolve().parent.parent
        / "knowledge"
        / "medical"
        / "guidelines.json"
    )

MILVUS_HOST = "localhost"
MILVUS_PORT = 19530
COLLECTION_NAME = "medical_knowledge"
BATCH_SIZE = 64


def load_documents(path: Path) -> list[MedicalDocument]:
    """Load and validate medical guideline documents from JSON."""
    logger.info("Loading documents from %s", path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    docs = [MedicalDocument(**d) for d in data["documents"]]
    logger.info("Loaded %d documents.", len(docs))
    return docs


def ingest(
    milvus_host: str = MILVUS_HOST,
    milvus_port: int = MILVUS_PORT,
) -> dict:
    """Full ingestion pipeline: load → chunk → embed → insert.

    Returns:
        Summary dict with counts and timing.
    """
    from pymilvus import Collection, connections, utility

    t0 = time.perf_counter()

    # 1. Load documents
    docs = load_documents(GUIDELINES_PATH)

    # 2. Chunk
    chunker = ChunkingService()
    chunks = chunker.chunk_documents(docs)
    logger.info("Chunking complete: %d chunks.", len(chunks))

    # 3. Embed
    embedder = EmbeddingService()
    embedder.load()
    texts = [c.content for c in chunks]
    embeddings = embedder.encode(texts)
    logger.info("Embedding complete: shape %s", embeddings.shape)

    # 4. Connect to Milvus
    connections.connect("default", host=milvus_host, port=milvus_port)
    if not utility.has_collection(COLLECTION_NAME):
        logger.error(
            "Collection '%s' not found. Run scripts/init-milvus.py first.",
            COLLECTION_NAME,
        )
        sys.exit(1)

    collection = Collection(COLLECTION_NAME)

    # 5. Insert in batches
    total_inserted = 0
    for i in range(0, len(chunks), BATCH_SIZE):
        batch_chunks = chunks[i : i + BATCH_SIZE]
        batch_embeddings = embeddings[i : i + BATCH_SIZE]

        entities = [
            [c.content for c in batch_chunks],  # content
            [c.source for c in batch_chunks],  # source
            [c.category for c in batch_chunks],  # category
            batch_embeddings.tolist(),  # embedding
        ]
        insert_result = collection.insert(entities)
        total_inserted += insert_result.insert_count
        logger.info(
            "Inserted batch %d–%d (%d rows).",
            i,
            i + len(batch_chunks),
            insert_result.insert_count,
        )

    # 6. Flush and build index
    collection.flush()
    logger.info("Flush complete. Total rows in collection: %d", collection.num_entities)

    elapsed = time.perf_counter() - t0
    summary = {
        "documents": len(docs),
        "chunks": len(chunks),
        "inserted": total_inserted,
        "elapsed_seconds": round(elapsed, 2),
    }
    logger.info("Ingestion summary: %s", summary)
    return summary


if __name__ == "__main__":
    ingest()

"""
Document chunking service with configurable size and overlap.

Task 3.1.2 — Chunk & normalise medical guideline documents.

Strategy:
    - Split by paragraphs first (natural boundaries)
    - If a paragraph exceeds ``max_chunk_chars``, split by sentences
    - Merge small consecutive paragraphs to fill chunks efficiently
    - Maintain ``overlap_chars`` character overlap between adjacent chunks
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from knowledge_base.schemas import DocumentChunk, MedicalDocument

logger = logging.getLogger(__name__)

# ── Defaults ───────────────────────────────────────────────────────

DEFAULT_MAX_CHUNK_CHARS = 1200
DEFAULT_OVERLAP_CHARS = 150
MIN_CHUNK_CHARS = 80


@dataclass
class ChunkingService:
    """Deterministic document chunker with paragraph-aware splitting."""

    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS
    overlap_chars: int = DEFAULT_OVERLAP_CHARS

    def chunk_document(self, doc: MedicalDocument) -> list[DocumentChunk]:
        """Split a single document into overlapping chunks.

        Args:
            doc: Source medical document.

        Returns:
            Ordered list of ``DocumentChunk`` objects.
        """
        text = _normalise_text(doc.content)
        if not text:
            return []

        raw_chunks = self._split_text(text)
        chunks: list[DocumentChunk] = []
        total = len(raw_chunks)

        for idx, content in enumerate(raw_chunks):
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc.doc_id}__chunk_{idx}",
                    doc_id=doc.doc_id,
                    content=content,
                    source=doc.source,
                    category=doc.category,
                    chunk_index=idx,
                    total_chunks=total,
                )
            )

        logger.info("Chunked '%s' → %d chunks", doc.doc_id, total)
        return chunks

    def chunk_documents(self, docs: list[MedicalDocument]) -> list[DocumentChunk]:
        """Chunk a batch of documents.

        Returns:
            Flat list of all chunks across all documents.
        """
        all_chunks: list[DocumentChunk] = []
        for doc in docs:
            all_chunks.extend(self.chunk_document(doc))
        logger.info(
            "Total: %d documents → %d chunks", len(docs), len(all_chunks)
        )
        return all_chunks

    # ── internal ───────────────────────────────────────────────────

    def _split_text(self, text: str) -> list[str]:
        """Split text into chunks respecting paragraph and sentence boundaries."""
        paragraphs = _split_paragraphs(text)
        sentences_per_para = [_split_sentences(p) for p in paragraphs]

        # Flatten to sentence list while keeping paragraph separators
        sentences: list[str] = []
        for group in sentences_per_para:
            sentences.extend(group)

        if not sentences:
            return [text] if len(text) >= MIN_CHUNK_CHARS else []

        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for sent in sentences:
            sent_len = len(sent)

            if current_len + sent_len > self.max_chunk_chars and current:
                chunk_text = " ".join(current).strip()
                if len(chunk_text) >= MIN_CHUNK_CHARS:
                    chunks.append(chunk_text)

                # Compute overlap: keep trailing sentences up to overlap_chars
                overlap: list[str] = []
                overlap_len = 0
                for s in reversed(current):
                    if overlap_len + len(s) > self.overlap_chars:
                        break
                    overlap.insert(0, s)
                    overlap_len += len(s)

                current = overlap
                current_len = overlap_len

            current.append(sent)
            current_len += sent_len

        # Flush remainder
        if current:
            chunk_text = " ".join(current).strip()
            if len(chunk_text) >= MIN_CHUNK_CHARS:
                chunks.append(chunk_text)
            elif chunks:
                # Merge tiny remainder into last chunk
                chunks[-1] = chunks[-1] + " " + chunk_text

        return chunks if chunks else ([text] if len(text) >= MIN_CHUNK_CHARS else [])


# ── Helpers ────────────────────────────────────────────────────────


def _normalise_text(text: str) -> str:
    """Collapse whitespace, strip leading/trailing space."""
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _split_paragraphs(text: str) -> list[str]:
    """Split on double-newline (paragraph boundary)."""
    parts = re.split(r"\n{2,}", text)
    return [p.strip() for p in parts if p.strip()]


def _split_sentences(text: str) -> list[str]:
    """Naive sentence splitter on period/question/exclamation followed by space."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in parts if s.strip()]

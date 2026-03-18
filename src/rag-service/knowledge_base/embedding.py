"""
Embedding service wrapping ``sentence-transformers``.

Task 3.1.3 — Generate 384-dim embeddings for Milvus ingestion.

Model: ``all-MiniLM-L6-v2`` (384 dimensions, cosine similarity).
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # allow tests to run without the heavy package installed
    SentenceTransformer = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


class EmbeddingService:
    """Lazy-loaded sentence-transformer wrapper."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        self._model: Optional[object] = None

    @property
    def dimension(self) -> int:
        return EMBEDDING_DIM

    def load(self) -> None:
        """Download / load the sentence-transformer model into memory."""
        if self._model is not None:
            return
        if SentenceTransformer is None:
            raise RuntimeError(
                "sentence_transformers is not installed. "
                "Run: pip install sentence-transformers"
            )
        logger.info("Loading embedding model '%s' …", self.model_name)
        self._model = SentenceTransformer(self.model_name)
        logger.info("Embedding model loaded (dim=%d).", EMBEDDING_DIM)

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode a list of texts into a (N, 384) float32 array.

        Args:
            texts: List of strings to embed.

        Returns:
            numpy array of shape ``(len(texts), 384)``.

        Raises:
            RuntimeError: If :meth:`load` has not been called.
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        embeddings: np.ndarray = self._model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def encode_single(self, text: str) -> list[float]:
        """Encode a single text and return a plain list of floats."""
        vec = self.encode([text])
        return vec[0].tolist()

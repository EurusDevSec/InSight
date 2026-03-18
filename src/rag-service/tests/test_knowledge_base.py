"""
Unit tests for Task 3.1 — Knowledge Base Setup.

Covers:
    - Document loading & schema validation
    - Chunking logic (sizes, overlap, edge cases)
    - Embedding service (dimension, normalisation)
    - Keyword scoring
    - Hybrid search (with mocked Milvus)

Run:
    cd src/rag-service
    pytest tests/test_knowledge_base.py -v
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from knowledge_base.chunking import (
    DEFAULT_MAX_CHUNK_CHARS,
    DEFAULT_OVERLAP_CHARS,
    MIN_CHUNK_CHARS,
    ChunkingService,
    _normalise_text,
    _split_paragraphs,
    _split_sentences,
)
from knowledge_base.search import _keyword_score, _tokenise
from knowledge_base.schemas import (
    DocumentChunk,
    EmbeddingRecord,
    MedicalDocument,
    SearchQuery,
    SearchResponse,
    SearchResult,
)

# ── Paths ──────────────────────────────────────────────────────────

GUIDELINES_PATH = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
    / "medical"
    / "guidelines.json"
)


# ══════════════════════════════════════════════════════════════════
#  Fixtures
# ══════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def guidelines_data() -> dict:
    """Load the raw JSON once for the test session."""
    with open(GUIDELINES_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_documents(guidelines_data: dict) -> list[MedicalDocument]:
    """Parse all documents from guidelines.json."""
    return [MedicalDocument(**d) for d in guidelines_data["documents"]]


@pytest.fixture
def sample_document() -> MedicalDocument:
    return MedicalDocument(
        doc_id="test_doc",
        title="Test Document",
        source="Unit Test",
        category="test",
        tags=["test", "unit"],
        content=(
            "This is the first paragraph about insulin dosing. "
            "It contains important medical information.\n\n"
            "This is the second paragraph about carbohydrate counting. "
            "Patients should count carbs carefully.\n\n"
            "This is the third paragraph about glycemic load. "
            "GL is calculated from GI and carb grams."
        ),
        language="en",
    )


@pytest.fixture
def chunking_service() -> ChunkingService:
    return ChunkingService()


@pytest.fixture
def small_chunker() -> ChunkingService:
    """Chunker with small limits to force splitting."""
    return ChunkingService(max_chunk_chars=200, overlap_chars=40)


# ══════════════════════════════════════════════════════════════════
#  Test: Guidelines Data Integrity
# ══════════════════════════════════════════════════════════════════


class TestGuidelinesData:
    """Verify the guidelines.json data file is well-formed."""

    def test_file_exists(self) -> None:
        assert GUIDELINES_PATH.exists(), f"Missing: {GUIDELINES_PATH}"

    def test_valid_json(self, guidelines_data: dict) -> None:
        assert "documents" in guidelines_data
        assert "version" in guidelines_data

    def test_minimum_document_count(self, all_documents: list[MedicalDocument]) -> None:
        assert len(all_documents) >= 20, (
            f"Need ≥20 documents, got {len(all_documents)}"
        )

    def test_document_categories_present(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        categories = {d.category for d in all_documents}
        required = {
            "insulin_dosing",
            "carb_counting",
            "emergency_protocol",
            "vn_food_guidance",
        }
        missing = required - categories
        assert not missing, f"Missing required categories: {missing}"

    def test_all_documents_have_content(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        for doc in all_documents:
            assert len(doc.content) >= 100, (
                f"Document '{doc.doc_id}' content too short ({len(doc.content)} chars)"
            )

    def test_all_documents_have_tags(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        for doc in all_documents:
            assert len(doc.tags) >= 1, f"Document '{doc.doc_id}' has no tags"

    def test_unique_doc_ids(self, all_documents: list[MedicalDocument]) -> None:
        ids = [d.doc_id for d in all_documents]
        assert len(ids) == len(set(ids)), "Duplicate doc_ids found"

    def test_sources_are_cited(self, all_documents: list[MedicalDocument]) -> None:
        for doc in all_documents:
            assert len(doc.source) >= 5, (
                f"Document '{doc.doc_id}' has missing or short source"
            )


# ══════════════════════════════════════════════════════════════════
#  Test: Pydantic Schemas
# ══════════════════════════════════════════════════════════════════


class TestSchemas:
    def test_medical_document_schema(self) -> None:
        doc = MedicalDocument(
            doc_id="x",
            title="T",
            source="S",
            category="C",
            tags=["a"],
            content="Hello world.",
        )
        assert doc.language == "en"  # default

    def test_document_chunk_schema(self) -> None:
        chunk = DocumentChunk(
            chunk_id="x__chunk_0",
            doc_id="x",
            content="text",
            source="S",
            category="C",
            chunk_index=0,
            total_chunks=1,
        )
        assert chunk.chunk_id == "x__chunk_0"

    def test_search_query_defaults(self) -> None:
        q = SearchQuery(query="test")
        assert q.top_k == 5
        assert q.category_filter is None

    def test_search_query_validation(self) -> None:
        with pytest.raises(Exception):
            SearchQuery(query="test", top_k=0)  # ge=1
        with pytest.raises(Exception):
            SearchQuery(query="test", top_k=100)  # le=50

    def test_search_result_schema(self) -> None:
        r = SearchResult(
            chunk_id="c1",
            content="text",
            source="S",
            category="C",
            vector_score=0.9,
            keyword_score=0.5,
            combined_score=0.78,
        )
        assert r.combined_score == 0.78

    def test_embedding_record_schema(self) -> None:
        r = EmbeddingRecord(
            chunk_id="c1",
            content="text",
            source="S",
            category="C",
            embedding=[0.1] * 384,
        )
        assert len(r.embedding) == 384


# ══════════════════════════════════════════════════════════════════
#  Test: Text Normalisation Helpers
# ══════════════════════════════════════════════════════════════════


class TestTextHelpers:
    def test_normalise_collapses_whitespace(self) -> None:
        assert _normalise_text("  hello   world  ") == "hello world"

    def test_normalise_crlf(self) -> None:
        assert _normalise_text("a\r\nb") == "a\nb"

    def test_split_paragraphs(self) -> None:
        text = "Para 1.\n\nPara 2.\n\n\nPara 3."
        parts = _split_paragraphs(text)
        assert len(parts) == 3

    def test_split_sentences(self) -> None:
        text = "First sentence. Second sentence! Third?"
        parts = _split_sentences(text)
        assert len(parts) == 3

    def test_split_sentences_abbreviations(self) -> None:
        """Abbreviations like 'mg/dL' should not split."""
        text = "BG < 70 mg/dL is dangerous. Treat immediately."
        parts = _split_sentences(text)
        assert len(parts) == 2


# ══════════════════════════════════════════════════════════════════
#  Test: Chunking Service
# ══════════════════════════════════════════════════════════════════


class TestChunkingService:
    def test_single_short_document(self, chunking_service: ChunkingService) -> None:
        """Short docs that fit in one chunk produce exactly 1 chunk."""
        doc = MedicalDocument(
            doc_id="short",
            title="Short",
            source="Test",
            category="test",
            tags=[],
            content="A" * 200,
        )
        chunks = chunking_service.chunk_document(doc)
        assert len(chunks) == 1
        assert chunks[0].chunk_index == 0
        assert chunks[0].total_chunks == 1

    def test_empty_content_produces_no_chunks(
        self, chunking_service: ChunkingService
    ) -> None:
        doc = MedicalDocument(
            doc_id="empty",
            title="E",
            source="T",
            category="t",
            tags=[],
            content="",
        )
        chunks = chunking_service.chunk_document(doc)
        assert len(chunks) == 0

    def test_long_document_produces_multiple_chunks(
        self, small_chunker: ChunkingService
    ) -> None:
        long_content = (
            "Sentence one about insulin. " * 10
            + "\n\n"
            + "Sentence two about carbs. " * 10
            + "\n\n"
            + "Sentence three about GL. " * 10
        )
        doc = MedicalDocument(
            doc_id="long",
            title="Long",
            source="T",
            category="t",
            tags=[],
            content=long_content,
        )
        chunks = small_chunker.chunk_document(doc)
        assert len(chunks) > 1

    def test_chunk_metadata_preserved(self, sample_document: MedicalDocument) -> None:
        chunker = ChunkingService(max_chunk_chars=200, overlap_chars=30)
        chunks = chunker.chunk_document(sample_document)
        for chunk in chunks:
            assert chunk.doc_id == "test_doc"
            assert chunk.source == "Unit Test"
            assert chunk.category == "test"

    def test_chunk_ids_unique(self, sample_document: MedicalDocument) -> None:
        chunker = ChunkingService(max_chunk_chars=200, overlap_chars=30)
        chunks = chunker.chunk_document(sample_document)
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_ids_format(self, sample_document: MedicalDocument) -> None:
        chunker = ChunkingService(max_chunk_chars=200, overlap_chars=30)
        chunks = chunker.chunk_document(sample_document)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == f"test_doc__chunk_{i}"

    def test_all_content_covered(self, sample_document: MedicalDocument) -> None:
        """All named entities from the original should appear in some chunk."""
        chunker = ChunkingService(max_chunk_chars=200, overlap_chars=30)
        chunks = chunker.chunk_document(sample_document)
        combined = " ".join(c.content for c in chunks)
        assert "insulin dosing" in combined
        assert "carbohydrate counting" in combined
        assert "glycemic load" in combined

    def test_chunk_documents_batch(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        chunker = ChunkingService()
        chunks = chunker.chunk_documents(all_documents)
        assert len(chunks) >= len(all_documents), (
            "At least 1 chunk per document expected"
        )
        # Verify all doc_ids represented
        doc_ids_in_chunks = {c.doc_id for c in chunks}
        doc_ids_original = {d.doc_id for d in all_documents}
        assert doc_ids_original == doc_ids_in_chunks

    def test_no_chunk_exceeds_max_size(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        chunker = ChunkingService()
        chunks = chunker.chunk_documents(all_documents)
        tolerance = 1.3  # 30% tolerance for boundary effects
        max_allowed = chunker.max_chunk_chars * tolerance
        for chunk in chunks:
            assert len(chunk.content) <= max_allowed, (
                f"Chunk '{chunk.chunk_id}' too large: {len(chunk.content)} > {max_allowed}"
            )

    def test_no_chunk_below_min_size(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        chunker = ChunkingService()
        chunks = chunker.chunk_documents(all_documents)
        for chunk in chunks:
            assert len(chunk.content) >= MIN_CHUNK_CHARS, (
                f"Chunk '{chunk.chunk_id}' too small: {len(chunk.content)}"
            )


# ══════════════════════════════════════════════════════════════════
#  Test: Embedding Service
# ══════════════════════════════════════════════════════════════════


class TestEmbeddingService:
    """Tests that work without downloading the real model (mocked)."""

    def test_raises_if_not_loaded(self) -> None:
        from knowledge_base.embedding import EmbeddingService

        svc = EmbeddingService()
        with pytest.raises(RuntimeError, match="not loaded"):
            svc.encode(["hello"])

    def test_dimension_constant(self) -> None:
        from knowledge_base.embedding import EMBEDDING_DIM, EmbeddingService

        svc = EmbeddingService()
        assert svc.dimension == EMBEDDING_DIM == 384

    @patch("knowledge_base.embedding.SentenceTransformer", create=True)
    def test_encode_returns_correct_shape(self, mock_st_cls: MagicMock) -> None:
        from knowledge_base.embedding import EmbeddingService

        # Mock the model's encode to return fake embeddings
        mock_model = MagicMock()
        fake_embeddings = np.random.randn(3, 384).astype(np.float32)
        mock_model.encode.return_value = fake_embeddings
        mock_st_cls.return_value = mock_model

        svc = EmbeddingService()
        svc.load()
        result = svc.encode(["a", "b", "c"])

        assert result.shape == (3, 384)
        assert result.dtype == np.float32

    @patch("knowledge_base.embedding.SentenceTransformer", create=True)
    def test_encode_single_returns_list(self, mock_st_cls: MagicMock) -> None:
        from knowledge_base.embedding import EmbeddingService

        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.randn(1, 384).astype(np.float32)
        mock_st_cls.return_value = mock_model

        svc = EmbeddingService()
        svc.load()
        result = svc.encode_single("hello")

        assert isinstance(result, list)
        assert len(result) == 384

    @patch("knowledge_base.embedding.SentenceTransformer", create=True)
    def test_load_idempotent(self, mock_st_cls: MagicMock) -> None:
        from knowledge_base.embedding import EmbeddingService

        mock_st_cls.return_value = MagicMock()

        svc = EmbeddingService()
        svc.load()
        svc.load()  # second call should be no-op
        assert mock_st_cls.call_count == 1


# ══════════════════════════════════════════════════════════════════
#  Test: Keyword Scoring
# ══════════════════════════════════════════════════════════════════


class TestKeywordScoring:
    def test_tokenise_lowercase(self) -> None:
        tokens = _tokenise("Hello World 123!")
        assert tokens == ["hello", "world", "123"]

    def test_tokenise_empty(self) -> None:
        assert _tokenise("") == []

    def test_keyword_score_perfect_match(self) -> None:
        score = _keyword_score("insulin dosing", "insulin dosing guidelines")
        assert score > 0.5

    def test_keyword_score_no_match(self) -> None:
        score = _keyword_score("insulin dosing", "the weather is nice today")
        assert score == 0.0

    def test_keyword_score_partial_match(self) -> None:
        score = _keyword_score(
            "insulin carb ratio",
            "The insulin-to-carb ratio (ICR) determines dosing.",
        )
        assert 0.0 < score <= 1.0

    def test_keyword_score_range(self) -> None:
        score = _keyword_score("test query", "test query test query")
        assert 0.0 <= score <= 1.0

    def test_keyword_score_empty_query(self) -> None:
        assert _keyword_score("", "some document") == 0.0

    def test_keyword_score_empty_document(self) -> None:
        assert _keyword_score("some query", "") == 0.0


# ══════════════════════════════════════════════════════════════════
#  Test: Search Service (Mocked Milvus)
# ══════════════════════════════════════════════════════════════════


class TestSearchService:
    """Integration-style tests with Milvus calls mocked."""

    @staticmethod
    def _make_mock_hit(
        hit_id: int, content: str, source: str, category: str, score: float
    ) -> MagicMock:
        hit = MagicMock()
        hit.id = hit_id
        hit.score = score
        hit.entity.get = lambda k, default="": {
            "content": content,
            "source": source,
            "category": category,
        }.get(k, default)
        return hit

    @patch("knowledge_base.search.SearchService.connect")
    def test_search_returns_results(self, mock_connect: MagicMock) -> None:
        from knowledge_base.embedding import EmbeddingService
        from knowledge_base.search import SearchService

        # Mock embedding service
        mock_embedder = MagicMock(spec=EmbeddingService)
        mock_embedder.encode_single.return_value = [0.1] * 384

        svc = SearchService(embedding_service=mock_embedder)

        # Mock collection
        mock_collection = MagicMock()
        hit1 = self._make_mock_hit(1, "Insulin bolus calculation", "ADA", "insulin_dosing", 0.92)
        hit2 = self._make_mock_hit(2, "Carb counting basics", "ADA", "carb_counting", 0.85)
        mock_collection.search.return_value = [[hit1, hit2]]
        svc._collection = mock_collection

        query = SearchQuery(query="insulin dosing for 60g carb", top_k=2)
        response = svc.search(query)

        assert isinstance(response, SearchResponse)
        assert response.total_found == 2
        assert response.results[0].vector_score >= response.results[1].vector_score or \
               response.results[0].combined_score >= response.results[1].combined_score

    @patch("knowledge_base.search.SearchService.connect")
    def test_search_category_filter(self, mock_connect: MagicMock) -> None:
        from knowledge_base.embedding import EmbeddingService
        from knowledge_base.search import SearchService

        mock_embedder = MagicMock(spec=EmbeddingService)
        mock_embedder.encode_single.return_value = [0.1] * 384

        svc = SearchService(embedding_service=mock_embedder)
        mock_collection = MagicMock()
        svc._collection = mock_collection
        mock_collection.search.return_value = [[]]

        query = SearchQuery(
            query="emergency", top_k=3, category_filter="emergency_protocol"
        )
        svc.search(query)

        # Verify category filter was passed
        call_kwargs = mock_collection.search.call_args
        assert 'category == "emergency_protocol"' in (call_kwargs.kwargs.get("expr", "") or call_kwargs[1].get("expr", ""))

    @patch("knowledge_base.search.SearchService.connect")
    def test_search_empty_results(self, mock_connect: MagicMock) -> None:
        from knowledge_base.embedding import EmbeddingService
        from knowledge_base.search import SearchService

        mock_embedder = MagicMock(spec=EmbeddingService)
        mock_embedder.encode_single.return_value = [0.1] * 384

        svc = SearchService(embedding_service=mock_embedder)
        mock_collection = MagicMock()
        mock_collection.search.return_value = [[]]
        svc._collection = mock_collection

        query = SearchQuery(query="nonexistent topic", top_k=5)
        response = svc.search(query)

        assert response.total_found == 0
        assert response.results == []

    def test_search_raises_if_not_connected(self) -> None:
        from knowledge_base.embedding import EmbeddingService
        from knowledge_base.search import SearchService

        mock_embedder = MagicMock(spec=EmbeddingService)
        svc = SearchService(embedding_service=mock_embedder)

        with pytest.raises(RuntimeError, match="Not connected"):
            svc.search(SearchQuery(query="test"))

    @patch("knowledge_base.search.SearchService.connect")
    def test_reranking_boosts_keyword_hits(self, mock_connect: MagicMock) -> None:
        """A candidate with lower vector score but strong keyword match
        should rank higher after re-ranking."""
        from knowledge_base.embedding import EmbeddingService
        from knowledge_base.search import SearchService

        mock_embedder = MagicMock(spec=EmbeddingService)
        mock_embedder.encode_single.return_value = [0.1] * 384

        svc = SearchService(embedding_service=mock_embedder, alpha=0.5)
        mock_collection = MagicMock()

        # Hit A: high vector score, low keyword relevance
        hit_a = self._make_mock_hit(
            1, "General overview of patient care", "WHO", "clinical", 0.90
        )
        # Hit B: lower vector score, but content matches query keywords
        hit_b = self._make_mock_hit(
            2,
            "Insulin bolus calculation for carbohydrate counting",
            "ADA",
            "insulin_dosing",
            0.80,
        )
        mock_collection.search.return_value = [[hit_a, hit_b]]
        svc._collection = mock_collection

        query = SearchQuery(query="insulin carbohydrate bolus", top_k=2)
        response = svc.search(query)

        # Hit B should be re-ranked higher due to keyword match
        assert response.results[0].content == hit_b.entity.get("content")


# ══════════════════════════════════════════════════════════════════
#  Test: Full Pipeline (Chunk → Embed mock → records)
# ══════════════════════════════════════════════════════════════════


class TestFullPipeline:
    """End-to-end pipeline test without Milvus."""

    def test_chunk_all_guidelines(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        chunker = ChunkingService()
        chunks = chunker.chunk_documents(all_documents)

        # Should produce meaningful number of chunks
        assert len(chunks) >= 25, f"Expected ≥25 chunks, got {len(chunks)}"

        # Each chunk should have non-empty content
        for c in chunks:
            assert c.content.strip()

    @patch("knowledge_base.embedding.SentenceTransformer", create=True)
    def test_embed_all_chunks(
        self,
        mock_st_cls: MagicMock,
        all_documents: list[MedicalDocument],
    ) -> None:
        from knowledge_base.embedding import EmbeddingService

        chunker = ChunkingService()
        chunks = chunker.chunk_documents(all_documents)

        # Mock model returns correct shape
        n = len(chunks)
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.randn(n, 384).astype(np.float32)
        mock_st_cls.return_value = mock_model

        embedder = EmbeddingService()
        embedder.load()
        texts = [c.content for c in chunks]
        embeddings = embedder.encode(texts)

        assert embeddings.shape == (n, 384)
        assert embeddings.dtype == np.float32

    def test_embedding_records_from_chunks(
        self, all_documents: list[MedicalDocument]
    ) -> None:
        """Build EmbeddingRecord objects from chunks + fake vectors."""
        chunker = ChunkingService()
        chunks = chunker.chunk_documents(all_documents)

        records = []
        for c in chunks:
            records.append(
                EmbeddingRecord(
                    chunk_id=c.chunk_id,
                    content=c.content,
                    source=c.source,
                    category=c.category,
                    embedding=[0.0] * 384,
                )
            )

        assert len(records) == len(chunks)
        for r in records:
            assert len(r.embedding) == 384

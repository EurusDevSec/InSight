"""
FastAPI application for the RAG advisory service.

Endpoints:
    POST /api/rag/advise   — Main RAG advisory endpoint
    GET  /health           — Service health check
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()  # load .env before os.getenv calls
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from knowledge_base.embedding import EmbeddingService
from knowledge_base.search import SearchService
from personalization.clinical_rules import ClinicalRules
from personalization.emergency import EmergencyDetector
from personalization.grounding import GroundingValidator
from rag_pipeline.llm_client import LLMClient
from rag_pipeline.prompt_builder import PromptBuilder
from rag_pipeline.rag_service import RAGService
from rag_pipeline.schemas import AdviceRequest, AdviceResponse

logger = logging.getLogger(__name__)

# ── Application Factory ───────────────────────────────────────────

app = FastAPI(
    title="InSight RAG Service",
    description="Glycemic Load advisory powered by Retrieval-Augmented Generation",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Service Singletons (created on startup) ───────────────────────

_rag_service: RAGService | None = None
_clinical_rules: ClinicalRules | None = None
_emergency_detector = EmergencyDetector()
_grounding_validator: GroundingValidator | None = None


@app.on_event("startup")
async def _startup() -> None:
    global _rag_service, _clinical_rules, _grounding_validator
    import time as _time
    t_start = _time.time()

    # Embedding
    embedding_svc = EmbeddingService()
    embedding_svc.load()

    # Search
    search_svc = SearchService(
        embedding_service=embedding_svc,
        milvus_host=os.getenv("MILVUS_HOST", "localhost"),
        milvus_port=int(os.getenv("MILVUS_PORT", "19530")),
    )
    search_svc.connect()

    # LLM
    llm = LLMClient(
        model=os.getenv("LLM_MODEL", "gemini-2.0-flash"),
        base_url=os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        api_key=os.getenv("GEMINI_API_KEY", ""),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
    )
    llm.connect()

    # RAG orchestrator
    _rag_service = RAGService(
        search_service=search_svc,
        llm_client=llm,
        top_k=int(os.getenv("RAG_TOP_K", "5")),
    )

    # Personalization
    _clinical_rules = ClinicalRules()
    _grounding_validator = GroundingValidator()

    startup_ms = (_time.time() - t_start) * 1000
    logger.info(f"RAG service started successfully in {startup_ms:.0f}ms")


# ── Endpoints ──────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "rag-service", "version": "0.3.0"}


@app.post("/api/rag/advise", response_model=AdviceResponse)
async def advise(request: AdviceRequest, debug: bool = False) -> AdviceResponse:
    """Main RAG advisory endpoint.

    Flow: query → retrieve medical chunks → build prompt → LLM → structured response.
    Pass debug=true to include retrieved chunks, prompt preview, and raw LLM output.
    """
    if _rag_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        response = _rag_service.advise(request, debug=debug)
        return response
    except Exception:
        logger.exception("Error in RAG advise endpoint")
        raise HTTPException(status_code=500, detail="Internal RAG service error")


# ── Entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

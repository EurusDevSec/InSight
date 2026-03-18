"""
InSight RAG Pipeline Module — Task 3.2
=======================================

Retrieval-Augmented Generation pipeline:
    query → retrieve medical chunks → build prompt → generate advice.

Components:
    - schemas: Request/Response Pydantic models
    - llm_client: OpenAI-compatible LLM client
    - prompt_builder: Prompt template construction
    - rag_service: Main RAG orchestrator
"""

from rag_pipeline.llm_client import LLMClient
from rag_pipeline.prompt_builder import PromptBuilder
from rag_pipeline.rag_service import RAGService
from rag_pipeline.schemas import AdviceRequest, AdviceResponse

__all__ = [
    "LLMClient",
    "PromptBuilder",
    "RAGService",
    "AdviceRequest",
    "AdviceResponse",
]

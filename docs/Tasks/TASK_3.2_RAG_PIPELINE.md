## 💡 Context

> **Task ID**: S7-001
> **Phase**: Phase 3 - RAG Agent & Logic
> **Sprint**: Sprint 7 - RAG Pipeline
> **Status**: ✅ DONE
> **Created**: 06/03/2026
> **Target**: 24/03/2026
> **Assignee**: Hoàng (chính), Việt, Hoài
> **Blocked by**: TASK_3.1
> **Blocks**: TASK_3.3, TASK_4.3

> Xây dựng RAG pipeline (Python FastAPI + Gemini API) từ query đến response.

---

## ☺️ Refined

> **User Story:**
> As a **diabetic patient**, I want to **receive contextual insulin advice based on my meal's GL** so that **I can manage my blood sugar accurately.**

**Acceptance Criteria:**

- [x] LLM Client setup (Python OpenAI-compatible, Gemini API)
- [x] RAG pipeline: query → retrieve chunks → generate response
- [x] API endpoint `POST /api/rag/advise` hoạt động
- [x] Response quality: 56 test scenarios pass (đúng ngữ cảnh)

---

## 🛠️ Implementation

### Subtasks

- [x] 3.2.1 Setup LLM Client (OpenAI-compatible, Gemini API) — **Hoàng** → `rag_pipeline/llm_client.py`
- [x] 3.2.2 Implement RAG pipeline (query → retrieve → generate) — **Hoàng** → `rag_pipeline/rag_service.py`
- [x] 3.2.3 Tạo API endpoints cho RAG service — **Việt** → `main.py` (FastAPI)
- [x] 3.2.4 Test response quality (56 test scenarios) — **Hoài** → `tests/test_rag_pipeline.py`

### Branch & PR

- [x] Branch: `feat/s7/rag-pipeline`
- [x] PR Created
- [x] 56/56 test scenarios pass

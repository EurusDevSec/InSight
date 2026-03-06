## 💡 Context

> **Task ID**: S7-001
> **Phase**: Phase 3 - RAG Agent & Logic
> **Sprint**: Sprint 7 - RAG Pipeline
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 24/03/2026
> **Assignee**: Hoàng (chính), Việt, Hoài
> **Blocked by**: TASK_3.1
> **Blocks**: TASK_3.3, TASK_4.3

> Tích hợp LangChain4j trong Spring Boot, xây dựng RAG pipeline từ query đến response.

---

## ☺️ Refined

> **User Story:**
> As a **diabetic patient**, I want to **receive contextual insulin advice based on my meal's GL** so that **I can manage my blood sugar accurately.**

**Acceptance Criteria:**

- [ ] LangChain4j setup trong Spring Boot
- [ ] RAG pipeline: query → retrieve chunks → generate response
- [ ] API endpoint `POST /api/rag/advise` hoạt động
- [ ] Response quality: 10 test scenarios pass (đúng ngữ cảnh)

---

## 🛠️ Implementation

### Subtasks

- [ ] 3.2.1 Setup LangChain4j trong Spring Boot — **Hoàng**
- [ ] 3.2.2 Implement RAG pipeline (query → retrieve → generate) — **Hoàng**
- [ ] 3.2.3 Tạo API endpoints cho RAG service — **Việt**
- [ ] 3.2.4 Test response quality (10 test scenarios) — **Hoài**

### Branch & PR

- [ ] Branch: `feat/s7/rag-pipeline`
- [ ] PR Created
- [ ] 10/10 test scenarios pass

## 💡 Context

> **Task ID**: S6-001
> **Phase**: Phase 3 - RAG Agent & Logic
> **Sprint**: Sprint 6 - Kiến thức Y khoa
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 22/03/2026
> **Assignee**: Hoàng (chính), Hoài
> **Blocked by**: TASK_1.2 (Milvus collections cần ready)
> **Blocks**: TASK_3.2 (RAG pipeline cần knowledge base)

> Thu thập, chuẩn hóa, embedding hướng dẫn y khoa ADA/MOH vào Milvus vector DB.

---

## ☺️ Refined

> **User Story:**
> As a **RAG engineer**, I want to **have medical guidelines indexed in Milvus** so that **the RAG Agent can retrieve accurate insulin dosing information.**

**Acceptance Criteria:**

- [ ] Hướng dẫn ADA/MOH thu thập xong (≥ 20 tài liệu)
- [ ] Tài liệu chunked & chuẩn hóa
- [ ] Embeddings nhập vào Milvus thành công
- [ ] Hybrid search (keyword + vector + re-ranking) hoạt động
- [ ] Search query test: "liều insulin cho 60g Carb" trả về kết quả đúng

---

## 🛠️ Implementation

### Subtasks

- [ ] 3.1.1 Thu thập hướng dẫn ADA/MOH về quản lý tiểu đường — **Hoài**
- [ ] 3.1.2 Chuẩn hóa & chunk tài liệu y khoa — **Hoàng**
- [ ] 3.1.3 Embedding & nhập vào Milvus — **Hoàng**
- [ ] 3.1.4 Implement hybrid search (keyword + vector + re-ranking) — **Hoàng**

### Branch & PR

- [ ] Branch: `feat/s6/knowledge-base`
- [ ] PR Created
- [ ] Hybrid search verified

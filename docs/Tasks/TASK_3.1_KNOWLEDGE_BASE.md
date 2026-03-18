## 💡 Context

> **Task ID**: S6-001
> **Phase**: Phase 3 - RAG Agent & Logic
> **Sprint**: Sprint 6 - Kiến thức Y khoa
> **Status**: ✅ DONE
> **Created**: 06/03/2026
> **Target**: 22/03/2026
> **Completed**: 18/03/2026 (E2E ingestion + search verified)
> **Assignee**: Hoàng (chính), Hoài
> **Blocked by**: TASK_1.2 (Milvus collections cần ready)
> **Blocks**: TASK_3.2 (RAG pipeline cần knowledge base)

> Thu thập, chuẩn hóa, embedding hướng dẫn y khoa ADA/MOH vào Milvus vector DB.

---

## ☺️ Refined

> **User Story:**
> As a **RAG engineer**, I want to **have medical guidelines indexed in Milvus** so that **the RAG Agent can retrieve accurate insulin dosing information.**

**Acceptance Criteria:**

- [x] Hướng dẫn ADA/MOH thu thập xong (≥ 20 tài liệu) → **26 tài liệu, 7 categories, 5 sources**
- [x] Tài liệu chunked & chuẩn hóa → **ChunkingService, 46 chunks, max 1200 chars, overlap 150**
- [x] Embeddings nhập vào Milvus thành công → **46 rows inserted, CUDA GPU, 8.4s (18/03/2026)**
- [x] Hybrid search (keyword + vector + re-ranking) hoạt động → **α=0.7 vector + 0.3 BM25, score=0.709 cho bolus query**
- [x] Search query test: "liều insulin cho 60g Carb" trả về kết quả đúng → **E2E verified: [carb_counting] ADA Nutrition, score=0.508; [insulin_dosing] ADA Standards, score=0.709**

---

## 🛠️ Implementation

### Subtasks

- [x] 3.1.1 Thu thập hướng dẫn ADA/MOH về quản lý tiểu đường — **Hoài** (26 docs ✅)
- [x] 3.1.2 Chuẩn hóa & chunk tài liệu y khoa — **Hoàng** (ChunkingService, 46 chunks ✅)
- [x] 3.1.3 Embedding & nhập vào Milvus — **Hoàng** (46 rows inserted, CUDA GPU ✅)
- [x] 3.1.4 Implement hybrid search (keyword + vector + re-ranking) — **Hoàng** (SearchService, E2E verified ✅)

### Branch & PR

- [x] Branch: `feat/s6/knowledge-base`
- [ ] PR Created
- [x] Hybrid search verified (50/50 unit tests + E2E Milvus search 18/03/2026)

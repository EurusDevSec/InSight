## 💡 Context

> **Task ID**: S8-001
> **Phase**: Phase 3 - RAG Agent & Logic
> **Sprint**: Sprint 8 - Cá nhân hóa
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 01/06/2026
> **Assignee**: Hoàng (chính), Hoài
> **Blocked by**: TASK_3.2
> **Blocks**: TASK_4.3 (E2E cần RAG complete)

> Dynamic prompting dựa trên glucose hiện tại, thuốc đang dùng. Giao thức khẩn cấp. Strict RAG Grounding.

---

## ☺️ Refined

> **User Story:**
> As a **diabetic patient**, I want **personalized insulin advice based on my current glucose and medications** so that **the recommendation is clinically accurate for MY situation.**

**Acceptance Criteria:**

- [ ] Dynamic prompt thay đổi dựa trên glucose level + thuốc
- [ ] Giao thức khẩn cấp: phát hiện hạ đường huyết → hướng dẫn cấp cứu
- [ ] Strict RAG Grounding: response chỉ từ chunks hợp lệ (chống hallucination)
- [ ] Test scenarios lâm sàng pass (glucose thấp/bình thường/cao)

---

## 🛠️ Implementation

### Subtasks

- [ ] 3.3.1 Implement dynamic prompt dựa trên glucose + thuốc — **Hoàng**
- [ ] 3.3.2 Implement giao thức khẩn cấp (hạ đường huyết) — **Hoàng**
- [ ] 3.3.3 Strict RAG Grounding (chống hallucination) — **Hoàng**
- [ ] 3.3.4 Test với scenarios lâm sàng — **Hoài**

### Branch & PR

- [ ] Branch: `feat/s8/personalization`
- [ ] PR Created
- [ ] Clinical scenarios verified

## 💡 Context

> **Task ID**: S10-002
> **Phase**: Phase 4 - Tích hợp & Mobile
> **Sprint**: Sprint 10 - Tích hợp E2E
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 26/03/2026
> **Assignee**: Hoàng (chính), Hoài
> **Blocked by**: TASK_4.2
> **Blocks**: TASK_5.1 (UAT cần E2E working)

> Test end-to-end: Ảnh → GL → Tư vấn. Panic Mode ≤ 1s. Disclaimer hiển thị.

---

## ☺️ Refined

> **User Story:**
> As a **QA tester**, I want to **verify the full pipeline works within latency targets** so that **we can proceed to UAT.**

**Acceptance Criteria:**

- [ ] Full pipeline: Ảnh → Tư vấn hoàn thành trong ≤ 5 giây
- [ ] Panic Mode: ≤ 1 giây response
- [ ] Disclaimer UI hiển thị đúng ở mọi kết quả
- [ ] No critical crashes trong 10 test runs liên tiếp

---

## 🛠️ Implementation

### Subtasks

- [ ] 4.3.1 Full pipeline test: Ảnh → Tư vấn ≤ 5 giây — **Hoàng**
- [ ] 4.3.2 Panic Mode test: ≤ 1 giây — **Hoàng**
- [ ] 4.3.3 Disclaimer UI hiển thị đúng — **Hoài**

### Branch & PR

- [ ] Branch: `test/s10/e2e-testing`
- [ ] PR Created
- [ ] All latency targets met

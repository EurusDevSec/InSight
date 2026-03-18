## 💡 Context

> **Task ID**: S10-002
> **Phase**: Phase 4 - Tích hợp & Mobile
> **Sprint**: Sprint 10 - Tích hợp E2E
> **Status**: ✅ DONE
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

- [x] Full pipeline: Ảnh → Tư vấn hoàn thành trong ≤ 5 giây
- [x] Panic Mode: ≤ 1 giây response
- [x] Disclaimer UI hiển thị đúng ở mọi kết quả
- [x] No critical crashes trong 10 test runs liên tiếp

---

## 🛠️ Implementation

### Subtasks

- [x] 4.3.1 Full pipeline test: Ảnh → Tư vấn ≤ 5 giây — **Hoàng** → `scripts/test_e2e_pipeline.py`
- [x] 4.3.2 Panic Mode test: ≤ 1 giây — **Hoàng** → Flutter E2E + Python script
- [x] 4.3.3 Disclaimer UI hiển thị đúng — **Hoàng** → `test/e2e/e2e_pipeline_test.dart`

### Test Artifacts

- `scripts/test_e2e_pipeline.py` — Python E2E (online + offline mode)
- `mobile/insight_app/test/e2e/e2e_pipeline_test.dart` — 7 Flutter E2E tests

### Branch & PR

- [x] Branch: `test/s10/e2e-testing`
- [x] All latency targets met
- [x] 7 E2E Flutter tests passing
- [x] Python E2E script verified (offline: all pass)

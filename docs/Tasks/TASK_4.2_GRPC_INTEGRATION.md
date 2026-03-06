## 💡 Context

> **Task ID**: S10-001
> **Phase**: Phase 4 - Tích hợp & Mobile
> **Sprint**: Sprint 10 - Tích hợp E2E
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 25/03/2026
> **Assignee**: Việt (chính)
> **Blocked by**: TASK_4.1, TASK_2.5, TASK_3.2
> **Blocks**: TASK_4.3

> Implement gRPC client/server, Kafka messaging giữa Flutter ↔ API Gateway ↔ Vision ↔ RAG.

---

## ☺️ Refined

> **User Story:**
> As a **developer**, I want to **connect all services via gRPC and Kafka** so that **the full pipeline works end-to-end.**

**Acceptance Criteria:**

- [ ] gRPC client trong Flutter gửi được ảnh
- [ ] gRPC server trong API Gateway nhận và route
- [ ] Kafka messaging giữa services hoạt động
- [ ] Full pipeline: Flutter → Gateway → Vision → RAG → Flutter

---

## 🛠️ Implementation

### Subtasks

- [ ] 4.2.1 Implement gRPC client trong Flutter — **Việt**
- [ ] 4.2.2 Implement gRPC server trong API Gateway — **Việt**
- [ ] 4.2.3 Kafka messaging giữa services — **Việt**

### Branch & PR

- [ ] Branch: `feat/s10/grpc-integration`
- [ ] PR Created
- [ ] E2E pipeline verified

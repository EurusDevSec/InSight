## 💡 Context

> **Task ID**: S10-001
> **Phase**: Phase 4 - Tích hợp & Mobile
> **Sprint**: Sprint 10 - Tích hợp E2E
> **Status**: ✅ DONE
> **Created**: 06/03/2026
> **Target**: 25/03/2026
> **Assignee**: Hoàng (chính)
> **Blocked by**: TASK_4.1, TASK_2.5, TASK_3.2
> **Blocks**: TASK_4.3

> Implement API Gateway orchestration: Flutter → Gateway → Vision → RAG → Flutter. REST proxy pattern + Kafka events.

---

## ☺️ Refined

> **User Story:**
> As a **developer**, I want to **connect all services via the API Gateway** so that **the full pipeline works end-to-end.**

**Acceptance Criteria:**

- [x] Flutter gửi ảnh qua Gateway (multipart POST)
- [x] API Gateway nhận, forwarding đến Vision + RAG
- [x] Kafka messaging cho audit events
- [x] Full pipeline: Flutter → Gateway → Vision → RAG → Flutter

> **Note:** Kiến trúc thực tế dùng REST proxy thay vì raw gRPC. Proto file phục vụ mục đích API contract documentation.

---

## 🛠️ Implementation

### Subtasks

- [x] 4.2.1 Flutter refactor: single Gateway call thay vì gọi trực tiếp Vision/RAG — **Hoàng** → `api_service.dart`, `meal_viewmodel.dart`
- [x] 4.2.2 API Gateway REST endpoint: `POST /api/gateway/analyze` — **Hoàng** → `AnalysisController.java`, `PipelineService.java`
- [x] 4.2.3 Service clients: VisionServiceClient + RagServiceClient — **Hoàng** → `client/`
- [x] 4.2.4 Kafka event publishing — **Hoàng** → `KafkaEventPublisher.java`
- [x] 4.2.5 Proto contract update (API documentation) — **Hoàng** → `insight.proto`
- [x] 4.2.6 Gateway tests: 15 tests (5 controller + 10 pipeline) — **Hoàng**
- [x] 4.2.7 Flutter tests: 40 tests passing after refactor — **Hoàng**

### Architecture Decision

- **REST proxy** thay vì gRPC (thực tế cho đồ án, Python services là REST)
- **Graceful degradation**: RAG fail → Vision-only kết quả + warning
- **Non-blocking Kafka**: audit events fire-and-forget

### Branch & PR

- [x] Branch: `feat/s10/grpc-integration`
- [x] E2E pipeline verified
- [x] 15 Gateway tests passing
- [x] 40 Flutter tests passing

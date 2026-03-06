## 💡 Context

> **Task ID**: S1-001
> **Phase**: Phase 1 - Nền tảng & Dữ liệu
> **Sprint**: Sprint 1 - Hạ tầng
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 17/03/2026
> **Assignee**: Việt (chính), Hoàng, Hoài
> **Blocked by**: TASK_1.0 (Project Kickoff)
> **Blocks**: TASK_1.2, TASK_1.3

> Setup hạ tầng dev: Docker Compose cho toàn bộ services, Spring Boot skeleton, Python Vision skeleton, CI/CD.

---

## ☺️ Refined

> **User Story:**
> As a **developer**, I want to **have a fully working dev environment with Docker Compose** so that **I can start implementing services immediately.**

**Acceptance Criteria:**

- [ ] Docker Compose chạy PostgreSQL + Milvus + Redis + Kafka thành công
- [ ] Spring Boot project skeleton (API Gateway) compile + run
- [ ] Python Vision Service skeleton (FastAPI) chạy được
- [ ] CI/CD pipeline (GitHub Actions) chạy lint + test + build xanh
- [ ] `docker compose up` → tất cả services healthy

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.1.1 Setup Docker Compose (PostgreSQL + Milvus + Redis + Kafka) — **Việt**
- [ ] 1.1.2 Setup Spring Boot project skeleton (API Gateway) — **Việt**
- [ ] 1.1.3 Setup Python Vision Service skeleton (FastAPI/TorchServe) — **Hoàng**
- [ ] 1.1.4 Setup CI/CD pipeline (GitHub Actions: lint, test, build) — **Hoài**

### Branch & PR

- [ ] Branch: `infra/s1/environment-setup`
- [ ] PR Created
- [ ] `docker compose up` thành công
- [ ] CI/CD pipeline xanh

---

## 📝 Notes

> **Docker Compose services:** postgres:16, milvus:2.3, redis:7, kafka (bitnami), api-gateway (Spring Boot), vision-service (Python)
> **Ports:** PostgreSQL 5432, Milvus 19530, Redis 6379, Kafka 9092, API Gateway 8080, Vision 8000

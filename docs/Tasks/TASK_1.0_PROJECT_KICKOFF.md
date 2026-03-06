## 💡 Context

> **Task ID**: S0-001
> **Phase**: Phase 1 - Nền tảng & Dữ liệu
> **Sprint**: Sprint 0 - Khởi động
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 07/03/2026
> **Assignee**: Hoàng (chính), Hoài, Việt
> **Blocked by**: Không
> **Blocks**: TASK_1.1, TASK_1.2, TASK_1.3 (tất cả task Phase 1 phụ thuộc vào kickoff)

> Khởi động dự án InSight: tạo repo, viết tài liệu kiến trúc, thiết kế schema DB, định nghĩa API contracts.
> Đây là nền tảng cho toàn bộ dự án, team phải đồng bộ trước khi code.

---

## ☺️ Refined

> **User Story:**
> As a **development team**, we want to **set up the project repository with architecture docs, DB schema, and API contracts** so that **all team members have a shared understanding and can start development in Sprint 1.**

**Acceptance Criteria:**

- [ ] GitHub repo tạo xong với branch strategy (main → develop → feature/*)
- [ ] README.md, .gitignore, PR template có đầy đủ
- [ ] Tài liệu kiến trúc hệ thống (architecture.md) viết xong
- [ ] API contracts (Proto3 files + OpenAPI spec) định nghĩa xong
- [ ] Database schema (ERD) thiết kế xong
- [ ] Team đã họp kickoff, hiểu rõ plan Sprint 1

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.0.1 Tạo GitHub repo + branch strategy — **Hoàng**
- [ ] 1.0.2 Setup README, .gitignore, PR template — **Hoài**
- [ ] 1.0.3 Viết tài liệu kiến trúc hệ thống (architecture.md) — **Hoàng**
- [ ] 1.0.4 Định nghĩa API contracts (Proto3 + OpenAPI) — **Hoàng**
- [ ] 1.0.5 Thiết kế Database schema (ERD) — **Việt**
- [ ] 1.0.6 Họp kickoff — phân công chi tiết Sprint 1 — **Hoàng**

### Branch & PR

- [ ] Branch: `docs/s0/project-kickoff`
- [ ] PR Created
- [ ] All docs reviewed by Hoàng

---

## 📝 Notes

> **Deliverables:**
> - architecture.md với mermaid diagrams
> - .proto files cho gRPC services
> - ERD diagram (dbdiagram.io hoặc draw.io)
> - README với tech stack, cách chạy dev

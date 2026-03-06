## 💡 Context

> **Task ID**: S1-002
> **Phase**: Phase 1 - Nền tảng & Dữ liệu
> **Sprint**: Sprint 1 - Hạ tầng
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 22/03/2026
> **Assignee**: Việt (chính), Hoàng
> **Blocked by**: TASK_1.1 (Environment Setup)
> **Blocks**: TASK_2.x, TASK_3.x

> Implement database schema, Milvus collections, Redis config, migration scripts.

---

## ☺️ Refined

> **User Story:**
> As a **backend developer**, I want to **have the database schema and vector DB ready** so that **services can persist and query data.**

**Acceptance Criteria:**

- [ ] PostgreSQL schema (users, meals, food_items, gl_records) implemented
- [ ] Milvus collections (medical_knowledge, food_embeddings) created
- [ ] Redis cache config (sessions, rate limiting) ready
- [ ] Migration scripts (Flyway/Liquibase) chạy thành công
- [ ] Seed data cho food_items (10 món VN) có trong migration

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.2.1 Implement PostgreSQL schema (users, meals, food_items, gl_records) — **Việt**
- [ ] 1.2.2 Setup Milvus collections (medical_knowledge, food_embeddings) — **Hoàng**
- [ ] 1.2.3 Setup Redis cache config (sessions, rate limiting) — **Việt**
- [ ] 1.2.4 Viết migration scripts (Flyway/Liquibase) — **Việt**

### Branch & PR

- [ ] Branch: `feat/s1/database-schema`
- [ ] PR Created
- [ ] Migrations chạy thành công
- [ ] Hoàng reviewed

---

## 📝 Notes

> **Tables chính:** users (id, name, glucose_level, medications), meals (id, user_id, image_url, gl_result), food_items (id, name, carb_per_100g, gi, density_factor), gl_records (id, meal_id, total_carb, total_gl, insulin_suggestion)

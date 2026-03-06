## 💡 Context

> **Task ID**: S5-001
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 5 - Tính thể tích
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 19/03/2026
> **Assignee**: Việt (chính), Hoàng
> **Blocked by**: TASK_2.3, TASK_2.4
> **Blocks**: TASK_3.x (RAG cần GL input), TASK_4.3 (E2E testing)

> Implement công thức tính thể tích từ depth map, áp dụng Density Factor, tính Carb → GL.

---

## ☺️ Refined

> **User Story:**
> As a **user**, I want to **get accurate Glycemic Load from a food photo** so that **I can calculate my insulin dose.**

**Acceptance Criteria:**

- [ ] Công thức tích phân V = ∫∫ depth(x,y) dA implemented
- [ ] Density Factor áp dụng cho món nước (Phở, Bún)
- [ ] Pipeline: Thể tích → Khối lượng → Carb → GL
- [ ] Sai số thể tích ≤ 15% so với ground-truth

---

## 🛠️ Implementation

### Subtasks

- [ ] 2.5.1 Implement công thức tích phân V = ∫∫ depth(x,y) dA — **Việt**
- [ ] 2.5.2 Thiết kế & áp dụng Density Factor cho món nước (Phở, Bún) — **Hoàng**
- [ ] 2.5.3 Tính Carb → GL từ thể tích + dinh dưỡng DB — **Việt**

### Branch & PR

- [ ] Branch: `feat/s5/volume-estimation`
- [ ] PR Created
- [ ] Sai số ≤ 15% trên 10 mẫu

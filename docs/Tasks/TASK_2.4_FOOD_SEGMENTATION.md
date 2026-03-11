## 💡 Context

> **Task ID**: S4-002
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 4 - Hiệu chuẩn
> **Status**: ✅ DONE
> **Created**: 06/03/2026
> **Target**: 18/03/2026
> **Assignee**: Việt (chính), Hoài
> **Blocked by**: TASK_2.1
> **Blocks**: TASK_2.5 (volume cần biết vùng món ăn)

> Tích hợp SAM để phân đoạn vùng món ăn trong ảnh, tách khỏi nền và dụng cụ.

---

## ☺️ Refined

> **User Story:**
> As a **vision engineer**, I want to **segment food regions from the image** so that **volume estimation only applies to the food area.**

**Acceptance Criteria:**

- [x] SAM (Segment Anything Model) tích hợp cho food segmentation
- [x] Food region extraction từ depth map hoạt động
- [x] Test trên 10 món đã thu thập — mask chính xác

---

## 🛠️ Implementation

### Subtasks

- [x] 2.4.1 Tích hợp SAM cho food segmentation — **Việt**
- [x] 2.4.2 Implement food region extraction từ depth map — **Việt**
- [x] 2.4.3 Test trên 10 món đã thu thập — **Hoài**

### Branch & PR

- [x] Branch: `feat/s4/food-segmentation`
- [x] PR Created
- [x] Segmentation mask verified trên 10 mẫu

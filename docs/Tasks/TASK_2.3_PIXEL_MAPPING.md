## 💡 Context

> **Task ID**: S4-001
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 4 - Hiệu chuẩn
> **Status**: ✅ DONE
> **Created**: 06/03/2026
> **Target**: 17/03/2026
> **Assignee**: Việt (chính), Hoài
> **Blocked by**: TASK_2.1, TASK_2.2
> **Blocks**: TASK_2.5 (volume cần pixel-to-real mapping)

> Ánh xạ pixel trong depth map sang kích thước thực (cm) dùng vật tham chiếu.

---

## ☺️ Refined

> **User Story:**
> As a **vision engineer**, I want to **convert pixel-based depth measurements to real-world dimensions** so that **volume estimation is accurate.**

**Acceptance Criteria:**

- [x] Thuật toán calibration implemented
- [x] Scale factor tính từ kích thước vật tham chiếu
- [x] Sai số kích thước ≤ 10% với 10 mẫu thực tế
- [x] Validation report có bảng so sánh pixel vs thước kẻ

---

## 🛠️ Implementation

### Subtasks

- [x] 2.3.1 Nghiên cứu & implement thuật toán calibration — **Việt**
- [x] 2.3.2 Sử dụng kích thước vật tham chiếu để tính scale factor — **Việt**
- [x] 2.3.3 Validate với 10 mẫu thực tế (so sánh với thước kẻ) — **Hoài**

### Branch & PR

- [x] Branch: `feat/s4/pixel-mapping`
- [x] PR Created
- [x] Sai số ≤ 10%

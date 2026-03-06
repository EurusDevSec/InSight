## 💡 Context

> **Task ID**: S4-001
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 4 - Hiệu chuẩn
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 22/04/2026
> **Assignee**: Việt (chính), Hoài
> **Blocked by**: TASK_2.1, TASK_2.2
> **Blocks**: TASK_2.5 (volume cần pixel-to-real mapping)

> Ánh xạ pixel trong depth map sang kích thước thực (cm) dùng vật tham chiếu.

---

## ☺️ Refined

> **User Story:**
> As a **vision engineer**, I want to **convert pixel-based depth measurements to real-world dimensions** so that **volume estimation is accurate.**

**Acceptance Criteria:**

- [ ] Thuật toán calibration implemented
- [ ] Scale factor tính từ kích thước vật tham chiếu
- [ ] Sai số kích thước ≤ 10% với 10 mẫu thực tế
- [ ] Validation report có bảng so sánh pixel vs thước kẻ

---

## 🛠️ Implementation

### Subtasks

- [ ] 2.3.1 Nghiên cứu & implement thuật toán calibration — **Việt**
- [ ] 2.3.2 Sử dụng kích thước vật tham chiếu để tính scale factor — **Việt**
- [ ] 2.3.3 Validate với 10 mẫu thực tế (so sánh với thước kẻ) — **Hoài**

### Branch & PR

- [ ] Branch: `feat/s4/pixel-mapping`
- [ ] PR Created
- [ ] Sai số ≤ 10%

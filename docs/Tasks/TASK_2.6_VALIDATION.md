## 💡 Context

> **Task ID**: S5-002
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 5 - Tính thể tích
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 12/05/2026
> **Assignee**: Hoài (chính), Việt, Hoàng
> **Blocked by**: TASK_2.5
> **Blocks**: Không (nhưng kết quả ảnh hưởng Phase 3+)

> Validation toàn bộ Vision Engine: so sánh với ground-truth, tạo accuracy report.

---

## ☺️ Refined

> **User Story:**
> As a **researcher**, I want to **validate the Vision Engine accuracy** so that **I can report results for my thesis defense.**

**Acceptance Criteria:**

- [ ] So sánh kết quả 10 món với ground-truth (đổ nước)
- [ ] Bảng accuracy report (sai số theo từng món)
- [ ] Nếu sai số > 15% → pipeline được tối ưu lại

---

## 🛠️ Implementation

### Subtasks

- [ ] 2.6.1 So sánh kết quả với ground-truth (10 món) — **Hoài**
- [ ] 2.6.2 Tạo bảng accuracy report — **Hoài**
- [ ] 2.6.3 Tối ưu pipeline nếu sai số > 15% — **Việt + Hoàng**

### Branch & PR

- [ ] Branch: `feat/s5/validation`
- [ ] PR Created
- [ ] Accuracy report có đầy đủ

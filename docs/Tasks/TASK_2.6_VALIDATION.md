## 💡 Context

> **Task ID**: S5-002
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 5 - Tính thể tích
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 20/03/2026
> **Assignee**: Hoài (chính), Việt, Hoàng
> **Blocked by**: TASK_2.5
> **Blocks**: Không (nhưng kết quả ảnh hưởng Phase 3+)

> Validation toàn bộ Vision Engine: so sánh với ground-truth, tạo accuracy report.

---

## ☺️ Refined

> **User Story:**
> As a **researcher**, I want to **validate the Vision Engine accuracy** so that **I can report results for my thesis defense.**

**Acceptance Criteria:**

- [ ] So sánh kết quả trên Nutrition5k benchmark (N=100-500, lab-grade ground truth)
- [ ] So sánh kết quả trên VN demo samples (5-10 mẫu)
- [ ] Bảng accuracy report (sai số theo từng loại món, N5k + VN)
- [ ] Nếu sai số > 15% → pipeline được tối ưu lại

---

## 🛠️ Implementation

### Subtasks

- [ ] 2.6.1 So sánh kết quả với Nutrition5k ground-truth (N=100-500) — **Hoài**
- [ ] 2.6.2 So sánh kết quả với VN demo samples (5-10 mẫu) — **Hoài**
- [ ] 2.6.3 Tạo bảng accuracy report (benchmark + VN demo) — **Hoài**
- [ ] 2.6.4 Tối ưu pipeline nếu sai số > 15% — **Việt + Hoàng**

### Branch & PR

- [ ] Branch: `feat/s5/validation`
- [ ] PR Created
- [ ] Accuracy report có đầy đủ

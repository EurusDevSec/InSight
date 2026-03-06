## 💡 Context

> **Task ID**: S2-001
> **Phase**: Phase 1 - Nền tảng & Dữ liệu
> **Sprint**: Sprint 2 - Thu thập dữ liệu
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 12/03/2026
> **Assignee**: Hoài (chính), Hoàng
> **Blocked by**: TASK_1.0 (format dữ liệu cần Hoàng định nghĩa)
> **Blocks**: TASK_2.1, TASK_2.6 (Vision Engine cần dataset để test)

> Thu thập dataset 10 món Việt Nam phổ biến với ảnh + ground-truth thể tích + dữ liệu dinh dưỡng.

---

## ☺️ Refined

> **User Story:**
> As a **researcher**, I want to **have a dataset of 10 Vietnamese dishes with ground-truth volume and nutrition data** so that **I can train and validate the Vision Engine.**

**Acceptance Criteria:**

- [ ] JSON schema định nghĩa xong cho mỗi món ăn
- [ ] 10 món VN phổ biến đã chụp ảnh (≥ 3 góc, ≥ 2 cỡ bát mỗi món)
- [ ] Ground-truth thể tích đo bằng đổ nước cho mỗi mẫu
- [ ] Khối lượng thực tế từng thành phần đã cân
- [ ] Dữ liệu dinh dưỡng (Carb, GI, GL) tra cứu xong
- [ ] Density Factor DB cho ≥ 5 loại món nước VN
- [ ] Dataset validated & reviewed bởi Hoàng

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.3.1 Định nghĩa format dữ liệu (JSON schema cho mỗi món) — **Hoàng**
- [ ] 1.3.2 Chụp ảnh 10 món VN phổ biến (nhiều góc, nhiều cỡ bát) — **Hoài**
- [ ] 1.3.3 Đo ground-truth thể tích bằng đổ nước — **Hoài**
- [ ] 1.3.4 Cân khối lượng thực tế từng thành phần — **Hoài**
- [ ] 1.3.5 Tra cứu & nhập dữ liệu dinh dưỡng (Carb, GI, GL) — **Hoài**
- [ ] 1.3.6 Xây dựng Density Factor DB cho món VN — **Hoàng**
- [ ] 1.3.7 Validate & review dataset — **Hoàng**

### Branch & PR

- [ ] Branch: `feat/s2/data-collection`
- [ ] PR Created
- [ ] Dataset ≥ 10 món + ground-truth
- [ ] Hoàng reviewed

---

## 📝 Notes

> **10 món gợi ý:** Cơm trắng, Phở bò, Bún bò Huế, Bánh mì, Cơm tấm, Bún thịt nướng, Mì xào, Cháo, Xôi, Trà sữa
> **Density Factor mẫu:** Phở (30% đặc, 70% nước), Bún bò (35% đặc, 65% nước)
> **Tools:** Cân điện tử (±1g), cốc đong (±10ml), điện thoại chụp ảnh

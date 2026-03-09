## 💡 Context

> **Task ID**: S2-001
> **Phase**: Phase 1 - Nền tảng & Dữ liệu
> **Sprint**: Sprint 2 - Thu thập dữ liệu
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Updated**: 07/03/2026 — Chuyển sang Hybrid Approach (benchmark dataset + mini VN demo)
> **Target**: 12/03/2026
> **Assignee**: Hoàng (chính), Hoài
> **Blocked by**: TASK_1.0 (format dữ liệu cần Hoàng định nghĩa)
> **Blocks**: TASK_2.1, TASK_2.6 (Vision Engine cần dataset để test)

> **Hybrid Approach**: Sử dụng Nutrition5k benchmark (N=100-500, lab-grade ground truth) để phát triển & validate pipeline + thu thập 5-10 mẫu món Việt để demo thực tế. Import dữ liệu dinh dưỡng từ USDA/Bảng TPDD VN thay vì tra cứu thủ công.

---

## ☺️ Refined

> **User Story:**
> As a **researcher**, I want to **have a validated benchmark dataset (Nutrition5k) and a Vietnamese food demo dataset** so that **I can develop, validate the Vision Engine with statistical significance, and demonstrate real-world applicability on Vietnamese dishes.**

**Acceptance Criteria:**

- [ ] JSON schema định nghĩa xong cho mỗi mẫu
- [ ] Nutrition5k subset downloaded & parsed (100-500 mẫu, có RGB + depth + weight ground truth)
- [ ] Bảng dinh dưỡng Việt Nam (USDA/TPDD VN) imported vào DB tự động (≥ 10 món)
- [ ] Density Factor DB từ food science literature (≥ 10 loại món VN)
- [ ] 5-10 mẫu món Việt chụp ảnh demo (≥ 2 góc, estimated values từ literature)
- [ ] Scripts: download, parse, import, validate tự động
- [ ] Dataset validated & reviewed bởi Hoàng

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.3.1 Định nghĩa format dữ liệu (JSON schema cho mỗi món) — **Hoàng** (30 phút)
- [ ] 1.3.2 Download Nutrition5k subset + viết script parse sang InSight format — **Hoàng** (1 giờ)
- [ ] 1.3.3 Import bảng dinh dưỡng VN (USDA/TPDD VN) vào PostgreSQL — **Hoàng** (1 giờ)
- [ ] 1.3.4 Xây dựng Density Factor DB từ food science literature — **Hoàng** (30 phút)
- [ ] 1.3.5 Chụp 5-10 mẫu món Việt cho demo (estimated values) — **Hoài** (1-2 giờ)
- [ ] 1.3.6 Compile dataset + validate scripts — **Hoàng** (30 phút)

### Branch & PR

- [ ] Branch: `feat/s2/data-collection`
- [ ] PR Created
- [ ] Nutrition5k subset parsed + Vietnamese demo samples ready
- [ ] Hoàng reviewed

---

## 📝 Notes

> **Tại sao Hybrid Approach?**
>
> - Tự thu thập 22 mẫu: tốn 5-8 giờ, N quá nhỏ, ground truth thủ công sai số cao
> - Nutrition5k (Google Research): 5,006 mẫu, lab-grade ground truth (weight, calories, carb, protein, fat), có cả RGB + depth
> - Kết hợp: validate pipeline trên benchmark (N=500, thuyết phục) + demo trên món Việt (5-10 mẫu, ấn tượng)
>
> **Benchmark datasets:**
>
> - **Nutrition5k**: RGB + depth + weight/nutrition ground truth (Google Research, 2021)
> - **USDA FoodData Central**: 370,000+ entries dinh dưỡng
> - **Bảng TPDD Việt Nam**: ~500 món Việt, macro nutrients
>
> **Trình bày hội đồng:** "Hệ thống được validate trên Nutrition5k benchmark (N=500) đạt accuracy X%. Ngoài ra nhóm thu thập thêm 10 mẫu món Việt Nam để demonstrate khả năng áp dụng thực tế."
>
> **10 món VN demo:** Cơm trắng, Phở bò, Bún bò Huế, Bánh mì, Cơm tấm, Bún thịt nướng, Mì xào, Cháo, Xôi, Trà sữa
> **Density Factor:** Từ published food science literature (không tự đo)

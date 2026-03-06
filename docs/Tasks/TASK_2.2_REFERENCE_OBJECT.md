## 💡 Context

> **Task ID**: S3-002
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 3 - Model Depth
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 15/04/2026
> **Assignee**: Hoàng (chính), Hoài, Việt
> **Blocked by**: TASK_2.1
> **Blocks**: TASK_2.3 (calibration cần biết vật tham chiếu)

> Train/fine-tune YOLO để nhận diện bát/thìa/đũa tiêu chuẩn VN làm vật tham chiếu kích thước.

---

## ☺️ Refined

> **User Story:**
> As a **user**, I want the **app to automatically detect bowls/spoons as size reference** so that **I don't need to place a card or coin next to my food.**

**Acceptance Criteria:**

- [ ] YOLO model nhận diện được bát, thìa, đũa VN (≥ 90% accuracy)
- [ ] Dataset huấn luyện annotated (≥ 200 ảnh)
- [ ] Model integrated vào Vision pipeline
- [ ] Kích thước thực tế mapping cho mỗi loại dụng cụ

---

## 🛠️ Implementation

### Subtasks

- [ ] 2.2.1 Train/fine-tune YOLO cho nhận diện bát/thìa/đũa VN — **Hoàng**
- [ ] 2.2.2 Tạo dataset huấn luyện (annotate bounding box) — **Hoài**
- [ ] 2.2.3 Integrate nhận diện vật tham chiếu vào pipeline — **Việt**

### Branch & PR

- [ ] Branch: `feat/s3/reference-object`
- [ ] PR Created
- [ ] Accuracy ≥ 90% trên test set

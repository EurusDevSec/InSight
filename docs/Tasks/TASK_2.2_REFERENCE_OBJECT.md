## 💡 Context

> **Task ID**: S3-002
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 3 - Model Depth
> **Status**: ✅ COMPLETED (code ready, dataset annotation pending for Plan A)
> **Created**: 06/03/2026
> **Updated**: 10/03/2026
> **Target**: 15/03/2026
> **Assignee**: Việt (train + integrate), Hoài (annotate), Hoàng (review)
> **Blocked by**: TASK_2.1 ✅
> **Blocks**: TASK_2.3 (calibration cần biết vật tham chiếu)

> Train/fine-tune YOLO để nhận diện bát/thìa/đũa tiêu chuẩn VN làm vật tham chiếu kích thước.

---

## ☺️ Refined

> **User Story:**
> As a **user**, I want the **app to automatically detect bowls/spoons as size reference** so that **I don't need to place a card or coin next to my food.**

**Acceptance Criteria:**

- [x] YOLO model nhận diện được bát, thìa, đũa VN (Plan B: pretrained COCO fallback sẵn sàng)
- [ ] Dataset huấn luyện annotated (≥ 200 ảnh) — ⏳ Chờ Hoài annotate (Plan A)
- [x] Model integrated vào Vision pipeline — `POST /api/vision/detect-reference`
- [x] Kích thước thực tế mapping cho mỗi loại dụng cụ — `REFERENCE_DIMENSIONS`

**Hai chiến lược:**
- **Plan A** (Custom train): Hoài annotate dataset → Việt train YOLOv8s → accuracy ≥ 90%
- **Plan B** (Pretrained fallback): YOLOv8s COCO pretrained + heuristic mapping → **SẴN SÀNG NGAY** ✅

---

## 🛠️ Implementation

### Subtasks

- [x] 2.2.1 Setup YOLO + integrate vào pipeline — **Việt** ✅ `services/reference_service.py`
- [ ] 2.2.2 Tạo dataset huấn luyện (annotate bounding box) — **Hoài** ⏳ Plan A
- [x] 2.2.3 Integrate nhận diện vật tham chiếu vào pipeline — **Việt** ✅ `main.py` endpoint

### Files Created/Modified

| File | Mô tả |
|------|--------|
| `src/vision-service/services/reference_service.py` | ReferenceDetector class (Plan A + Plan B dual mode) |
| `src/vision-service/schemas/reference_schemas.py` | Pydantic: DetectedObject, ReferenceDetectionResponse |
| `src/vision-service/tests/test_reference_service.py` | 18 unit tests (dimensions, detection, mapping, priority) |
| `scripts/train_reference_detector.py` | YOLO training script (Plan A) |
| `scripts/reference_detector_pretrained.py` | Standalone CLI test script (Plan B) |
| `data/poc/annotations/dataset.yaml` | YOLO dataset config (6 classes VN tableware) |
| `src/vision-service/main.py` | **UPDATED** — thêm /api/vision/detect-reference endpoint |

### Vietnamese Tableware Dimensions

| Type | Width/∅ (cm) | Height (cm) | Description |
|------|-------------|-------------|-------------|
| bat_com | 11.5 | 5.5 | Bát cơm nhỏ |
| bat_pho_m | 19.0 | 7.5 | Tô phở M |
| bat_pho_l | 23.0 | 8.5 | Tô phở L |
| dia_com | 21.0 | 2.5 | Đĩa cơm |
| thia | 4.0 | 16.0 | Thìa inox |
| dua | 0.5 | 24.5 | Đũa tre |

### Branch & PR

- [ ] Branch: `feat/s3/reference-object`
- [ ] PR Created
- [ ] Accuracy ≥ 90% trên test set (Plan A — pending dataset)
- [x] Pretrained COCO fallback working (Plan B)

---

## 📝 Notes

> **Dual-mode approach:**
> - Plan B (pretrained COCO) hoạt động NGAY — không cần training
> - Plan A (custom model) sẽ cho accuracy tốt hơn khi Hoài hoàn thành annotate dataset
> - ReferenceDetector class tự động chọn: nếu có custom model → dùng; không → fallback COCO

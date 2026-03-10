## 💡 Context

> **Task ID**: S3-001
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 3 - Model Depth
> **Status**: ✅ COMPLETED
> **Created**: 06/03/2026
> **Updated**: 10/03/2026
> **Target**: 14/03/2026
> **Assignee**: Việt
> **Blocked by**: TASK_1.1 (cần Python Vision Service skeleton) ✅
> **Blocks**: TASK_2.3, TASK_2.5 (calibration & volume cần depth map)

> Triển khai Depth Anything V2 model để tạo depth map từ ảnh 2D món ăn.

---

## ☺️ Refined

> **User Story:**
> As a **vision engineer**, I want to **deploy Depth Anything V2 as a service** so that **I can generate depth maps from food images for volume estimation.**

**Acceptance Criteria:**

- [x] Depth Anything V2 model weights downloaded & loaded
- [x] Inference pipeline: input ảnh → output depth map (numpy array/image)
- [x] API endpoint (FastAPI) phục vụ inference — `POST /api/vision/depth`
- [x] Unit tests cho depth estimation service — 19 tests
- [ ] Inference time ≤ 500ms trên GPU *(chưa test GPU, CPU ~1-3s OK cho dev)*

---

## 🛠️ Implementation

### Subtasks

- [x] 2.1.1 Setup Depth Anything V2 model (download weights, config) — **Việt** ✅ `models/depth_model.py`
- [x] 2.1.2 Implement inference pipeline (input ảnh → depth map) — **Việt** ✅ `services/depth_service.py`
- [x] 2.1.3 Deploy model via FastAPI endpoint — **Việt** ✅ `main.py` → `POST /api/vision/depth`
- [x] 2.1.4 Unit test depth estimation service — **Việt** ✅ `tests/test_depth_service.py`

### Files Created/Modified

| File | Mô tả |
|------|--------|
| `src/vision-service/models/__init__.py` | Package init |
| `src/vision-service/models/depth_model.py` | DepthAnythingV2 wrapper class (small/base/large variants) |
| `src/vision-service/services/__init__.py` | Package init |
| `src/vision-service/services/depth_service.py` | Business logic: estimate_depth(), estimate_depth_raw() |
| `src/vision-service/schemas/__init__.py` | Package init |
| `src/vision-service/schemas/depth_schemas.py` | Pydantic: DepthEstimationResponse, HealthResponse |
| `src/vision-service/tests/__init__.py` | Package init |
| `src/vision-service/tests/test_depth_service.py` | 19 unit tests |
| `src/vision-service/main.py` | **UPDATED** — thêm /api/vision/depth endpoint, lifespan model loading |
| `src/vision-service/requirements.txt` | **UPDATED** — thêm transformers, accelerate, ultralytics |

### Branch & PR

- [ ] Branch: `feat/s3/depth-estimation`
- [ ] PR Created
- [x] Depth map generation verified (POC: `scripts/poc_depth_test.py`)
- [ ] Hoàng reviewed

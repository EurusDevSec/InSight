## 💡 Context

> **Task ID**: S3-001
> **Phase**: Phase 2 - Vision Engine
> **Sprint**: Sprint 3 - Model Depth
> **Status**: ⬜ NOT STARTED
> **Created**: 06/03/2026
> **Target**: 08/04/2026
> **Assignee**: Việt
> **Blocked by**: TASK_1.1 (cần Python Vision Service skeleton)
> **Blocks**: TASK_2.3, TASK_2.5 (calibration & volume cần depth map)

> Triển khai Depth Anything V2 model để tạo depth map từ ảnh 2D món ăn.

---

## ☺️ Refined

> **User Story:**
> As a **vision engineer**, I want to **deploy Depth Anything V2 as a service** so that **I can generate depth maps from food images for volume estimation.**

**Acceptance Criteria:**

- [ ] Depth Anything V2 model weights downloaded & loaded
- [ ] Inference pipeline: input ảnh → output depth map (numpy array/image)
- [ ] API endpoint (FastAPI hoặc TorchServe) phục vụ inference
- [ ] Unit tests cho depth estimation service
- [ ] Inference time ≤ 500ms trên GPU

---

## 🛠️ Implementation

### Subtasks

- [ ] 2.1.1 Setup Depth Anything V2 model (download weights, config) — **Việt**
- [ ] 2.1.2 Implement inference pipeline (input ảnh → depth map) — **Việt**
- [ ] 2.1.3 Deploy model via TorchServe / FastAPI endpoint — **Việt**
- [ ] 2.1.4 Unit test depth estimation service — **Việt**

### Branch & PR

- [ ] Branch: `feat/s3/depth-estimation`
- [ ] PR Created
- [ ] Depth map generation verified
- [ ] Hoàng reviewed

## 💡 Context

> **Task ID**: S1-001  
> **Phase**: Phase 1 - Data + Model Development  
> **Sprint**: Sprint 1 - Data + Baseline Training  
> **Status**: ✅ COMPLETED (24/02/2026)  
> **Created**: 10/02/2026  
> **Target**: ~~17/02/2026~~ → Xong 24/02/2026  
> **Assignee**: Hoàng  
> **Blocked by**: Không  
> **Blocks**: S1-002, S1-003, S1-004, S1-005 (tất cả task sprint 1 phụ thuộc vào env)

> Thiết lập cấu trúc dự án HolmHz theo best practice đã rút ra từ 3 SOTA projects.
> Đây là nền tảng cho toàn bộ sprint 1, phải xong trước khi bắt tay vào code.

---
## ☺️ Refined

> **User Story:**
> As a **ML Engineer**, I want to **set up the HolmHz project structure with proper packaging, configs, and tooling** so that **all subsequent development follows a consistent, reproducible pattern learned from CNNDetection, UniversalFakeDetect, and DeepfakeBench.**
**Acceptance Criteria:**

- [ ] Cấu trúc `src/holmhz/` theo best practice (backbones/, detectors/, data/, losses/, metrics/, training/, evaluation/, xai/, export/, utils/)
- [ ] `pyproject.toml` configured với `pip install -e .` hoạt động
- [ ] `.env.example` có placeholder cho dataset paths, wandb key
- [ ] YAML config skeleton trong `configs/` (train.yaml, test.yaml)
- [ ] Weights & Biases project tạo xong, `wandb login` thành công
- [ ] Colab notebook template connect được Google Drive
- [ ] `Makefile` có target: `train`, `test`, `serve`, `lint`
- [ ] `ruff` linting chạy clean trên codebase ban đầu
- [ ] `.gitignore` bao gồm data/, weights/, outputs/

---

## 🛠️ Implementation

### Subtasks

- [ ] 1.1.1 Setup cấu trúc thư mục `src/holmhz/` theo Section 10 PROJECT_PLAN
- [ ] 1.1.2 Cấu hình `pyproject.toml` + `requirements.txt` (PyTorch, timm, albumentations, wandb, fastapi, gradio)
- [ ] 1.1.3 Setup Weights & Biases project `holmhz`
- [ ] 1.1.4 Tạo Colab notebook template (mount drive, install deps, import holmhz)

### Branch & PR

- [ ] Branch: `feat/s1/environment-setup`
- [ ] PR Created
- [ ] Lint Passed (`ruff check .`)
- [ ] `pip install -e .` thành công

---

## 📝 Notes

> **Patterns áp dụng từ benchmark projects:**
>
> - Registry pattern cho backbones/detectors (`__init__.py` factory) — từ DeepfakeBench
> - YAML config per-detector — từ DeepfakeBench `config/detector/`
> - `base.py` abstract class ở mỗi package — pattern chung cả 3 project
> - Installable package (`pip install -e .`) — thay vì `sys.path` hack

> **Tham khảo:**
>
> - Section 10 trong [PROJECT_PLAN.md](../PROJECT_PLAN.md) — cấu trúc thư mục chi tiết
> - DeepfakeBench cấu trúc `training/` — mẫu tốt nhất cho separation of concerns

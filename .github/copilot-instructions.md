# InSight — AI Assistant Instructions

> **Mục đích:** File này giúp AI assistant nắm bắt context dự án NHANH NHẤT khi bắt đầu session mới.
> **KHÔNG CẦN đọc toàn bộ source code.** Chỉ cần đọc đúng files được liệt kê bên dưới.

---

## 🚀 Quick Context (ĐỌC ĐẦU TIÊN)

### Dự án là gì?

**InSight** — Đồ án tốt nghiệp: Hệ thống ước lượng Glycemic Load thời gian thực cho bệnh nhân tiểu đường.

- **Core idea:** Chụp ảnh món ăn → Ước lượng thể tích (Depth Anything V2) → Tính GL → RAG Agent tư vấn liều Insulin
  - **Vision Engine** (Python) — Depth map, phân đoạn, tính thể tích
  - **RAG Agent** (Python/FastAPI) — Tra cứu hướng dẫn y khoa, tư vấn cá nhân hóa (Gemini API + Milvus)
  - **Mobile App** (Flutter) — Chụp ảnh, hiển thị kết quả, Panic Mode
- **Tech Stack:** Flutter (Mobile) + Java Spring Boot (API Gateway) + Python FastAPI (Vision + RAG) + gRPC + Kafka + PostgreSQL + Milvus + Redis
- **Team:** 3 người — Hoàng (Lead ~50%) + Việt (Core Dev ~30%) + Hoài (Support ~20%)
- **Timeline:** 4 tháng (03/2026 - 06/2026), 5 phases, 14 sprints × ~1-2 tuần
- **Methodology:** Agile / Scrum

### Files PHẢI ĐỌC khi bắt đầu session mới

Đọc theo thứ tự ưu tiên:

| #   | File                                                                  | Mục đích                                                            | Khi nào đọc           |
| --- | --------------------------------------------------------------------- | ------------------------------------------------------------------- | --------------------- |
| 1   | [`docs/plan.md`](../docs/plan.md)                                     | **Master plan** — scope, KPIs, timeline, tasks, architecture        | **LUÔN ĐỌC ĐẦU TIÊN** |
| 2   | [`docs/CONTEXT.md`](../docs/CONTEXT.md)                               | **Session context** — tiến trình, decisions, cấu trúc code hiện tại | **ĐỌC SAU plan.md**   |
| 3   | [`docs/architecture.md`](../docs/architecture.md)                     | Kiến trúc chi tiết — services, Kafka topics, diagrams               | Khi cần hiểu WHY/WHAT |
| 4   | [`docs/architecture_explainer.md`](../docs/architecture_explainer.md) | Giải thích kiến trúc đơn giản                                       | Khi cần hiểu nhanh    |

### Task Files (đọc khi cần làm task cụ thể)

Tất cả task files nằm trong thư mục [`docs/Tasks/`](../docs/Tasks/):

| Phase                  | Task Files                                                                                                                                                                              |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Phase 1** Nền tảng   | `TASK_1.0_PROJECT_KICKOFF.md`, `TASK_1.1_ENVIRONMENT_SETUP.md`, `TASK_1.2_DATABASE_SCHEMA.md`, `TASK_1.3_DATA_COLLECTION.md`                                                            |
| **Phase 2** Vision     | `TASK_2.1_DEPTH_ESTIMATION.md`, `TASK_2.2_REFERENCE_OBJECT.md`, `TASK_2.3_PIXEL_MAPPING.md`, `TASK_2.4_FOOD_SEGMENTATION.md`, `TASK_2.5_VOLUME_ESTIMATION.md`, `TASK_2.6_VALIDATION.md` |
| **Phase 3** RAG        | `TASK_3.1_KNOWLEDGE_BASE.md`, `TASK_3.2_RAG_PIPELINE.md`, `TASK_3.3_PERSONALIZATION.md`                                                                                                 |
| **Phase 4** Tích hợp   | `TASK_4.1_FLUTTER_APP.md`, `TASK_4.2_GRPC_INTEGRATION.md`, `TASK_4.3_E2E_TESTING.md`, `TASK_4.4_PERFORMANCE.md`                                                                         |
| **Phase 5** Hoàn thiện | `TASK_5.1_UAT.md`, `TASK_5.2_BUG_FIXES.md`, `TASK_5.3_DEFENSE_PREP.md`                                                                                                                  |

**Format mỗi task file:** Context → User Story → Acceptance Criteria → Subtasks (Hoàng / Việt / Hoài) → Branch & PR → Notes

---

## 📋 Nguyên tắc Làm việc (PHẢI TUÂN THỦ)

### 1. Task Workflow

- Mỗi task có file riêng trong `docs/Tasks/` → đọc task file trước khi bắt tay làm
- Follow Acceptance Criteria như checklist — tick khi hoàn thành
- **Dependency chain:** xem "Blocked by" trong task file → đảm bảo dependency đã xong

### 2. Git Convention

- **Branch naming:** `feat/s[X]/[feature]`, `fix/s[X]/[bug]`, `infra/[setup]`, `docs/[topic]`
- **Commit format:** `type(scope): description` (VD: `feat(vision): add depth estimation endpoint`)
- **Types:** `feat`, `fix`, `docs`, `infra`, `test`, `refactor`, `chore`
- **PR required** cho mọi merge vào `main`

### 3. Code Standards

- **Java:** Spring Boot 3.3, Java 21, Virtual Threads (API Gateway only)
- **Python:** 3.11+, PyTorch, Depth Anything V2, FastAPI, OpenAI SDK (Gemini API)
- **Flutter:** 3.x, ONNX Runtime, gRPC client
- **Config:** YAML-driven (không hardcode), Docker Compose
- **Testing:** Unit tests cho core functions, integration tests cho pipeline

### 4. Khi User Hỏi "Tiếp tục" / "Continue"

1. Đọc `docs/plan.md` → xác định phase/sprint hiện tại
2. Đọc task file tương ứng trong `docs/Tasks/`
3. Tìm subtask chưa hoàn thành (checkbox `- [ ]`)
4. Thực hiện subtask tiếp theo

### 5. Ngôn ngữ

- Code comments, variable names, API docs: **English**
- Documentation (`docs/`, `tasks/`): **Vietnamese** (nhóm Việt Nam)
- Khi user hỏi bằng tiếng Việt → trả lời tiếng Việt

---

## 🗂️ Cấu trúc Dự án

```
InSight/
├── .github/
│   ├── copilot-instructions.md    # File này — AI assistant guide
│   └── PULL_REQUEST_TEMPLATE.md   # PR template
├── docs/
│   ├── plan.md                    # ⭐ MASTER PLAN — đọc đầu tiên
│   ├── architecture.md            # Kiến trúc hệ thống
│   ├── Tasks/                     # ⭐ 20 TASK FILES (Phase 1-5)
│   │   ├── TASK_1.0_PROJECT_KICKOFF.md
│   │   ├── TASK_1.1_ENVIRONMENT_SETUP.md
│   │   ├── ...
│   │   └── TASK_5.3_DEFENSE_PREP.md
│   └── Guides/                    # Hướng dẫn chi tiết
├── example/                       # Mẫu tham khảo (KHÔNG phải của dự án)
├── src/                           # Source code
│   ├── mobile/                    # Flutter app
│   ├── api-gateway/               # Spring Boot API Gateway
│   ├── vision-service/            # Python Vision Engine
│   └── rag-service/               # Python RAG Agent (Gemini + Milvus)
├── infra/                         # Docker Compose, K8s manifests
├── data/                          # Dataset (gitignored)
└── scripts/                       # Automation scripts
```

---

## ⚡ Quick Reference

| Cần biết                      | Đọc file                        |
| ----------------------------- | ------------------------------- |
| Mục tiêu, KPIs, scope?        | `docs/plan.md` Section 1, 8     |
| Timeline, sprint nào?         | `docs/plan.md` Section 5, 6     |
| Kiến trúc hệ thống?           | `docs/architecture.md`          |
| Task cụ thể cần làm?          | `docs/Tasks/TASK_X.X_[NAME].md` |
| Git branch/commit convention? | File này Section 2              |

---

_Last updated: 06/03/2026_

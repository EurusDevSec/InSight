# ZERO DOOR — AI Assistant Instructions

> **Mục đích:** File này giúp AI assistant nắm bắt context dự án NHANH NHẤT khi bắt đầu session mới.
> **KHÔNG CẦN đọc toàn bộ source code.** Chỉ cần đọc đúng files được liệt kê bên dưới.

---

## 🚀 Quick Context (ĐỌC ĐẦU TIÊN)

### Dự án là gì?

**ZERO DOOR** — Nghiên cứu khoa học (NCKH cấp trường) về Self-Healing cho Microservices.
- **Core idea:** 3 AI Agents hoạt động theo vòng lặp **Attack → Detect → Heal**
  - **Nemesis** (Red Team) — tự động sinh payload tấn công bằng LLM
  - **Gaia** (Observer) — giám sát metrics, phát hiện anomaly
  - **Hephaestus** (Blue Team) — tự động heal qua Kubernetes API
- **Tech Stack:** Java Spring Boot (Agents) + Go (Chaos Worker) + Kubernetes + Kafka + Prometheus
- **Team:** 2 người — Hoàng (Lead Dev ~70%) + hpt8001 (Support ~30%)
- **Timeline:** 6 tháng (01/2026 - 06/2026), 12 sprints × 2 tuần
- **Methodology:** Scrumban

### Files PHẢI ĐỌC khi bắt đầu session mới

Đọc theo thứ tự ưu tiên:

| # | File | Mục đích | Khi nào đọc |
|---|------|---------|-------------|
| 1 | [`docs/context.md`](../docs/context.md) | **Session cache** — trạng thái hiện tại, task progress, vấn đề đã giải quyết | **LUÔN ĐỌC ĐẦU TIÊN** |
| 2 | [`docs/plan.md`](../docs/plan.md) | Master plan — scope, KPIs, architecture, timeline, references | Khi cần hiểu WHY/WHAT |
| 3 | [`docs/workflow.md`](../docs/workflow.md) | Quy trình Scrumban — sprint structure, git flow, ceremonies | Khi cần hiểu HOW |
| 4 | [`docs/architecture.md`](../docs/architecture.md) | Kiến trúc chi tiết — agents, Kafka topics, diagrams | Khi làm code/design |

### Task Files (đọc khi cần làm task cụ thể)

Tất cả task files nằm trong thư mục [`tasks/`](../tasks/):

| Phase | Task Files |
|-------|-----------|
| **Phase 1** Setup | `TASK_S1_INFRA_SETUP.md`, `TASK_S2_K8S_CLUSTER.md`, `TASK_S3_DEV_ENVIRONMENT.md` |
| **Phase 1** Design | `TASK_S4_ARCHITECTURE_DESIGN.md`, `TASK_S5_KAFKA_SETUP.md`, `TASK_S6_OBSERVABILITY.md` |
| **Phase 2** Target+Gaia | `TASK_S7_TARGET_APP.md`, `TASK_S8_AGENT_GAIA.md` |
| **Phase 3** Nemesis | `TASK_S9_CHAOS_WORKER.md`, `TASK_S10_AGENT_NEMESIS.md` |
| **Phase 4** Hephaestus | `TASK_S11_AGENT_HEPHAESTUS.md` |
| **Phase 5** War Game | `TASK_S12_WAR_GAME.md` |
| **Phase 6** Closing | `TASK_S13_REPORT_DEFENSE.md` |

**Format mỗi task file:** Context → User Story → Acceptance Criteria → Subtasks (🔴 Lead / 🟡 hpt8001) → Branch & PR → Notes

---

## 📋 Nguyên tắc Làm việc (PHẢI TUÂN THỦ)

### 1. Context Management
- **Trước khi code:** Luôn đọc `docs/context.md` trước → biết đang ở đâu, task nào đang làm
- **Sau khi xong task:** Cập nhật `docs/context.md` với kết quả (status, vấn đề gặp, quyết định)
- **KHÔNG BAO GIỜ** giả định trạng thái project — luôn kiểm tra context.md

### 2. Task Workflow
- Mỗi task có file riêng trong `tasks/` → đọc task file trước khi bắt tay làm
- Follow Acceptance Criteria như checklist — tick khi hoàn thành
- Subtask có icon: 🔴 = Hoàng làm, 🟡 = hpt8001 làm
- **Dependency chain:** xem "Blocked by" trong task file → đảm bảo dependency đã xong

### 3. Git Convention
- **Branch naming:** `feat/s[X]/[feature]`, `fix/s[X]/[bug]`, `infra/[setup]`, `docs/[topic]`
- **Commit format:** `type(scope): description` (VD: `feat(gaia): implement anomaly detector`)
- **Types:** `feat`, `fix`, `docs`, `infra`, `test`, `refactor`, `chore`
- **PR required** cho mọi merge vào `main`

### 4. Code Standards
- **Java:** Spring Boot 3.x, Java 17+, Lombok, Spring AI
- **Go:** 1.21+, standard library first, minimal dependencies
- **Config:** YAML-driven (không hardcode), Kubernetes manifests
- **Testing:** Unit tests cho mỗi component, integration tests cho Kafka messaging

### 5. Khi User Hỏi "Tiếp tục" / "Continue"
1. Đọc `docs/context.md` → xác định task hiện tại
2. Đọc task file tương ứng trong `tasks/`
3. Tìm subtask chưa hoàn thành (checkbox `- [ ]`)
4. Thực hiện subtask tiếp theo
5. Cập nhật context.md khi xong

### 6. Khi User Hỏi Về Kiến trúc / Design
- Đọc `docs/architecture.md` + `docs/plan.md` Section 5
- Tham khảo Kafka message schemas trong task files (S4, S8, S10, S11)
- Luôn giữ consistent với design đã document

### 7. Ngôn ngữ
- Code comments, variable names, API docs: **English**
- Documentation (`docs/`, `tasks/`): **Vietnamese** (nhóm Việt Nam)
- Khi user hỏi bằng tiếng Việt → trả lời tiếng Việt
- Khi user hỏi bằng tiếng Anh → trả lời tiếng Anh

---

## 🗂️ Cấu trúc Dự án

```
zero_door/
├── .github/
│   └── copilot-instructions.md    # File này — AI assistant guide
├── docs/
│   ├── context.md                 # ⭐ SESSION CACHE — đọc đầu tiên
│   ├── plan.md                    # Master plan (scope, KPIs, refs)
│   ├── workflow.md                # Scrumban process
│   ├── architecture.md            # System architecture chi tiết
│   ├── references.md              # Academic papers + resources
│   ├── slides.md                  # Presentation draft
│   └── go-mastery.md              # Go learning guide
├── tasks/                         # ⭐ 13 TASK FILES (Phase 1-6)
│   ├── TASK_S1_INFRA_SETUP.md
│   ├── TASK_S2_K8S_CLUSTER.md
│   ├── ...
│   └── TASK_S13_REPORT_DEFENSE.md
├── example/                       # Reference project (HolmHz)
│   ├── PROJECT_PLAN.md            # Example plan structure
│   ├── TASK_1.1_ENVIRONMENT_SETUP.md  # Example task format
│   └── CONTEXT.md                 # Example context file
├── src/                           # Source code (tạo khi bắt đầu code)
│   ├── target-app/
│   ├── agent-nemesis/
│   ├── agent-gaia/
│   └── agent-hephaestus/
├── infra/                         # K8s manifests, Helm charts
├── experiments/                   # Experiment results & data
└── scripts/                       # Automation scripts
```

---

## ⚡ Quick Reference

| Cần biết | Đọc file |
|---------|----------|
| Project đang ở đâu? Task nào đang làm? | `docs/context.md` |
| Mục tiêu, KPIs, scope? | `docs/plan.md` Section 2, 7 |
| Kiến trúc 3 Agents? Kafka topics? | `docs/architecture.md` + `docs/plan.md` Section 5 |
| Sprint nào? Quy trình? | `docs/workflow.md` |
| Task cụ thể cần làm? | `tasks/TASK_S[X]-[XXX]_[NAME].md` |
| Git branch/commit convention? | File này Section 3 |
| Papers tham khảo? | `docs/references.md` |
| Example project format? | `example/PROJECT_PLAN.md` |

---

_Last updated: 04/03/2026_

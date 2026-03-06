# 📖 HƯỚNG DẪN CHI TIẾT TASK 1.0: PROJECT KICKOFF

> **Dành cho**: Toàn team — Hoàng (Lead), Việt (Core), Hoài (Support)
> **Triết lý**: "Measure twice, cut once" — Chuẩn bị kỹ trước khi code
> **Trạng thái**: ⬜ NOT STARTED
> **Thời gian dự kiến**: 06/03 → 07/03/2026 (2 ngày)
> **Tiền đề**: Không — Đây là task đầu tiên
> **Tham chiếu**: [TASK_1.0_PROJECT_KICKOFF.md](../Tasks/TASK_1.0_PROJECT_KICKOFF.md) | [plan.md](../plan.md) Section 6

---

## 📋 Mục lục

- [Bức tranh tổng thể: Kickoff nằm ở đâu?](#bức-tranh-tổng-thể-kickoff-nằm-ở-đâu)
- [Tại sao Kickoff quan trọng?](#tại-sao-kickoff-quan-trọng)
- [Bước 1: Tạo GitHub Repository](#bước-1-tạo-github-repository)
- [Bước 2: Viết tài liệu kiến trúc](#bước-2-viết-tài-liệu-kiến-trúc)
- [Bước 3: Định nghĩa API Contracts](#bước-3-định-nghĩa-api-contracts)
- [Bước 4: Thiết kế Database Schema](#bước-4-thiết-kế-database-schema)
- [Bước 5: Họp Kickoff](#bước-5-họp-kickoff)
- [Checklist hoàn thành](#checklist-hoàn-thành)

---

## Bức tranh tổng thể: Kickoff nằm ở đâu?

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    DỰ ÁN INSIGHT — PHASE 1: NỀN TẢNG                     │
│                                                                           │
│  ► Task 1.0  KHỞI ĐỘNG DỰ ÁN  ◄◄◄  BẠN ĐANG Ở ĐÂY                    │
│    │                                                                      │
│    │  Đây là "bản thiết kế" trước khi xây nhà.                           │
│    │  Không có kiến trúc rõ ràng → code sẽ loạn, phải refactor.         │
│    │  Không có API contracts → 3 người code 3 kiểu, không ghép được.    │
│    │                                                                      │
│    │  📌 Phân công:                                                      │
│    │  • Hoàng: GitHub repo + Architecture docs + API contracts + Kickoff │
│    │  • Hoài: README + .gitignore + PR template                         │
│    │  • Việt: Database schema (ERD)                                      │
│    │                                                                      │
│    ├───► Task 1.1  Environment Setup (Docker, Spring Boot, Python)        │
│    ├───► Task 1.2  Database & Schema (implement từ ERD)                  │
│    └───► Task 1.3  Data Collection (chụp ảnh, đo ground-truth)           │
│                                                                           │
│  ⚡ Làm song song: 3 người làm 3 phần, ghép lại cuối ngày 07/03        │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Tại sao Kickoff quan trọng?

```
┌─────────────────────────────────────────────────────────────────────────┐
│  BÀI HỌC TỪ DỰ ÁN THẤT BẠI:                                           │
│                                                                         │
│  ❌ Không có kiến trúc → Mỗi người code 1 kiểu → Không ghép được     │
│  ❌ Không có API contract → Frontend chờ backend → Lãng phí thời gian │
│  ❌ Không có DB schema → Mỗi table thiết kế khác → Data inconsistent  │
│  ❌ Không có Git convention → Merge conflict liên tục                  │
│                                                                         │
│  ✅ CÓ kiến trúc → 3 người code song song, ghép vào cuối sprint      │
│  ✅ CÓ Proto3 contract → Flutter/Java/Python đều generate được code   │
│  ✅ CÓ ERD → Flyway migration chạy 1 lần, schema đồng bộ            │
│  ✅ CÓ Git convention → PR clean, review dễ, không conflict           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Bước 1: Tạo GitHub Repository

**Assignee: Hoàng** | **Thời gian: ~30 phút**

### 1.1 Tạo cấu trúc thư mục dự án

```bash
# Đảm bảo đang ở thư mục project
cd R:/_Projects/Eurus_Workspace/InSight

# Tạo cấu trúc folder theo architecture.md
mkdir -p src/mobile
mkdir -p src/api-gateway/src/main/java
mkdir -p src/api-gateway/src/main/proto
mkdir -p src/api-gateway/src/main/resources
mkdir -p src/vision-service/models
mkdir -p src/vision-service/services
mkdir -p src/vision-service/api
mkdir -p src/rag-service/src/main/java
mkdir -p src/rag-service/knowledge/medical
mkdir -p infra/docker
mkdir -p infra/k8s
mkdir -p data/raw
mkdir -p data/processed
mkdir -p scripts
mkdir -p experiments
```

> **Tại sao chia folder theo service?** Vì InSight dùng kiến trúc microservices — mỗi service một repo riêng trong `src/`. Khi deploy, mỗi service là 1 Docker container.

### 1.2 Setup .gitignore

Đã có sẵn `.gitignore`, nhưng kiểm tra các mục quan trọng:

```gitignore
# Đảm bảo có các mục sau:
# Build
*.class
*.jar
build/
target/
__pycache__/
*.pyc
.gradle/

# IDE
.idea/
.vscode/
*.iml

# Data (CỰC KỲ QUAN TRỌNG — không push data lên GitHub)
data/
*.h5
*.pt
*.pth
*.onnx

# Environment
.env
*.env
secrets/
node_modules/

# Example (mẫu tham khảo, không liên quan dự án)
example/
```

### 1.3 Setup README.md

```bash
# Tạo README.md tại root
cat > README.md << 'EOF'
# 🔬 InSight — Insulin Insight System

> Hệ thống ước lượng Glycemic Load thời gian thực cho bệnh nhân tiểu đường
> Sử dụng Computer Vision 3D và RAG Agent cá nhân hóa

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Java 21+ (API Gateway, RAG Service)
- Python 3.11+ (Vision Service)
- Flutter 3.x (Mobile App)

### Run Development Environment
```bash
# Start all services
docker compose up -d

# Check health
docker compose ps
```

## 📁 Project Structure

```
src/
├── mobile/          # Flutter mobile app
├── api-gateway/     # Spring Boot API Gateway
├── vision-service/  # Python Vision Engine (Depth Anything V2)
└── rag-service/     # Java RAG Agent (LangChain4j + Milvus)
```

## 👥 Team
- **Hoàng** — Tech Lead / Architect
- **Việt** — Backend / Vision Engineer
- **Hoài** — Frontend / Testing / Documentation
EOF
```

### 1.4 Setup Branch Strategy

```bash
# Tạo branch develop từ main
git checkout -b develop
git push -u origin develop

# Branch strategy:
# main ← stable releases only
# develop ← integration branch
# feature/* ← individual features
# fix/* ← bug fixes
# docs/* ← documentation
```

> **Convention:**
> - `feat/s[sprint]/[tên-task]` — VD: `feat/s1/environment-setup`
> - `fix/s[sprint]/[bug]` — VD: `fix/s3/depth-nan-values`
> - `docs/[topic]` — VD: `docs/architecture-update`

---

## Bước 2: Viết tài liệu kiến trúc

**Assignee: Hoàng** | **Thời gian: ~3 giờ**

> **File `docs/architecture.md` đã có sẵn!** Hoàng cần review và bổ sung nếu thiếu.

### 2.1 Kiểm tra architecture.md hiện tại

File `docs/architecture.md` đã chứa:
- ✅ High-Level Architecture diagram
- ✅ Component Diagram chi tiết
- ✅ Sequence Diagram (Standard Mode, Panic Mode, Đồ uống)
- ✅ Data Flow diagrams
- ✅ Folder structure cho Mobile, Backend, Data
- ✅ ERD (Entity Relationship Diagram)
- ✅ Tech stack với lý do lựa chọn

### 2.2 Nếu cần bổ sung

Thêm các mục sau nếu chưa có:

1. **Kafka Topics & Message Schemas** — Các topic dùng cho event-driven communication:
   - `vision.request` — Gateway → Vision Service
   - `vision.result` — Vision Service → Logic Service
   - `rag.query` — Logic → RAG Service
   - `rag.response` — RAG → Logic

2. **Error Handling Strategy** — Retry, Circuit Breaker, Fallback

3. **Security Model** — OAuth2 flow, JWT validation

---

## Bước 3: Định nghĩa API Contracts

**Assignee: Hoàng** | **Thời gian: ~2 giờ**

### 3.1 Tạo Proto3 file cho gRPC

```bash
mkdir -p src/api-gateway/src/main/proto
```

```protobuf
// src/api-gateway/src/main/proto/insight.proto
syntax = "proto3";

package insight;

option java_package = "com.insight.grpc";
option java_multiple_files = true;

// === Vision Service ===
service VisionService {
  // Ước lượng thể tích từ ảnh
  rpc EstimateVolume(VolumeRequest) returns (VolumeResponse);
}

message VolumeRequest {
  bytes image_data = 1;            // Ảnh gốc (JPEG/PNG bytes)
  string food_type = 2;            // Loại món (nếu đã biết)
  ReferenceObject reference = 3;   // Vật tham chiếu đã detect
}

message ReferenceObject {
  string type = 1;      // "bowl", "spoon", "chopstick"
  float width_px = 2;    // Chiều rộng pixel
  float height_px = 3;   // Chiều cao pixel
  float real_size_cm = 4; // Kích thước thực (cm)
}

message VolumeResponse {
  float volume_ml = 1;         // Thể tích (ml)
  float confidence = 2;        // Độ tin cậy (0-1)
  bytes depth_map = 3;          // Depth map (optional)
  string error_message = 4;    // Lỗi nếu có
}

// === GL Calculation ===
service GLService {
  // Tính Glycemic Load
  rpc CalculateGL(GLRequest) returns (GLResponse);
}

message GLRequest {
  float volume_ml = 1;
  string food_id = 2;
  string food_type = 3;
  map<string, string> form_data = 4;  // Dữ liệu từ form hỏi nhanh
}

message GLResponse {
  float total_carbs = 1;
  float glycemic_load = 2;
  float glycemic_index = 3;
  string insulin_suggestion = 4;  // Từ RAG Agent
  string disclaimer = 5;
  float confidence = 6;
}

// === RAG Advisor ===
service RAGService {
  // Tư vấn liều Insulin
  rpc GetAdvice(AdviceRequest) returns (AdviceResponse);
}

message AdviceRequest {
  float total_carbs = 1;
  float current_glucose = 2;   // mg/dL
  repeated string medications = 3;
  string meal_context = 4;      // "breakfast", "lunch", "dinner"
}

message AdviceResponse {
  string advice = 1;            // "60g Carb → Tiêm thêm 1 Unit"
  string reasoning = 2;        // Lý do (từ RAG retrieval)
  repeated string sources = 3;  // Nguồn tham chiếu
  bool is_emergency = 4;        // Có phải khẩn cấp?
  string emergency_action = 5;  // Hành động khẩn cấp nếu có
}
```

> **Tại sao dùng Proto3 thay vì REST?** gRPC nhanh hơn REST 7-10 lần (binary serialization + HTTP/2). Quan trọng hơn, Proto3 file **sinh code tự động** cho Java, Python, Dart (Flutter) — 3 ngôn ngữ trong dự án đều dùng cùng 1 contract.

### 3.2 Generate code từ Proto

```bash
# Java (Spring Boot) — gradle plugin tự generate
# Python — dùng grpcio-tools
pip install grpcio-tools
python -m grpc_tools.protoc -I=src/api-gateway/src/main/proto \
  --python_out=src/vision-service/api \
  --grpc_python_out=src/vision-service/api \
  src/api-gateway/src/main/proto/insight.proto

# Flutter — dùng protoc_plugin
# Sẽ setup ở Task 4.1
```

---

## Bước 4: Thiết kế Database Schema

**Assignee: Việt** | **Thời gian: ~2 giờ**

### 4.1 ERD đã có trong architecture.md

File `docs/architecture.md` Section 5.3 đã chứa ERD diagram với các bảng:

| Table | Mô tả | Columns chính |
|-------|--------|--------------|
| `USER` | Người dùng | id, email, name, medication, insulin_settings |
| `MEAL_LOG` | Lịch sử bữa ăn | id, user_id, total_carbs, total_gl, insulin_suggestion |
| `MEAL_ITEM` | Từng món trong bữa | id, meal_log_id, food_id, volume_ml, weight_g, carbs_g |
| `FOOD` | Thông tin dinh dưỡng | id, name_vi, carb_per_100g, gi_index, category |
| `DENSITY_FACTOR` | Hệ số mật độ | id, food_id, variant, solid_ratio, density |
| `GLUCOSE_READING` | Đường huyết | id, user_id, value_mgdl, measured_at |
| `FAVORITE_RESTAURANT` | Quán quen | id, user_id, name, custom_density_factors |

### 4.2 Tạo file ERD diagram

Việt dùng [dbdiagram.io](https://dbdiagram.io) hoặc draw.io để vẽ ERD trực quan, export thành hình và lưu `docs/erd.png`.

### 4.3 Seed data cho 10 món VN

```sql
-- Seed data cho FOOD table
INSERT INTO food (id, name_vi, name_en, carb_per_100g, gi_index, category) VALUES
  (gen_random_uuid(), 'Cơm trắng', 'White rice', 28.0, 73, 'rice'),
  (gen_random_uuid(), 'Phở bò', 'Beef pho', 15.0, 46, 'noodle_soup'),
  (gen_random_uuid(), 'Bún bò Huế', 'Hue beef noodle', 18.0, 52, 'noodle_soup'),
  (gen_random_uuid(), 'Bánh mì', 'Vietnamese sandwich', 49.0, 65, 'bread'),
  (gen_random_uuid(), 'Cơm tấm', 'Broken rice', 28.0, 73, 'rice'),
  (gen_random_uuid(), 'Bún thịt nướng', 'Grilled pork noodle', 20.0, 50, 'noodle'),
  (gen_random_uuid(), 'Mì xào', 'Stir-fried noodle', 25.0, 55, 'noodle'),
  (gen_random_uuid(), 'Cháo', 'Rice porridge', 12.0, 78, 'porridge'),
  (gen_random_uuid(), 'Xôi', 'Sticky rice', 37.0, 87, 'rice'),
  (gen_random_uuid(), 'Trà sữa', 'Milk tea', 20.0, 55, 'beverage');

-- Seed data cho DENSITY_FACTOR
INSERT INTO density_factor (id, food_id, variant, solid_ratio, density) VALUES
  -- Phở bò: 30% đặc (bánh phở + thịt), 70% nước
  (gen_random_uuid(), (SELECT id FROM food WHERE name_vi='Phở bò'), 'standard', 0.30, 1.02),
  -- Bún bò Huế: 35% đặc, 65% nước
  (gen_random_uuid(), (SELECT id FROM food WHERE name_vi='Bún bò Huế'), 'standard', 0.35, 1.03),
  -- Cháo: 20% đặc, 80% nước
  (gen_random_uuid(), (SELECT id FROM food WHERE name_vi='Cháo'), 'standard', 0.20, 1.01);
```

---

## Bước 5: Họp Kickoff

**Assignee: Hoàng (chủ trì)** | **Thời gian: 30 phút**

### 5.1 Agenda

1. **Review kiến trúc** (10 phút): Hoàng trình bày architecture.md, giải thích luồng xử lý
2. **Review API contracts** (5 phút): Đồng ý Proto3 schemas
3. **Review DB schema** (5 phút): Việt trình bày ERD
4. **Phân công Sprint 1** (10 phút): Xác nhận ai làm gì trong Task 1.1 + 1.2

### 5.2 Definition of Done cho Sprint 0

- [ ] Hoàng: Repo + Architecture docs + Proto3 files ✅
- [ ] Hoài: README + .gitignore + PR template ✅
- [ ] Việt: ERD diagram + seed SQL ✅
- [ ] Team: Hiểu rõ plan, biết task Sprint 1 của mình

---

## Checklist hoàn thành

- [ ] GitHub repo có đầy đủ folder structure
- [ ] README.md có tech stack + quick start
- [ ] .gitignore bao gồm data/, example/, secrets/
- [ ] PR template tại `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] `docs/architecture.md` reviewed và đầy đủ
- [ ] `src/api-gateway/src/main/proto/insight.proto` tạo xong
- [ ] ERD diagram export thành hình
- [ ] Seed SQL cho 10 món VN
- [ ] Team đã họp kickoff, đồng bộ plan Sprint 1

---

## Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| `gh` chưa cài | `winget install GitHub.cli` hoặc download từ github.com/cli/cli |
| Git push bị reject | `git pull --rebase origin main` trước khi push |
| Proto3 compile lỗi | Kiểm tra syntax: `protoc --lint_out=. insight.proto` |
| Team chưa có quyền push | Owner (Hoàng) thêm collaborators trong repo Settings |

---

> **Tạo**: 06/03/2026
> **Cập nhật**: 06/03/2026

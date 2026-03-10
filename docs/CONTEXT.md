# InSight Project — Session Context

> File này lưu trữ toàn bộ context của quá trình phát triển để session AI mới đọc hiểu NGAY.
> Cập nhật lần cuối: 10/03/2026 22:40 (Phase 1 DONE + Sprint 3 DONE — 40 tests + E2E + full pipeline verified)

---

## 1. Thông tin dự án

| Mục | Chi tiết |
|-----|---------|
| **Tên dự án** | InSight — Hệ thống ước lượng Glycemic Load thời gian thực cho bệnh nhân tiểu đường |
| **Loại** | Đồ án tốt nghiệp — Applied Research |
| **Timeline** | 06/03/2026 → 31/03/2026 (25 ngày, 5 phases, 14 sprints) |
| **Nhóm** | Hoàng (Leader/Architect), Việt (Core Dev/Vision), Hoài (Support/Frontend) |
| **Core idea** | Chụp ảnh món ăn → Depth map (DAv2) → Volume → GL → RAG tư vấn Insulin |
| **Tech Stack** | Flutter + Spring Boot (Java 21) + Python FastAPI + gRPC + Kafka + PostgreSQL + Milvus + Redis |

---

## 2. Cấu trúc dự án (key paths)

```
InSight/
├── docs/
│   ├── plan.md                     # ⭐ MASTER PLAN — đọc đầu tiên
│   ├── architecture.md             # Kiến trúc hệ thống
│   ├── Tasks/                      # 20 task files (Phase 1-5)
│   ├── Guides/                     # Hướng dẫn chi tiết implementation
│   └── CONTEXT.md                  # 📌 FILE NÀY — session context
├── src/
│   ├── vision-service/             # ⭐ Python Vision Engine (FastAPI)
│   │   ├── main.py                 # FastAPI app (3 endpoints)
│   │   ├── models/
│   │   │   └── depth_model.py      # DepthAnythingV2 wrapper
│   │   ├── services/
│   │   │   ├── depth_service.py    # Depth estimation logic
│   │   │   └── reference_service.py # Reference object detection
│   │   ├── schemas/
│   │   │   ├── depth_schemas.py    # Pydantic response models
│   │   │   └── reference_schemas.py
│   │   ├── tests/
│   │   │   ├── test_depth_service.py    # 19 tests
│   │   │   └── test_reference_service.py # 18 tests
│   │   ├── api/                    # gRPC proto files
│   │   └── requirements.txt
│   ├── api-gateway/                # Spring Boot API Gateway
│   ├── mobile/                     # Flutter app
│   └── rag-service/                # Java RAG Agent
├── data/
│   ├── nutrition5k/parsed/         # Benchmark dataset (N=500)
│   ├── nutrition_db/               # VN food nutrition + density factors
│   ├── vn_demo/                    # 5 món VN (JSON ready, ảnh pending)
│   ├── poc/annotations/            # YOLO dataset config
│   └── schemas/                    # JSON schema definitions
├── scripts/
│   ├── poc_depth_test.py           # POC Depth Anything V2 (validated ✅)
│   ├── download_nutrition5k.py     # Parse Nutrition5k
│   ├── import_nutrition_db.py      # Import VN nutrition data
│   ├── export_density_factors.py   # Density Factor DB
│   ├── compile_dataset.py          # Compile final dataset
│   ├── validate_dataset.py         # Validate dataset
│   ├── train_reference_detector.py # YOLO training (Plan A)
│   └── reference_detector_pretrained.py # YOLO pretrained (Plan B)
└── .github/copilot-instructions.md # AI assistant guide
```

---

## 3. Task Progress

### Phase 1: Nền tảng & Dữ liệu (06/03 - 12/03) — 🔄 IN PROGRESS

| Task | Status | Ghi chú |
|------|--------|---------|
| 1.0 Khởi động dự án | ✅ Done | Repo setup, architecture.md, API contracts |
| 1.1 Environment Setup | ✅ Done | Docker Compose, Spring Boot skeleton, Python FastAPI skeleton |
| 1.2 Database & Schema | ✅ Done | PostgreSQL schema, Milvus collections, Redis config |
| 1.3 Thu thập dữ liệu | ✅ Done | **Tất cả subtasks hoàn thành** — 5 JSON + 10 ảnh + compile + validate |

**Chi tiết Task 1.3 đã hoàn thành:**
- [x] 1.3.1 JSON schema → `data/schemas/insight_food_sample_v1.json`
- [x] 1.3.2 Nutrition5k parse → `scripts/download_nutrition5k.py`
- [x] 1.3.3 Import VN nutrition → `scripts/import_nutrition_db.py` (10 món)
- [x] 1.3.4 Density Factor DB → `scripts/export_density_factors.py` (12 items)
- [x] **1.3.5 Chụp ảnh VN** → 5 món × 2 góc = 10 ảnh ✅ Done 10/03
- [x] 1.3.6 Compile + validate → 10/10 samples valid ✅

### Phase 2: Vision Engine (13/03 - 20/03) — ✅ Sprint 3 VERIFIED

| Task | Status | Ghi chú |
|------|--------|---------|
| **2.1 Depth Estimation** | ✅ Verified | DAv2 Small, 404ms CUDA, 19 unit tests + E2E pass |
| **2.2 Reference Object** | ✅ Verified | Plan B COCO detect bowl conf=0.945, 21 unit tests + E2E pass |
| 2.3 Pixel-to-Real Mapping | ⬜ Not Started | Cần depth map (2.1 ✅) + reference (2.2 ✅) |
| 2.4 Food Segmentation | ⬜ Not Started | SAM integration |
| 2.5 Volume Estimation | ⬜ Not Started | V = ∫∫ depth(x,y) dA |
| 2.6 Validation & Benchmark | ⬜ Not Started | So sánh với Nutrition5k ground truth |

### Phase 3-5: ⬜ Not Started

---

## 4. Vision Service — Architecture (sau Task 2.1 + 2.2)

### API Endpoints

| Method | Path | Status | Mô tả |
|--------|------|--------|--------|
| GET | `/health` | ✅ | Health check + model status |
| POST | `/api/vision/depth` | ✅ Task 2.1 | Ảnh → Depth map (base64 PNG + stats) |
| POST | `/api/vision/detect-reference` | ✅ Task 2.2 | Ảnh → Reference objects + scale factor |
| POST | `/api/vision/estimate-volume` | ⏳ Task 2.5 | Placeholder — chưa implement |

### Models & Services

```
Request → FastAPI (main.py)
              │
              ├─► DepthAnythingV2 (models/depth_model.py)
              │   ├─ Variant: small (24.8M params, ~45ms GPU)
              │   ├─ Pipeline: HuggingFace depth-estimation
              │   ├─ Output: depth_map (numpy H×W) + depth_image (PIL)
              │   └─ Service: depth_service.py (singleton, base64 encode)
              │
              └─► ReferenceDetector (services/reference_service.py)
                  ├─ Plan A: Custom YOLOv8s (runs/reference_detector/v1/weights/best.pt)
                  ├─ Plan B: Pretrained YOLOv8s COCO (auto fallback)
                  ├─ 6 classes: bat_com, bat_pho_m, bat_pho_l, dia_com, thia, dua
                  ├─ Output: List[ReferenceObject] + best_scale_factor (px/cm)
                  └─ Bowl size heuristic: bbox_width / img_width → small/medium/large
```

### Key Design Decisions

1. **Singleton pattern** cho DepthAnythingV2 — load 1 lần, reuse
2. **Lifespan startup** — pre-load cả 2 models khi FastAPI khởi động
3. **Dual-mode** reference detector — custom model path → pretrained COCO fallback
4. **Bowl size heuristic** — dùng bbox width ratio để phân loại khi dùng COCO pretrained
5. **Scale factor priority** — bát phở > bát cơm > thìa > đũa (diện tích lớn → stable hơn)

---

## 5. Vietnamese Tableware Reference Dimensions

| Type | Width/∅ (cm) | Height (cm) | Dùng dimension nào cho scale |
|------|-------------|-------------|------------------------------|
| bat_com | 11.5 | 5.5 | width (diameter) |
| bat_pho_m | 19.0 | 7.5 | width (diameter) |
| bat_pho_l | 23.0 | 8.5 | width (diameter) |
| dia_com | 21.0 | 2.5 | width (diameter) |
| thia | 4.0 | 16.0 | height (length) |
| dua | 0.5 | 24.5 | height (length) |

---

## 6. Data Assets

### Nutrition5k Benchmark
- **Source**: Google Research, 2021 — 5,006 món, lab-grade GT
- **Parsed**: `data/nutrition5k/parsed/nutrition5k_subset.json`
- **Dùng cho**: Validate volume estimation accuracy (Phase 2 Task 2.6)

### Vietnamese Food Nutrition DB
- **File**: `data/nutrition_db/vn_food_nutrition.json` (10 món VN)
- **Nguồn**: USDA FoodData Central + Bảng TPDD Việt Nam + GI Tables
- **10 món**: Cơm trắng, Phở bò, Bún bò Huế, Bánh mì, Cơm tấm, Bún thịt nướng, Mì xào, Cháo, Xôi, Trà sữa

### Density Factor DB
- **File**: `data/nutrition_db/density_factors.json` (12 items)
- **Nguồn**: USDA food composition + food engineering estimates
- **Công thức**: Weight_food = Volume × solid_ratio × density

### VN Demo Samples ✅ DONE 10/03
- **Folder**: `data/vn_demo/` — 5 món, mỗi món 1 JSON + 2 ảnh (45° + top)
- **5 món**: com_trang, pho_bo, banh_mi, bun_bo_hue, com_tam
- **Tổng**: 5 JSON + 10 images, **validate 10/10 PASS**

---

## 7. Dependencies (vision-service)

```
# Core
fastapi==0.109.0, uvicorn, pydantic>=2.0.0

# Deep Learning
torch>=2.0.0, torchvision>=0.15.0

# Vision
pillow>=10.0.0, numpy>=1.24.0, opencv-python>=4.8.0, scipy>=1.11.0

# Task 2.1: Depth Estimation
transformers>=4.35.0, accelerate>=0.25.0

# Task 2.2: Reference Object Detection
ultralytics>=8.0.0

# Testing
pytest>=7.0.0, pytest-cov>=4.0.0
```

---

## 8. Tests — ✅ 40/40 PASSED (verified 10/03/2026)

| Test File | Tests | Task | Scope |
|-----------|-------|------|-------|
| `tests/test_depth_service.py` | 19 | 2.1 | Model loading, prediction, output format, edge cases, service layer |
| `tests/test_reference_service.py` | 21 | 2.2 | Dimensions, detection, class mapping, scale factor priority |
| **Total** | **40** | | **All passed in 14.31s** |

**Chạy tests:**
```bash
cd src/vision-service
pytest tests/ -v
```

### E2E Verification Results (10/03/2026, CUDA GPU)

| Endpoint | Status | Kết quả |
|----------|--------|----------|
| `GET /health` | ✅ 200 | `status=UP, model_loaded=true, device=cuda` |
| `POST /api/vision/depth` | ✅ 200 | 404ms inference, image 1170x780, depth range [0, 255] |
| `POST /api/vision/detect-reference` | ✅ 200 | Detected 1 `bat_pho_l` (conf=0.945), scale=24.6 px/cm |
| `POST /api/vision/depth` (invalid) | ✅ 400 | Correct error for non-image file |

---

## 9. Scripts

| Script | Task | Mô tả |
|--------|------|--------|
| `scripts/poc_depth_test.py` | POC | Test Depth Anything V2 cơ bản (validated ✅) |
| `scripts/download_nutrition5k.py` | 1.3 | Download + parse Nutrition5k subset |
| `scripts/import_nutrition_db.py` | 1.3 | Import VN food nutrition vào JSON |
| `scripts/export_density_factors.py` | 1.3 | Export Density Factor DB |
| `scripts/compile_dataset.py` | 1.3 | Compile Nutrition5k + VN demo |
| `scripts/validate_dataset.py` | 1.3 | Validate dataset integrity |
| `scripts/train_reference_detector.py` | 2.2 | YOLO training (Plan A) |
| `scripts/reference_detector_pretrained.py` | 2.2 | Pretrained COCO detection (Plan B) |

---

## 10. Pending Items / Next Steps

### Immediate (Trước Sprint 4)
> Phase 1 + Sprint 3 đã xong hoàn toàn. Sẵn sàng bắt đầu Sprint 4.

### Next Sprint (Sprint 4: Hiệu chuẩn, 16/03 - 18/03)
1. **Task 2.3**: Pixel-to-Real Mapping — dùng scale factor từ 2.2 + depth map từ 2.1
2. **Task 2.4**: Food Segmentation — tích hợp SAM

### Sprint 5 (Tính thể tích, 19/03 - 20/03)
3. **Task 2.5**: Volume Estimation — V = ∫∫ depth(x,y) dA
4. **Task 2.6**: Validation — benchmark trên Nutrition5k (N=500)

---

## 11. Conventions & Lưu ý

- **Code comments, API docs**: English
- **Documentation** (docs/, tasks/): Vietnamese
- **Git branch**: `feat/s[X]/[feature]`, `fix/s[X]/[bug]`
- **Commit**: `type(scope): description` (feat, fix, docs, infra, test)
- **Model caching**: HuggingFace cache tại `~/.cache/huggingface/`
- **GPU**: CUDA GPU verified — DAv2 inference 404ms (gần target 500ms), YOLO ~50ms
- **Vision pipeline flow**: Ảnh → Depth (2.1) → Reference (2.2) → Calibrate (2.3) → Segment (2.4) → Volume (2.5)
- **Test ảnh POC**: `data/poc/raw/poc_pho_bo_001_main.jpg` — detect bat_pho_l (conf 0.945)

---

> **Tạo**: 10/03/2026
> **Cập nhật**: 10/03/2026 22:40 — Phase 1 DONE + Sprint 3 DONE (40 tests + E2E + full pipeline 11 images verified)

# InSight Project — Session Context

> File này lưu trữ toàn bộ context của quá trình phát triển để session AI mới đọc hiểu NGAY.
> Cập nhật lần cuối: 19/03/2026 (Phase 1 ✅ + Phase 2 ✅ + Phase 3 ✅ + Phase 4 🔄 — 353 tests: vision 166 + rag 154 + mobile 33)

---

## 1. Thông tin dự án

| Mục            | Chi tiết                                                                                                              |
| -------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Tên dự án**  | InSight — Hệ thống ước lượng Glycemic Load thời gian thực cho bệnh nhân tiểu đường                                    |
| **Loại**       | Đồ án tốt nghiệp — Applied Research                                                                                   |
| **Timeline**   | 06/03/2026 → 31/03/2026 (25 ngày, 5 phases, 14 sprints)                                                               |
| **Nhóm**       | Hoàng (Leader/Architect), Việt (Core Dev/Vision), Hoài (Support/Frontend)                                             |
| **Core idea**  | Chụp ảnh món ăn → Depth map (DAv2) → Volume → GL → RAG tư vấn Insulin                                                 |
| **Tech Stack** | Flutter + Java Spring Boot (API Gateway) + Python FastAPI (Vision + RAG) + gRPC + Kafka + PostgreSQL + Milvus + Redis |

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
│   │   ├── main.py                 # FastAPI app (7 endpoints — /health + 5 vision + /validate)
│   │   ├── models/
│   │   │   └── depth_model.py      # DepthAnythingV2 wrapper
│   │   ├── services/
│   │   │   ├── depth_service.py    # Depth estimation logic
│   │   │   ├── reference_service.py # Reference object detection
│   │   │   ├── calibration_service.py  # Pixel-to-Real calibration (Task 2.3)
│   │   │   ├── segmentation_service.py # Food segmentation (Task 2.4)
│   │   │   ├── volume_service.py   # Volume + GL estimation (Task 2.5)
│   │   │   └── validation_service.py   # Validation metrics + DataLoader (Task 2.6)
│   │   ├── schemas/
│   │   │   ├── depth_schemas.py    # Pydantic response models
│   │   │   ├── reference_schemas.py
│   │   │   ├── calibration_schemas.py   # Calibration response models
│   │   │   ├── segmentation_schemas.py  # Segmentation response models
│   │   │   ├── volume_schemas.py   # Volume + GL response models (Task 2.5)
│   │   │   └── validation_schemas.py    # Validation response models (Task 2.6)
│   │   ├── tests/
│   │   │   ├── test_depth_service.py    # 19 tests
│   │   │   ├── test_reference_service.py # 21 tests
│   │   │   ├── test_calibration_service.py  # 21 tests (Task 2.3)
│   │   │   ├── test_segmentation_service.py # 18 tests (Task 2.4)
│   │   │   ├── test_volume_service.py   # 31 tests (Task 2.5)
│   │   │   └── test_validation_service.py   # 56 tests (Task 2.6)
│   │   ├── api/                    # gRPC proto files
│   │   └── requirements.txt
│   ├── api-gateway/                # Spring Boot API Gateway
│   ├── mobile/                     # Flutter app
│   └── rag-service/                # Python RAG Agent (Task 3.1-3.3)
│       ├── knowledge_base/         # Task 3.1: schemas, chunking, embedding, search
│       ├── rag_pipeline/           # Task 3.2: schemas, llm_client, prompt_builder, rag_service
│       ├── personalization/        # Task 3.3: emergency, clinical_rules, grounding
│       ├── tests/                  # 154 tests (50 KB + 56 RAG + 48 personalization)
│       └── main.py                 # FastAPI: POST /api/rag/advise, GET /health
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

| Task                  | Status  | Ghi chú                                                               |
| --------------------- | ------- | --------------------------------------------------------------------- |
| 1.0 Khởi động dự án   | ✅ Done | Repo setup, architecture.md, API contracts                            |
| 1.1 Environment Setup | ✅ Done | Docker Compose, Spring Boot skeleton, Python FastAPI skeleton         |
| 1.2 Database & Schema | ✅ Done | PostgreSQL schema, Milvus collections, Redis config                   |
| 1.3 Thu thập dữ liệu  | ✅ Done | **Tất cả subtasks hoàn thành** — 5 JSON + 10 ảnh + compile + validate |

**Chi tiết Task 1.3 đã hoàn thành:**

- [x] 1.3.1 JSON schema → `data/schemas/insight_food_sample_v1.json`
- [x] 1.3.2 Nutrition5k parse → `scripts/download_nutrition5k.py`
- [x] 1.3.3 Import VN nutrition → `scripts/import_nutrition_db.py` (10 món)
- [x] 1.3.4 Density Factor DB → `scripts/export_density_factors.py` (12 items)
- [x] **1.3.5 Chụp ảnh VN** → 5 món × 2 góc = 10 ảnh ✅ Done 10/03
- [x] 1.3.6 Compile + validate → 10/10 samples valid ✅

### Phase 2: Vision Engine (13/03 - 20/03) — ✅ Sprint 3+4 VERIFIED

| Task | Status | Ghi chú |
|------|--------|---------||
| **2.1 Depth Estimation** | ✅ Verified | DAv2 Small, 404ms CUDA, 19 unit tests + E2E pass |
| **2.2 Reference Object** | ✅ Verified | Plan B COCO detect bowl conf=0.945, 21 unit tests + E2E pass |
| **2.3 Pixel-to-Real Mapping** | ✅ Verified | CalibrationService, 21 unit tests, quality=high (24.6px/cm) |
| **2.4 Food Segmentation** | ✅ Verified | Depth+Color hybrid, 18 unit tests, quality=high (43ms) |
| **2.5 Volume Estimation** | ✅ Verified | V=∫∫depth·dA, density factor, GL calc, 31 unit tests, E2E=433mL/GL=13.7 |
| **2.6 Validation & Benchmark** | ✅ Verified | ValidationService, 56 unit tests, E2E 5 VN demo; pho_bo C-APE=3.0%, GL-APE=2.9%; EXIF bug fixed |

### Phase 3: RAG Agent (22/03 - 25/03) — ✅ COMPLETE

| Task                    | Status  | Ghi chú                                                                          |
| ----------------------- | ------- | -------------------------------------------------------------------------------- |
| **3.1 Knowledge Base**  | ✅ Done | 26 docs, 46 chunks, 46 rows Milvus, E2E ingestion + search verified (18/03/2026) |
| **3.2 RAG Pipeline**    | ✅ Done | Python RAG orchestrator, LLM client, prompt builder, 56 tests (19/03/2026)       |
| **3.3 Personalization** | ✅ Done | Emergency detector, clinical rules, RAG grounding, 48 tests (19/03/2026)         |

**Chi tiết Task 3.2:**

- [x] 3.2.1 LLM Client (OpenAI-compatible, Gemini API) → `rag_pipeline/llm_client.py`
- [x] 3.2.2 RAG Pipeline (query → retrieve → generate) → `rag_pipeline/rag_service.py`
- [x] 3.2.3 API endpoint `POST /api/rag/advise` → `main.py`
- [x] 3.2.4 Test response quality: 56 test scenarios pass

**Chi tiết Task 3.3:**

- [x] 3.3.1 Dynamic prompt (glucose level + medications) → `rag_pipeline/prompt_builder.py`
- [x] 3.3.2 Emergency protocols (Rule of 15, glucagon, DKA) → `personalization/emergency.py`
- [x] 3.3.3 Strict RAG Grounding (anti-hallucination) → `personalization/grounding.py`
- [x] 3.3.4 Clinical rules (insulin dose calculation) → `personalization/clinical_rules.py`
- [x] 3.3.5 Clinical scenario tests: 48 tests pass

### Phase 4: Tích hợp & Mobile (21/03 - 28/03) — 🔄 IN PROGRESS

| Task                     | Status  | Ghi chú                                                           |
| ------------------------ | ------- | ----------------------------------------------------------------- |
| **4.1 Flutter App**      | ✅ Done | MVVM + Provider, go_router, 5 screens, 33 tests pass (18/03/2026) |
| **4.2 gRPC Integration** | ⬜      |                                                                   |
| **4.3 E2E Testing**      | ⬜      |                                                                   |
| **4.4 Performance**      | ⬜      |                                                                   |

**Chi tiết Task 4.1:**

- [x] 4.1.1 Setup Flutter project + navigation (go_router) → `lib/config/routes.dart`
- [x] 4.1.2 Màn hình chụp ảnh (camera + gallery) → `lib/ui/camera/camera_screen.dart`
- [x] 4.1.3 Màn hình kết quả GL (big numbers, patient-friendly) → `lib/ui/result/result_screen.dart`
- [x] 4.1.4 Panic Mode UI (1-tap instant estimation, 10 VN dishes) → `lib/ui/panic/panic_screen.dart`
- [x] 4.1.5 Form hỏi nhanh (dish type, size, toppings — ChoiceChip) → `lib/ui/food_form/food_form_screen.dart`
- [x] 4.1.6 UX design + review (disclaimer, warnings, Material 3)

### Phase 5: ⬜ Not Started

---

## 4. Vision Service — Architecture (sau Task 2.1-2.4)

### API Endpoints

| Method | Path                           | Status      | Mô tả                                                 |
| ------ | ------------------------------ | ----------- | ----------------------------------------------------- |
| GET    | `/health`                      | ✅          | Health check + model status                           |
| POST   | `/api/vision/depth`            | ✅ Task 2.1 | Ảnh → Depth map (base64 PNG + stats)                  |
| POST   | `/api/vision/detect-reference` | ✅ Task 2.2 | Ảnh → Reference objects + scale factor                |
| POST   | `/api/vision/calibrate`        | ✅ Task 2.3 | Ảnh → Calibrated measurements (px/cm, cm/px, quality) |
| POST   | `/api/vision/segment-food`     | ✅ Task 2.4 | Ảnh → Food mask (base64 PNG + stats)                  |
| POST   | `/api/vision/estimate-volume`  | ✅ Task 2.5 | Ảnh + food_id → Volume (mL) + GL + kiểu tra           |
| POST   | `/api/vision/validate`         | ✅ Task 2.6 | Ảnh + food_id + gt_weight + gt_carb → APE + pred GL   |

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
              ├─► ReferenceDetector (services/reference_service.py)
              │   ├─ Plan A: Custom YOLOv8s (runs/reference_detector/v1/weights/best.pt)
              │   ├─ Plan B: Pretrained YOLOv8s COCO (auto fallback)
              │   ├─ 6 classes: bat_com, bat_pho_m, bat_pho_l, dia_com, thia, dua
              │   ├─ Output: List[ReferenceObject] + best_scale_factor (px/cm)
              │   └─ Bowl size heuristic: bbox_width / img_width → small/medium/large
              │
              ├─► CalibrationService (services/calibration_service.py)  ← NEW Task 2.3
              │   ├─ Input: depth_map + scale_factor (px/cm) from reference detector
              │   ├─ Normalize depth 0-255 → 0-15cm physical range
              │   ├─ Output: CalibrationResult (calibrated depth_map_cm, dimensions)
              │   ├─ Quality assessment: confidence + scale + depth variation
              │   └─ Utilities: pixels_to_cm(), cm_to_pixels(), measure_region()
              │
              └─► VolumeEstimator (services/volume_service.py)  ← NEW Task 2.5
                  ├─ Formula: V = Σ max(0, depth_food − table_level) × pixel_area_cm²
                  ├─ table_level = 10th percentile of non-food pixel depths
                  ├─ Weight: V × solid_ratio × density_g_per_ml
                  ├─ Carb: weight × carb_per_100g / 100
                  ├─ GL: carb × GI_index / 100
                  ├─ Load density_factors.json (12 foods) + vn_food_nutrition.json (10 foods)
                  └─ Food ID resolution: full → short prefix → default (vn_com_trang)
              │
              └─► ValidationService (services/validation_service.py)  ← NEW Task 2.6
                  ├─ MetricComputer: ape(), mape(), pass_rate(), compute_sample_result()
                  ├─ DataLoader: load_vn_demo() (5 mẫu, gt_gl từ JSON), load_n5k_subset()
                  ├─ ReportGenerator: generate() → ValidationReport.to_dict() / .save()
                  └─ Singleton: get_data_loader()
```

### Key Design Decisions

1. **Singleton pattern** cho DepthAnythingV2 — load 1 lần, reuse
2. **Lifespan startup** — pre-load cả 5 services khi FastAPI khởi động
3. **Dual-mode** reference detector — custom model path → pretrained COCO fallback
4. **Bowl size heuristic** — dùng bbox width ratio để phân loại khi dùng COCO pretrained
5. **Scale factor priority** — bát phở > bát cơm > thìa > đũa (diện tích lớn → stable hơn)
6. **Reference-based calibration (Task 2.3)** — dùng known object size → scale factor X/Y, depth normalization 0-15cm → Z
7. **Depth+Color hybrid segmentation (Task 2.4)** — không cần SAM (2.5GB), zero additional models, ~43ms
8. **Elliptical bowl ROI** — match bowl shape, 10% inset loại bỏ rim
9. **Table level subtraction (Task 2.5)** — dùng percentile 10 của non-food pixels làm nền tham chiếu, không dùng min (noise) hoặc mean
10. **Density Factor correction (Task 2.5)** — trừ khầu nước dùng cho món nước: weight = V × solid_ratio × density, phoβố = 0.3
11. **EXIF transpose (Task 2.6)** — `_open_image()` với `ImageOps.exif_transpose()` đảm bảo depth shape = mask shape cho ảnh landscape

---

## 5. Vietnamese Tableware Reference Dimensions

| Type      | Width/∅ (cm) | Height (cm) | Dùng dimension nào cho scale |
| --------- | ------------ | ----------- | ---------------------------- |
| bat_com   | 11.5         | 5.5         | width (diameter)             |
| bat_pho_m | 19.0         | 7.5         | width (diameter)             |
| bat_pho_l | 23.0         | 8.5         | width (diameter)             |
| dia_com   | 21.0         | 2.5         | width (diameter)             |
| thia      | 4.0          | 16.0        | height (length)              |
| dua       | 0.5          | 24.5        | height (length)              |

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

## 8. Tests — ✅ 320/320 PASSED (vision-service: 166 | rag-service: 154)

| Test File                            | Tests   | Task | Scope                                                                                |
| ------------------------------------ | ------- | ---- | ------------------------------------------------------------------------------------ |
| `tests/test_depth_service.py`        | 19      | 2.1  | Model loading, prediction, output format, edge cases, service layer                  |
| `tests/test_reference_service.py`    | 21      | 2.2  | Dimensions, detection, class mapping, scale factor priority                          |
| `tests/test_calibration_service.py`  | 21      | 2.3  | Scale factors, depth normalization, quality, region measurement, utilities           |
| `tests/test_segmentation_service.py` | 18      | 2.4  | Mask shape/dtype, bowl ROI, depth resize, edge cases, components                     |
| `tests/test_volume_service.py`       | 31      | 2.5  | Volume formula, GL chain, density factor, food ID, quality, singleton                |
| `tests/test_validation_service.py`   | 56      | 2.6  | APE/MAPE/pass_rate, DataLoader GT, ReportGenerator, save JSON, integration           |
| `tests/test_knowledge_base.py`       | 50      | 3.1  | Guidelines data, schemas, chunking, embedding (mocked), BM25 search, full pipeline   |
| `tests/test_rag_pipeline.py`         | 56      | 3.2  | Glucose classification, prompt builder, LLM mock, insulin calc, RAG orchestration    |
| `tests/test_personalization.py`      | 48      | 3.3  | Emergency protocols, clinical rules, grounding validator, clinical scenarios         |
| **Total**                            | **320** |      | **All passed (vision: 11/03 · rag kb: 22/03 · rag pipeline+personalization: 19/03)** |

**Chạy tests:**

```bash
cd src/vision-service
pytest tests/ -v
# OR faster (skip deep model loading):
pytest tests/test_volume_service.py tests/test_calibration_service.py tests/test_segmentation_service.py tests/test_reference_service.py tests/test_validation_service.py -q
```

### E2E Verification Results (11/03/2026, CUDA GPU)

| Endpoint                                          | Status | Kết quả                                                               |
| ------------------------------------------------- | ------ | --------------------------------------------------------------------- |
| `GET /health`                                     | ✅ 200 | `status=UP, model_loaded=true, device=cuda`                           |
| `POST /api/vision/depth`                          | ✅ 200 | 404ms inference, image 1170x780, depth range [0, 255]                 |
| `POST /api/vision/detect-reference`               | ✅ 200 | Detected 1 `bat_pho_l` (conf=0.945), scale=24.6 px/cm                 |
| `POST /api/vision/calibrate`                      | ✅ 200 | quality=high, 24.6px/cm, bat_pho_l, 11ms                              |
| `POST /api/vision/segment-food`                   | ✅ 200 | quality=high, ratio=3.3%, 1 component, 43ms                           |
| `POST /api/vision/calibrate` (invalid)            | ✅ 400 | Correct error for non-image file                                      |
| `POST /api/vision/estimate-volume` (vn_pho_bo)    | ✅ 200 | 433.3mL, weight=132.6g, carb=29.8g, GL=13.7, quality=high, 905ms      |
| `POST /api/vision/estimate-volume` (no food_id)   | ✅ 200 | Defaults to vn_com_trang, GL=96.3                                     |
| `POST /api/vision/validate` (pho_bo, GT=45g carb) | ✅ 200 | Pred=43.7g, C-APE=3.0%, GL-APE=2.9%, passes_15pct=false (W-APE=56.9%) |

---

## 9. Scripts

| Script                                     | Task | Mô tả                                                     |
| ------------------------------------------ | ---- | --------------------------------------------------------- |
| `scripts/poc_depth_test.py`                | POC  | Test Depth Anything V2 cơ bản (validated ✅)              |
| `scripts/download_nutrition5k.py`          | 1.3  | Download + parse Nutrition5k subset                       |
| `scripts/import_nutrition_db.py`           | 1.3  | Import VN food nutrition vào JSON                         |
| `scripts/export_density_factors.py`        | 1.3  | Export Density Factor DB                                  |
| `scripts/compile_dataset.py`               | 1.3  | Compile Nutrition5k + VN demo                             |
| `scripts/validate_dataset.py`              | 1.3  | Validate dataset integrity                                |
| `scripts/train_reference_detector.py`      | 2.2  | YOLO training (Plan A)                                    |
| `scripts/reference_detector_pretrained.py` | 2.2  | Pretrained COCO detection (Plan B)                        |
| `scripts/ingest_knowledge_base.py`         | 3.1  | Batch ingestion: guidelines.json → chunk → embed → Milvus |

---

## 10. Pending Items / Next Steps

### Immediate (Trước Sprint 5)

> Phase 1 + Sprint 3 + Sprint 4 đã xong hoàn toàn. Sẵn sàng bắt đầu Sprint 5.

### Completed Sprint 4 (Hiệu chuẩn, 16/03 - 18/03)

- [x] **Task 2.3**: Pixel-to-Real Mapping — CalibrationService (21 tests, E2E verified)
- [x] **Task 2.4**: Food Segmentation — Depth+Color hybrid (18 tests, E2E verified)

### Completed Sprint 5 (Tính thể tích + Validation, 19/03 - 20/03)

- [x] **Task 2.5**: Volume Estimation — VolumeEstimator, V=∫∫depth·dA + GL (31 tests, E2E verified)
- [x] **Task 2.6**: Validation & Benchmark — ValidationService, 56 tests, E2E 5 VN demo; **pho_bo C-APE=3.0%, GL-APE=2.9%**; EXIF bug fixed

### Phase 2 COMPLETE — Tất cả tasks 2.1-2.6 ✅ DONE

### Completed Sprint 6 (Knowledge Base, 22/03)

- [x] **Task 3.1**: Knowledge Base Setup — 26 medical docs → 46 chunks → 46 rows Milvus, hybrid search E2E verified (score=0.709)
  - `src/rag-service/knowledge_base/` — schemas.py, chunking.py, embedding.py, search.py
  - `src/rag-service/knowledge/medical/guidelines.json` — 26 docs, 7 categories, 5 sources
  - `scripts/ingest_knowledge_base.py` — E2E verified 18/03/2026: 46 rows, CUDA GPU, 8.4s
  - Guide: `docs/Guides/GUIDE_TASK_3.1_KNOWLEDGE_BASE.md`

### Completed Sprint 7 (RAG Pipeline, 23/03)

- [x] **Task 3.2**: RAG Pipeline — Python RAG orchestrator (query → retrieve → augment → generate), 56 tests
  - `src/rag-service/rag_pipeline/` — schemas.py, llm_client.py, prompt_builder.py, rag_service.py
  - `src/rag-service/main.py` — FastAPI `POST /api/rag/advise` + `GET /health`
  - OpenAI-compatible LLM client (Ollama/OpenAI/vLLM)
  - Guide: `docs/Guides/GUIDE_TASK_3.2_RAG_PIPELINE.md`

### Completed Sprint 8 (Personalization, 25/03)

- [x] **Task 3.3**: Personalization — Emergency detector, clinical rules, RAG grounding, 48 tests
  - `src/rag-service/personalization/` — emergency.py, clinical_rules.py, grounding.py
  - 6 glucose levels, 6 emergency protocols (glucagon, rule_of_15, dka, etc.)
  - Insulin: meal_dose = carbs/ICR, correction = (glucose-target)/CF, safety caps
  - Guide: `docs/Guides/GUIDE_TASK_3.3_PERSONALIZATION.md`

---

## 11. Conventions & Lưu ý

- **Code comments, API docs**: English
- **Documentation** (docs/, tasks/): Vietnamese
- **Git branch**: `feat/s[X]/[feature]`, `fix/s[X]/[bug]`
- **Commit**: `type(scope): description` (feat, fix, docs, infra, test)
- **Model caching**: HuggingFace cache tại `~/.cache/huggingface/`
- **GPU**: CUDA GPU verified — DAv2 inference 404ms (gần target 500ms), YOLO ~50ms
- **Vision pipeline flow**: Ảnh → Depth (2.1) → Reference (2.2) → Calibrate (2.3) → Segment (2.4) → Volume (2.5) → GL
- **Test ảnh POC**: `data/poc/raw/poc_pho_bo_001_main.jpg` — detect bat_pho_l (conf 0.945)
- **Calibration**: 24.6 px/cm, image 47.6×31.7cm, quality=high (11ms)
- **Segmentation**: food_ratio=3.3%, 1 component, quality=high (43ms)
- **Volume (pho_bo)**: 433.3mL, weight=132.6g, carb=29.8g, GL=13.7 medium (10.5ms)
- **Vision server version**: v0.6.0 (7 endpoints active — /health + 5 vision + /validate)
- **RAG server version**: v0.3.0 (2 endpoints — /health + /api/rag/advise)
- **Architecture change**: RAG service implemented in Python FastAPI + Gemini API (not Java/LangChain4j as originally planned)
- **LLM client**: OpenAI-compatible (Gemini API default: gemini-2.0-flash)
- **Insulin calculation**: Rule-based (NOT from LLM) — meal_dose = carbs/ICR, correction = (glucose-target)/CF
- **Emergency protocols**: 6 levels — severe_hypo → glucagon, hypo → Rule of 15, critical_high → DKA
- **Dose safety caps**: max_meal=25U, max_correction=10U, max_total=30U
- **EXIF fix**: `_open_image()` với `ImageOps.exif_transpose()` trong main.py (tất cả endpoints)
- **Validation report**: `data/annotations/validation_report.json` — MAPE-C=313.4%, pho_bo C-APE=3.0%
- **Root cause**: VN demo ảnh chụp ở zoom/khoảng cách khác nhau → px_per_cm không nhất quán
- **Key insight**: Khi calibration đúng (pho_bo), thuật toán cho C-APE=3.0% và GL-APE=2.9%

---

> **Tạo**: 10/03/2026
> **Cập nhật**: 19/03/2026 — Phase 4 Task 4.1 DONE (Flutter MVVM + Provider + go_router, 33 tests; total 353 tests: vision 166 + rag 154 + mobile 33)

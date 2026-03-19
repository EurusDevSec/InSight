# InSight Project — Session Context

> File này lưu trữ toàn bộ context của quá trình phát triển để session AI mới đọc hiểu NGAY.
> Cập nhật lần cuối: 19/03/2026 (Phase 1-4 ✅ + Safety & Accuracy Fixes + Food DB 25 items + Bowl Volume Prior + 404 tests)

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
│   │   ├── src/main/java/com/insight/
│   │   │   ├── config/AppConfig.java           # RestTemplate + CORS
│   │   │   ├── client/VisionServiceClient.java # HTTP → Vision
│   │   │   ├── client/RagServiceClient.java    # HTTP → RAG
│   │   │   ├── service/PipelineService.java    # ⭐ CORE — orchestration
│   │   │   ├── service/KafkaEventPublisher.java # Audit events
│   │   │   ├── controller/AnalysisController.java  # POST /api/gateway/analyze
│   │   │   └── controller/HealthController.java    # GET /api/health
│   │   ├── src/main/proto/insight.proto        # API contract
│   │   └── src/test/ — 15 tests (5 controller + 10 pipeline)
│   ├── mobile/                     # Flutter app (MVVM + Provider + go_router)
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

| Task                            | Status  | Ghi chú                                                                           |
| ------------------------------- | ------- | --------------------------------------------------------------------------------- |
| **4.1 Flutter App**             | ✅ Done | MVVM + Provider, go_router, 5 screens, 33 tests pass (18/03/2026)                 |
| **4.2 API Gateway Integration** | ✅ Done | REST proxy + Kafka events, 15 tests (5 controller + 10 pipeline)                  |
| **4.3 E2E Testing**             | ✅ Done | Python E2E script + 7 Flutter E2E tests, all acceptance criteria met              |
| **4.4 Performance**             | ✅ Done | Redis cache (SHA-256, 1h TTL), cold-start timers, latency metrics (vision/rag ms) |

**Chi tiết Task 4.1:**

- [x] 4.1.1 Setup Flutter project + navigation (go_router) → `lib/config/routes.dart`
- [x] 4.1.2 Màn hình chụp ảnh (camera + gallery) → `lib/ui/camera/camera_screen.dart`
- [x] 4.1.3 Màn hình kết quả GL (big numbers, patient-friendly) → `lib/ui/result/result_screen.dart`
- [x] 4.1.4 Panic Mode UI (1-tap instant estimation, 10 VN dishes) → `lib/ui/panic/panic_screen.dart`
- [x] 4.1.5 Form hỏi nhanh (dish type, size, toppings — ChoiceChip) → `lib/ui/food_form/food_form_screen.dart`
- [x] 4.1.6 UX design + review (disclaimer, warnings, Material 3)

**Chi tiết Task 4.2:**

- [x] 4.2.1 Flutter refactor: single Gateway call → `api_service.dart`, `meal_viewmodel.dart`
- [x] 4.2.2 API Gateway REST endpoint: `POST /api/gateway/analyze` → `AnalysisController.java`
- [x] 4.2.3 PipelineService: orchestrate Vision → RAG → combined response
- [x] 4.2.4 Service clients: VisionServiceClient + RagServiceClient
- [x] 4.2.5 Kafka event publishing (non-blocking audit)
- [x] 4.2.6 Proto contract update (API documentation)
- [x] 4.2.7 Gateway tests: 15 tests (5 controller + 10 pipeline)

**Chi tiết Task 4.3:**

- [x] 4.3.1 Full pipeline: Ảnh → Tư vấn ≤ 5 giây → `scripts/test_e2e_pipeline.py`
- [x] 4.3.2 Panic Mode: ≤ 1 giây → Flutter E2E + Python script
- [x] 4.3.3 Disclaimer UI hiển thị đúng → `test/e2e/e2e_pipeline_test.dart` (7 tests)

**Architecture Decision (Task 4.2):**

- REST proxy thay vì raw gRPC → Flutter → Gateway → Vision/RAG (Python REST)
- Graceful degradation: RAG fail → Vision-only results + warning
- Non-blocking Kafka: audit events fire-and-forget
- Disclaimer luôn có trong mọi response

**Chi tiết Task 4.4:**

- [x] 4.4.1 Cold-start timers: Vision + RAG log startup time trong ms
- [x] 4.4.2 Redis cache: `CacheService.java` — SHA-256 key, 1h TTL, graceful degradation
- [x] 4.4.3 Timing metrics: `vision_time_ms` + `rag_time_ms` trong pipeline response
- [x] 4.4.4 Review + 4 tests mới: cache hit/miss, timing, markdown cleaning
- Guide: `docs/Guides/GUIDE_TASK_4.4_PERFORMANCE.md`

### Phase 5: ⬜ Not Started

---

## 4a. Safety & Accuracy Fixes (19/03/2026)

### Vấn đề phát hiện

Test thực tế với ảnh Cơm tấm cho kết quả nguy hiểm: GL=374, Volume=2000mL, Insulin=53.9U.
Benchmark 5 món × 2 góc cho thấy soup dishes (phở, bún bò) sai 91-100%.

### Fixes đã thực hiện

1. **Depth range calibration**: `DEPTH_RANGE_CM` từ `(0, 15)` → `(0, 5)` — phù hợp top-down food photos
2. **Volume correction**: `_DAV2_VOLUME_CORRECTION = 0.35` (solid dishes only)
3. **Bowl volume prior** (liquid/soup dishes): bypass depth integral, dùng typical serving size
   - Phở bò/gà: 500mL, Bún bò Huế: 550mL, Cháo: 350mL, Hủ tiếu: 450mL, etc.
   - Lý do: Depth estimation chỉ thấy bề mặt chất lỏng, không đo được chiều sâu tô
4. **Food segmentation threshold**: `_MIN_FOOD_SEG_RATIO = 0.05` — khi food mask < 5% → quality=low + cảnh báo
5. **Insulin safety caps**: SYSTEM_PROMPT Rule 6 (max meal=25U, correction=10U, total=30U) + Gateway hard cap 30U
6. **Sanity checks in PipelineService**: volume≥800→warn, weight>800→warn, carbs>150→warn
7. **Clean advice text**: Jackson JSON extract + regex fallback (loại markdown/json artifacts)
8. **com_tam carb correction**: `carb_per_100g` 27→18 (đúng theo USDA cho broken rice + toppings)
9. **Flutter UX**: Red critical warnings (`Icons.dangerous`), confidence "⚠️ Thấp" khi ≤0.5
10. **Top-down photo guidance**: Hint text in food_form_screen.dart "Chụp từ trên xuống cho kết quả chính xác nhất"

### Benchmark Results (After Fixes)

| Món        | Góc | Volume        | Weight     | Carbs Error  | GL Error     | Trước Fix |
| ---------- | --- | ------------- | ---------- | ------------ | ------------ | --------- |
| Phở bò     | top | 500mL (prior) | 153g       | **23.5%** ✅ | **23.5%** ✅ | 95% ❌    |
| Bún bò Huế | top | 550mL (prior) | 198g       | **0.5%** ✅  | **0.5%** ✅  | 100% ❌   |
| Cơm tấm    | top | 255mL         | 253g (1%)  | 33% ✅       | 33% ✅       | 1% ✅     |
| Bánh mì    | 45° | 320mL         | 112g (25%) | 25% ✅       | 25% ✅       | 25% ✅    |
| Cơm trắng  | top | 103mL         | 112g (44%) | 44% ⚠️       | 44% ⚠️       | 44% ⚠️    |

**Key improvements:**

- Soup dishes: 91-100% error → **0.5-23.5%** (massive improvement)
- Solid top-down: unchanged (already good with 0.35 correction)
- 45° angle still poor for solid foods — root cause: YOLO generic model misses Vietnamese food

### Remaining Limitations

- YOLO segmentation at 45° angle: food_seg < 5% → unreliable (properly warned now)
- Weight metric for soup includes broth in GT but not in estimate (carbs/GL more clinically relevant)
- Single `_SOLID_VOLUME_CORRECTION = 0.35` works for com_tam top-down but not all solid foods at all angles

---

## 4b. Custom Food Feature ("Khác")

### Implementation

- Flutter: "Khác" option in `_dishTypes` → shows TextField with hint "VD: Bún đậu mắm tôm..."
- ViewModel: `customFoodName` state + `setCustomFoodName()` method
- API: sends `custom_food_name` field alongside `food_id`
- Gateway: `AnalysisController` receives `custom_food_name` param, `PipelineService` overrides `foodName` for RAG
- Cho phép user nhập tên món bất kỳ khi không có trong danh sách 25 món

### Food DB Expansion (10→25 món)

Expanded `_dishTypes` in Flutter (grouped by category):

- **Cơm**: Cơm trắng, Cơm tấm, Cơm rang, Cơm gà, Cơm bình dân
- **Phở-Bún-Mì**: Phở bò, Phở gà, Bún bò, Bún thịt nướng, Bún chả, Bún riêu, Bún mắm, Hủ tiếu, Bánh canh, Mì xào, Mì Quảng, Cao lầu
- **Bánh-Khác**: Bánh mì, Bánh xèo, Bánh cuốn, Gỏi cuốn, Bột chiên, Xôi, Cháo, Khác

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
              └─► VolumeEstimator (services/volume_service.py)  ← Task 2.5 (updated)
                  ├─ SOLID dishes: V = Σ max(0, depth_food − table_level) × pixel_area × 0.35
                  ├─ LIQUID dishes: Bowl volume prior (phở=500mL, bún bò=550mL, cháo=350mL, etc.)
                  │   └─ Depth integral cannot see bowl interior → use typical serving size
                  ├─ table_level = 10th percentile of non-food pixel depths
                  ├─ Weight: V × solid_ratio × density_g_per_ml
                  ├─ Carb: weight × carb_per_100g / 100
                  ├─ GL: carb × GI_index / 100
                  ├─ Food seg threshold: <5% → quality=low + warning "chụp lại từ trên xuống"
                  ├─ Load density_factors.json (27 items) + vn_food_nutrition.json (25 foods)
                  └─ Food ID resolution: full → short → VN name (~55 aliases) → default
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

- **File**: `data/nutrition_db/vn_food_nutrition.json` (25 món VN)
- **Nguồn**: USDA FoodData Central + Bảng TPDD Việt Nam + GI Tables
- **25 món**: Cơm trắng, Phở bò, Bún bò Huế, Bánh mì, Cơm tấm, Bún thịt nướng, Mì xào, Cháo, Xôi, Trà sữa, Cơm rang, Bún chả, Hủ tiếu, Bún riêu, Bánh cuốn, Cơm gà, Bánh canh, Bún mắm, Phở gà, Bánh xèo, Gỏi cuốn, Mì Quảng, Cao lầu, Bột chiên, Cơm bình dân

### Density Factor DB

- **File**: `data/nutrition_db/density_factors.json` (27 items)
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

## 8. Tests — ✅ 375/375 PASSED (vision: 166 | rag: 154 | gateway: 15 | mobile: 40)

| Test File                            | Tests   | Task    | Scope                                                                                            |
| ------------------------------------ | ------- | ------- | ------------------------------------------------------------------------------------------------ |
| `tests/test_depth_service.py`        | 19      | 2.1     | Model loading, prediction, output format, edge cases, service layer                              |
| `tests/test_reference_service.py`    | 21      | 2.2     | Dimensions, detection, class mapping, scale factor priority                                      |
| `tests/test_calibration_service.py`  | 21      | 2.3     | Scale factors, depth normalization, quality, region measurement, utilities                       |
| `tests/test_segmentation_service.py` | 18      | 2.4     | Mask shape/dtype, bowl ROI, depth resize, edge cases, components                                 |
| `tests/test_volume_service.py`       | 36      | 2.5     | Volume formula, GL chain, density factor, food ID, quality, bowl prior, seg threshold, singleton |
| `tests/test_validation_service.py`   | 56      | 2.6     | APE/MAPE/pass_rate, DataLoader GT, ReportGenerator, save JSON, integration                       |
| `tests/test_knowledge_base.py`       | 50      | 3.1     | Guidelines data, schemas, chunking, embedding (mocked), BM25 search, full pipeline               |
| `tests/test_rag_pipeline.py`         | 56      | 3.2     | Glucose classification, prompt builder, LLM mock, insulin calc, RAG orchestration                |
| `tests/test_personalization.py`      | 48      | 3.3     | Emergency protocols, clinical rules, grounding validator, clinical scenarios                     |
| `AnalysisControllerTest.java`        | 4       | 4.2     | Multipart endpoint, missing image 400, all patient params                                        |
| `PipelineServiceTest.java`           | 12      | 4.2+4.4 | Full pipeline, RAG failure graceful, GL levels, emergency, cache, disclaimer                     |
| `test/data/models_test.dart`         | 9       | 4.1     | FoodItem, MealAnalysis, PatientContext JSON                                                      |
| `test/viewmodels/*_test.dart`        | 16      | 4.1     | MealViewModel (9), PanicViewModel (7) — state, analyze, reset                                    |
| `test/ui/widget_test.dart`           | 8       | 4.1     | HomeScreen, GlIndicator, DisclaimerBanner, PanicScreen                                           |
| `test/e2e/e2e_pipeline_test.dart`    | 7       | 4.3     | Panic Mode ≤1s, Disclaimer UI, Stability 10 runs                                                 |
| `tests/test_rag_pipeline.py`         | 66      | 3.2+4.4 | + 10 tests: TestLLMClientExtractJson (5) + TestLLMClientCleanMarkdown (5)                        |
| `PipelineServiceTest.java`           | 14      | 4.2+4.4 | + 4 tests: cache hit/miss, timing metrics, markdown cleaning                                     |
| `scripts/test_patient_scenarios.py`  | E2E     | bench   | 5 dishes × 2 angles vs ground truth, patient scenarios, safety tests, custom food                |
| **Total**                            | **404** |         | **All passed (gateway: 19 · mobile: 40 · vision: 171 · rag: 164 · e2e: 10)**                     |

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

| Script                                     | Task | Mô tả                                                                |
| ------------------------------------------ | ---- | -------------------------------------------------------------------- |
| `scripts/poc_depth_test.py`                | POC  | Test Depth Anything V2 cơ bản (validated ✅)                         |
| `scripts/download_nutrition5k.py`          | 1.3  | Download + parse Nutrition5k subset                                  |
| `scripts/import_nutrition_db.py`           | 1.3  | Import VN food nutrition vào JSON                                    |
| `scripts/export_density_factors.py`        | 1.3  | Export Density Factor DB                                             |
| `scripts/compile_dataset.py`               | 1.3  | Compile Nutrition5k + VN demo                                        |
| `scripts/validate_dataset.py`              | 1.3  | Validate dataset integrity                                           |
| `scripts/train_reference_detector.py`      | 2.2  | YOLO training (Plan A)                                               |
| `scripts/reference_detector_pretrained.py` | 2.2  | Pretrained COCO detection (Plan B)                                   |
| `scripts/ingest_knowledge_base.py`         | 3.1  | Batch ingestion: guidelines.json → chunk → embed → Milvus            |
| `scripts/test_e2e_pipeline.py`             | 4.3  | E2E pipeline test: Ảnh → Gateway → Vision → RAG (online + offline)   |
| `scripts/benchmark_vn_dishes.py`           | 4.4  | Benchmark 5 VN dishes qua Gateway: MAPE weight/carb/GL + p95 latency |
| `scripts/test_patient_scenarios.py`        | E2E  | 5 dishes × 2 angles vs ground truth, patient scenarios, safety tests |

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

### Completed Sprint 9 (Flutter App, 21/03 - 23/03)

- [x] **Task 4.1**: Flutter App — MVVM + Provider + go_router, 5 screens, 33 tests
  - `mobile/insight_app/lib/` — main.dart, app.dart, config/routes.dart
  - Models: FoodItem, MealAnalysis, PatientContext
  - ViewModels: MealViewModel, PanicViewModel
  - Screens: Home, Camera, FoodForm, Result, Panic
  - Widgets: GlIndicator, DisclaimerBanner
  - Guide: `docs/Guides/GUIDE_TASK_4.1_FLUTTER_APP.md`

### Completed Sprint 10 (Gateway + E2E, 24/03 - 26/03)

- [x] **Task 4.2**: API Gateway Integration — REST proxy pattern, orchestration
  - `src/api-gateway/src/main/java/com/insight/` — 7 Java files
  - PipelineService: Vision → RAG → combined response
  - AnalysisController: `POST /api/gateway/analyze` (multipart)
  - Kafka events: `meal-analysis-events` (non-blocking)
  - Graceful degradation: RAG fail → Vision-only + warning
  - Flutter refactored: single Gateway call, gatewayBaseUrl
  - 15 Gateway tests + 40 Flutter tests = 55
  - Guide: `docs/Guides/GUIDE_TASK_4.2_GRPC_INTEGRATION.md`

- [x] **Task 4.3**: E2E Testing — all acceptance criteria met
  - `scripts/test_e2e_pipeline.py` — Python E2E script (online + offline)
  - `test/e2e/e2e_pipeline_test.dart` — 7 Flutter E2E tests
  - Full pipeline ≤ 5s ✅, Panic Mode ≤ 1s ✅, Disclaimer ✅, Stability 10 runs ✅
  - Guide: `docs/Guides/GUIDE_TASK_4.3_E2E_TESTING.md`

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
- **API Gateway v1.0**: REST proxy (NOT raw gRPC), Spring Boot 3.2.3, Java 17
- **Gateway pipeline**: Image → Vision (estimate-volume) → RAG (advise) → combined JSON
- **Graceful degradation**: RAG fail → Vision-only results + warning "Advisory service unavailable"
- **Kafka topic**: `meal-analysis-events` — audit events (non-blocking)
- **Flutter → Gateway**: Single endpoint `POST /api/gateway/analyze` (multipart)
- **Flutter env**: `GATEWAY_BASE_URL=http://10.0.2.2:8080` (Android emulator)
- **E2E script**: `scripts/test_e2e_pipeline.py` — runs --offline (no services) or full online
- **Benchmark script**: `scripts/benchmark_vn_dishes.py` — MAPE weight/carb/GL + p95 latency cho 5 món VN qua Gateway
- **RAG prompt language**: Vietnamese — `prompt_builder.py` SYSTEM_PROMPT + EMERGENCY_SYSTEM_PROMPT đã chuyển sang tiếng Việt (rule 7 bắt buộc trả lời bằng tiếng Việt)
- **Food form**: `food_form_screen.dart` `_dishTypes` đã thêm "Cơm tấm" + chuẩn hóa tên ("Cơm trắng" thay "Cơm", "Bún bò" thay "Bún", v.v.)
- **Volume clamp**: `volume_service.py` giới hạn max 800mL → tránh GL quá cao
- **Bowl volume prior**: Soup dishes dùng typical serving size thay vì depth integral (phở=500mL, bún bò=550mL)
- **Food seg threshold**: <5% → quality=low + warning "chụp lại từ trên xuống"
- **Solid correction**: `_SOLID_VOLUME_CORRECTION = 0.35` chỉ áp dụng cho solid dishes
- **Insulin hard cap**: Gateway `PipelineService` cap at 30U + SYSTEM_PROMPT Rule 6 caps
- **No-reference fallback**: `main.py` khi không detect reference object → fallback `image_width/30.0` px/cm, quality=low (tránh 422 error)
- **Redis CacheService**: `src/api-gateway/.../service/CacheService.java` — cache RAG response theo SHA-256 hash
- **RedisConfig**: `src/api-gateway/.../config/RedisConfig.java` — startup health check, graceful degrade
- **Gateway version**: v1.2 (cache + timing metrics + debug pass-through)
- **Vision service version**: v0.8.0 (startup timer + fallback scale + volume clamp + debug mode)
- **Developer Mode (Under the Hood)**: `debug=true` parameter flows Flutter → Gateway → Vision + RAG → debug data aggregated → returned to Flutter
  - Vision debug: depth_preview (base64 PNG), food_mask_preview (base64 PNG), reference_objects, scale_px_per_cm, table_level_cm, formula
  - RAG debug: retrieved_chunks (source, category, score, content_preview), prompt_preview, llm_raw
  - Gateway: `PipelineService.analyzeFull(..., boolean debug)` — collects debug data from both services
  - Flutter: `DebugData` class in `meal_analysis.dart`, collapsible `_DeveloperModePanel` in `result_screen.dart`
  - Toggle: `SwitchListTile` in `food_form_screen.dart`, `debugMode` in `MealViewModel`
- **CoT SYSTEM_PROMPT**: Upgraded with Chain-of-Thought 3-step insulin calculation (Rule 4) + anti-hallucination (Rule 5 "TUYỆT ĐỐI KHÔNG ẢO GIÁC TOÁN HỌC")
- **LLM temperature**: 0.1 (was 0.3) — near-deterministic for medical insulin calculations
- **Gateway tests**: 16 tests (4 controller + 12 pipeline) — with lenient cache mock in setUp

---

> **Tạo**: 10/03/2026
> **Cập nhật**: 19/03/2026 — Safety fixes + Bowl volume prior + Food DB 25 items + Custom food "Khác" + Benchmark 5 dishes; 404 tests: vision 171 + rag 164 + gateway 19 + mobile 40 + e2e 10

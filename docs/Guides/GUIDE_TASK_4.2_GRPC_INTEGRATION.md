# 📖 HƯỚNG DẪN CHI TIẾT TASK 4.2: API GATEWAY INTEGRATION

> **Assignee**: Hoàng (chính), Việt (review)
> **Thời gian**: Sprint 10 (Phase 4)
> **Tiền đề**: Task 4.1 (Flutter App ✅), Task 2.x (Vision Service ✅), Task 3.x (RAG Service ✅)
> **Tham chiếu**: [TASK_4.2](../Tasks/TASK_4.2_GRPC_INTEGRATION.md) | [plan.md](../plan.md)
> **Cập nhật**: 06/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Flutter App ──► API Gateway ──► Vision Service (Python/FastAPI)    │
│       (4.1✅)     (4.2◄◄◄)       ──► RAG Service (Python/FastAPI)  │
│                                                                     │
│  ► Task 4.2  API GATEWAY INTEGRATION  ◄◄◄  BẠN ĐANG Ở ĐÂY        │
│    │                                                                │
│    │  Mục tiêu: Gateway orchestrate Vision → RAG pipeline          │
│    │  Pattern: REST Proxy + Kafka Events                           │
│    │                                                                │
│    │  📌 Quyết định kiến trúc:                                     │
│    │  • REST-based proxy thay vì raw gRPC (thực tế cho đồ án)     │
│    │  • Proto file = API contract documentation                    │
│    │  • Kafka cho audit events (non-blocking)                      │
│    │  • Graceful degradation khi RAG fail                          │
│    │                                                                │
│    │  ⚡ PIPELINE:                                                  │
│    │    Flutter → Gateway → Vision (depth + volume + GL)           │
│    │                      → RAG (advice + insulin suggestion)      │
│    │                      → Kafka (audit event)                    │
│    │    Flutter ← Gateway ← Combined response                     │
│    │                                                                │
│    └───► Task 4.3: E2E testing                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Kiến trúc Gateway

```
┌──────────────┐     multipart/form-data      ┌──────────────────┐
│  Flutter App  │ ──────────────────────────── │  API Gateway     │
│  (mobile)     │       POST /api/gateway/     │  (Spring Boot)   │
│               │       analyze                │  port 8080       │
└──────────────┘                               └────────┬─────────┘
                                                        │
                                    ┌───────────────────┼───────────────────┐
                                    │                   │                   │
                                    ▼                   ▼                   ▼
                          ┌─────────────┐     ┌─────────────┐     ┌────────────┐
                          │ Vision Svc  │     │  RAG Svc    │     │   Kafka    │
                          │ FastAPI     │     │  FastAPI    │     │  Broker    │
                          │ port 8000   │     │  port 8001  │     │  port 9092 │
                          │             │     │             │     │            │
                          │ POST /api/  │     │ POST /api/  │     │ topic:     │
                          │ vision/     │     │ rag/advise  │     │ meal-      │
                          │ estimate-   │     │             │     │ analysis-  │
                          │ volume      │     │             │     │ events     │
                          └─────────────┘     └─────────────┘     └────────────┘
```

---

## 2. Cấu trúc Source Code

```
src/api-gateway/
├── build.gradle                           # Spring Boot 3.2.3 + Kafka
├── src/main/
│   ├── proto/
│   │   └── insight.proto                  # API contract (documentation)
│   ├── resources/
│   │   └── application.yml                # Config (ports, URLs, Kafka)
│   └── java/com/insight/
│       ├── ApiGatewayApplication.java     # Entry point
│       ├── config/
│       │   └── AppConfig.java             # RestTemplate + CORS
│       ├── client/
│       │   ├── VisionServiceClient.java   # HTTP → Vision
│       │   └── RagServiceClient.java      # HTTP → RAG
│       ├── service/
│       │   ├── PipelineService.java       # ⭐ CORE — orchestration
│       │   └── KafkaEventPublisher.java   # Audit events
│       └── controller/
│           ├── AnalysisController.java    # POST /api/gateway/analyze
│           └── HealthController.java      # GET /api/health
└── src/test/java/com/insight/
    ├── controller/
    │   └── AnalysisControllerTest.java    # 5 tests
    └── service/
        └── PipelineServiceTest.java       # 10 tests
```

---

## 3. Pipeline Logic (PipelineService)

### 3.1 Flow chính

```
analyzeFull(image, foodId, glucoseLevel, diabetesType, ...)
    │
    ├─1─► visionClient.estimateVolume(image, foodId)
    │     → food_name, volume_ml, weight_g, carbs_g, glycemic_load
    │     → estimation_quality → confidence mapping
    │
    ├─2─► GL Level Classification
    │     GL < 10   → "low"
    │     10 ≤ GL ≤ 20 → "medium"
    │     GL > 20   → "high"
    │
    ├─3─► ragClient.getAdvice(foodName, GL, carbsG, patientContext)
    │     → advice, insulin_suggestion, emergency_alert
    │     ⚠️ Graceful: nếu RAG fail → trả Vision-only + warning
    │
    ├─4─► Build response (LinkedHashMap, cố định thứ tự field)
    │     + disclaimer (luôn có)
    │     + pipeline_time_ms
    │
    └─5─► kafkaPublisher.publishMealAnalysis(response)  [non-blocking]
```

### 3.2 Confidence Mapping

| estimation_quality | confidence | GL Level  |
| ------------------ | ---------- | --------- |
| "high"             | 0.9        | —         |
| "medium"           | 0.7        | —         |
| "low"              | 0.5        | + warning |

### 3.3 Graceful RAG Failure

```java
try {
    Map<String, Object> ragResult = ragClient.getAdvice(...);
    // extract advice, insulin, emergency
} catch (Exception e) {
    // NOT re-thrown — pipeline continues
    warnings.add("Advisory service unavailable — showing volume analysis only");
    // advice = null, insulinSuggestion = null
}
```

### 3.4 Emergency Alert Handling

```java
if (ragResult.containsKey("emergency_alert")) {
    Map<String, Object> alert = (Map<String, Object>) ragResult.get("emergency_alert");
    String alertType = (String) alert.getOrDefault("alert_type", "WARNING");
    String action = (String) alert.getOrDefault("immediate_action", "");
    warnings.add("⚠️ " + alertType + ": " + action);
}
```

---

## 4. REST Endpoints

### 4.1 POST /api/gateway/analyze

**Content-Type:** `multipart/form-data`

**Parameters:**

| Field                | Type   | Required | Default  | Mô tả                     |
| -------------------- | ------ | -------- | -------- | ------------------------- |
| `image`              | File   | ✅       | —        | JPEG/PNG, max 10MB        |
| `food_id`            | String | ❌       | null     | ID món (vn_com_trang)     |
| `glucose_level`      | Double | ❌       | null     | Đường huyết mg/dL         |
| `diabetes_type`      | String | ❌       | "type_2" | type_1/type_2/gestational |
| `insulin_carb_ratio` | Double | ❌       | null     | 1 Unit per X grams        |
| `correction_factor`  | Double | ❌       | null     | mg/dL per 1 Unit          |
| `target_glucose`     | Double | ❌       | 120.0    | Mục tiêu mg/dL            |

**Response (200 OK):**

```json
{
  "food_name": "Cơm trắng",
  "volume_ml": 433.2,
  "weight_g": 180.5,
  "carbs_g": 45.5,
  "glycemic_load": 13.7,
  "gl_level": "medium",
  "confidence": 0.9,
  "advice": "Với GL trung bình, bạn nên ăn kèm rau xanh...",
  "insulin_suggestion": "4.5 units (ICR 1:10, 45.5g carbs)",
  "warnings": [],
  "pipeline_time_ms": 2340,
  "disclaimer": "Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ."
}
```

### 4.2 GET /api/health

```json
{
  "status": "UP",
  "service": "insight-api-gateway"
}
```

---

## 5. Service Clients

### 5.1 VisionServiceClient

```java
@Service
public class VisionServiceClient {
    @Value("${insight.services.vision-url}")
    private String visionBaseUrl;  // default: http://localhost:8000

    // POST multipart/form-data → /api/vision/estimate-volume
    public Map<String, Object> estimateVolume(MultipartFile image, String foodId);

    // GET /health → boolean
    public boolean isHealthy();
}
```

### 5.2 RagServiceClient

```java
@Service
public class RagServiceClient {
    @Value("${insight.services.rag-url}")
    private String ragBaseUrl;  // default: http://localhost:8001

    // POST JSON → /api/rag/advise
    public Map<String, Object> getAdvice(
        String mealDescription, Double glycemicLoad,
        Double carbsG, Map<String, Object> patientContext);

    // GET /health → boolean
    public boolean isHealthy();
}
```

---

## 6. Kafka Events

**Topic:** `meal-analysis-events`

**Message:** JSON serialization toàn bộ response

```java
@Service
public class KafkaEventPublisher {
    // Non-blocking: exception caught, logged, không break pipeline
    public void publishMealAnalysis(Map<String, Object> analysisResult);
}
```

---

## 7. Proto Contract (insight.proto)

Proto file phục vụ mục đích **API contract documentation** (không compile thành gRPC code):

```protobuf
service InsightService {
  rpc AnalyzeMeal (MealAnalysisRequest) returns (MealAnalysisResponse);
}

message MealAnalysisRequest {
  bytes image_data = 1;
  string food_id = 2;
  PatientContext patient_context = 3;
}

message MealAnalysisResponse {
  string food_name = 1;
  double volume_ml = 2;
  double weight_g = 3;
  double carbs_g = 4;
  double glycemic_load = 5;
  string gl_level = 6;
  double confidence = 7;
  string advice = 8;
  string insulin_suggestion = 9;
  repeated string warnings = 10;
  int64 pipeline_time_ms = 11;
  string disclaimer = 12;
}
```

---

## 8. Configuration

### 8.1 application.yml (key settings)

```yaml
server:
  port: 8080
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 10MB

insight:
  services:
    vision-url: ${VISION_SERVICE_URL:http://localhost:8000}
    rag-url: ${RAG_SERVICE_URL:http://localhost:8001}
  kafka:
    topic:
      meal-analysis: meal-analysis-events
```

### 8.2 Environment Variables

| Biến                 | Default               | Mô tả              |
| -------------------- | --------------------- | ------------------ |
| `VISION_SERVICE_URL` | http://localhost:8000 | Vision service URL |
| `RAG_SERVICE_URL`    | http://localhost:8001 | RAG service URL    |

---

## 9. Tests

### 9.1 PipelineServiceTest — 10 tests

| Test                                | Mô tả                                      |
| ----------------------------------- | ------------------------------------------ |
| fullPipelineReturnsCorrectResult    | Vision + RAG gọi thành công, verify fields |
| pipelineGracefullyHandlesRagFailure | RAG exception → Vision-only + warning      |
| glLevelLow                          | GL < 10 → "low"                            |
| glLevelMedium                       | 10 ≤ GL ≤ 20 → "medium"                    |
| glLevelHigh                         | GL > 20 → "high"                           |
| emergencyAlertAddedToWarnings       | Emergency alert → warnings list            |
| lowQualityEstimationAddsWarning     | quality="low" → warning + confidence 0.5   |
| responseAlwaysHasDisclaimer         | disclaimer field luôn có                   |
| pipelineTimeMsIsTracked             | pipeline_time_ms ≥ 0                       |

### 9.2 AnalysisControllerTest — 5 tests

| Test                                 | Mô tả                             |
| ------------------------------------ | --------------------------------- |
| analyzeShouldReturnMealResult        | Full params → 200 + đầy đủ fields |
| analyzeShouldWorkWithImageOnly       | Image-only → 200                  |
| analyzeShouldReturn400WithoutImage   | No image → 400                    |
| analyzeShouldIncludeAllPatientParams | Tất cả patient params             |

### 9.3 Chạy tests

```bash
cd src/api-gateway
./gradlew test              # All 15 tests
./gradlew test --info       # Verbose output
```

---

## 10. Chạy Services

```bash
# 1. Infrastructure
cd infra/docker && docker compose up -d

# 2. Vision Service
cd src/vision-service && python main.py

# 3. RAG Service
cd src/rag-service && python main.py

# 4. API Gateway
cd src/api-gateway && ./gradlew bootRun

# 5. Test endpoint
curl -X POST http://localhost:8080/api/gateway/analyze \
  -F "image=@test.jpg" \
  -F "food_id=vn_com_trang" \
  -F "glucose_level=120"
```

---

## 11. Thiết kế đáng chú ý

| Pattern                  | Mô tả                                                 |
| ------------------------ | ----------------------------------------------------- |
| **REST Proxy**           | Gateway forward HTTP thay vì gRPC (đơn giản, thực tế) |
| **Graceful Degradation** | RAG fail → Vision-only results + warning              |
| **Non-blocking Kafka**   | Audit events fire-and-forget                          |
| **Disclaimer**           | Luôn có trong mọi response                            |
| **Safe Type Casting**    | Helper methods getNum/getStr tránh ClassCastException |
| **LinkedHashMap**        | Response fields cố định thứ tự                        |
| **CORS**                 | Cho phép tất cả origins (dev mode)                    |

---

_Cập nhật lần cuối: 06/03/2026_

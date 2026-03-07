# Kiến trúc hệ thống InSight

> Tài liệu chi tiết về kiến trúc kỹ thuật của hệ thống ước lượng Glycemic Load

---

## Mục lục

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Sơ đồ thành phần hệ thống](#2-sơ-đồ-thành-phần-hệ-thống)
3. [Luồng xử lý](#3-luồng-xử-lý)
4. [Luồng dữ liệu](#4-luồng-dữ-liệu)
5. [Kiến trúc từng layer](#5-kiến-trúc-từng-layer)
6. [Công nghệ và lý do lựa chọn](#6-công-nghệ-và-lý-do-lựa-chọn)

---

## 1. Tổng quan kiến trúc

### 1.1 Phong cách kiến trúc

Hệ thống InSight được xây dựng theo kiến trúc **Hybrid Edge-Cloud Event-Driven** kết hợp **Clean Architecture**:

- **Edge Computing:** Xử lý sơ bộ trên thiết bị mobile (YOLO detection, image preprocessing)
- **Cloud Processing:** Xử lý nặng trên server (Depth estimation, RAG Agent)
- **Event-Driven:** Giao tiếp giữa services qua Kafka events
- **Clean Architecture:** Tách biệt rõ ràng giữa các layer (Presentation, Domain, Data)

### 1.2 Nguyên tắc thiết kế

- **Separation of Concerns:** Mỗi service làm một việc
- **Loose Coupling:** Services giao tiếp qua message queue
- **Fail-Safe:** Có fallback cho mọi tình huống (Panic Mode)
- **User-Centric:** Ưu tiên tốc độ và UX hơn độ chính xác tuyệt đối

---

## 2. Sơ đồ thành phần hệ thống

### 2.1 High-Level Architecture (Tổng quan dễ hiểu)

Mô hình hoạt động như một **Bệnh viện thu nhỏ**:

- **Mobile (Y tá):** Xử lý sơ cứu, lọc nhiễu, phản ứng nhanh.
- **Cloud (Bác sĩ):** Xử lý chuyên sâu, chẩn đoán hình ảnh 3D và kê đơn thuốc.

```mermaid
graph LR
    subgraph "TIỀN TUYẾN (Mobile App)"
        User((Người dùng)) -->|Chụp ảnh| Mobile[App InSight]
        Mobile -->|1. Sàng lọc & Cắt vật thể| EdgeAI[AI Sơ bộ (YOLO Int8)]
        Mobile -.->|⚠️ Mất mạng/Khẩn cấp| Panic[Panic Mode (Offline)]
    end

    EdgeAI ==>|2. Vận chuyển tốc độ cao (gRPC)| Gateway[API Gateway]

    subgraph "HẬU PHƯƠNG (Cloud Server)"
        Gateway -->|3. Hàng đợi xử lý| Queue[Kafka Queue]
        Queue --> Vision[AI Thị giác 3D<br/>(Depth Anything)]
        Vision -->|Thể tích| Logic[Tính toán Dinh dưỡng]
        Logic <-->|4. Hội chẩn| RAG[Bác sĩ AI (RAG Agent)]
    end

    Panic -.->|Ước lượng nhanh| User
    Logic ==>|Chính xác cá nhân hóa| User
```

### 2.2 Component Diagram (Chi tiết)

```mermaid
graph TD
    subgraph "Mobile Layer"
        UI[Flutter UI<br/>• Camera Screen<br/>• Result Screen<br/>• Panic Mode]
        EdgeProcessor[Edge Processor<br/>• YOLO Detection<br/>• Image Crop<br/>• Cutlery Detection]
        LocalDB[SQLite<br/>• Food Templates<br/>• User History<br/>• Quán Quen Config]
    end

    subgraph "Gateway Layer"
        APIGateway[API Gateway<br/>• Rate Limiting<br/>• Auth Validation<br/>• Request Routing]
        LoadBalancer[Load Balancer<br/>• Health Check<br/>• Circuit Breaker]
    end

    subgraph "Vision Layer"
        DepthEstimator[Depth Estimator<br/>• Depth Anything V2<br/>• TorchServe]
        VolumeCalculator[Volume Calculator<br/>• Integral Computation<br/>• Density Factor]
        CutleryDetector[Cutlery Detector<br/>• Reference Object<br/>• Scale Calibration]
    end

    subgraph "Logic Layer"
        GLCalculator[GL Calculator<br/>• Volume → Weight<br/>• Weight → Carb<br/>• Carb → GL]
        InsulinAdvisor[Insulin Advisor<br/>• RAG Retrieval<br/>• Context Injection<br/>• Response Generation]
        UserContext[User Context<br/>• Glucose Level<br/>• Medication<br/>• History]
    end

    subgraph "Data Layer"
        FoodDB[(Food Database<br/>• Density Factors<br/>• Carb per 100g)]
        MedicalKB[(Medical KB<br/>• ADA Guidelines<br/>• MOH Guidelines)]
        UserDB[(User Database<br/>• Profiles<br/>• History<br/>• CGM Data)]
    end

    UI --> EdgeProcessor
    EdgeProcessor --> LocalDB
    UI --> APIGateway
    APIGateway --> LoadBalancer
    LoadBalancer --> DepthEstimator
    LoadBalancer --> GLCalculator
    DepthEstimator --> VolumeCalculator
    VolumeCalculator --> CutleryDetector
    CutleryDetector --> GLCalculator
    GLCalculator --> InsulinAdvisor
    InsulinAdvisor --> UserContext
    InsulinAdvisor --> MedicalKB
    GLCalculator --> FoodDB
    UserContext --> UserDB
```

---

## 3. Luồng xử lý

### 3.1 Luồng chuẩn (Standard Mode)

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant App as 📱 Flutter App
    participant Edge as 🔧 Edge AI
    participant Gateway as ☕ API Gateway
    participant Vision as 🐍 Vision Engine
    participant Logic as ☕ Logic Service
    participant RAG as 🤖 RAG Agent
    participant DB as 🗄️ Database

    User->>App: Chụp ảnh món ăn
    App->>Edge: Xử lý sơ bộ

    Edge->>Edge: YOLO Detection (Food + Cutlery)
    Edge->>Edge: Crop image theo bounding box
    Edge->>Edge: Detect vật tham chiếu (bát/thìa)

    alt Phát hiện món nước (Phở, Bún)
        Edge->>App: Cần thêm thông tin
        App->>User: Form: "Đây là Phở hay Bún?"
        User->>App: Chọn loại món
    end

    App->>Gateway: Upload (ảnh + loại món + reference)
    Gateway->>Gateway: Validate + Auth
    Gateway->>Vision: Request Volume Estimation

    activate Vision
    Vision->>Vision: Depth Anything V2 Inference
    Vision->>Vision: Generate Depth Map
    Vision->>Vision: Apply Calibration (reference object)
    Vision->>Vision: Calculate Volume (∫∫ depth dA)
    Vision->>Vision: Apply Density Factor
    Vision-->>Gateway: Volume (ml) + Confidence
    deactivate Vision

    Gateway->>Logic: Calculate GL
    activate Logic
    Logic->>DB: Get Food Density & Carb/100g
    DB-->>Logic: Food Data
    Logic->>Logic: Volume → Weight (ρ)
    Logic->>Logic: Weight → Carbs
    Logic->>Logic: Carbs → GL

    Logic->>RAG: Request Insulin Advice
    activate RAG
    RAG->>DB: Get User Context (Glucose, Meds)
    RAG->>RAG: Retrieve Medical Guidelines
    RAG->>RAG: Generate Actionable Response
    RAG-->>Logic: "60g Carb → Tiêm thêm 1 Unit"
    deactivate RAG

    Logic-->>Gateway: GL + Recommendation + Disclaimer
    deactivate Logic

    Gateway-->>App: Response
    App->>User: Hiển thị kết quả (<5 giây)
```

### 3.2 Luồng nhanh (Panic Mode)

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant App as 📱 Flutter App
    participant Cache as 💾 Local Cache

    User->>App: Bấm "Ước lượng nhanh"
    App->>User: Hiện thư viện ảnh món ăn

    Note over App: Thư viện: Cơm, Phở, Bún,<br/>Bánh mì, Xôi, Cháo...

    User->>App: Chọn ảnh giống nhất

    alt Có quán quen đã calibrate
        App->>Cache: Lookup quán quen
        Cache-->>App: Density Factor riêng
    else Dùng giá trị mặc định
        App->>Cache: Lookup giá trị trung bình
        Cache-->>App: Carb trung bình
    end

    App->>App: Tính GL từ cache
    App->>User: Hiển thị kết quả (<1 giây)

    Note over User,App: ⚠️ Kèm badge "Ước lượng"
```

### 3.3 Luồng đồ uống (có Carb ẩn)

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant App as 📱 Flutter App
    participant Edge as 🔧 Edge AI
    participant Gateway as ☕ API Gateway

    User->>App: Chụp ảnh đồ uống
    App->>Edge: Detect object
    Edge->>Edge: Nhận diện: "Trà sữa"
    Edge->>App: Loại = Đồ uống

    App->>User: Form 1: "Size: S/M/L/XL?"
    User->>App: Chọn "L"

    App->>User: Form 2: "Độ ngọt?"
    User->>App: Chọn "100%"

    App->>User: Form 3: "Có trân châu?"
    User->>App: Chọn "Có"

    App->>Gateway: Upload + Metadata

    Note over Gateway: Carb = Base(L, 100%) + Topping
    Note over Gateway: = 50g + 20g = 70g Carb

    Gateway-->>App: 70g Carb, GL = 35
    App->>User: Hiển thị kết quả
```

---

## 4. Luồng dữ liệu

### 4.1 Data Flow Overview

```mermaid
flowchart TB
    subgraph Input
        Camera[📷 Camera]
        CGM[📊 CGM Device]
        Manual[✍️ Manual Input]
    end

    subgraph Processing
        EdgeAI[🔧 Edge AI]
        VisionEngine[🐍 Vision Engine]
        GLCalc[📐 GL Calculator]
        RAGAgent[🤖 RAG Agent]
    end

    subgraph Storage
        UserDB[(👤 User DB)]
        FoodDB[(🍜 Food DB)]
        MedicalKB[(📚 Medical KB)]
        Cache[(⚡ Cache)]
    end

    subgraph Output
        Result[📊 GL Result]
        Advice[💊 Insulin Advice]
        History[📈 History Log]
    end

    Camera --> EdgeAI
    CGM --> UserDB
    Manual --> UserDB

    EdgeAI --> VisionEngine
    VisionEngine --> GLCalc
    GLCalc --> FoodDB
    GLCalc --> RAGAgent
    RAGAgent --> MedicalKB
    RAGAgent --> UserDB

    GLCalc --> Result
    RAGAgent --> Advice
    Result --> Cache
    Advice --> History
    History --> UserDB
```

### 4.2 Data Flow Chi tiết (C4 Level 2)

```mermaid
flowchart LR
    subgraph External
        U[👤 Bệnh nhân]
        D[👨‍⚕️ Bác sĩ]
        CGM[📊 CGM Device]
    end

    subgraph "InSight System"
        subgraph Mobile
            MA[📱 Flutter App]
            LC[💾 Local Cache]
        end

        subgraph Backend
            API[API Gateway]
            VS[Vision Service]
            LS[Logic Service]
            RAG[RAG Service]
        end

        subgraph Data
            DB[(PostgreSQL)]
            VDB[(Milvus)]
            Cache[(Redis)]
        end
    end

    U -->|Ảnh| MA
    CGM -->|Glucose| MA
    MA <-->|Sync| LC
    MA -->|gRPC| API
    API -->|Image| VS
    VS -->|Volume| API
    API -->|Calculate| LS
    LS -->|Query| RAG
    RAG -->|Retrieve| VDB
    LS -->|CRUD| DB
    API -->|Cache| Cache
    RAG -->|Advice| API
    API -->|Result| MA
    MA -->|Display| U

    D -->|Monitor| API
    API -->|Analytics| D
```

---

## 5. Kiến trúc từng layer

### 5.1 Mobile Layer (Flutter)

```
lib/
├── core/
│   ├── constants/
│   ├── utils/
│   └── di/                 # Dependency Injection
├── data/
│   ├── models/             # Data models
│   ├── repositories/       # Repository implementations
│   └── datasources/
│       ├── local/          # SQLite, SharedPrefs
│       └── remote/         # gRPC client
├── domain/
│   ├── entities/           # Business entities
│   ├── repositories/       # Repository interfaces
│   └── usecases/           # Business logic
├── presentation/
│   ├── screens/
│   │   ├── camera/         # Chụp ảnh
│   │   ├── result/         # Hiển thị kết quả
│   │   ├── panic/          # Panic Mode
│   │   └── settings/       # Cài đặt, quán quen
│   ├── widgets/
│   └── bloc/               # State management
└── edge/
    ├── yolo/               # YOLO detection
    ├── onnx/               # ONNX runtime
    └── preprocessing/      # Image preprocessing
```

### 5.2 Backend Layer (Java + Python)

```
backend/
├── api-gateway/                    # Spring Boot Gateway
│   ├── src/main/java/
│   │   ├── config/
│   │   ├── controller/
│   │   ├── filter/                 # Auth, Rate limiting
│   │   └── grpc/                   # gRPC endpoints
│   └── src/main/proto/             # Protobuf definitions
│
├── vision-service/                 # Python Vision Engine
│   ├── models/
│   │   ├── depth_anything/         # Depth estimation
│   │   └── cutlery_detector/       # Reference detection
│   ├── services/
│   │   ├── depth_service.py
│   │   ├── volume_service.py
│   │   └── calibration_service.py
│   └── api/
│       └── grpc_server.py
│
├── logic-service/                  # Java Logic Service
│   ├── src/main/java/
│   │   ├── domain/
│   │   │   ├── entity/
│   │   │   ├── repository/
│   │   │   └── service/
│   │   ├── application/
│   │   │   ├── usecase/
│   │   │   └── dto/
│   │   └── infrastructure/
│   │       ├── persistence/
│   │       ├── messaging/          # Kafka
│   │       └── external/           # CGM API
│   └── src/main/resources/
│
└── rag-service/                    # RAG Agent
    ├── src/main/java/
    │   ├── langchain/              # LangChain4j integration
    │   ├── retrieval/              # Vector search
    │   ├── generation/             # Response generation
    │   └── prompts/                # Prompt templates
    └── knowledge/
        └── medical/                # ADA/MOH guidelines
        
```

### 5.3 Data Layer

![alt text](<User Meal Logging Ecosystem-2026-03-07-005230.png>)

```mermaid
erDiagram
    USER ||--o{ MEAL_LOG : logs
    USER ||--o{ GLUCOSE_READING : has
    USER ||--o{ FAVORITE_RESTAURANT : saves

    MEAL_LOG ||--|{ MEAL_ITEM : contains
    MEAL_ITEM }|--|| FOOD : references

    FOOD ||--o{ DENSITY_FACTOR : has

    USER {
        uuid id PK
        string email
        string name
        json medication
        json insulin_settings
        datetime created_at
    }

    MEAL_LOG {
        uuid id PK
        uuid user_id FK
        datetime logged_at
        float total_carbs
        float total_gl
        string insulin_suggestion
        boolean disclaimer_shown
    }

    MEAL_ITEM {
        uuid id PK
        uuid meal_log_id FK
        uuid food_id FK
        float volume_ml
        float weight_g
        float carbs_g
        float confidence_score
    }

    FOOD {
        uuid id PK
        string name_vi
        string name_en
        float carb_per_100g
        float gi_index
        string category
    }

    DENSITY_FACTOR {
        uuid id PK
        uuid food_id FK
        string variant
        float solid_ratio
        float density
    }

    GLUCOSE_READING {
        uuid id PK
        uuid user_id FK
        float value_mgdl
        datetime measured_at
        string source
    }

    FAVORITE_RESTAURANT {
        uuid id PK
        uuid user_id FK
        string name
        json custom_density_factors
    }
```

---

## 6. Công nghệ và lý do lựa chọn

### 6.1 Mobile

| Công nghệ    | Phiên bản | Lý do lựa chọn                               |
| ------------ | --------- | -------------------------------------------- |
| Flutter      | 3.x       | Cross-platform, 60fps, hot reload            |
| ONNX Runtime | 1.17      | Chạy model AI trên mobile, Int8 quantization |
| gRPC         | -         | Nhanh hơn REST 7-10x, strongly typed         |
| SQLite       | -         | Offline storage, Panic Mode cache            |

### 6.2 Backend

| Công nghệ         | Phiên bản | Lý do lựa chọn                          |
| ----------------- | --------- | --------------------------------------- |
| Java 21           | LTS       | Virtual Threads, GraalVM ready          |
| Spring Boot       | 3.3       | Production-ready, ecosystem phong phú   |
| Python            | 3.11+     | AI/ML ecosystem, PyTorch support        |
| Depth Anything V2 | Latest    | SOTA monocular depth estimation         |
| LangChain4j       | 0.28+     | Native Java AI, không cần Python bridge |

### 6.3 Data & Infrastructure

| Công nghệ      | Phiên bản | Lý do lựa chọn                |
| -------------- | --------- | ----------------------------- |
| PostgreSQL     | 16        | ACID, JSON support, mature    |
| Milvus         | 2.3       | Vector search, HNSW index     |
| Redis          | 7         | In-memory cache, pub/sub      |
| Apache Kafka   | -         | Event-driven, high throughput |
| Docker Compose | -         | Dev environment consistency   |

### 6.4 Observability

| Công nghệ              | Mục đích            |
| ---------------------- | ------------------- |
| Prometheus + Grafana   | Metrics, dashboard  |
| Loki + Promtail        | Centralized logging |
| OpenTelemetry + Jaeger | Distributed tracing |

### 6.5 Security

| Công nghệ         | Mục đích                      |
| ----------------- | ----------------------------- |
| Keycloak          | OAuth2/OIDC, SSO              |
| Spring Security 6 | JWT validation, rate limiting |
| TLS 1.3           | Transport encryption          |
| AES-256           | Data at rest encryption       |

---

## Tài liệu tham khảo

- [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)
- [LangChain4j](https://github.com/langchain4j/langchain4j)
- [Milvus Documentation](https://milvus.io/docs)
- [Spring Boot 3.3 Reference](https://docs.spring.io/spring-boot/docs/3.3.x/reference/html/)

---

_Cập nhật lần cuối: 28-01-2026_

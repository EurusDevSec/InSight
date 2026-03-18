# Hướng dẫn thực hiện Giai đoạn 1: Nền tảng và Dữ liệu

> **Thời gian:** Tuần 1-3 (3 tuần)  
> **Mục tiêu:** Setup xong hạ tầng, team đồng bộ, có dữ liệu để bắt đầu train model

---

## Mục lục

- [Sprint 0: Khởi động](#sprint-0-khởi-động-tuần-1)
- [Sprint 1: Hạ tầng](#sprint-1-hạ-tầng-tuần-2)
- [Sprint 2: Thu thập dữ liệu](#sprint-2-thu-thập-dữ-liệu-tuần-3)
- [Checklist hoàn thành Giai đoạn 1](#checklist-hoàn-thành-giai-đoạn-1)

---

## Sprint 0: Khởi động (Tuần 1)

### Mục tiêu

- Team hiểu rõ dự án và kiến trúc
- Có Git repo chuẩn chỉnh
- Có tài liệu kiến trúc cơ bản

### Phân công

| Task                               | Người thực hiện | Deadline |
| ---------------------------------- | --------------- | -------- |
| Viết Architecture Decision Records | Tôi             | Ngày 2   |
| Setup Git repo + branch protection | HI              | Ngày 1   |
| Viết README.md                     | HI              | Ngày 2   |
| Review & họp đồng bộ               | Team            | Ngày 3   |

---

### Task 1: Setup Git Repository

**Người thực hiện:** HI

#### Bước 1: Tạo repo trên GitHub

1. Vào GitHub → New Repository
2. Đặt tên: `insight-app`
3. Chọn: Private (hoặc Public nếu muốn)
4. **Không** tick "Add README" (sẽ tạo sau)

#### Bước 2: Clone và setup cấu trúc thư mục

```bash
git clone https://github.com/<your-team>/insight-app.git
cd insight-app
```

Tạo cấu trúc thư mục:

```bash
mkdir -p backend/api-gateway
mkdir -p backend/vision-service
mkdir -p backend/logic-service
mkdir -p backend/rag-service
mkdir -p mobile/insight_app
mkdir -p docs/adr
mkdir -p data/raw
mkdir -p data/processed
mkdir -p scripts
mkdir -p infra/docker
mkdir -p infra/k8s
```

Cấu trúc sẽ như sau:

```
insight-app/
├── backend/
│   ├── api-gateway/        # Java Spring Boot
│   ├── vision-service/     # Python
│   ├── logic-service/      # Java
│   └── rag-service/        # Python RAG (Gemini + Milvus)
├── mobile/
│   └── insight_app/        # Flutter
├── docs/
│   ├── adr/                # Architecture Decision Records
│   ├── plan.md
│   └── architecture.md
├── data/
│   ├── raw/                # Ảnh gốc chưa xử lý
│   └── processed/          # Ảnh đã annotate
├── scripts/                # Scripts tiện ích
├── infra/
│   ├── docker/             # Docker compose files
│   └── k8s/                # Kubernetes configs (nếu cần)
├── .gitignore
├── README.md
└── docker-compose.yml
```

#### Bước 3: Tạo file .gitignore

```bash
touch .gitignore
```

Nội dung `.gitignore`:

```gitignore
# IDE
.idea/
.vscode/
*.iml

# Python
__pycache__/
*.py[cod]
.env
venv/
.venv/

# Java
target/
*.class
*.jar
*.log

# Flutter
mobile/insight_app/build/
mobile/insight_app/.dart_tool/
mobile/insight_app/.packages

# Data (không push ảnh lên Git)
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Docker
*.log

# OS
.DS_Store
Thumbs.db

# Secrets
*.env
secrets/
```

Tạo file giữ chỗ cho thư mục data:

```bash
touch data/raw/.gitkeep
touch data/processed/.gitkeep
```

#### Bước 4: Setup Branch Protection

1. Vào GitHub repo → Settings → Branches
2. Add rule cho branch `main`:
   - ✅ Require pull request before merging
   - ✅ Require approvals: 1
   - ✅ Dismiss stale pull request approvals
3. Add rule cho branch `develop`:
   - ✅ Require pull request before merging

#### Bước 5: Tạo branch develop

```bash
git checkout -b develop
git push -u origin develop
```

#### Bước 6: Commit đầu tiên

```bash
git add .
git commit -m "chore: initial project structure"
git push origin develop
```

---

### Task 2: Viết README.md

**Người thực hiện:** HI

Tạo file `README.md` ở root:

```markdown
# InSight - Insulin Insight

> Hệ thống ước lượng Glycemic Load thời gian thực cho bệnh nhân tiểu đường

## Giới thiệu

InSight giúp bệnh nhân tiểu đường ước lượng lượng Carbohydrate và Glycemic Load của món ăn thông qua camera điện thoại, từ đó tính toán liều Insulin cần tiêm.

## Công nghệ

- **Mobile:** Flutter + ONNX Runtime
- **Backend:** Java 21 + Spring Boot 3.3
- **Vision:** Python + Depth Anything V2
- **AI:** Python RAG + Gemini API + Milvus
- **Database:** PostgreSQL, Redis
- **Message Queue:** Apache Kafka

## Cấu trúc dự án
```

insight-app/
├── backend/ # Microservices
├── mobile/ # Flutter app
├── docs/ # Tài liệu
├── data/ # Dataset
├── scripts/ # Scripts tiện ích
└── infra/ # Docker, K8s configs

````

## Quickstart

### Yêu cầu

- Docker & Docker Compose
- Java 21
- Python 3.11+
- Flutter 3.x

### Chạy local

```bash
# Start infrastructure
docker compose up -d

# Check services
docker compose ps
````

## Team

- **Tôi** - Tech Lead / AI Lead
- **V** - Backend Lead / Vision Engineer
- **HI** - Frontend / Documentation

## License

Private - Đồ án tốt nghiệp

````

---

### Task 3: Viết Architecture Decision Records (ADR)

**Người thực hiện:** Tôi

ADR là tài liệu ghi lại **tại sao** chúng ta chọn công nghệ này thay vì công nghệ khác. Rất quan trọng khi bảo vệ đồ án.

#### ADR 001: Chọn gRPC thay vì REST

Tạo file `docs/adr/001-grpc-over-rest.md`:

```markdown
# ADR 001: Sử dụng gRPC thay vì REST API

## Ngày quyết định
2026-01-27

## Trạng thái
Đã chấp nhận

## Bối cảnh
Hệ thống cần giao tiếp giữa Mobile App và Backend với yêu cầu:
- Độ trễ thấp (< 2 giây cho toàn bộ pipeline)
- Truyền dữ liệu binary (ảnh) hiệu quả
- Type-safe giữa các service

## Quyết định
Sử dụng **gRPC với Protocol Buffers** cho giao tiếp Mobile ↔ Gateway và giữa các Microservices.

## Lý do
| Tiêu chí | REST/JSON | gRPC/Protobuf |
|----------|-----------|---------------|
| Kích thước payload | Lớn (text) | Nhỏ hơn 30-50% (binary) |
| Tốc độ serialize | Chậm | Nhanh hơn 5-10x |
| Type-safety | Không (runtime) | Có (compile-time) |
| Streaming | Khó | Native support |
| Code generation | Manual | Tự động từ .proto |

## Hệ quả
- Cần học Protocol Buffers
- Cần setup code generation trong CI/CD
- Debug khó hơn (không đọc được raw request như JSON)

## Tham khảo
- https://grpc.io/docs/what-is-grpc/
````

#### ADR 002: Chọn Kafka thay vì RabbitMQ

Tạo file `docs/adr/002-kafka-over-rabbitmq.md`:

```markdown
# ADR 002: Sử dụng Apache Kafka thay vì RabbitMQ

## Ngày quyết định

2026-01-27

## Trạng thái

Đã chấp nhận

## Bối cảnh

Cần message queue để:

- Giảm coupling giữa API Gateway và Vision Service
- Đảm bảo không mất request khi Vision Service quá tải
- Hỗ trợ replay message nếu cần debug

## Quyết định

Sử dụng **Apache Kafka** làm message broker.

## Lý do

| Tiêu chí          | RabbitMQ            | Kafka                   |
| ----------------- | ------------------- | ----------------------- |
| Throughput        | 20K msg/s           | 100K+ msg/s             |
| Message retention | Xóa sau khi consume | Lưu lại (configurable)  |
| Replay messages   | Không               | Có                      |
| Ordering          | Không đảm bảo       | Đảm bảo trong partition |
| Learning curve    | Dễ                  | Trung bình              |

Kafka phù hợp hơn vì:

1. **Retention:** Có thể xem lại message cũ để debug
2. **Scalability:** Dễ scale khi có nhiều người dùng
3. **Event Sourcing:** Phù hợp với kiến trúc event-driven

## Hệ quả

- Cần Zookeeper hoặc KRaft (Kafka 3.x+)
- Tốn RAM hơn RabbitMQ
- Cấu hình phức tạp hơn

## Tham khảo

- https://kafka.apache.org/documentation/
```

#### ADR 003: Chọn Depth Anything V2

Tạo file `docs/adr/003-depth-anything-v2.md`:

```markdown
# ADR 003: Sử dụng Depth Anything V2 cho ước lượng độ sâu

## Ngày quyết định

2026-01-27

## Trạng thái

Đã chấp nhận

## Bối cảnh

Cần model AI để ước lượng độ sâu (depth) từ một bức ảnh 2D duy nhất (monocular depth estimation) để tính thể tích món ăn.

## Các lựa chọn đã xem xét

1. **MiDaS** - Intel
2. **Depth Anything V1** - TikTok
3. **Depth Anything V2** - TikTok (2024)
4. **ZoeDepth** - Intel

## Quyết định

Sử dụng **Depth Anything V2** phiên bản Large.

## Lý do

| Model                 | Độ chính xác (RMSE↓) | Tốc độ     | Model size |
| --------------------- | -------------------- | ---------- | ---------- |
| MiDaS                 | 0.357                | Nhanh      | 100MB      |
| Depth Anything V1     | 0.298                | Trung bình | 335MB      |
| **Depth Anything V2** | **0.261**            | Trung bình | 335MB      |
| ZoeDepth              | 0.270                | Chậm       | 400MB      |

Depth Anything V2 có:

1. **SOTA accuracy** trên các benchmark (NYU Depth, KITTI)
2. **Zero-shot generalization** tốt - không cần fine-tune cho món ăn VN
3. **Pretrained weights** sẵn có
4. **Cộng đồng active** - dễ tìm support

## Hệ quả

- Cần GPU để inference (hoặc chấp nhận chậm trên CPU)
- Model nặng, cần optimize nếu muốn chạy trên mobile

## Tham khảo

- https://github.com/DepthAnything/Depth-Anything-V2
- Paper: "Depth Anything V2" (2024)
```

---

### Task 4: Họp đồng bộ Team

**Người thực hiện:** Cả team

#### Agenda cuộc họp (30-45 phút)

1. **Demo Git repo** (HI - 5 phút)
   - Show cấu trúc thư mục
   - Giải thích branching strategy

2. **Giải thích kiến trúc** (Tôi - 15 phút)
   - Dùng sơ đồ "Bệnh viện thu nhỏ" để giải thích
   - Trả lời câu hỏi của V và HI

3. **Review ADRs** (Tôi - 10 phút)
   - Đọc qua 3 ADR
   - V và HI confirm hiểu tại sao chọn công nghệ đó

4. **Phân công Sprint 1** (Tôi - 10 phút)
   - Giao task cụ thể cho V
   - Confirm deadline

#### Kết quả mong đợi

- [ ] Cả team hiểu luồng hoạt động của hệ thống
- [ ] V hiểu rõ task của mình ở Sprint 1
- [ ] HI biết cần chuẩn bị gì cho Sprint 2

---

## Sprint 1: Hạ tầng (Tuần 2)

### Mục tiêu

- PostgreSQL + Milvus + Redis + Kafka chạy được
- CI/CD pipeline cơ bản (build + test)
- `docker compose up` là xong

### Phân công

| Task                    | Người thực hiện | Deadline |
| ----------------------- | --------------- | -------- |
| Viết docker-compose.yml | V               | Ngày 2   |
| Setup PostgreSQL schema | V               | Ngày 3   |
| Setup Milvus collection | V               | Ngày 4   |
| Setup GitHub Actions CI | V               | Ngày 5   |
| Review & test           | Tôi             | Ngày 5   |

---

### Task 1: Viết docker-compose.yml

**Người thực hiện:** V

Tạo file `docker-compose.yml` ở root:

```yaml
version: "3.8"

services:
  # === DATABASE ===
  postgres:
    image: postgres:16-alpine
    container_name: insight-postgres
    environment:
      POSTGRES_USER: insight
      POSTGRES_PASSWORD: insight123
      POSTGRES_DB: insight_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U insight"]
      interval: 10s
      timeout: 5s
      retries: 5

  # === CACHE ===
  redis:
    image: redis:7-alpine
    container_name: insight-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # === MESSAGE QUEUE ===
  kafka:
    image: bitnami/kafka:3.6
    container_name: insight-kafka
    environment:
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
    ports:
      - "9092:9092"
    volumes:
      - kafka_data:/bitnami/kafka
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "kafka-topics.sh --bootstrap-server localhost:9092 --list",
        ]
      interval: 30s
      timeout: 10s
      retries: 5

  # === VECTOR DATABASE ===
  milvus-etcd:
    image: quay.io/coreos/etcd:v3.5.5
    container_name: insight-milvus-etcd
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    volumes:
      - milvus_etcd:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd

  milvus-minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    container_name: insight-milvus-minio
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - milvus_minio:/minio_data
    command: minio server /minio_data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  milvus:
    image: milvusdb/milvus:v2.3.3
    container_name: insight-milvus
    environment:
      ETCD_ENDPOINTS: milvus-etcd:2379
      MINIO_ADDRESS: milvus-minio:9000
    ports:
      - "19530:19530"
      - "9091:9091"
    volumes:
      - milvus_data:/var/lib/milvus
    depends_on:
      - milvus-etcd
      - milvus-minio
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
      interval: 30s
      timeout: 20s
      retries: 3

  # === MONITORING (Optional - bật sau nếu cần) ===
  # prometheus:
  #   image: prom/prometheus:v2.47.0
  #   container_name: insight-prometheus
  #   ports:
  #     - "9090:9090"
  #   volumes:
  #     - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  postgres_data:
  redis_data:
  kafka_data:
  milvus_etcd:
  milvus_minio:
  milvus_data:
```

#### Chạy thử

```bash
# Start tất cả services
docker compose up -d

# Kiểm tra status
docker compose ps

# Xem logs nếu có lỗi
docker compose logs -f postgres
docker compose logs -f milvus
```

#### Kết quả mong đợi

```
NAME                    STATUS    PORTS
insight-postgres        running   0.0.0.0:5432->5432/tcp
insight-redis           running   0.0.0.0:6379->6379/tcp
insight-kafka           running   0.0.0.0:9092->9092/tcp
insight-milvus          running   0.0.0.0:19530->19530/tcp
insight-milvus-etcd     running
insight-milvus-minio    running
```

---

### Task 2: Setup PostgreSQL Schema

**Người thực hiện:** V

Tạo file `scripts/init-db.sql`:

```sql
-- =============================================
-- InSight Database Schema
-- Version: 1.0.0
-- =============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- USERS TABLE
-- =============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,

    -- Thông tin y tế
    diabetes_type VARCHAR(20), -- 'type1', 'type2'
    insulin_type VARCHAR(50),  -- 'rapid', 'long-acting', 'mixed'
    insulin_ratio DECIMAL(5,2), -- Units per 10g Carb
    target_glucose_min INT DEFAULT 80,
    target_glucose_max INT DEFAULT 140,

    -- CGM Integration
    cgm_provider VARCHAR(50), -- 'freestyle_libre', 'dexcom', null
    cgm_access_token TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- FOODS TABLE (Cơ sở dữ liệu món ăn)
-- =============================================
CREATE TABLE foods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_vi VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),

    -- Dinh dưỡng (per 100g)
    carb_per_100g DECIMAL(6,2) NOT NULL,
    protein_per_100g DECIMAL(6,2),
    fat_per_100g DECIMAL(6,2),
    fiber_per_100g DECIMAL(6,2),

    -- Glycemic Index
    gi_value INT, -- 0-100
    gi_category VARCHAR(10), -- 'low', 'medium', 'high'

    -- Phân loại
    category VARCHAR(50), -- 'rice', 'noodle', 'bread', 'drink', etc.
    is_liquid BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- DENSITY FACTORS (Hệ số mật độ cho món nước)
-- =============================================
CREATE TABLE density_factors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    food_id UUID REFERENCES foods(id),

    variant VARCHAR(50), -- 'default', 'ít bánh', 'nhiều bánh'
    solid_ratio DECIMAL(4,2), -- 0.30 = 30% đặc, 70% nước
    density DECIMAL(4,2) DEFAULT 1.0, -- g/ml

    -- Cho calibrate quán quen
    restaurant_name VARCHAR(100),
    user_id UUID REFERENCES users(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- MEAL LOGS (Lịch sử ăn uống)
-- =============================================
CREATE TABLE meal_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),

    -- Thời gian
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meal_type VARCHAR(20), -- 'breakfast', 'lunch', 'dinner', 'snack'

    -- Ảnh
    image_url TEXT,

    -- Kết quả
    total_volume_ml DECIMAL(8,2),
    total_weight_g DECIMAL(8,2),
    total_carbs_g DECIMAL(8,2),
    total_gl DECIMAL(8,2),

    -- AI Response
    insulin_suggestion DECIMAL(5,2),
    confidence_score DECIMAL(4,2),
    rag_response TEXT,

    -- Tracking
    is_panic_mode BOOLEAN DEFAULT FALSE,
    disclaimer_shown BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- MEAL ITEMS (Chi tiết từng món trong bữa)
-- =============================================
CREATE TABLE meal_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meal_log_id UUID REFERENCES meal_logs(id),
    food_id UUID REFERENCES foods(id),

    -- Kết quả tính toán
    volume_ml DECIMAL(8,2),
    weight_g DECIMAL(8,2),
    carbs_g DECIMAL(8,2),

    -- Thông tin bổ sung từ form
    portion_size VARCHAR(20), -- 'full', 'half', 'quarter'
    sweetness_level VARCHAR(20), -- 'full', 'less', 'none'
    sauce_amount VARCHAR(20), -- 'none', 'little', 'normal', 'extra'

    confidence_score DECIMAL(4,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- GLUCOSE READINGS (Đọc đường huyết từ CGM)
-- =============================================
CREATE TABLE glucose_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),

    value_mgdl INT NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    source VARCHAR(20), -- 'cgm', 'manual'

    -- Liên kết với bữa ăn (nếu có)
    meal_log_id UUID REFERENCES meal_logs(id),
    reading_type VARCHAR(20), -- 'before_meal', 'after_meal_1h', 'after_meal_2h'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- FAVORITE RESTAURANTS (Quán quen)
-- =============================================
CREATE TABLE favorite_restaurants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),

    name VARCHAR(100) NOT NULL,
    address TEXT,

    -- Custom density factors sẽ lưu trong bảng density_factors
    -- với restaurant_name và user_id

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES
-- =============================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_foods_category ON foods(category);
CREATE INDEX idx_foods_name_vi ON foods(name_vi);
CREATE INDEX idx_meal_logs_user ON meal_logs(user_id, logged_at DESC);
CREATE INDEX idx_glucose_user ON glucose_readings(user_id, measured_at DESC);
CREATE INDEX idx_density_food ON density_factors(food_id);
CREATE INDEX idx_density_restaurant ON density_factors(restaurant_name, user_id);

-- =============================================
-- SEED DATA: Một số món ăn cơ bản
-- =============================================
INSERT INTO foods (name_vi, name_en, carb_per_100g, gi_value, gi_category, category, is_liquid) VALUES
-- Cơm, xôi
('Cơm trắng', 'White Rice', 28.0, 73, 'high', 'rice', FALSE),
('Xôi', 'Sticky Rice', 30.0, 87, 'high', 'rice', FALSE),
('Cơm chiên', 'Fried Rice', 25.0, 65, 'medium', 'rice', FALSE),

-- Phở, Bún
('Phở bò', 'Beef Pho', 12.0, 55, 'low', 'noodle', TRUE),
('Phở gà', 'Chicken Pho', 11.0, 55, 'low', 'noodle', TRUE),
('Bún bò Huế', 'Hue Beef Noodle', 13.0, 58, 'medium', 'noodle', TRUE),
('Bún chả', 'Grilled Pork Noodle', 15.0, 50, 'low', 'noodle', FALSE),

-- Bánh mì
('Bánh mì thịt', 'Vietnamese Sandwich', 35.0, 75, 'high', 'bread', FALSE),
('Bánh mì trứng', 'Egg Sandwich', 32.0, 70, 'high', 'bread', FALSE),

-- Đồ uống
('Trà sữa trân châu (M)', 'Bubble Tea (M)', 45.0, 65, 'medium', 'drink', TRUE),
('Trà sữa trân châu (L)', 'Bubble Tea (L)', 45.0, 65, 'medium', 'drink', TRUE),
('Cà phê sữa đá', 'Vietnamese Iced Coffee', 25.0, 60, 'medium', 'drink', TRUE),
('Nước ngọt (lon)', 'Soft Drink (can)', 11.0, 63, 'medium', 'drink', TRUE);

-- =============================================
-- SEED DATA: Density Factors mặc định
-- =============================================
INSERT INTO density_factors (food_id, variant, solid_ratio, density)
SELECT id, 'default', 0.30, 1.05 FROM foods WHERE name_vi = 'Phở bò'
UNION ALL
SELECT id, 'ít bánh', 0.20, 1.03 FROM foods WHERE name_vi = 'Phở bò'
UNION ALL
SELECT id, 'nhiều bánh', 0.45, 1.08 FROM foods WHERE name_vi = 'Phở bò'
UNION ALL
SELECT id, 'default', 0.35, 1.05 FROM foods WHERE name_vi = 'Bún bò Huế'
UNION ALL
SELECT id, 'default', 1.0, 1.05 FROM foods WHERE name_vi = 'Trà sữa trân châu (M)'
UNION ALL
SELECT id, 'default', 1.0, 1.05 FROM foods WHERE name_vi = 'Trà sữa trân châu (L)';

-- Done!
SELECT 'Database initialized successfully!' as status;
```

#### Kiểm tra

```bash
# Kết nối vào PostgreSQL
docker exec -it insight-postgres psql -U insight -d insight_db

# Kiểm tra tables
\dt

# Kiểm tra data
SELECT * FROM foods;
SELECT * FROM density_factors;

# Thoát
\q
```

---

### Task 3: Setup Milvus Collection

**Người thực hiện:** V

Tạo file `scripts/init-milvus.py`:

```python
"""
Script khởi tạo Milvus collection cho InSight RAG
Chạy: python scripts/init-milvus.py
"""

from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)

# Kết nối Milvus
print("Connecting to Milvus...")
connections.connect("default", host="localhost", port="19530")

# Tên collection
COLLECTION_NAME = "medical_knowledge"

# Xóa collection cũ nếu có
if utility.has_collection(COLLECTION_NAME):
    print(f"Dropping existing collection: {COLLECTION_NAME}")
    utility.drop_collection(COLLECTION_NAME)

# Định nghĩa schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),  # 'ADA', 'MOH', etc.
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),  # 'insulin_dosing', 'emergency', etc.
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)  # all-MiniLM-L6-v2
]

schema = CollectionSchema(fields, description="Medical knowledge base for diabetes management")

# Tạo collection
print(f"Creating collection: {COLLECTION_NAME}")
collection = Collection(COLLECTION_NAME, schema)

# Tạo index cho vector search
print("Creating index...")
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 256}
}
collection.create_index("embedding", index_params)

# Load collection
collection.load()

print("✅ Milvus collection created successfully!")
print(f"   Collection: {COLLECTION_NAME}")
print(f"   Fields: {[f.name for f in fields]}")

# Disconnect
connections.disconnect("default")
```

#### Cài đặt và chạy

```bash
# Cài pymilvus
pip install pymilvus

# Chạy script
python scripts/init-milvus.py
```

---

### Task 4: Setup GitHub Actions CI

**Người thực hiện:** V

Tạo file `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # ===== BACKEND JAVA =====
  backend-java:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend/api-gateway

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: "21"
          distribution: "temurin"
          cache: maven

      - name: Build with Maven
        run: |
          if [ -f pom.xml ]; then
            mvn clean verify -DskipTests
          else
            echo "No pom.xml found, skipping Java build"
          fi

  # ===== BACKEND PYTHON =====
  backend-python:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend/vision-service

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
            pip install pytest
          else
            echo "No requirements.txt found, skipping Python setup"
          fi

      - name: Run tests
        run: |
          if [ -d tests ]; then
            pytest tests/
          else
            echo "No tests found, skipping"
          fi

  # ===== MOBILE FLUTTER =====
  mobile:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: mobile/insight_app

    steps:
      - uses: actions/checkout@v4

      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: "3.16.0"
          channel: "stable"

      - name: Check Flutter
        run: |
          if [ -f pubspec.yaml ]; then
            flutter pub get
            flutter analyze
          else
            echo "No pubspec.yaml found, skipping Flutter build"
          fi

  # ===== DOCKER COMPOSE =====
  docker:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Validate docker-compose
        run: docker compose config
```

---

### Task 5: Kiểm tra tổng thể

**Người thực hiện:** Tôi + V

#### Checklist Sprint 1

```bash
# 1. Start all services
docker compose up -d

# 2. Check all healthy
docker compose ps
# Tất cả phải là "running" hoặc "healthy"

# 3. Test PostgreSQL
docker exec -it insight-postgres psql -U insight -d insight_db -c "SELECT COUNT(*) FROM foods;"
# Expected: 13

# 4. Test Redis
docker exec -it insight-redis redis-cli ping
# Expected: PONG

# 5. Test Kafka
docker exec -it insight-kafka kafka-topics.sh --bootstrap-server localhost:9092 --list
# Expected: (empty hoặc có topic mặc định)

# 6. Test Milvus
python scripts/init-milvus.py
# Expected: ✅ Milvus collection created successfully!

# 7. Push code
git add .
git commit -m "feat(infra): add docker-compose and database schema"
git push origin develop

# 8. Check GitHub Actions
# Vào GitHub repo -> Actions -> Check CI pass
```

---

## 🧪 Sprint 1.5: POC với dữ liệu mẫu (Trước Sprint 2)

> **Thời gian:** 1-2 ngày
> **Mục tiêu:** Kiểm tra pipeline hoạt động với dữ liệu giả TRƯỚC khi đầu tư thời gian đi thu thập thực tế

### Tại sao cần bước này?

```
❌ Rủi ro nếu bỏ qua:
   Thu thập 25 mẫu (4 ngày) → Phát hiện script lỗi → Mất công

✅ Lợi ích của POC:
   Test với 5 mẫu giả (2 giờ) → Fix bug → Thu thập thật → Smooth
```

---

### Task 1: Tải ảnh mẫu từ Internet

**Mục tiêu:** Có 5 ảnh món ăn để test pipeline

#### Nguồn ảnh miễn phí (không vi phạm bản quyền):

| Nguồn             | Link                                         | Ghi chú                  |
| ----------------- | -------------------------------------------- | ------------------------ |
| **Unsplash**      | https://unsplash.com/s/photos/pho            | Ảnh chất lượng cao, free |
| **Pexels**        | https://pexels.com/search/vietnamese%20food/ | Free, nhiều món Việt     |
| **Pixabay**       | https://pixabay.com/images/search/pho/       | Free, commercial use OK  |
| **Google Images** | Tìm "phở bò" + filter "Creative Commons"     | Cẩn thận license         |

#### Danh sách 5 ảnh mẫu cần tải:

| #   | Món       | Tên file                     | Nguồn gợi ý |
| --- | --------- | ---------------------------- | ----------- |
| 1   | Phở bò    | `poc_pho_bo_001_main.jpg`    | Unsplash    |
| 2   | Cơm trắng | `poc_com_trang_001_main.jpg` | Pexels      |
| 3   | Bánh mì   | `poc_banh_mi_001_main.jpg`   | Unsplash    |
| 4   | Trà sữa   | `poc_tra_sua_001_main.jpg`   | Pexels      |
| 5   | Bún bò    | `poc_bun_bo_001_main.jpg`    | Pixabay     |

**Lưu vào:** `data/poc/raw/`

```bash
# Tạo thư mục
mkdir -p data/poc/raw
mkdir -p data/poc/annotations

# Tải ảnh và lưu vào data/poc/raw/ với đúng tên file
```

---

### Task 2: Tạo Mock Ground Truth

**Mục tiêu:** Tạo file `ground_truth.json` giả với số liệu ước lượng

Tạo file `data/poc/annotations/ground_truth.json`:

```json
{
  "version": "1.0-poc",
  "created_at": "2026-01-30",
  "created_by": "POC_TEST",
  "description": "Dữ liệu POC với giá trị ước lượng, KHÔNG phải đo thực tế",
  "total_samples": 5,
  "samples": [
    {
      "id": "poc_pho_bo_001",
      "image_file": "raw/poc_pho_bo_001_main.jpg",
      "food_name": "Phở bò",
      "food_category": "noodle",
      "ground_truth": {
        "total_weight_g": 450,
        "solid_weight_g": 140,
        "liquid_volume_ml": 310,
        "is_liquid": true,
        "measurement_method": "estimated_for_poc"
      },
      "reference_object": {
        "type": "spoon",
        "known_length_cm": 15.0
      },
      "metadata": {
        "restaurant": "Internet Sample",
        "notes": "Ảnh từ Unsplash, giá trị ước lượng dựa trên portion size trung bình"
      }
    },
    {
      "id": "poc_com_trang_001",
      "image_file": "raw/poc_com_trang_001_main.jpg",
      "food_name": "Cơm trắng",
      "food_category": "rice",
      "ground_truth": {
        "total_weight_g": 200,
        "solid_weight_g": 200,
        "liquid_volume_ml": 0,
        "is_liquid": false,
        "measurement_method": "estimated_for_poc"
      },
      "reference_object": {
        "type": "spoon",
        "known_length_cm": 15.0
      },
      "metadata": {
        "restaurant": "Internet Sample",
        "notes": "1 chén cơm trung bình ~200g"
      }
    },
    {
      "id": "poc_banh_mi_001",
      "image_file": "raw/poc_banh_mi_001_main.jpg",
      "food_name": "Bánh mì thịt",
      "food_category": "bread",
      "ground_truth": {
        "total_weight_g": 250,
        "solid_weight_g": 250,
        "liquid_volume_ml": 0,
        "is_liquid": false,
        "measurement_method": "estimated_for_poc"
      },
      "reference_object": {
        "type": "none",
        "known_length_cm": 0
      },
      "metadata": {
        "restaurant": "Internet Sample",
        "notes": "1 ổ bánh mì tiêu chuẩn ~250g"
      }
    },
    {
      "id": "poc_tra_sua_001",
      "image_file": "raw/poc_tra_sua_001_main.jpg",
      "food_name": "Trà sữa trân châu",
      "food_category": "drink",
      "ground_truth": {
        "total_weight_g": 500,
        "solid_weight_g": 50,
        "liquid_volume_ml": 450,
        "is_liquid": true,
        "measurement_method": "estimated_for_poc"
      },
      "reference_object": {
        "type": "none",
        "known_length_cm": 0
      },
      "metadata": {
        "restaurant": "Internet Sample",
        "size": "M",
        "notes": "Size M ~500ml, trân châu ~50g"
      }
    },
    {
      "id": "poc_bun_bo_001",
      "image_file": "raw/poc_bun_bo_001_main.jpg",
      "food_name": "Bún bò Huế",
      "food_category": "noodle",
      "ground_truth": {
        "total_weight_g": 500,
        "solid_weight_g": 180,
        "liquid_volume_ml": 320,
        "is_liquid": true,
        "measurement_method": "estimated_for_poc"
      },
      "reference_object": {
        "type": "spoon",
        "known_length_cm": 15.0
      },
      "metadata": {
        "restaurant": "Internet Sample",
        "notes": "Bún bò thường nhiều cái hơn phở"
      }
    }
  ]
}
```

---

### Task 3: Test Validate Script

**Mục tiêu:** Đảm bảo script validation hoạt động

```bash
# Tạo script validate cho POC
python scripts/validate_dataset.py --path data/poc/annotations/ground_truth.json
```

Sửa script `scripts/validate_dataset.py` để nhận tham số:

```python
"""
Kiểm tra tính toàn vẹn của dataset
Chạy: python scripts/validate_dataset.py [--path <path_to_ground_truth>]
"""

import json
import os
import argparse
from pathlib import Path

def validate_dataset(gt_path: str = "data/annotations/ground_truth.json"):
    errors = []
    warnings = []

    # Load ground truth
    gt_file = Path(gt_path)
    if not gt_file.exists():
        print(f"❌ Không tìm thấy {gt_path}")
        return False

    with open(gt_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    samples = data['samples']
    base_dir = gt_file.parent.parent  # data/poc/ hoặc data/

    print(f"📊 Kiểm tra {len(samples)} mẫu từ {gt_path}...\n")

    for sample in samples:
        sample_id = sample['id']

        # 1. Kiểm tra ảnh tồn tại
        img_path = base_dir / sample['image_file']
        if not img_path.exists():
            errors.append(f"[{sample_id}] Thiếu ảnh: {img_path}")

        # 2. Kiểm tra ground truth hợp lệ
        gt = sample['ground_truth']
        if gt['total_weight_g'] <= 0:
            errors.append(f"[{sample_id}] Trọng lượng <= 0")

        if gt['is_liquid'] and gt['liquid_volume_ml'] <= 0:
            warnings.append(f"[{sample_id}] Món nước nhưng không có thể tích nước")

        # 3. Kiểm tra metadata
        if not sample['metadata'].get('restaurant'):
            warnings.append(f"[{sample_id}] Thiếu thông tin quán")

    # Report
    print("=" * 50)
    if errors:
        print(f"❌ {len(errors)} LỖI:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ Không có lỗi nghiêm trọng!")

    if warnings:
        print(f"\n⚠️  {len(warnings)} CẢNH BÁO:")
        for w in warnings:
            print(f"   - {w}")

    print("=" * 50)
    valid = len(samples) - len(errors)
    print(f"📈 Kết quả: {valid}/{len(samples)} mẫu hợp lệ")

    return len(errors) == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default='data/annotations/ground_truth.json',
                        help='Path to ground_truth.json')
    args = parser.parse_args()

    validate_dataset(args.path)
```

---

### Task 4: Test Depth Estimation (Optional nhưng khuyến khích)

**Mục tiêu:** Xác nhận Depth Anything V2 chạy được với ảnh mẫu

```bash
# Cài đặt dependencies
pip install torch torchvision transformers pillow

# Tạo script test nhanh
```

Tạo file `scripts/poc_depth_test.py`:

```python
"""
POC: Test Depth Anything V2 với ảnh mẫu
Chạy: python scripts/poc_depth_test.py data/poc/raw/poc_pho_bo_001_main.jpg
"""

import sys
from pathlib import Path

def test_depth_estimation(image_path: str):
    print("🔄 Loading Depth Anything V2...")

    try:
        import torch
        from transformers import pipeline
        from PIL import Image

        # Load model (sẽ download lần đầu ~350MB)
        pipe = pipeline(
            task="depth-estimation",
            model="depth-anything/Depth-Anything-V2-Small-hf",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )

        print(f"✅ Model loaded on {'GPU' if torch.cuda.is_available() else 'CPU'}")

        # Load image
        image = Image.open(image_path)
        print(f"📷 Image: {image.size[0]}x{image.size[1]}")

        # Run inference
        print("🔄 Running depth estimation...")
        result = pipe(image)

        depth_map = result["depth"]
        print(f"✅ Depth map generated: {depth_map.size}")

        # Save output
        output_path = Path(image_path).stem + "_depth.png"
        depth_map.save(output_path)
        print(f"💾 Saved to: {output_path}")

        return True

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install torch torchvision transformers pillow")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/poc_depth_test.py <image_path>")
        sys.exit(1)

    test_depth_estimation(sys.argv[1])
```

---

### Task 5: POC Checklist

Hoàn thành các bước sau trước khi chuyển sang Sprint 2:

- [ ] Tải được 5 ảnh mẫu vào `data/poc/raw/`
- [ ] Tạo được `data/poc/annotations/ground_truth.json`
- [ ] Script `validate_dataset.py` chạy không lỗi với POC data
- [ ] (Optional) Depth Anything V2 chạy được, output depth map

```bash
# Quick test all
python scripts/validate_dataset.py --path data/poc/annotations/ground_truth.json

# Expected output:
# ✅ Không có lỗi nghiêm trọng!
# 📈 Kết quả: 5/5 mẫu hợp lệ
```

---

### 🎯 Kết quả mong đợi sau Sprint 1.5

| Câu hỏi                             | Trả lời được sau POC  |
| ----------------------------------- | --------------------- |
| Scripts có chạy được không?         | ✅ Đã test            |
| Format JSON đúng chưa?              | ✅ Đã validate        |
| Depth model load được không?        | ✅ Đã test (optional) |
| Cần sửa gì trước khi thu thập thật? | ✅ Đã biết            |

**Sau khi POC pass → Tự tin đi thu thập dữ liệu thật ở Sprint 2!**

---

## Sprint 2: Thu thập dữ liệu (Tuần 3)

### Mục tiêu

- Có dataset 10 món ăn Việt Nam
- Có ground-truth thể tích thực tế
- Dữ liệu sẵn sàng cho Vision Engine

### Phân công

| Task                          | Người thực hiện | Deadline |
| ----------------------------- | --------------- | -------- |
| Định nghĩa format dữ liệu     | Tôi             | Ngày 1   |
| Chuẩn bị dụng cụ đo           | HI              | Ngày 1   |
| Chụp ảnh + đo thể tích 10 món | HI              | Ngày 2-4 |
| Validate và upload            | HI + Tôi        | Ngày 5   |

---

### ⚠️ Tại sao không dùng Dataset có sẵn (Food-101, VFN, etc.)?

Đây là câu hỏi rất hay và quan trọng. Có 3 lý do chính:

#### 1. Thiếu Ground-Truth về thể tích

| Dataset có sẵn            | Có gì                      | Thiếu gì                                    |
| ------------------------- | -------------------------- | ------------------------------------------- |
| **Food-101**              | 101 loại thức ăn, 101K ảnh | ❌ Không có thể tích, không có trọng lượng  |
| **VFN (Vietnamese Food)** | ~30 món Việt Nam           | ❌ Chỉ có nhãn tên món, không có dinh dưỡng |
| **Nutrition5k**           | 5K ảnh + dinh dưỡng        | ❌ Món Mỹ, không có món Việt Nam            |
| **MenuMatch**             | Ảnh + calo                 | ❌ Ảnh chất lượng thấp, không có thể tích   |

**Vấn đề cốt lõi:** InSight cần **thể tích thực tế (ml)** để tính Carb → Insulin. Không có dataset nào cung cấp thông tin này cho món Việt Nam.

#### 2. Bài toán của InSight khác biệt

```
Bài toán Food Recognition thông thường:
  Ảnh → Tên món (Classification)

Bài toán của InSight:
  Ảnh → Tên món → Thể tích (ml) → Trọng lượng (g) → Carb (g) → Insulin (units)
         ↑           ↑              ↑
      Có dataset   KHÔNG CÓ      Tự tính từ
      có sẵn       DATASET       bảng dinh dưỡng
```

#### 3. Tính đặc thù của món Việt Nam

- **Phở/Bún:** Tỷ lệ nước/cái khác nhau tùy quán
- **Trà sữa:** Size S/M/L khác nhau tùy thương hiệu
- **Cơm bình dân:** Portion size không chuẩn hóa

→ Cần dữ liệu thực tế từ các quán ăn Việt Nam để model học được sự đa dạng này.

#### Kết luận: Chiến lược Hybrid

| Giai đoạn              | Dữ liệu                    | Mục đích                                   |
| ---------------------- | -------------------------- | ------------------------------------------ |
| **Sprint 2 (Bây giờ)** | 25 mẫu tự thu thập         | Proof-of-concept, có ground-truth thể tích |
| **Giai đoạn 2-3**      | Food-101 + VFN             | Pretrain/fine-tune model nhận diện tên món |
| **Production**         | User feedback + Correction | Continuous learning                        |

**Tóm lại:** Dataset có sẵn sẽ dùng sau để tăng độ chính xác nhận diện món. Nhưng bước đầu, chúng ta PHẢI tự thu thập để có ground-truth thể tích - thứ không ai có.

---

### Task 1: Định nghĩa format dữ liệu

**Người thực hiện:** Tôi

Tạo file `data/README.md`:

```markdown
# InSight Dataset

## Cấu trúc thư mục
```

data/
├── raw/ # Ảnh gốc
│ ├── pho_bo_001.jpg
│ ├── pho_bo_002.jpg
│ └── ...
├── processed/ # Ảnh đã crop/annotate
│ └── ...
├── annotations/ # Ground truth
│ └── ground_truth.json
└── README.md

````

## Format ảnh

- **Kích thước:** Tối thiểu 1280x720, khuyến nghị 1920x1080
- **Format:** JPG hoặc PNG
- **Yêu cầu:**
  - Chụp từ trên xuống (góc 45-90 độ)
  - Có vật tham chiếu (thìa/đũa) trong khung hình
  - Ánh sáng đủ, không bị bóng đổ quá đậm
  - Không bị mờ/rung

## Format annotation (ground_truth.json)

```json
{
  "version": "1.0",
  "created_at": "2026-01-30",
  "created_by": "HI",
  "samples": [
    {
      "id": "pho_bo_001",
      "image_file": "raw/pho_bo_001.jpg",
      "food_name": "Phở bò",
      "food_category": "noodle",

      "ground_truth": {
        "total_volume_ml": 450,
        "solid_weight_g": 135,
        "liquid_weight_g": 315,
        "total_weight_g": 450,
        "measurement_method": "water_displacement"
      },

      "reference_object": {
        "type": "spoon",
        "known_length_cm": 15.0
      },

      "metadata": {
        "restaurant": "Phở Thìn",
        "portion_size": "normal",
        "notes": "Bánh phở vừa"
      }
    }
  ]
}
````

## Phương pháp đo thể tích

### Cách 1: Đổ nước (Water displacement)

1. Đặt bát rỗng vào một bát lớn hơn
2. Đổ nước đầy bát nhỏ cho tràn ra
3. Đo lượng nước tràn = Thể tích bát

### Cách 2: Dùng cốc đo lường

1. Đổ món ăn vào cốc đo lường
2. Ghi nhận thể tích

### Cách 3: Cân + Density

1. Cân món ăn (g)
2. Thể tích = Khối lượng / Density

## Danh sách 10 món cần thu thập

| #   | Món          | Category | Số mẫu cần |
| --- | ------------ | -------- | ---------- |
| 1   | Cơm trắng    | rice     | 3          |
| 2   | Phở bò       | noodle   | 3          |
| 3   | Phở gà       | noodle   | 2          |
| 4   | Bún chả      | noodle   | 2          |
| 5   | Bánh mì thịt | bread    | 3          |
| 6   | Cơm tấm      | rice     | 3          |
| 7   | Xôi          | rice     | 2          |
| 8   | Bún bò Huế   | noodle   | 2          |
| 9   | Trà sữa      | drink    | 3          |
| 10  | Cà phê sữa   | drink    | 2          |

**Tổng: 25 mẫu**

````

---

### Task 2: Chuẩn bị dụng cụ

**Người thực hiện:** HI

#### Checklist dụng cụ (Bắt buộc)

| Dụng cụ | Mục đích | Mua ở đâu | Giá ước tính |
|---------|----------|-----------|--------------|
| ✅ Điện thoại camera tốt | Chụp ảnh | Có sẵn | - |
| ✅ Cốc đo lường 500ml | Đo thể tích nước | Shopee/Lazada | 30-50K |
| ✅ Cân điện tử (độ chính xác 1g) | Cân thức ăn | Shopee/Lazada | 80-150K |
| ✅ Thìa inox tiêu chuẩn 15cm | Vật tham chiếu | Có sẵn | - |
| ✅ Đũa tiêu chuẩn 24cm | Vật tham chiếu | Có sẵn | - |
| ✅ Tô/Bát nhiều size | Đựng thức ăn | Có sẵn | - |

#### Checklist dụng cụ (Khuyến nghị)

| Dụng cụ | Mục đích | Ghi chú |
|---------|----------|---------|
| 📱 Tripod điện thoại | Giữ góc chụp ổn định | Có thể dùng cốc kê tạm |
| 💡 Đèn LED nhỏ | Đảm bảo ánh sáng | Chụp ban ngày gần cửa sổ thay thế |
| 📝 Sổ ghi chép | Ghi nhanh số đo | Hoặc dùng Google Keep |

#### Thiết lập "Góc chụp cố định"

```
┌─────────────────────────────────┐
│                                 │
│    [Đèn/Cửa sổ]                 │
│         ↓ ánh sáng              │
│                                 │
│    ┌─────────┐                  │
│    │  🍜 Tô  │ ← Đặt cố định    │
│    │  ──────  │    tại 1 vị trí │
│    │  🥄 Thìa │                  │
│    └─────────┘                  │
│         ↑                       │
│    [Điện thoại] góc 45-60°      │
│                                 │
│    ════════════════             │
│         Bàn                     │
└─────────────────────────────────┘
```

**Tip:** Dùng băng keo đánh dấu vị trí đặt tô trên bàn để các ảnh có góc nhìn nhất quán.

---

### Task 3: Quy trình chụp ảnh CHI TIẾT

**Người thực hiện:** HI

#### 📋 Workflow tổng quan (cho MỖI mẫu)

```
1. MUA/ĐẶT món ăn
       ↓
2. CHỤP ẢNH (trước khi ăn!)
       ↓
3. ĐO LƯỜNG (cân + đo thể tích)
       ↓
4. GHI CHÉP vào Google Sheet
       ↓
5. LƯU ẢNH đúng tên file
```

**Thời gian ước tính:** 5-10 phút/mẫu

---

#### Bước 1: Setup trước khi chụp

**Checklist nhanh:**
- [ ] Bàn sạch, nền đơn sắc (trắng/gỗ/xám)
- [ ] Ánh sáng đủ (gần cửa sổ hoặc bật đèn)
- [ ] Thìa 15cm đặt cạnh tô (KHÔNG đè lên thức ăn)
- [ ] Điện thoại sạc đủ pin

**Ví dụ setup đúng vs sai:**

```
✅ ĐÚNG:                          ❌ SAI:
┌────────────────┐               ┌────────────────┐
│   🍜           │               │   🍜    📱     │
│      ────      │               │ shadows ░░░░░  │
│   🥄           │               │   🥄 (đè lên)  │
└────────────────┘               └────────────────┘
 Nền sạch, thìa rõ               Có bóng, thìa bị che
```

---

#### Bước 2: Chụp ảnh

**Yêu cầu kỹ thuật:**

| Tiêu chí | Yêu cầu | Lý do |
|----------|---------|-------|
| Góc chụp | 45-60° từ trên xuống | Thấy được bề mặt + chiều sâu |
| Khoảng cách | 30-50cm | Toàn bộ tô + thìa trong khung |
| Focus | Vào món ăn | Không bị mờ |
| Flash | TẮT | Tránh bóng đổ cứng |

**Chụp 2 góc cho mỗi mẫu:**

```
Góc 1 (Chính):              Góc 2 (Phụ):
     📱                          📱
      \  45°                    /  60°
       \                       /
    ┌──────┐               ┌──────┐
    │  🍜  │               │  🍜  │
    └──────┘               └──────┘
```

**Đặt tên file:**
```
{tên_món}_{số_thứ_tự}_{góc}.jpg

Ví dụ:
- pho_bo_001_main.jpg
- pho_bo_001_side.jpg
- com_trang_002_main.jpg
```

---

#### Bước 3: Đo lường (QUAN TRỌNG NHẤT)

##### 3A. Với MÓN KHÔ (Cơm, Xôi, Bánh mì)

```
Quy trình:
1. Cân tổng trọng lượng (bao gồm tô) → A gram
2. Ăn xong, cân tô rỗng → B gram
3. Trọng lượng thức ăn = A - B gram

Ví dụ:
- Tổng (cơm + tô): 450g
- Tô rỗng: 200g
- → Cơm = 250g
```

##### 3B. Với MÓN NƯỚC (Phở, Bún, Canh)

```
Quy trình phức tạp hơn:
1. Cân TỔNG (tô + nước + cái) → A gram
2. Dùng đũa gắp riêng PHẦN CÁI ra đĩa, cân → B gram
3. Đổ NƯỚC vào cốc đo lường → C ml
4. Cân tô rỗng → D gram

Kết quả:
- Tổng thể tích nước: C ml
- Trọng lượng cái: B gram
- Tổng trọng lượng: A - D gram

Ví dụ Phở bò:
- Tổng: 650g, Tô: 200g → Thức ăn: 450g
- Phần cái (bánh + thịt + hành): 140g
- Nước: 310ml
```

##### 3C. Với ĐỒ UỐNG (Trà sữa, Cà phê)

```
Quy trình:
1. Ghi nhận SIZE (S/M/L) và THƯƠNG HIỆU
2. Đổ ra cốc đo lường → A ml
3. Nếu có topping (trân châu), gạn riêng và cân → B gram

Ví dụ Trà sữa Gongcha M:
- Thể tích: 450ml
- Trân châu: 50g
```

---

#### Bước 4: Ghi chép vào Google Sheet

**Tạo Google Sheet với các cột sau:**

| Cột | Tên cột | Ví dụ | Ghi chú |
|-----|---------|-------|---------|
| A | ID | pho_bo_001 | Theo format đặt tên file |
| B | Tên món | Phở bò | Tiếng Việt |
| C | Category | noodle | rice/noodle/bread/drink |
| D | Tổng trọng lượng (g) | 450 | Không tính tô |
| E | Phần cái (g) | 140 | Chỉ với món nước |
| F | Phần nước (ml) | 310 | Chỉ với món nước |
| G | Quán | Phở Thìn | Tên quán/thương hiệu |
| H | Địa chỉ | 13 Lò Đúc | Optional |
| I | Size | M | Với đồ uống |
| J | Ghi chú | Bánh phở vừa | Mô tả thêm |
| K | Ngày chụp | 2026-01-30 | |

**Link mẫu:** [Tạo copy từ template này](https://docs.google.com/spreadsheets/d/create)

---

#### Bước 5: Upload và tổ chức file

```bash
# Cấu trúc thư mục
data/
├── raw/                          # Ảnh gốc chưa xử lý
│   ├── pho_bo_001_main.jpg
│   ├── pho_bo_001_side.jpg
│   ├── pho_bo_002_main.jpg
│   ├── com_trang_001_main.jpg
│   └── ...
├── annotations/
│   └── ground_truth.json         # Export từ Google Sheet
└── measurements.xlsx             # Backup từ Google Sheet
```

**Quy trình upload:**
1. Kết nối điện thoại với máy tính
2. Copy ảnh vào `data/raw/`
3. Đổi tên file theo format
4. Export Google Sheet → Excel → lưu vào `data/`

---

### 📅 Lịch thu thập đề xuất (4 ngày)

| Ngày | Buổi | Món cần thu thập | Số mẫu | Ghi chú |
|------|------|------------------|--------|---------|
| **Ngày 1** | Sáng | Phở bò, Phở gà | 5 | Đi quán phở gần nhà |
| | Trưa | Cơm trắng, Cơm tấm | 4 | Quán cơm bình dân |
| **Ngày 2** | Sáng | Bánh mì thịt | 3 | Tiệm bánh mì |
| | Trưa | Bún chả, Bún bò | 4 | |
| **Ngày 3** | Sáng | Xôi | 2 | Quán xôi sáng |
| | Chiều | Trà sữa (2 quán) | 4 | Gongcha + Phúc Long |
| **Ngày 4** | Sáng | Cà phê sữa | 2 | Highlands hoặc quán quen |
| | | **Buffer** | +1 | Chụp bù nếu thiếu |

**Tổng: 25 mẫu trong 4 ngày**

---

### 🎯 Checklist TRƯỚC khi đi thu thập

Mỗi lần ra ngoài, kiểm tra:

- [ ] Điện thoại sạc đủ pin (>50%)
- [ ] Bộ nhớ điện thoại còn trống (>2GB)
- [ ] Mang theo: Cân điện tử, cốc đo lường, thìa 15cm
- [ ] Mở sẵn Google Sheet trên điện thoại
- [ ] Biết quán nào sẽ đến

---

### Task 4: Tạo file ground_truth.json

**Người thực hiện:** HI (với hỗ trợ của Tôi)

Sau khi chụp xong, chuyển đổi Google Sheet sang JSON theo format đã định nghĩa.

#### Script tự động chuyển đổi

Tạo file `scripts/sheet_to_json.py`:

```python
"""
Chuyển đổi Google Sheet/Excel sang ground_truth.json
Chạy: python scripts/sheet_to_json.py data/measurements.xlsx
"""

import pandas as pd
import json
import sys
from datetime import datetime

def convert_to_ground_truth(excel_path: str, output_path: str = "data/annotations/ground_truth.json"):
    # Đọc Excel
    df = pd.read_excel(excel_path)

    samples = []
    for _, row in df.iterrows():
        # Xử lý món khô vs món nước
        is_liquid = row.get('Category', '') in ['noodle', 'drink']

        sample = {
            "id": row['ID'],
            "image_file": f"raw/{row['ID']}_main.jpg",
            "food_name": row['Tên món'],
            "food_category": row['Category'],

            "ground_truth": {
                "total_weight_g": float(row['Tổng trọng lượng (g)']),
                "solid_weight_g": float(row.get('Phần cái (g)', row['Tổng trọng lượng (g)'])),
                "liquid_volume_ml": float(row.get('Phần nước (ml)', 0)),
                "is_liquid": is_liquid,
                "measurement_method": "scale_and_measuring_cup"
            },

            "reference_object": {
                "type": "spoon",
                "known_length_cm": 15.0
            },

            "metadata": {
                "restaurant": str(row.get('Quán', '')),
                "address": str(row.get('Địa chỉ', '')),
                "size": str(row.get('Size', '')),
                "notes": str(row.get('Ghi chú', '')),
                "captured_date": str(row.get('Ngày chụp', ''))
            }
        }
        samples.append(sample)

    # Tạo output
    output = {
        "version": "1.0",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "created_by": "HI",
        "total_samples": len(samples),
        "samples": samples
    }

    # Ghi file
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported {len(samples)} samples to {output_path}")

    # Validate
    print("\n📊 Thống kê:")
    print(f"   - Tổng mẫu: {len(samples)}")
    for cat in df['Category'].unique():
        count = len(df[df['Category'] == cat])
        print(f"   - {cat}: {count} mẫu")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/sheet_to_json.py <path_to_excel>")
        print("Example: python scripts/sheet_to_json.py data/measurements.xlsx")
        sys.exit(1)

    convert_to_ground_truth(sys.argv[1])
```

#### Chạy script

```bash
# Cài thư viện (nếu chưa có)
pip install pandas openpyxl

# Export Google Sheet về Excel, lưu vào data/measurements.xlsx

# Chạy chuyển đổi
python scripts/sheet_to_json.py data/measurements.xlsx
```

---

### Task 5: Validate dữ liệu

**Người thực hiện:** Tôi

Tạo file `scripts/validate_dataset.py`:

```python
"""
Kiểm tra tính toàn vẹn của dataset
Chạy: python scripts/validate_dataset.py
"""

import json
import os
from pathlib import Path

def validate_dataset():
    errors = []
    warnings = []

    # Load ground truth
    gt_path = Path("data/annotations/ground_truth.json")
    if not gt_path.exists():
        print("❌ Không tìm thấy ground_truth.json")
        return

    with open(gt_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    samples = data['samples']
    print(f"📊 Kiểm tra {len(samples)} mẫu...\n")

    for sample in samples:
        sample_id = sample['id']

        # 1. Kiểm tra ảnh tồn tại
        img_path = Path("data") / sample['image_file']
        if not img_path.exists():
            errors.append(f"[{sample_id}] Thiếu ảnh: {sample['image_file']}")

        # 2. Kiểm tra ground truth hợp lệ
        gt = sample['ground_truth']
        if gt['total_weight_g'] <= 0:
            errors.append(f"[{sample_id}] Trọng lượng <= 0")

        if gt['is_liquid'] and gt['liquid_volume_ml'] <= 0:
            warnings.append(f"[{sample_id}] Món nước nhưng không có thể tích nước")

        # 3. Kiểm tra metadata
        if not sample['metadata'].get('restaurant'):
            warnings.append(f"[{sample_id}] Thiếu thông tin quán")

    # Report
    print("=" * 50)
    if errors:
        print(f"❌ {len(errors)} LỖI:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ Không có lỗi!")

    if warnings:
        print(f"\n⚠️  {len(warnings)} CẢNH BÁO:")
        for w in warnings:
            print(f"   - {w}")

    print("=" * 50)
    valid = len(samples) - len(errors)
    print(f"📈 Kết quả: {valid}/{len(samples)} mẫu hợp lệ")

if __name__ == "__main__":
    validate_dataset()
```

---

### 🏁 Kết thúc Sprint 2: Checklist cuối cùng

Trước khi chuyển sang Giai đoạn 2 (Vision Engine), đảm bảo:

- [ ] Có ít nhất **20 mẫu hợp lệ** (cho phép 5 mẫu lỗi/loại bỏ)
- [ ] Mỗi category (rice, noodle, bread, drink) có ít nhất **3 mẫu**
- [ ] Tất cả ảnh đã được đổi tên đúng format
- [ ] `ground_truth.json` được tạo và validate thành công
- [ ] Script validate báo **0 lỗi**

```bash
# Chạy validate lần cuối
python scripts/validate_dataset.py

# Commit (KHÔNG commit ảnh nếu quá 100MB)
git add data/annotations/
git add scripts/sheet_to_json.py scripts/validate_dataset.py
git commit -m "feat(data): add ground truth for 25 food samples"
git push origin develop
```

**🎉 Hoàn thành Sprint 2 → Sẵn sàng cho Giai đoạn 2: Vision Engine!**`

---

## Checklist hoàn thành Giai đoạn 1

### Sprint 0 ✓

- [ ] Git repo được setup với cấu trúc thư mục chuẩn
- [ ] Branch protection được bật cho main và develop
- [ ] README.md có hướng dẫn cơ bản
- [ ] 3 ADR được viết (gRPC, Kafka, Depth Anything)
- [ ] Team đã họp đồng bộ, hiểu kiến trúc

### Sprint 1 ✓

- [ ] `docker compose up -d` chạy thành công
- [ ] PostgreSQL có 13 món ăn seed data
- [ ] Redis ping được
- [ ] Kafka chạy được
- [ ] Milvus collection được tạo
- [ ] GitHub Actions CI pass

### Sprint 2 ✓

- [ ] Có ít nhất 25 mẫu ảnh trong data/raw/
- [ ] Mỗi ảnh có ground-truth thể tích
- [ ] File ground_truth.json đúng format
- [ ] Data được commit (chỉ JSON, không commit ảnh nếu quá nặng)

---

## Troubleshooting

### Docker compose không chạy được

```bash
# Check logs
docker compose logs -f

# Nếu port đã bị chiếm
netstat -ano | findstr :5432
# Kill process đang chiếm port
```

### Milvus không kết nối được

```bash
# Check Milvus đã ready chưa
docker logs insight-milvus

# Thường cần đợi 1-2 phút sau khi start
```

### GitHub Actions fail

1. Vào Actions tab xem log chi tiết
2. Thường do thiếu file (pom.xml, requirements.txt, pubspec.yaml)
3. Nếu chưa có code, CI sẽ skip - đó là expected

---

**Hoàn thành Giai đoạn 1 → Sẵn sàng cho Giai đoạn 2: Vision Engine!**

_Cập nhật: 28-01-2026_
````

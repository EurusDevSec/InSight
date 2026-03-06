# 📖 HƯỚNG DẪN CHI TIẾT TASK 1.2: DATABASE & SCHEMA

> **Assignee**: Việt (chính), Hoàng
> **Thời gian**: 09/03 → 10/03/2026
> **Tiền đề**: Task 1.1 (PostgreSQL + Milvus phải đang chạy)
> **Tham chiếu**: [TASK_1.2](../Tasks/TASK_1.2_DATABASE_SCHEMA.md) | [architecture.md Section 5.3](../architecture.md)

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 1.1  Environment ✅ DONE (Docker đang chạy)                  │
│                                                                     │
│  ► Task 1.2  DATABASE & SCHEMA  ◄◄◄  BẠN ĐANG Ở ĐÂY              │
│    │                                                                │
│    │  Mục tiêu: Schema ready + seed data 10 món VN                 │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Việt: PostgreSQL schema + Redis config + Flyway migrations │
│    │  • Hoàng: Milvus collections setup                            │
│    │                                                                │
│    │  📊 Bảng cần tạo:                                             │
│    │  ┌────────┐ ┌──────────┐ ┌───────────┐ ┌──────┐              │
│    │  │ users  │→│ meal_log │→│ meal_item │→│ food │              │
│    │  └────────┘ └──────────┘ └───────────┘ └──────┘              │
│    │       ↓                                    ↓                  │
│    │  ┌─────────────────┐            ┌────────────────┐           │
│    │  │ glucose_reading │            │ density_factor │           │
│    │  └─────────────────┘            └────────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 1: Setup Flyway Migrations — Việt

### 1.1 Tạo thư mục migrations

```bash
mkdir -p src/api-gateway/src/main/resources/db/migration
```

### 1.2 Migration V1: Create Tables

```sql
-- src/api-gateway/src/main/resources/db/migration/V1__create_tables.sql

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    medication JSONB DEFAULT '[]',
    insulin_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Food Database
CREATE TABLE food (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    carb_per_100g FLOAT NOT NULL,
    gi_index FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Density Factors (cho món nước: Phở, Bún, Cháo...)
CREATE TABLE density_factor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    food_id UUID REFERENCES food(id) ON DELETE CASCADE,
    variant VARCHAR(100) DEFAULT 'standard',
    solid_ratio FLOAT NOT NULL,  -- Tỷ lệ phần đặc (0.0 - 1.0)
    density FLOAT NOT NULL,      -- g/ml
    created_at TIMESTAMP DEFAULT NOW()
);

-- Meal Logs
CREATE TABLE meal_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    logged_at TIMESTAMP DEFAULT NOW(),
    total_carbs FLOAT,
    total_gl FLOAT,
    insulin_suggestion TEXT,
    disclaimer_shown BOOLEAN DEFAULT TRUE,
    image_url TEXT,
    confidence_score FLOAT
);

-- Meal Items (từng món trong bữa)
CREATE TABLE meal_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_log_id UUID REFERENCES meal_log(id) ON DELETE CASCADE,
    food_id UUID REFERENCES food(id),
    volume_ml FLOAT,
    weight_g FLOAT,
    carbs_g FLOAT,
    confidence_score FLOAT
);

-- Glucose Readings
CREATE TABLE glucose_reading (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    value_mgdl FLOAT NOT NULL,
    measured_at TIMESTAMP DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'manual'  -- 'manual', 'cgm_freestyle', 'cgm_dexcom'
);

-- Favorite Restaurants (Quán quen)
CREATE TABLE favorite_restaurant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    custom_density_factors JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_meal_log_user ON meal_log(user_id);
CREATE INDEX idx_meal_item_log ON meal_item(meal_log_id);
CREATE INDEX idx_glucose_user ON glucose_reading(user_id);
CREATE INDEX idx_food_category ON food(category);
```

### 1.3 Migration V2: Seed Data 10 món VN

```sql
-- src/api-gateway/src/main/resources/db/migration/V2__seed_food_data.sql

-- 10 món Việt Nam phổ biến
INSERT INTO food (name_vi, name_en, carb_per_100g, gi_index, category) VALUES
('Cơm trắng',       'White rice',              28.0, 73, 'rice'),
('Phở bò',          'Beef pho',                15.0, 46, 'noodle_soup'),
('Bún bò Huế',      'Hue beef noodle',         18.0, 52, 'noodle_soup'),
('Bánh mì',         'Vietnamese sandwich',      49.0, 65, 'bread'),
('Cơm tấm',         'Broken rice plate',        28.0, 73, 'rice'),
('Bún thịt nướng',  'Grilled pork noodle',     20.0, 50, 'noodle'),
('Mì xào',          'Stir-fried noodle',        25.0, 55, 'noodle'),
('Cháo',            'Rice porridge',            12.0, 78, 'porridge'),
('Xôi',             'Sticky rice',              37.0, 87, 'rice'),
('Trà sữa',         'Milk tea (L, 100%)',       20.0, 55, 'beverage');

-- Density Factors cho món nước
INSERT INTO density_factor (food_id, variant, solid_ratio, density) VALUES
((SELECT id FROM food WHERE name_vi='Phở bò'),      'standard', 0.30, 1.02),
((SELECT id FROM food WHERE name_vi='Phở bò'),      'nhiều bánh', 0.45, 1.03),
((SELECT id FROM food WHERE name_vi='Bún bò Huế'),  'standard', 0.35, 1.03),
((SELECT id FROM food WHERE name_vi='Cháo'),         'standard', 0.20, 1.01),
((SELECT id FROM food WHERE name_vi='Cháo'),         'đặc',      0.35, 1.02);
```

### 1.4 Verify migrations

```bash
# Chạy Spring Boot → Flyway tự chạy migrations
cd src/api-gateway && ./gradlew bootRun

# Kiểm tra tables
docker exec insight-postgres psql -U insight -d insight_db -c "\dt"
# Kỳ vọng: 6 tables + flyway_schema_history

# Kiểm tra seed data
docker exec insight-postgres psql -U insight -d insight_db \
  -c "SELECT name_vi, carb_per_100g, gi_index FROM food ORDER BY name_vi;"
# Kỳ vọng: 10 rows
```

---

## Bước 2: Setup Milvus Collections — Hoàng

### 2.1 Script tạo collections

```python
# scripts/setup_milvus.py
"""Tạo Milvus collections cho InSight Knowledge Base"""
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# Connect
connections.connect("default", host="localhost", port="19530")
print("✅ Connected to Milvus")

# === Collection 1: Medical Knowledge ===
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
]
schema = CollectionSchema(fields, description="Medical knowledge for RAG")
medical_kb = Collection("medical_knowledge", schema)
medical_kb.create_index("embedding", {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {"M": 16, "efConstruction": 256},
})
print("✅ Collection 'medical_knowledge' created with HNSW index")

# === Collection 2: Food Embeddings ===
fields2 = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="food_name", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=1024),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
]
schema2 = CollectionSchema(fields2, description="Food image/text embeddings")
food_emb = Collection("food_embeddings", schema2)
food_emb.create_index("embedding", {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {"M": 16, "efConstruction": 256},
})
print("✅ Collection 'food_embeddings' created with HNSW index")

print("\n🎉 Milvus setup complete!")
```

```bash
pip install pymilvus
python scripts/setup_milvus.py
```

---

## Bước 3: Redis Config — Việt

```yaml
# Thêm vào application.yml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000  # 1 hour
  data:
    redis:
      host: localhost
      port: 6379
      password: insight_redis_2026
```

```bash
# Verify Redis
docker exec insight-redis redis-cli -a insight_redis_2026 SET test "hello" && \
docker exec insight-redis redis-cli -a insight_redis_2026 GET test
# Kỳ vọng: "hello"
```

---

## Checklist

- [ ] Flyway migrations V1 + V2 chạy thành công
- [ ] 6 tables created trong PostgreSQL
- [ ] 10 món VN + density factors có trong DB
- [ ] Milvus collections `medical_knowledge` + `food_embeddings` created
- [ ] Redis connected + cache config ready
- [ ] Hoàng reviewed schema

## Troubleshooting

| Vấn đề | Fix |
|--------|-----|
| Flyway checksum mismatch | Xóa DB: `docker exec insight-postgres psql -U insight -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"` |
| Milvus connection refused | Kiểm tra `docker ps` → milvus phải running |
| pymilvus ImportError | `pip install pymilvus==2.3.4` |

---

> **Tạo**: 06/03/2026

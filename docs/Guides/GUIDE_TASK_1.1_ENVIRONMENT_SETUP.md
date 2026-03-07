# 📖 HƯỚNG DẪN CHI TIẾT TASK 1.1: ENVIRONMENT SETUP

> **Assignee**: Việt (chính), Hoài
> **Thời gian**: 08/03 → 09/03/2026
> **Tiền đề**: Task 1.0 | **Tham chiếu**: [TASK_1.1](../Tasks/TASK_1.1_ENVIRONMENT_SETUP.md) | [architecture.md](../architecture.md)

---

## Bước 1: Docker Compose — Việt (3 giờ)

### 1.1 Tạo docker-compose.yml

```yaml
# infra/docker/docker-compose.yml
version: '3.9'
services:
  postgres:
    image: postgres:16-alpine
    container_name: insight-postgres
    environment:
      POSTGRES_DB: insight_db
      POSTGRES_USER: insight
      POSTGRES_PASSWORD: insight_dev_2026
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U insight"]
      interval: 5s
      retries: 5

  milvus:
    image: milvusdb/milvus:v2.3.4
    container_name: insight-milvus
    environment:
      ETCD_USE_EMBED: "true"
      COMMON_STORAGETYPE: local
    ports: ["19530:19530", "9091:9091"]
    volumes: [milvus_data:/var/lib/milvus]

  redis:
    image: redis:7-alpine
    container_name: insight-redis
    command: redis-server --requirepass insight_redis_2026
    ports: ["6379:6379"]
    volumes: [redis_data:/data]

  kafka:
    image: bitnami/kafka:3.6
    container_name: insight-kafka
    environment:
      KAFKA_CFG_NODE_ID: 0
      KAFKA_CFG_PROCESS_ROLES: controller,broker
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 0@kafka:9093
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CFG_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
    ports: ["9092:9092"]
    volumes: [kafka_data:/bitnami/kafka]

volumes:
  postgres_data:
  milvus_data:
  redis_data:
  kafka_data:
```

### 1.2 Chạy và verify

> [!NOTE]
> File docker-compose duy nhất nằm tại `infra/docker/docker-compose.yml`.
> Luôn chạy lệnh từ **project root** (`R:\_Projects\Eurus_Workspace\InSight`) với flag `-f`.

```bash
# Từ project root — start tất cả services
docker compose -f infra/docker/docker-compose.yml up -d

# Hoặc chỉ start postgres + redis trước
docker compose -f infra/docker/docker-compose.yml up -d postgres redis

# Kiểm tra status
docker compose -f infra/docker/docker-compose.yml ps

# Verify seed data (14 rows)
docker exec insight-postgres psql -U insight -d insight_db \
  -c "SELECT name_vi, category FROM foods ORDER BY category;"
```

---

## Bước 2: Spring Boot API Gateway — Việt (2 giờ)

### 2.1 application.yml

```yaml
# src/api-gateway/src/main/resources/application.yml
spring:
  application.name: insight-api-gateway
  datasource:
    url: jdbc:postgresql://localhost:5432/insight_db
    username: insight
    password: insight_dev_2026
  jpa:
    hibernate.ddl-auto: validate
  data.redis:
    host: localhost
    port: 6379
    password: insight_redis_2026
  kafka:
    bootstrap-servers: localhost:9092
server.port: 8080
```

### 2.2 Health endpoint

```java
// com.insight.controller.HealthController
@RestController
public class HealthController {
    @GetMapping("/api/health")
    public Map<String, String> health() {
        return Map.of("status", "UP", "service", "insight-api-gateway");
    }
}
```

---

## Bước 3: Python Vision Service Skeleton — Việt (2 giờ)

### 3.1 FastAPI skeleton

```python
# src/vision-service/main.py
from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI(title="InSight Vision Service", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "UP", "service": "insight-vision-service"}

@app.post("/api/vision/estimate-volume")
async def estimate_volume(image: UploadFile = File(...)):
    return {"volume_ml": 0.0, "message": "Not implemented — Task 2.1"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.2 requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
torch>=2.0.0
pillow>=10.0.0
numpy>=1.24.0
```

---

## Bước 4: CI/CD — Hoài (1 giờ)

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main, develop] }
jobs:
  api-gateway:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: src/api-gateway } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', distribution: 'temurin' }
      - run: ./gradlew build test
  vision-service:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: src/vision-service } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt && pip install ruff && ruff check .
```

---

## Checklist

- [ ] `docker compose up` → PostgreSQL + Milvus + Redis + Kafka healthy
- [ ] Spring Boot `/api/health` → OK
- [ ] Python `/health` → OK
- [ ] GitHub Actions CI xanh

## Troubleshooting

| Vấn đề | Fix |
|--------|-----|
| Port conflict | Đổi port: `5433:5432` |
| Milvus crash | Tăng Docker RAM ≥ 6GB |
| Kafka unhealthy | `docker volume rm` rồi chạy lại |

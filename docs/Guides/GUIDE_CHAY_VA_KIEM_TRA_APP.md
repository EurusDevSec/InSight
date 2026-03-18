# Hướng dẫn Chạy và Kiểm tra InSight App trên Thực tế

> **Mục đích:** Hướng dẫn từng bước cách khởi động toàn bộ hệ thống InSight và test ứng dụng trên thiết bị thật (điện thoại, máy ảo Android, hoặc Chrome).

---

## Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Chọn thiết bị chạy Flutter](#2-chọn-thiết-bị-chạy-flutter)
3. [Khởi động hệ thống (5 bước)](#3-khởi-động-hệ-thống-5-bước)
4. [Kiểm tra sức khỏe dịch vụ](#4-kiểm-tra-sức-khỏe-dịch-vụ)
5. [Test ứng dụng trên thiết bị](#5-test-ứng-dụng-trên-thiết-bị)
6. [Chạy test tự động](#6-chạy-test-tự-động)
7. [Tắt hệ thống](#7-tắt-hệ-thống)
8. [Xử lý lỗi thường gặp](#8-xử-lý-lỗi-thường-gặp)

---

## 1. Yêu cầu hệ thống

### Phần mềm cần cài sẵn

| Tool           | Version tối thiểu | Kiểm tra bằng                |
| -------------- | ----------------- | ---------------------------- |
| Docker Desktop | 24+               | `docker --version`           |
| Java (OpenJDK) | 17+               | `java -version`              |
| Python         | 3.11+             | `python --version`           |
| Flutter        | 3.35+             | `flutter --version`          |
| Android SDK    | API 21+           | Android Studio → SDK Manager |
| Git            | 2.x               | `git --version`              |

### Tài nguyên máy

- **RAM:** Tối thiểu 16 GB (Docker + Python models + Spring Boot + Android Emulator)
- **Disk:** ~15 GB trống (Docker images + models + Android emulator)
- **GPU (tùy chọn):** NVIDIA GPU giúp Vision Service nhanh hơn, nhưng CPU vẫn chạy được

### API Key cần có

- **GEMINI_API_KEY:** File `src/rag-service/.env` phải có key hợp lệ từ [Google AI Studio](https://aistudio.google.com/apikey)

---

## 2. Chọn thiết bị chạy Flutter

Flutter app InSight hỗ trợ 3 cách chạy. Dưới đây là so sánh:

| Thiết bị               | Camera hoạt động?  | Độ chân thực | Cài đặt Gateway URL         | Khuyến nghị          |
| ---------------------- | ------------------ | ------------ | --------------------------- | -------------------- |
| **Android Emulator**   | Giả lập (pick ảnh) | Cao          | `http://10.0.2.2:8080`      | **Khuyến nghị nhất** |
| **Điện thoại Android** | Có (camera thật)   | Rất cao      | `http://<IP-máy-tính>:8080` | Tốt nhất cho demo    |
| **Chrome (Web)**       | Hạn chế            | Trung bình   | `http://localhost:8080`     | Chỉ test UI          |

### Option A — Android Emulator (Khuyến nghị)

Đây là cách đơn giản nhất, không cần điện thoại thật.

**Bước 1: Tạo emulator**

Mở Android Studio → **More Actions** (hoặc **Tools**) → **Device Manager** → **Create Virtual Device**:

1. Chọn **Pixel 6** (hoặc Pixel 7) → Next
2. Chọn system image **API 34 (Android 14)** → Download nếu chưa có → Next
3. Đặt tên (VD: `Pixel_6_API34`) → Finish
4. Nhấn ▶ để khởi động emulator

Hoặc tạo bằng command line:

```bash
# Liệt kê system images có sẵn
sdkmanager --list | grep "system-images"

# Tải system image (nếu chưa có)
sdkmanager "system-images;android-34;google_apis;x86_64"

# Tạo emulator
avdmanager create avd -n Pixel_6_API34 -k "system-images;android-34;google_apis;x86_64" -d pixel_6

# Khởi động emulator
emulator -avd Pixel_6_API34
```

**Bước 2: Cấu hình Gateway URL**

File `mobile/insight_app/.env` **giữ nguyên** (mặc định đã đúng):

```
GATEWAY_BASE_URL=http://10.0.2.2:8080
```

> **Giải thích:** `10.0.2.2` là địa chỉ đặc biệt trong Android Emulator, ánh xạ về `localhost` của máy tính host. Vì Gateway chạy trên máy tính ở port 8080, emulator dùng `10.0.2.2:8080` để kết nối tới nó.

**Bước 3: Chạy app**

```bash
cd mobile/insight_app
flutter pub get
flutter run
# Flutter tự nhận emulator đang chạy
```

---

### Option B — Điện thoại Android thật (tốt nhất cho demo)

Camera thật hoạt động đầy đủ, trải nghiệm chân thực nhất.

**Bước 1: Bật Developer Mode trên điện thoại**

1. Vào **Cài đặt → Giới thiệu điện thoại**
2. Nhấn vào **Số bản dựng (Build Number)** liên tục 7 lần
3. Quay lại **Cài đặt → Tùy chọn nhà phát triển (Developer Options)**
4. Bật **USB Debugging**
5. Cắm cáp USB vào máy tính, đồng ý **"Cho phép USB Debugging"** trên điện thoại

**Bước 2: Kiểm tra kết nối**

```bash
flutter devices
# Kết quả phải hiện tên điện thoại, ví dụ:
# SM A536B (mobile) • RXXXXXXXXX • android-arm64 • Android 14
```

**Bước 3: Tìm IP máy tính**

Máy tính và điện thoại phải **cùng mạng WiFi**.

```bash
# Windows
ipconfig
# Tìm dòng "IPv4 Address" của WiFi adapter, VD: 192.168.1.100
```

**Bước 4: Cập nhật Gateway URL**

Sửa file `mobile/insight_app/.env`:

```
GATEWAY_BASE_URL=http://192.168.1.100:8080
```

_(Thay `192.168.1.100` bằng IP thật của máy bạn)_

**Bước 5: Chạy app**

```bash
cd mobile/insight_app
flutter pub get
flutter run -d <device-id>
# device-id lấy từ flutter devices ở bước 2
```

> **Lưu ý:** Đảm bảo Windows Firewall cho phép kết nối vào port 8080, 8000, 8001 từ mạng LAN.

---

### Option C — Chrome (chỉ test UI)

Nhanh nhất để test giao diện, **nhưng camera và một số tính năng mobile không hoạt động**.

**Bước 1: Cập nhật Gateway URL**

Sửa file `mobile/insight_app/.env`:

```
GATEWAY_BASE_URL=http://localhost:8080
```

**Bước 2: Chạy app**

```bash
cd mobile/insight_app
flutter pub get
flutter run -d chrome
```

> **Hạn chế:** `image_picker` (chụp ảnh) hoạt động hạn chế trên web — bạn chỉ có thể **chọn ảnh từ máy**, không mở camera trực tiếp. Panic Mode và UI navigation vẫn test được.

---

## 3. Khởi động hệ thống (5 bước)

> **THỨ TỰ QUAN TRỌNG:** Phải khởi động đúng thứ tự vì có dependency giữa các dịch vụ.

Mở **5 terminal riêng biệt** (hoặc dùng split terminal trong VS Code):

### Bước 1 — Khởi động hạ tầng (Docker)

```bash
# Terminal 1
cd infra/docker
docker compose up -d
```

Đợi tất cả container healthy:

```bash
docker compose ps
```

Kết quả mong đợi — tất cả `healthy` hoặc `running`:

```
NAME              STATUS
insight-postgres  running (healthy)
insight-redis     running (healthy)
insight-kafka     running (healthy)
milvus-etcd       running (healthy)
milvus-minio      running (healthy)
milvus-standalone running (healthy)
```

> **Thời gian chờ:** ~30-60 giây để tất cả container healthy. Milvus có thể mất lâu hơn (~1-2 phút).

### Bước 2 — Khởi động Vision Service

```bash
# Terminal 2
cd src/vision-service
pip install -r requirements.txt   # Chỉ cần lần đầu
python main.py
```

Chờ đến khi thấy log:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Vision service started — all models loaded
```

> **Thời gian chờ:** Lần đầu ~30-60 giây (tải model Depth Anything V2 + YOLO). Các lần sau nhanh hơn nếu model đã cache.

### Bước 3 — Khởi động RAG Service

```bash
# Terminal 3
cd src/rag-service
pip install -r requirements.txt   # Chỉ cần lần đầu
python main.py
```

Chờ đến khi thấy log:

```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     RAG service started successfully
```

> **Yêu cầu:** Milvus (Docker) phải đang chạy + `GEMINI_API_KEY` hợp lệ trong `src/rag-service/.env`

### Bước 4 — Khởi động API Gateway

```bash
# Terminal 4
cd src/api-gateway
./gradlew bootRun
```

Trên Windows, nếu `./gradlew` không chạy:

```bash
gradlew.bat bootRun
```

Chờ đến khi thấy log:

```
Started InsightApiGatewayApplication in X.XXX seconds
```

> **Yêu cầu:** PostgreSQL + Redis + Kafka (Docker) phải đang chạy.

### Bước 5 — Chạy Flutter App

```bash
# Terminal 5
cd mobile/insight_app
flutter pub get
flutter run
```

Chọn thiết bị khi được hỏi (hoặc dùng `-d <device>`:

```bash
flutter run -d emulator-5554     # Android Emulator
flutter run -d chrome             # Chrome
flutter run -d <phone-device-id>  # Điện thoại thật
```

---

## 4. Kiểm tra sức khỏe dịch vụ

Sau khi khởi động, chạy các lệnh sau để xác nhận mọi thứ OK:

### Health Check nhanh

```bash
# Vision Service
curl http://localhost:8000/health
# Mong đợi: {"status":"healthy", "model_loaded":true, ...}

# RAG Service
curl http://localhost:8001/health
# Mong đợi: {"status":"healthy", ...}

# API Gateway
curl http://localhost:8080/api/health
# Mong đợi: {"status":"UP", ...}
```

### Kiểm tra Docker containers

```bash
docker compose -f infra/docker/docker-compose.yml ps
# Tất cả healthy/running

# Kiểm tra riêng Milvus
curl http://localhost:9091/healthz
# Mong đợi: OK
```

### Script test endpoints tự động

```bash
python scripts/test_endpoints.py
```

Script sẽ test: health check, depth estimation, reference detection, error handling → In kết quả PASS/FAIL cho từng endpoint.

---

## 5. Test ứng dụng trên thiết bị

### Flow test chính: Chụp ảnh → Phân tích → Kết quả

1. **Mở app** → Màn hình Home hiện lên
2. **Nhấn nút Camera (📷)** → Chọn ảnh hoặc chụp ảnh món ăn
   - Trên emulator: Chọn ảnh từ gallery (có thể kéo-thả ảnh vào emulator)
   - Trên điện thoại: Chụp ảnh trực tiếp bằng camera
   - Trên Chrome: Chọn file ảnh từ máy
3. **Điền thông tin bệnh nhân** (nếu form hiện ra):
   - Glucose hiện tại: VD `120` mg/dL
   - Loại tiểu đường: VD `Type 2`
   - Insulin ratio: VD `10`
4. **Nhấn "Analyze" / "Phân tích"**
5. **Chờ kết quả** (thường 2-5 giây):
   - Tên món ăn (food_name)
   - Thể tích (volume_ml)
   - Khối lượng (weight_g)
   - Carbs (carbs_g)
   - Glycemic Load + GL level (low/medium/high)
   - Tư vấn từ RAG Agent
   - Disclaimer y khoa

### Test Panic Mode (tình huống khẩn cấp)

1. Từ bất kỳ màn hình nào → **Nhấn nút Panic (🚨)**
2. **Kết quả hiện ngay** (≤ 1 giây):
   - Hướng dẫn khẩn cấp cho hạ đường huyết
   - Các bước xử lý nhanh
3. Xác nhận: Panic mode **không cần kết nối mạng** (chạy offline)

### Test ảnh mẫu có sẵn

Dùng ảnh từ thư mục `data/vn_demo/` hoặc `data/poc/raw/`:

```
data/vn_demo/
├── pho_bo/         # Phở bò
├── com_tam/        # Cơm tấm
├── bun_bo_hue/     # Bún bò Huế
├── banh_mi/        # Bánh mì
└── com_trang/      # Cơm trắng

data/poc/raw/
└── poc_pho_bo_001_main.jpg   # Ảnh test chính
```

Để đưa ảnh vào emulator:

- **Kéo-thả** file ảnh từ File Explorer vào cửa sổ emulator
- Hoặc dùng lệnh: `adb push data/poc/raw/poc_pho_bo_001_main.jpg /sdcard/DCIM/`

---

## 6. Chạy test tự động

### A. Flutter Unit & Widget Tests

```bash
cd mobile/insight_app
flutter test
# 40 tests: models, services, view models, widgets, navigation
```

### B. Vision Service Tests

```bash
cd src/vision-service
python -m pytest tests/ -v
# 166 tests: depth estimation, reference detection, calibration, segmentation, volume
```

### C. RAG Service Tests

```bash
cd src/rag-service
python -m pytest tests/ -v
# 154 tests: embedding, retrieval, RAG pipeline, personalization
```

### D. API Gateway Tests

```bash
cd src/api-gateway
./gradlew test
# 15 tests: controller, service, health, error handling
```

### E. E2E Pipeline Test (yêu cầu tất cả dịch vụ đang chạy)

```bash
python scripts/test_e2e_pipeline.py
# Test: pipeline latency ≤5s, panic mode ≤1s, stability (10 runs), required fields
```

Tuỳ chọn:

```bash
# Chỉ gateway URL khác
python scripts/test_e2e_pipeline.py --gateway http://localhost:8080

# Nếu chỉ muốn test mà không cần chạy cả hệ thống (offline mock)
# → Dùng flutter test cho Flutter, pytest cho Python services
```

### F. Flutter Integration Tests (E2E trên thiết bị)

```bash
cd mobile/insight_app
flutter test integration_test/
# 7 tests: app launch, navigation, camera, analyze, panic mode, error handling, full flow
```

> **Lưu ý:** Integration tests cần emulator hoặc thiết bị đang kết nối.

---

## 7. Tắt hệ thống

Khi hoàn tất test, tắt theo thứ tự ngược:

```bash
# 1. Dừng Flutter app: Ctrl+C trong terminal flutter

# 2. Dừng API Gateway: Ctrl+C trong terminal gateway

# 3. Dừng RAG Service: Ctrl+C trong terminal rag

# 4. Dừng Vision Service: Ctrl+C trong terminal vision

# 5. Dừng Docker containers
cd infra/docker
docker compose down

# Nếu muốn xóa cả volume (data DB, Milvus) — CẨN THẬN, mất data:
# docker compose down -v
```

---

## 8. Xử lý lỗi thường gặp

### Docker không khởi động

```
Error: Cannot connect to the Docker daemon
```

**Fix:** Mở Docker Desktop và đợi nó ready (icon chuyển xanh).

---

### Vision Service — Model not found

```
FileNotFoundError: runs/reference_detector/v1/weights/best.pt
```

**Fix:** Chạy training script hoặc download pre-trained weights:

```bash
python scripts/train_reference_detector.py
```

---

### RAG Service — Milvus connection refused

```
MilvusException: connection refused
```

**Fix:** Kiểm tra Milvus container:

```bash
docker compose -f infra/docker/docker-compose.yml ps milvus-standalone
# Nếu không healthy, restart:
docker compose -f infra/docker/docker-compose.yml restart milvus-standalone
```

---

### RAG Service — Invalid GEMINI_API_KEY

```
AuthenticationError: Invalid API key
```

**Fix:** Kiểm tra file `src/rag-service/.env`:

```
GEMINI_API_KEY=<key-hợp-lệ-từ-Google-AI-Studio>
```

Lấy key mới tại: https://aistudio.google.com/apikey

---

### API Gateway — Cannot connect to PostgreSQL

```
Connection refused: localhost:5432
```

**Fix:** Kiểm tra Docker postgres container:

```bash
docker compose -f infra/docker/docker-compose.yml ps insight-postgres
docker compose -f infra/docker/docker-compose.yml logs insight-postgres
```

---

### Flutter — No devices found

```
No supported devices connected.
```

**Fix:**

- **Emulator:** Mở Android Studio → Device Manager → Start một emulator
- **Điện thoại:** Kiểm tra USB Debugging đã bật, cáp USB cắm đúng, nhấn "OK" trên popup điện thoại
- **Chrome:** `flutter run -d chrome` (luôn available)

Kiểm tra: `flutter devices` phải hiện ít nhất 1 device.

---

### Flutter — Connection refused khi gọi API

```
SocketException: Connection refused (OS Error: Connection refused)
```

**Fix theo thiết bị:**

| Thiết bị         | URL đúng trong `.env`       |
| ---------------- | --------------------------- |
| Android Emulator | `http://10.0.2.2:8080`      |
| Điện thoại thật  | `http://<IP-máy-tính>:8080` |
| Chrome           | `http://localhost:8080`     |

Kiểm tra thêm:

- Gateway có đang chạy không? `curl http://localhost:8080/api/health`
- Firewall Windows chặn port? → Tạm tắt firewall để test

---

### Emulator quá chậm

**Fix:**

1. Bật **Hardware Acceleration** trong BIOS (Intel VT-x hoặc AMD-V)
2. Cài HAXM: Android Studio → SDK Manager → SDK Tools → Intel x86 Emulator Accelerator
3. Dùng x86_64 system image thay vì arm64
4. Tăng RAM cho emulator: Device Manager → Edit → Show Advanced → RAM: 4096 MB

---

### Port đã bị chiếm

```
Address already in use: bind 0.0.0.0:8000
```

**Fix:**

```bash
# Windows — Tìm process đang dùng port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

---

## Tổng kết nhanh

```
┌─────────────────────────────────────────────────────────┐
│                THỨ TỰ KHỞI ĐỘNG                        │
│                                                         │
│  1. docker compose up -d         (PostgreSQL, Redis,    │
│                                   Kafka, Milvus)        │
│  2. python main.py               (Vision — port 8000)   │
│  3. python main.py               (RAG — port 8001)      │
│  4. ./gradlew bootRun            (Gateway — port 8080)  │
│  5. flutter run                  (App — trên thiết bị)  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                    THIẾT BỊ                              │
│                                                         │
│  Emulator:   10.0.2.2:8080  (Khuyến nghị)              │
│  Phone:      <LAN-IP>:8080  (Demo tốt nhất)            │
│  Chrome:     localhost:8080  (Chỉ test UI)              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                HEALTH CHECK                              │
│                                                         │
│  curl http://localhost:8000/health   → Vision OK?       │
│  curl http://localhost:8001/health   → RAG OK?          │
│  curl http://localhost:8080/api/health → Gateway OK?    │
└─────────────────────────────────────────────────────────┘
```

---

_Last updated: 06/2026_

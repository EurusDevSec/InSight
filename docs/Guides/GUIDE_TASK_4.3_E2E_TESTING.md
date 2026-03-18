# 📖 HƯỚNG DẪN CHI TIẾT TASK 4.3: E2E TESTING

> **Assignee**: Hoàng (chính), Hoài (UI tests)
> **Thời gian**: Sprint 10 (Phase 4)
> **Tiền đề**: Task 4.1 (Flutter App ✅), Task 4.2 (API Gateway ✅)
> **Tham chiếu**: [TASK_4.3](../Tasks/TASK_4.3_E2E_TESTING.md) | [plan.md](../plan.md)
> **Cập nhật**: 06/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 4.1 Flutter App ✅  |  Task 4.2 API Gateway ✅                │
│                                                                     │
│  ► Task 4.3  E2E TESTING  ◄◄◄  BẠN ĐANG Ở ĐÂY                    │
│    │                                                                │
│    │  Mục tiêu: Verify full pipeline hoạt động đúng                │
│    │  Acceptance Criteria:                                          │
│    │  ✅ Full pipeline: Ảnh → Tư vấn ≤ 5 giây                     │
│    │  ✅ Panic Mode: ≤ 1 giây response                             │
│    │  ✅ Disclaimer UI hiển thị đúng ở mọi kết quả                │
│    │  ✅ No crashes trong 10 test runs liên tiếp                   │
│    │                                                                │
│    │  📌 2 loại test:                                              │
│    │  • Python E2E script (full pipeline qua network)              │
│    │  • Flutter unit + widget tests (client-side)                  │
│    │                                                                │
│    └───► Task 5.1: UAT                                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Tổng quan Test Strategy

| Acceptance Criteria | Test Type        | File                              | Kết quả       |
| ------------------- | ---------------- | --------------------------------- | ------------- |
| Full pipeline ≤ 5s  | Python E2E       | `scripts/test_e2e_pipeline.py`    | Tested online |
| Panic Mode ≤ 1s     | Flutter + Python | Cả hai                            | ✅ < 1ms      |
| Disclaimer UI       | Flutter widget   | `test/e2e/e2e_pipeline_test.dart` | ✅            |
| Stability 10 runs   | Flutter + Python | Cả hai                            | ✅            |

---

## 2. Python E2E Test Script

**File:** `scripts/test_e2e_pipeline.py`

### 2.1 Mô tả

Script Python test toàn bộ pipeline qua HTTP:

- Gửi ảnh → Gateway → Vision → RAG → nhận response
- Đo latency, validate fields, kiểm tra disclaimer
- 10 runs liên tiếp cho stability

### 2.2 Chạy

```bash
# Install dependencies
pip install requests Pillow

# Offline mode (không cần services chạy)
python scripts/test_e2e_pipeline.py --offline

# Full E2E (cần tất cả services)
python scripts/test_e2e_pipeline.py

# Custom URLs
python scripts/test_e2e_pipeline.py \
  --gateway http://localhost:8080 \
  --vision http://localhost:8000 \
  --rag http://localhost:8001
```

### 2.3 Test Cases

| Test                    | Acceptance Criteria | Target         |
| ----------------------- | ------------------- | -------------- |
| **4.3.1 Full Pipeline** | Ảnh → Tư vấn        | ≤ 5s           |
| **4.3.2 Panic Mode**    | Cached lookup       | ≤ 1s           |
| **4.3.3 Disclaimer**    | Advisory text       | Always present |
| **Stability**           | 10 consecutive      | 0 failures     |

### 2.4 Output mẫu (offline)

```
============================================================
  InSight E2E Pipeline Test — Task 4.3
============================================================

── 4.3.2 Panic Mode Test ──
  ✅ PASS — Cơm trắng (1 chén): GL=33.0 (high) (0.0ms)
  ✅ PASS — Phở bò (1 tô): GL=30.0 (high) (0.0ms)
  ✅ PASS — Rau xào (1 đĩa): GL=3.0 (low) (0.0ms)
  ✅ PASS — Trái cây (1 phần): GL=8.0 (low) (0.0ms)
  ✅ PASS — All dishes < 1s

============================================================
  SUMMARY
============================================================
  ✅ PASS — 4.3.2 Panic Mode
  ✅ PASS — 4.3.3 Disclaimer
============================================================
  🎉 All E2E tests PASSED!
============================================================
```

### 2.5 Output mẫu (online — full pipeline)

```
── Service Health Check ──
  ✅ PASS — Gateway (http://localhost:8080)
  ✅ PASS — Vision (http://localhost:8000)
  ✅ PASS — RAG (http://localhost:8001)

── 4.3.1 Full Pipeline Test ──
  ✅ PASS — HTTP 200
  ✅ PASS — Required fields present (8 fields)
  ✅ PASS — Latency ≤ 5.0s (2.34s)
  ✅ PASS — GL level valid (medium)
  ✅ PASS — Disclaimer present

── Stability Test (10 runs) ──
  Run  1/10: ✅ (2.12s)
  Run  2/10: ✅ (1.98s)
  ... (10/10 OK)
  ✅ PASS — All 10 runs successful (10/10 ok, avg=2.05s)
```

---

## 3. Flutter E2E Tests

**File:** `mobile/insight_app/test/e2e/e2e_pipeline_test.dart`

### 3.1 Test Groups

| Group                          | Tests | Mô tả                            |
| ------------------------------ | ----- | -------------------------------- |
| E2E 4.3.2 — Panic Mode Latency | 2     | selectDish < 1s, all dishes < 1s |
| E2E 4.3.3 — Disclaimer UI      | 3     | HomeScreen, icon, PanicScreen    |
| E2E Stability — 10 runs        | 2     | ViewModel cycles, widget cycles  |
| **Tổng**                       | **7** |                                  |

### 3.2 Chi tiết Tests

**Panic Mode Latency:**

```dart
test('selecting a dish completes within 1 second', () {
  final stopwatch = Stopwatch()..start();
  vm.selectDish(0);
  stopwatch.stop();
  expect(stopwatch.elapsedMilliseconds, lessThan(1000));
});
```

**Disclaimer UI:**

```dart
testWidgets('disclaimer always visible on HomeScreen', (tester) async {
  // ...setup GoRouter + HomeScreen...
  expect(find.textContaining('tham khảo'), findsOneWidget);
  expect(find.textContaining('bác sĩ'), findsOneWidget);
  expect(find.byIcon(Icons.warning_amber), findsOneWidget);
});
```

**Stability:**

```dart
test('10 select/reset cycles without crash', () {
  for (var run = 0; run < 10; run++) {
    for (var i = 0; i < PanicViewModel.commonDishes.length; i++) {
      vm.selectDish(i);
      expect(vm.isSelected, isTrue);
    }
    vm.reset();
  }
});
```

### 3.3 Chạy

```bash
cd mobile/insight_app

# Chỉ E2E tests
flutter test test/e2e/e2e_pipeline_test.dart

# Tất cả tests (40 total)
flutter test
```

---

## 4. Toàn bộ Test Suite

### 4.1 Bảng tổng hợp

| Service      | Test File                      | Tests       | Framework         |
| ------------ | ------------------------------ | ----------- | ----------------- |
| Vision       | `src/vision-service/tests/`    | 166         | pytest            |
| RAG          | `src/rag-service/tests/`       | 154         | pytest            |
| Gateway      | `src/api-gateway/src/test/`    | 15          | JUnit 5 + Mockito |
| Flutter      | `mobile/insight_app/test/`     | 40          | flutter_test      |
| E2E (Python) | `scripts/test_e2e_pipeline.py` | 4 scenarios | requests          |
| **Tổng**     |                                | **375+**    |                   |

### 4.2 Chạy từng service

```bash
# Vision (166 tests)
cd src/vision-service && python -m pytest

# RAG (154 tests)
cd src/rag-service && python -m pytest

# Gateway (15 tests)
cd src/api-gateway && ./gradlew test

# Flutter (40 tests)
cd mobile/insight_app && flutter test

# E2E (offline)
python scripts/test_e2e_pipeline.py --offline

# E2E (full — cần services chạy)
python scripts/test_e2e_pipeline.py
```

---

## 5. Chuẩn bị Full E2E Test

### 5.1 Start Services

```bash
# 1. Infrastructure
cd infra/docker && docker compose up -d
# → PostgreSQL, Redis, Kafka, Milvus

# 2. Vision Service
cd src/vision-service
source .venv/bin/activate
python main.py
# → http://localhost:8000

# 3. RAG Service
cd src/rag-service
source .venv/bin/activate
python main.py
# → http://localhost:8001

# 4. API Gateway
cd src/api-gateway
./gradlew bootRun
# → http://localhost:8080
```

### 5.2 Run Full E2E

```bash
python scripts/test_e2e_pipeline.py
```

### 5.3 Verify Health

```bash
# Each service
curl http://localhost:8080/api/health
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

## 6. Troubleshooting

| Vấn đề             | Nguyên nhân             | Giải pháp                  |
| ------------------ | ----------------------- | -------------------------- |
| Gateway 502        | Vision/RAG service down | Start backend services     |
| Timeout > 5s       | Model loading chậm      | Retry sau khi model loaded |
| Flutter test fail  | Missing dependency      | `flutter pub get`          |
| Kafka connect fail | Docker not running      | `docker compose up -d`     |
| 400 Bad Request    | Missing image field     | Kiểm tra multipart request |

---

_Cập nhật lần cuối: 06/03/2026_

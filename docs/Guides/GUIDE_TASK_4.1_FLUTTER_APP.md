# 📖 HƯỚNG DẪN CHI TIẾT TASK 4.1: FLUTTER APP

> **Assignee**: Hoàng (chính), Hoài (UI support)
> **Thời gian**: Sprint 9 (Phase 4)
> **Tiền đề**: Task 1.1 (Environment Setup ✅), Task 4.2 (API Gateway — song song)
> **Tham chiếu**: [TASK_4.1](../Tasks/TASK_4.1_FLUTTER_APP.md) | [plan.md](../plan.md)
> **Cập nhật**: 06/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 1-3 ✅  Vision + RAG services hoạt động                      │
│                                                                     │
│  ► Task 4.1  FLUTTER APP  ◄◄◄  BẠN ĐANG Ở ĐÂY                    │
│    │                                                                │
│    │  Mục tiêu: Mobile app đầy đủ UI + UX cho người tiểu đường    │
│    │  Pattern: MVVM + Provider + GoRouter                          │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Hoàng: MVVM architecture, ViewModels, API integration      │
│    │  • Hoài: UI screens, widgets, styling                         │
│    │                                                                │
│    │  ⚡ 5 SCREENS:                                                │
│    │  ① HomeScreen — Landing page + 2 action buttons              │
│    │  ② CameraScreen — Chụp ảnh / chọn từ gallery                │
│    │  ③ FoodFormScreen — Chọn loại món, size, topping             │
│    │  ④ ResultScreen — Hiển thị GL + insulin + advice             │
│    │  ⑤ PanicScreen — Ước lượng nhanh (cached, ≤1s)              │
│    │                                                                │
│    └───► Task 4.2: Gateway integration, Task 4.3: E2E testing      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Kiến trúc MVVM

```
┌──────────────────────────────────────────────────────┐
│  UI Layer (Screens + Widgets)                         │
│  ├── HomeScreen, CameraScreen, FoodFormScreen         │
│  ├── ResultScreen, PanicScreen                        │
│  └── GlIndicator, DisclaimerBanner                    │
│         │ listen via Provider.of / Consumer           │
│         ▼                                             │
│  ViewModel Layer (ChangeNotifier)                     │
│  ├── MealViewModel — analyze flow state               │
│  └── PanicViewModel — cached GL lookup                │
│         │ calls                                       │
│         ▼                                             │
│  Data Layer (Models + Services)                       │
│  ├── FoodItem, MealAnalysis, PatientContext           │
│  └── ApiService — HTTP to Gateway                    │
└──────────────────────────────────────────────────────┘
```

**Provider Setup** (`main.dart`):

```dart
MultiProvider(
  providers: [
    ChangeNotifierProvider(create: (_) => MealViewModel(apiService)),
    ChangeNotifierProvider(create: (_) => PanicViewModel()),
  ],
  child: const InsightApp(),
)
```

---

## 2. Cấu trúc thư mục

```
mobile/insight_app/
├── .env                          # GATEWAY_BASE_URL
├── pubspec.yaml                  # Dependencies
├── lib/
│   ├── main.dart                 # Entry point, .env, Provider
│   ├── app.dart                  # MaterialApp.router
│   ├── config/
│   │   └── routes.dart           # GoRouter (5 routes)
│   ├── data/
│   │   ├── models/
│   │   │   ├── food_item.dart
│   │   │   ├── meal_analysis.dart
│   │   │   └── patient_context.dart
│   │   └── services/
│   │       └── api_service.dart  # HTTP client → Gateway
│   ├── viewmodels/
│   │   ├── meal_viewmodel.dart   # Analysis flow
│   │   └── panic_viewmodel.dart  # Cached lookup
│   └── ui/
│       ├── home/home_screen.dart
│       ├── camera/camera_screen.dart
│       ├── food_form/food_form_screen.dart
│       ├── result/result_screen.dart
│       ├── panic/panic_screen.dart
│       └── widgets/
│           ├── gl_indicator.dart
│           └── disclaimer_banner.dart
└── test/
    ├── data/models_test.dart        # 9 tests
    ├── viewmodels/
    │   ├── meal_viewmodel_test.dart # 9 tests
    │   └── panic_viewmodel_test.dart# 7 tests
    ├── ui/widget_test.dart          # 8 tests
    └── e2e/e2e_pipeline_test.dart   # 7 tests
```

---

## 3. Models

### 3.1 FoodItem

```dart
class FoodItem {
  final String name;
  final double volumeMl;
  final double weightG;
  final double carbsG;
  final double confidenceScore;
}
```

- `fromJson()` / `toJson()` với type coercion (int → double)

### 3.2 MealAnalysis

```dart
class MealAnalysis {
  final String foodName;
  final double volumeMl, weightG, carbsG;
  final double glycemicLoad;
  final String glLevel;           // 'low' | 'medium' | 'high'
  final double confidence;
  final String? advice;           // RAG output
  final String? insulinSuggestion;// Insulin recommendation
  final List<String> warnings;
}
```

- Parse từ Gateway JSON response

### 3.3 PatientContext

```dart
class PatientContext {
  final double? glucoseLevel;
  final String? medicationType;
  final double? insulinCarbRatio;
  final double? correctionFactor;
  final double? targetGlucose;
}
```

- `toJson()` — gửi kèm request API

---

## 4. ViewModels

### 4.1 MealViewModel

**State:** `selectedImage`, `selectedFoodType`, `selectedSize`, `result`, `advice`, `insulinSuggestion`, `isLoading`, `error`, `patientContext`

**Flow:**

1. `setImage(File)` → chọn ảnh
2. `setFoodType()` / `setSize()` → form input
3. `analyze()` → gọi `apiService.analyzePipeline()` → set `result`
4. `reset()` → xóa state

### 4.2 PanicViewModel

**State:** `selectedDish`, `isSelected`

**Data:** 10 món Việt Nam (cached static list)

**Flow:**

1. User tap dish → `selectDish(index)` → instant result (≤1s)
2. `reset()` → back to grid

---

## 5. Screens

### 5.1 Navigation (GoRouter)

| Route        | Screen         | Mô tả           |
| ------------ | -------------- | --------------- |
| `/`          | HomeScreen     | Landing page    |
| `/camera`    | CameraScreen   | Chụp ảnh        |
| `/food-form` | FoodFormScreen | Form thông tin  |
| `/result`    | ResultScreen   | Kết quả GL      |
| `/panic`     | PanicScreen    | Ước lượng nhanh |

**Flow chính:** Home → Camera → FoodForm → Result
**Flow panic:** Home → Panic

### 5.2 HomeScreen

- Title "InSight" + biểu tượng
- Button "Chụp ảnh phân tích" → `/camera`
- Button "Ước lượng nhanh ⚡" → `/panic`
- Disclaimer text inline

### 5.3 CameraScreen

- `image_picker`: camera hoặc gallery
- Max 1920px, quality 85%
- Auto chuyển `/food-form` sau khi chọn ảnh

### 5.4 FoodFormScreen

- Preview ảnh đã chọn
- ChoiceChip: loại món (Cơm, Phở, Bún, Cháo, Bánh mì, Xôi, Miến, Mì, Khác)
- ChoiceChip: kích cỡ (Nhỏ, Vừa, Lớn)
- FilterChip: topping (Thêm rau, Thêm thịt, Nước sốt, Trứng, Đồ chua, Tương ớt)
- Button "Phân tích GL" → gọi `vm.analyze()` → `/result`

### 5.5 ResultScreen

- `GlIndicator` widget (vòng tròn lớn hiển thị GL)
- Thông tin dinh dưỡng: volume, weight, carbs, confidence
- Insulin advice card (từ RAG)
- Warnings (nếu có)
- `DisclaimerBanner`
- Button "Phân tích món mới"

### 5.6 PanicScreen

- Grid 2 cột danh sách 10 món
- Tap → hiện kết quả GL ngay lập tức
- Buttons: "Chọn món khác" / "Xong"

---

## 6. Custom Widgets

### GlIndicator

- Circle 180×180, màu theo level (green/orange/red)
- Hiển thị: số GL + label "GL" + badge level (Thấp/Trung bình/Cao)

### DisclaimerBanner

- Orange background, icon warning
- Text: "Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ."

---

## 7. API Service

```dart
class ApiService {
  final String gatewayBaseUrl;  // default: http://10.0.2.2:8080

  Future<MealAnalysis> analyzePipeline({
    required File imageFile,
    String? foodId,
    PatientContext? patient,
  });

  Future<bool> checkGatewayHealth();
}
```

- **Endpoint:** `POST /api/gateway/analyze` (multipart)
- **Fields:** image, food_id, glucose_level, diabetes_type, insulin_carb_ratio, correction_factor, target_glucose

---

## 8. Dependencies

| Package          | Version  | Mục đích         |
| ---------------- | -------- | ---------------- |
| `provider`       | ^6.1.5+1 | State management |
| `http`           | ^1.6.0   | HTTP client      |
| `image_picker`   | ^1.2.1   | Camera/gallery   |
| `flutter_dotenv` | ^6.0.0   | Load .env        |
| `go_router`      | ^17.1.0  | Navigation       |

---

## 9. Chạy & Test

```bash
# Setup
cd mobile/insight_app
flutter pub get

# Chạy app
flutter run

# Chạy test
flutter test                # All 40 tests
flutter test test/e2e/      # E2E tests only

# Lint
flutter analyze
```

---

## 10. Test Coverage

| File                                        | Tests  | Mô tả                                   |
| ------------------------------------------- | ------ | --------------------------------------- |
| `test/data/models_test.dart`                | 9      | JSON parsing, round-trip, edge cases    |
| `test/viewmodels/meal_viewmodel_test.dart`  | 9      | State flow, analyze, error handling     |
| `test/viewmodels/panic_viewmodel_test.dart` | 7      | Select/reset, listener, data validation |
| `test/ui/widget_test.dart`                  | 8      | All 5 screens + 2 widgets               |
| `test/e2e/e2e_pipeline_test.dart`           | 7      | Latency, disclaimer, stability          |
| **Tổng**                                    | **40** | Unit + Widget + E2E                     |

---

## 11. Environment

```env
# mobile/insight_app/.env
GATEWAY_BASE_URL=http://10.0.2.2:8080
```

- `10.0.2.2` = Android emulator → host machine
- Đổi thành URL thật khi deploy production

---

_Cập nhật lần cuối: 06/03/2026_

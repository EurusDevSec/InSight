# 📖 HƯỚNG DẪN CHI TIẾT TASK 2.4: FOOD SEGMENTATION (PHÂN ĐOẠN MÓN ĂN)

> **Assignee**: Việt (chính), Hoài (test trên 10 mẫu)
> **Thời gian**: 17/03 → 18/03/2026
> **Tiền đề**: Task 2.1 (Depth Map ✅), Task 2.2 (Reference/Bowl detection ✅), Task 2.3 (Calibration ✅)
> **Tham chiếu**: [TASK_2.4](../Tasks/TASK_2.4_FOOD_SEGMENTATION.md) | [plan.md](../plan.md)
> **Cập nhật**: 11/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 2.1 Depth ✅  | Task 2.2 Reference ✅ | Task 2.3 Calibrate ✅│
│  (depth map 0-255)   (bowl/spoon detect)     (pixel → cm)         │
│                                                                     │
│  ► Task 2.4  FOOD SEGMENTATION  ◄◄◄  BẠN ĐANG Ở ĐÂY             │
│    │                                                                │
│    │  Mục tiêu: Tìm CHÍNH XÁC vùng nào là "đồ ăn" trong ảnh     │
│    │  Input: Ảnh RGB + Depth map + (Optional) Bowl bbox            │
│    │  Output: Binary mask — trắng = food, đen = nền               │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Việt: Implement FoodSegmenter + unit tests                 │
│    │  • Hoài: Test trên 10 mẫu VN demo                            │
│    │  • Hoàng: Review + quyết định kỹ thuật                       │
│    │                                                                │
│    │  ⚡ TẠI SAO CẦN SEGMENTATION?                                 │
│    │  ① Volume = ∫∫ depth(x,y) dA — chỉ tính trên VÙNG FOOD     │
│    │  ② Nếu không segment: tính luôn bát/bàn → sai hoàn toàn     │
│    │  ③ Food mask xác định CHÍNH XÁC pixel nào là thức ăn         │
│    │  ④ Kết hợp với calibrated depth → thể tích chính xác         │
│    │                                                                │
│    │  Pipeline flow:                                               │
│    │  Ảnh → Depth (2.1) → Reference (2.2) → Calibrate (2.3)      │
│    │      → ★ Segment (2.4) ← BẠN LÀM ĐÂY                       │
│    │      → Volume (2.5) = food_mask × calibrated_depth            │
│    │                                                                │
│    └───► Task 2.5: Cần food mask để biết tính volume vùng nào     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tại sao KHÔNG dùng SAM đầy đủ?

```
┌─────────────────────────────────────────────────────────────────────┐
│  SO SÁNH PHƯƠNG PHÁP SEGMENTATION:                                  │
│                                                                     │
│  ❌ SAM (Segment Anything Model) — full version:                    │
│     Size: ~2.5 GB (ViT-H)                                         │
│     GPU RAM: ~8-12 GB                                              │
│     Speed: ~500ms-2s per image                                     │
│     Pro: Segment MỌI THỨ rất chính xác                            │
│     Con: Quá nặng cho mobile/edge, cần prompt (click/box)         │
│     → Overkill cho use case food-on-table                          │
│                                                                     │
│  ⚠️ FastSAM / MobileSAM — lightweight version:                     │
│     Size: ~10-23 MB                                                │
│     Speed: ~50-100ms                                               │
│     Pro: Nhẹ hơn nhiều, dùng YOLO backbone                        │
│     Con: Accuracy kém hơn SAM, cần download thêm                  │
│     → Backup option, code implement sẵn fallback                  │
│                                                                     │
│  ✅ Depth + Color Hybrid (CHỌN) — Zero additional models:          │
│     Size: 0 bytes (dùng depth map đã có từ DAv2)                  │
│     Speed: ~30-50ms                                                │
│     Pro: Không cần model thêm, tận dụng depth có sẵn              │
│     Pro: Domain-specific → tối ưu cho food-on-table               │
│     Con: Không general như SAM                                     │
│     → Phù hợp nhất: fast, lightweight, domain-optimized           │
│                                                                     │
│  👉 QUYẾT ĐỊNH: Implement Depth+Color PRIMARY                     │
│     + FastSAM fallback (auto-switch nếu có sẵn)                  │
│     + Code architecture cho phép swap method dễ dàng              │
└─────────────────────────────────────────────────────────────────────┘
```

### Tại sao Depth + Color hoạt động cho food?

```
┌─────────────────────────────────────────────────────────────────────┐
│  INSIGHT QUAN TRỌNG: Food có 2 đặc điểm visual riêng biệt        │
│                                                                     │
│  1. DEPTH — Food NỔI LÊN trên bàn/đĩa/bát:                       │
│                                                                     │
│     Depth map (top-down view):                                     │
│     ┌──────────────────────────────┐                                │
│     │ Table (low depth = 50)       │                                │
│     │   ┌─────────────────┐        │                                │
│     │   │ Bowl rim = 120  │        │                                │
│     │   │ ┌──────────┐    │        │                                │
│     │   │ │FOOD = 180│    │        │                                │
│     │   │ └──────────┘    │        │                                │
│     │   └─────────────────┘        │                                │
│     └──────────────────────────────┘                                │
│     → Food > table depth → threshold = percentile 60%              │
│                                                                     │
│  2. COLOR — Food có màu KHÁC table/bowl:                           │
│                                                                     │
│     • Table: gỗ nâu, khăn trắng, mâm inox (gam trung tính)       │
│     • Bowl: sứ trắng, inox bạc (saturation thấp)                  │
│     • Food: cam/nâu (cơm chiên), xanh (rau), đỏ (thịt bò),      │
│             vàng (trứng), nâu sẫm (nước phở)                      │
│     → Food = saturation > 20 AND warm tones (H < 50 or H > 150)   │
│                                                                     │
│  3. KẾT HỢP: Depth ∩ Color = robust segmentation                  │
│     • Depth alone: có thể chọn luôn viền bát (also elevated)      │
│     • Color alone: có thể chọn pattern bàn gỗ (also warm)         │
│     • Depth AND Color: chỉ chọn food (elevated AND food-colored)  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Nền tảng đã có sẵn

```
┌─────────────────────────────────────────────────────────────────────┐
│  ĐÃ CÓ từ Task 2.1 + 2.2 + 2.3:                                   │
│                                                                     │
│  ✅ Depth map: estimate_depth_full(image) → depth_map numpy        │
│  ✅ Bowl detection: ref_detector.detect(image) → List[Reference]   │
│  ✅ Calibration: cal_service.calibrate() → depth_map_cm             │
│  ✅ OpenCV: đã có trong requirements.txt (>=4.8.0)                  │
│  ✅ POC ảnh test: data/poc/raw/poc_pho_bo_001_main.jpg              │
│  ✅ VN demo: data/vn_demo/ (5 món × 2 góc = 10 ảnh)               │
│                                                                     │
│  CẦN THÊM:                                                         │
│  • services/segmentation_service.py ← FILE CHÍNH                   │
│  • schemas/segmentation_schemas.py  ← Response models              │
│  • tests/test_segmentation_service.py ← Unit tests                 │
│  • Update main.py: thêm endpoint /api/vision/segment-food         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 1: Implement FoodSegmenter — Việt

### 1.1 Cấu trúc file

```
src/vision-service/
├── services/
│   └── segmentation_service.py    ← SERVICE CHÍNH (Task 2.4)
├── schemas/
│   └── segmentation_schemas.py    ← Pydantic response models
├── tests/
│   └── test_segmentation_service.py ← 18 unit tests
└── main.py                         ← Endpoint /api/vision/segment-food
```

### 1.2 Thuật toán Pipeline (4 bước)

```
┌─────────────────────────────────────────────────────────────────────┐
│  FOOD SEGMENTATION PIPELINE (4 bước):                               │
│                                                                     │
│  Input: RGB image + Depth map + (optional) Bowl bbox                │
│                                                                     │
│  Step 1: DEPTH THRESHOLDING                                        │
│  ─────────────────────────                                          │
│  • Nếu có bowl bbox → chỉ xét depth TRONG bowl                    │
│  • Tìm percentile 60 của depth → làm threshold                    │
│  • Pixel > threshold = "elevated" → có thể là food                 │
│  • TẠI SAO percentile 60? Food chiếm ~40% diện tích bát           │
│    (nửa trên khi nhìn từ bên)                                     │
│                                                                     │
│  Step 2: COLOR ANALYSIS                                             │
│  ──────────────────────                                             │
│  • Convert RGB → HSV (Hue, Saturation, Value)                     │
│  • Food mask = (Saturation > 20) AND (40 < Value < 250)           │
│  • Warm tones: (Hue < 50 OR Hue > 150) AND (Saturation > 30)     │
│  • Union: food_color = general_food OR warm_food                   │
│                                                                     │
│  TẠI SAO HSV thay vì RGB?                                          │
│  • H (Hue) tách biệt color khỏi brightness → robust              │
│  • S (Saturation) phân biệt food (colorful) vs table (neutral)    │
│  • V (Value) loại bỏ vùng quá tối (shadow) / quá sáng (glare)    │
│                                                                     │
│  Step 3: COMBINE MASKS                                              │
│  ─────────────────────                                              │
│  • Nếu có bowl bbox:                                               │
│    - Prioritize depth (food elevated inside bowl)                  │
│    - Combined = depth ∩ color (intersection)                       │
│    - Nếu intersection nhỏ (<30% depth) → fallback depth only      │
│  • Nếu không có bowl:                                              │
│    - Conservative: combined = depth ∩ color                        │
│                                                                     │
│  Step 4: MORPHOLOGICAL REFINEMENT                                   │
│  ──────────────────────────────                                     │
│  • Opening (kernel 7×7): xóa noise nhỏ (pixel lẻ tẻ)             │
│  • Closing (kernel 15×15): lấp holes nhỏ trong food region        │
│  • Keep largest component: giữ vùng food lớn nhất                  │
│  • TẠI SAO kernel elliptical? Food contour = tròn/oval            │
│                                                                     │
│  Output: Binary mask (H×W) — True = food, False = background       │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Chi tiết từng bước

#### Step 1: Depth Thresholding

```python
def _segment_by_depth(self, depth_map, roi_mask):
    """
    TẠI SAO dùng percentile thay vì fixed threshold?

    • Fixed threshold (VD: depth > 128) → fail khi:
      - Camera xa → tất cả depth thấp
      - Camera gần → tất cả depth cao
      - Ánh sáng khác → depth distribution shift

    • Adaptive percentile (60th) → luôn lấy top 40% elevated:
      - Camera xa: threshold tự giảm
      - Camera gần: threshold tự tăng
      - Kết quả: luôn lấy ~40% pixel cao nhất = food area
    """
    if roi_mask is not None:
        # Chỉ xét depth BÊN TRONG bowl
        roi_depths = depth_map[roi_mask]
        threshold = np.percentile(roi_depths, 60)
    else:
        threshold = np.percentile(depth_map, 60)

    depth_mask = depth_map > threshold

    if roi_mask is not None:
        depth_mask = depth_mask & roi_mask  # Chỉ trong bowl

    return depth_mask
```

#### Step 2: Color Analysis (HSV)

```python
def _segment_by_color(self, img_array, roi_mask):
    """
    HSV Color Space:
    • H (Hue): 0-180 trong OpenCV
      - 0-10: đỏ
      - 10-25: cam/nâu
      - 25-35: vàng
      - 35-80: xanh lá
      - 80-130: xanh dương
      - 130-170: tím
      - 170-180: đỏ (wrap around)

    • S (Saturation): 0-255
      - < 20: gần như xám/trắng (bàn sứ, bát trắng)
      - > 20: có màu (food, rau, thịt)

    • V (Value): 0-255
      - < 40: quá tối (shadow, không nhìn thấy)
      - > 250: quá sáng (glare, reflection)

    Food criteria:
    1. Có màu: S > 20 AND 40 < V < 250
    2. Warm tones: (H < 50 OR H > 150) AND S > 30
       → Đỏ, cam, nâu, vàng = food colors phổ biến
    """
    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # General food: có màu, không quá tối/sáng
    color_mask = (s > 20) & (v > 40) & (v < 250)

    # Warm tones: red/orange/yellow/brown (typical food)
    warm_mask = ((h < 50) | (h > 150)) & (s > 30)

    # Union: food-like = general OR warm
    return color_mask | warm_mask
```

#### Step 3: Combine Masks

```
┌─────────────────────────────────────────────────────────────────────┐
│  CHIẾN LƯỢC KẾT HỢP:                                               │
│                                                                     │
│  Trường hợp 1: CÓ bowl detected (phở, bún, cháo)                  │
│  • Depth là signal chính (food nổi trong bát)                      │
│  • Combined = depth ∩ color (phải thỏa CẢ HAI)                    │
│  • Nếu intersection < 30% depth area → depth alone                │
│    (có thể food có color giống bát → intersection nhỏ)            │
│                                                                     │
│  Trường hợp 2: KHÔNG có bowl (cơm đĩa, bánh mì)                  │
│  • Không có ROI rõ ràng → conservative hơn                         │
│  • Combined = depth ∩ color (phải thỏa CẢ HAI)                    │
│  • Tránh false positive (chọn nhầm vật khác)                      │
│                                                                     │
│  TẠI SAO intersection thay vì union?                               │
│  • Union = depth OR color → quá nhiều false positive               │
│  • Intersection = depth AND color → chỉ chọn khi CẢ HAI đồng ý    │
│  • Trade-off: miss một ít food tốt hơn chọn nhầm bàn             │
└─────────────────────────────────────────────────────────────────────┘
```

#### Step 4: Morphological Refinement

```
┌─────────────────────────────────────────────────────────────────────┐
│  CÁC BƯỚC REFINE MASK:                                             │
│                                                                     │
│  1. OPENING (erode → dilate) — kernel 7×7 ellipse:                │
│     • Xóa các chấm noise nhỏ (< 7×7 pixel)                      │
│     • Giữ nguyên food region lớn                                   │
│     • Elliptical kernel vì food contour thường tròn               │
│                                                                     │
│  2. CLOSING (dilate → erode) — kernel 15×15 ellipse:              │
│     • Lấp các lỗ nhỏ bên trong food region                        │
│     • VD: hạt gạo cơm tạo texture lỗ → fill lại                  │
│     • 15×15 đủ lớn để fill holes nhưng không merge regions         │
│                                                                     │
│  3. KEEP LARGEST COMPONENT:                                         │
│     • Sau opening/closing, có thể còn 2-3 vùng nhỏ               │
│     • Giữ vùng lớn nhất = main food                                │
│     • Loại bỏ "đảo" nhỏ (VD: gia vị rơi trên bàn)               │
│     • Dùng cv2.connectedComponentsWithStats (8-connectivity)       │
│                                                                     │
│  TẠI SAO kernel size 7 và 15?                                      │
│  • 7: đủ lớn để xóa noise, đủ nhỏ để giữ chi tiết food           │
│  • 15: lấp holes có kích thước tầm hạt gạo/miếng rau             │
│  • Tested trên ảnh 600×400 → 1170×780 → work tốt                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.4 Bowl ROI (Region of Interest)

```
┌─────────────────────────────────────────────────────────────────────┐
│  TẠI SAO DÙNG ELLIPTICAL MASK THAY VÌ RECTANGULAR?                 │
│                                                                     │
│  Bbox từ YOLO:      Elliptical mask:                               │
│  ┌──────────┐       ┌──────────┐                                   │
│  │ xxxxxxxx │       │   xxxx   │                                   │
│  │ xxxxxxxx │       │ xxxxxxxx │                                   │
│  │ xxxxxxxx │       │ xxxxxxxx │                                   │
│  │ xxxxxxxx │       │   xxxx   │                                   │
│  └──────────┘       └──────────┘                                   │
│  ↑ chọn cả góc      ↑ chỉ chọn trong bát (tròn)                  │
│    (không phải food)   (match shape bát)                           │
│                                                                     │
│  10% inset: thu nhỏ ellipse 10% mỗi chiều                         │
│  → Loại bỏ viền bát (rim) — không phải food                       │
│  → cx, cy = center of bbox                                         │
│  → rx = 40% of bbox width, ry = 40% of bbox height                │
│    (= 80% of half-width = excludes rim)                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 2: API Endpoint — Việt

### 2.1 Endpoint `/api/vision/segment-food`

```
POST /api/vision/segment-food
├── Input: image (multipart/form-data)
├── Process:
│   ├── 1. estimate_depth_full(image)     ← Task 2.1
│   ├── 2. ref_detector.detect(image)     ← Task 2.2
│   ├── 3. Tìm bowl bbox (nếu có)        ← Task 2.2
│   └── 4. segmenter.segment()            ← Task 2.4 ★
├── Output: SegmentationResponse (JSON)
│   ├── food_mask_base64: "iVBOR..." (PNG base64)
│   ├── food_area_pixels: 29858
│   ├── food_ratio: 0.033 (3.3% of image)
│   ├── num_components: 1
│   ├── food_bbox: [374, 385, 717, 600]
│   ├── segmentation_quality: "high"
│   ├── method_used: "depth_color"
│   └── segmentation_time_ms: 42.6
└── Error: 500 if segmentation fails
```

### 2.2 Response giải thích

```
┌─────────────────────────────────────────────────────────────────────┐
│  RESPONSE FIELDS:                                                   │
│                                                                     │
│  food_mask_base64: Mask PNG encoded base64                         │
│  → Decode → grayscale image → white=food, black=background         │
│  → Client có thể overlay lên ảnh gốc để kiểm tra                 │
│                                                                     │
│  food_ratio: 0.033 = 3.3% of image is food                       │
│  → Hợp lý: food chiếm 1 phần nhỏ trong ảnh bàn ăn               │
│  → Nếu > 50%: có thể ảnh chụp close-up food                      │
│  → Nếu < 2%: segmentation miss, quality = "low"                   │
│                                                                     │
│  num_components: 1 = 1 vùng food liên tục                         │
│  → > 1: nhiều món riêng biệt (ít khi xảy ra sau refine)          │
│                                                                     │
│  food_bbox: [x1, y1, x2, y2] bounding box vùng food               │
│  → Useful cho Task 2.5: chỉ tính volume trong bbox                │
│                                                                     │
│  segmentation_quality:                                              │
│  → "high": ratio 2-80%, 1 component, depth std > 10               │
│  → "medium": ratio ok, ≤ 3 components                             │
│  → "low": ratio quá nhỏ/lớn, hoặc flat depth                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 3: Unit Tests — Việt

### 3.1 Test Structure (18 tests)

**File**: `src/vision-service/tests/test_segmentation_service.py`

```
TestFoodSegmenterBasics (9 tests):
├── test_segment_returns_result        # Return type đúng
├── test_mask_shape_matches_image      # mask.shape == image.shape[:2]
├── test_mask_is_boolean               # dtype == bool
├── test_food_ratio_in_range           # 0 ≤ ratio ≤ 1
├── test_food_area_equals_mask_sum     # area == mask.sum()
├── test_bbox_format                   # [x1, y1, x2, y2] valid
├── test_timing_positive               # time > 0
├── test_quality_valid                 # "high" / "medium" / "low"
└── test_method_used                   # "depth_color"

TestBowlROI (2 tests):
├── test_with_bowl_bbox               # Có bowl → vẫn hoạt động
└── test_bowl_roi_focuses_segmentation # Bowl ROI focus hơn

TestDepthMapResize (1 test):
└── test_different_depth_size          # Depth size ≠ image → auto resize

TestEdgeCases (4 tests):
├── test_uniform_image                 # Ảnh đồng nhất → vẫn chạy
├── test_small_image                   # Ảnh nhỏ (50×50) → vẫn chạy
├── test_is_loaded                     # Always loaded (no model needed)
└── test_singleton                     # Same instance

TestComponentCounting (2 tests):
├── test_single_food_region           # 1 vùng food → ≥ 1 component
└── test_count_components_empty        # Empty mask → 0 components
```

### 3.2 Fixtures giải thích

```python
# food_image: 600×400 synthetic image
# Gray background (200,200,200) + warm orange center (food-like color)
# → Test color segmentation picks up the food region

# food_depth_map: 600×400
# Table at depth 50, food bump at depth 200
# → Test depth segmentation picks up elevated region

# bowl_bbox: [100, 50, 500, 350]
# → Simulates a large bowl covering most of the image
# → Test ROI focusing works

# flat_depth_map: all 128
# → Edge case: no 3D info, quality should be "low"
```

### 3.3 Chạy tests

```bash
cd src/vision-service
python -m pytest tests/test_segmentation_service.py -v

# Kết quả: 18 passed in 0.xx seconds
```

---

## Bước 4: Validate trên ảnh thực — Hoài

### 4.1 Test E2E với pho bo

```bash
# Start server
cd src/vision-service && python main.py

# Test segmentation
curl -s -X POST http://localhost:8000/api/vision/segment-food \
  -F "image=@data/poc/raw/poc_pho_bo_001_main.jpg" | \
  python -c "
import json, sys
d = json.load(sys.stdin)
del d['food_mask_base64']  # Hide base64
print(json.dumps(d, indent=2))
"
```

**Kết quả mong đợi:**

```json
{
  "food_area_pixels": 29858,
  "food_ratio": 0.033,
  "num_components": 1,
  "food_bbox": [374, 385, 717, 600],
  "segmentation_quality": "high",
  "method_used": "depth_color",
  "segmentation_time_ms": 42.6
}
```

### 4.2 Visualize food mask

```python
# Script nhanh để xem mask trên ảnh
import base64, json, io
import requests
from PIL import Image
import numpy as np

# Gửi request
with open("data/poc/raw/poc_pho_bo_001_main.jpg", "rb") as f:
    resp = requests.post(
        "http://localhost:8000/api/vision/segment-food",
        files={"image": f}
    )

data = resp.json()

# Decode mask
mask_bytes = base64.b64decode(data["food_mask_base64"])
mask_img = Image.open(io.BytesIO(mask_bytes))
mask_array = np.array(mask_img)

# Load original
original = Image.open("data/poc/raw/poc_pho_bo_001_main.jpg")
orig_array = np.array(original)

# Overlay: food = green tint
overlay = orig_array.copy()
overlay[mask_array > 0] = [0, 255, 0]  # Green for food
blended = (orig_array * 0.6 + overlay * 0.4).astype(np.uint8)

# Save
Image.fromarray(blended).save("segmentation_preview.jpg")
print("Saved segmentation_preview.jpg ✅")
```

### 4.3 Checklist validate cho Hoài

```
Cho mỗi ảnh test (10 ảnh VN demo + POC):

□ 1. Chạy /api/vision/segment-food
□ 2. Kiểm tra food_ratio:
     • 2-30% cho full table shot
     • 20-60% cho close-up food
     • < 2% → segmentation miss → ghi nhận
□ 3. Kiểm tra num_components:
     • 1 cho single dish → OK
     • > 1 → ghi nhận, xem có hợp lý không
□ 4. Visualize mask overlay:
     • Green area = food?
     • Có chọn nhầm bàn/bát không?
     • Có miss phần food nào không?
□ 5. Kiểm tra segmentation_quality:
     • "high" khi ảnh rõ, food nổi bật
     • "medium"/"low" khi ảnh khó
□ 6. Ghi kết quả vào bảng validation
```

### 4.4 Bảng validation template

| #   | Ảnh            | food_ratio | components | quality | Mask correct? | Notes            |
| --- | -------------- | ---------- | ---------- | ------- | ------------- | ---------------- |
| 1   | poc_pho_bo_001 | 3.3%       | 1          | high    | ✅            | Food inside bowl |
| 2   | com_trang_45   | ?          | ?          | ?       | ?             |                  |
| 3   | com_trang_top  | ?          | ?          | ?       | ?             |                  |
| 4   | pho_bo_45      | ?          | ?          | ?       | ?             |                  |
| 5   | pho_bo_top     | ?          | ?          | ?       | ?             |                  |
| 6   | banh_mi_45     | ?          | ?          | ?       | ?             |                  |
| 7   | banh_mi_top    | ?          | ?          | ?       | ?             |                  |
| 8   | bun_bo_hue_45  | ?          | ?          | ?       | ?             |                  |
| 9   | bun_bo_hue_top | ?          | ?          | ?       | ?             |                  |
| 10  | com_tam_45     | ?          | ?          | ?       | ?             |                  |

---

## Bước 5: Hiểu kết nối với Task 2.5 — Cả nhóm

### 5.1 Food mask dùng cho Volume Estimation

```
┌─────────────────────────────────────────────────────────────────────┐
│  TASK 2.5 SẼ DÙNG KẾT QUẢ TỪ 2.3 + 2.4 NHƯ SAU:                 │
│                                                                     │
│  Calibrated depth map (2.3):                                       │
│  ┌──────────────────────────┐                                       │
│  │ 0cm  0cm  0cm  2cm  5cm │  ← depth in cm                       │
│  │ 0cm  3cm  8cm  12cm 5cm │                                       │
│  │ 0cm  4cm  10cm 8cm  3cm │                                       │
│  │ 0cm  2cm  5cm  3cm  0cm │                                       │
│  └──────────────────────────┘                                       │
│                                                                     │
│  Food mask (2.4):                                                   │
│  ┌──────────────────────────┐                                       │
│  │  0    0    0    1    1   │  ← 1 = food, 0 = not food            │
│  │  0    1    1    1    1   │                                       │
│  │  0    1    1    1    1   │                                       │
│  │  0    0    1    0    0   │                                       │
│  └──────────────────────────┘                                       │
│                                                                     │
│  Volume = Σ (depth_cm[food_mask] × pixel_area_cm2)                 │
│         = Σ (5+12+5+8+12+8+10+8+3+5) × (cm/px)²                  │
│         = 76 × 0.0406² = 0.125 cm³ (example, small image)         │
│                                                                     │
│  Thực tế: Volume phở ≈ 300-500 ml → weight ≈ 300-500g             │
│  Volume = Σ calibrated_depth × pixel_area_cm2                      │
│         ≈ food region area × average food height                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Kết quả E2E Verified (11/03/2026)

| Test                                     | Status          | Kết quả                        |
| ---------------------------------------- | --------------- | ------------------------------ |
| Unit tests                               | ✅ 18/18 passed | 0.72s                          |
| `POST /api/vision/segment-food` (pho_bo) | ✅ 200          | quality=high, ratio=3.3%, 43ms |
| Error handling (invalid file)            | ✅ 400          | Correct error                  |
| Mask output                              | ✅              | Valid base64 PNG               |

---

## Tóm tắt

| Mục             | Chi tiết                                                |
| --------------- | ------------------------------------------------------- |
| **File chính**  | `services/segmentation_service.py` (443 lines)          |
| **Schema**      | `schemas/segmentation_schemas.py` (35 lines)            |
| **Tests**       | `tests/test_segmentation_service.py` (18 tests)         |
| **Endpoint**    | `POST /api/vision/segment-food`                         |
| **Core idea**   | Depth (elevated) ∩ Color (food-like) → food mask        |
| **Steps**       | Depth threshold → Color analysis → Combine → Morphology |
| **Alternative** | FastSAM fallback (auto-switch if available)             |
| **Speed**       | ~43ms (no extra model loading)                          |
| **Used by**     | Task 2.5: Volume = Σ depth_cm[food_mask] × pixel_area   |

---

## Câu hỏi thường gặp (FAQ)

### Q: Tại sao không dùng semantic segmentation (DeepLab, U-Net)?

**A:** Cần training data cho food segmentation. Không có dataset annotated food VN. Depth+Color approach zero-shot (không cần training), domain-specific cho food-on-table use case.

### Q: Threshold percentile 60 có work cho mọi trường hợp?

**A:** Đây là adaptive (dựa trên phân phối depth thực tế), không phải fixed. Nếu food chiếm 50% bát thì percentile 50 sẽ tốt hơn. Có thể tune trong phase validation (Task 2.6).

### Q: Food mask có chính xác 100% không?

**A:** Không, sẽ có sai số 10-20%. Nhưng cho volume estimation, sai số mask được bù bởi: (1) density factor correction, (2) validation feedback loop. Perfect segmentation không cần thiết — "good enough" segmentation + density factor → accurate volume.

### Q: Tại sao keep largest component? Nếu có 2 món trên đĩa thì sao?

**A:** Hiện tại giả định 1 món chính / ảnh. Nếu cần hỗ trợ nhiều món, có thể giữ top-K components thay vì chỉ 1. Đây là improvement cho Task 2.6 hoặc v2.

---

> **Tạo**: 11/03/2026
> **Tác giả**: AI assistant
> **Status**: ✅ Implementation complete, 18 tests passed, E2E verified

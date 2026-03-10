# 📖 HƯỚNG DẪN CHI TIẾT TASK 2.2: NHẬN DIỆN VẬT THAM CHIẾU (REFERENCE OBJECT)

> **Assignee**: Việt (train + integrate), Hoài (annotate dataset), Hoàng (review + hướng dẫn)
> **Thời gian**: 14/03 → 15/03/2026
> **Tiền đề**: Task 2.1 (Depth Estimation ✅ — service chạy, có depth map), Task 1.3 (VN demo samples có JSON + ảnh)
> **Tham chiếu**: [TASK_2.2](../Tasks/TASK_2.2_REFERENCE_OBJECT.md) | [plan.md](../plan.md)
> **Cập nhật**: 10/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 2.1  Depth Estimation ✅                                      │
│  (Depth Anything V2 service running, depth map output)              │
│                                                                     │
│  ► Task 2.2  NHẬN DIỆN VẬT THAM CHIẾU  ◄◄◄  BẠN ĐANG Ở ĐÂY     │
│    │                                                                │
│    │  Mục tiêu: YOLO nhận diện bát/thìa/đũa → scale factor        │
│    │  Input: Ảnh 2D → Output: Bounding box + loại dụng cụ         │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Hoài: Tạo dataset annotated (≥ 200 ảnh, bounding box)     │
│    │  • Việt: Train/fine-tune YOLO + integrate vào pipeline       │
│    │  • Hoàng: Review + quyết định kỹ thuật                       │
│    │                                                                │
│    │  ⚡ TẠI SAO CẦN VẬT THAM CHIẾU?                              │
│    │  ① Depth map chỉ cho relative depth (tương đối)              │
│    │  ② Cần biết kích thước THỰC (cm) → cần 1 vật đã biết size   │
│    │  ③ Bát/thìa/đũa VN = vật tham chiếu tự nhiên (không kỳ quặc)│
│    │  ④ So với đặt thẻ ATM/đồng xu → user-friendly hơn nhiều     │
│    │                                                                │
│    │  Pipeline hoàn chỉnh:                                         │
│    │  Ảnh → Depth Map (2.1) → Detect bát/thìa (2.2)              │
│    │      → Calibrate pixel→cm (2.3) → Segment food (2.4)         │
│    │      → Tính volume (2.5) → Validate (2.6)                    │
│    │                                                                │
│    └───► Task 2.3: Pixel-to-Real cần biết loại + vị trí dụng cụ   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tại sao chọn cách tiếp cận này?

```
┌─────────────────────────────────────────────────────────────────────┐
│  SO SÁNH CÁC PHƯƠNG PHÁP XÁC ĐỊNH KÍCH THƯỚC:                     │
│                                                                     │
│  ❌ Đặt thẻ ATM / đồng xu:                                         │
│     - Kỳ quặc khi đi ăn ngoài                                     │
│     - User phải nhớ mang theo                                      │
│     - Không tự nhiên → giảm adoption                               │
│                                                                     │
│  ❌ Camera intrinsics (focal length):                                │
│     - Mỗi điện thoại khác nhau                                    │
│     - Cần calibration cho từng thiết bị                            │
│     - Không reliable                                                │
│                                                                     │
│  ✅ Nhận diện bát/thìa/đũa tự động (CHỌN):                        │
│     - Bát/thìa/đũa luôn CÓ SẴN trên bàn ăn VN                   │
│     - User không cần làm gì thêm                                  │
│     - Kích thước bát/thìa VN tương đối chuẩn                      │
│     - YOLO inference rất nhanh (~10-30ms)                          │
│                                                                     │
│  ✅ Fallback: Nếu không detect được → hỏi user chọn loại bát      │
└─────────────────────────────────────────────────────────────────────┘
```

### Kích thước chuẩn dụng cụ ăn VN

| Dụng cụ | Kích thước tiêu chuẩn | Nguồn | Ghi chú |
|---------|----------------------|-------|---------|
| **Bát cơm (S)** | ∅ 11-12 cm, cao 5-6 cm | Khảo sát thị trường VN | Bát cơm phổ thông |
| **Bát phở (M)** | ∅ 18-20 cm, cao 7-8 cm | Khảo sát thị trường VN | Tô phở tiêu chuẩn |
| **Bát phở (L)** | ∅ 22-24 cm, cao 8-9 cm | Khảo sát thị trường VN | Tô phở đặc biệt |
| **Đĩa cơm** | ∅ 20-22 cm | Khảo sát thị trường VN | Đĩa cơm tấm/bình dân |
| **Thìa inox** | Dài 15-17 cm, rộng 4 cm | Tiêu chuẩn VN | Thìa ăn canh |
| **Đũa tre/gỗ** | Dài 24-25 cm | Tiêu chuẩn VN | Đũa tre phổ thông |

---

## Bước 1: Tạo Dataset Huấn luyện — Hoài (2-3 giờ)

### 1.1 Chiến lược thu thập ảnh

```
┌─────────────────────────────────────────────────────────────────────┐
│  CHIẾN LƯỢC DATASET THỰC TẾ (target ≥ 200 ảnh):                    │
│                                                                     │
│  Tầng 1: Ảnh tự chụp (50-80 ảnh) — 1-2 giờ                       │
│  • Chụp bát/thìa/đũa trong nhiều bối cảnh ăn uống                │
│  • Đa dạng: góc chụp, ánh sáng, nền, loại dụng cụ                │
│  • Kết hợp luôn với Task 1.3.5 (chụp món VN demo)                │
│                                                                     │
│  Tầng 2: Open-source datasets (100-150 ảnh) — 30 phút             │
│  • Open Images V7 (Google) — categories: "Bowl", "Chopsticks"     │
│  • COCO dataset — categories: "bowl", "spoon", "knife"            │
│  • Roboflow Universe — search "asian tableware", "bowl detection"  │
│                                                                     │
│  Tầng 3: Augmentation (tăng 2-3x) — tự động                       │
│  • Flip, rotate, brightness, crop, scale                           │
│  • YOLO hỗ trợ augmentation khi training                          │
│                                                                     │
│  TỔNG: (80 + 120) × 2 (augment) = ~400 ảnh hiệu quả              │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Classes cần annotate

```yaml
# Định nghĩa classes cho YOLO
classes:
  0: bat_com      # Bát cơm nhỏ (∅ 11-12cm)
  1: bat_pho_m    # Bát/Tô phở M (∅ 18-20cm)
  2: bat_pho_l    # Bát/Tô phở L (∅ 22-24cm)
  3: dia_com      # Đĩa cơm (∅ 20-22cm)
  4: thia         # Thìa inox (15-17cm)
  5: dua          # Đũa tre/gỗ (24-25cm)
```

### 1.3 Hướng dẫn chụp ảnh cho dataset

```
Cho mỗi bối cảnh chụp:
□ 1. Đặt dụng cụ ăn trên bàn (tự nhiên, có món ăn hoặc không)
□ 2. Chụp 3-4 góc:
     - Top-down (nhìn thẳng)
     - 45 độ (góc ăn bình thường)
     - Nghiêng nhẹ (30 độ)
     - Gần (close-up nếu có nhiều dụng cụ)
□ 3. Đa dạng hóa:
     - Nhiều loại bát (sứ trắng, sứ in hoa, nhựa, inox)
     - Nhiều nền (bàn gỗ, khăn trải, mâm inox)
     - Ánh sáng: trong nhà, ngoài trời, đèn vàng
□ 4. Combo chụp kèm món ăn (kết hợp Task 1.3.5):
     - Bát phở + thìa + đũa (combo phổ biến)
     - Đĩa cơm + thìa
     - Bát cơm + đũa
```

### 1.4 Tool annotate bounding box

```
┌─────────────────────────────────────────────────────────────────────┐
│  TOOLS ANNOTATE (chọn 1):                                           │
│                                                                     │
│  ✅ Roboflow (khuyên dùng — Hoài):                                 │
│     - Web-based, không cần cài đặt                                │
│     - Free tier: 10,000 images                                     │
│     - Hỗ trợ export YOLO format trực tiếp                         │
│     - URL: https://app.roboflow.com                                │
│     - Workflow: Upload ảnh → Vẽ bbox → Label class → Export       │
│                                                                     │
│  Label Studio (alternative):                                        │
│     - Self-hosted, nhiều tính năng                                 │
│     - pip install label-studio → label-studio start                │
│     - Export YOLO format                                           │
│                                                                     │
│  CVAT (alternative):                                                │
│     - Docker-based, team collaboration                             │
│     - Nặng hơn, phù hợp dự án lớn                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.5 Export format YOLO

```
data/poc/annotations/
├── dataset.yaml              ← YOLO dataset config
├── images/
│   ├── train/                ← 80% ảnh training
│   │   ├── img_001.jpg
│   │   ├── img_002.jpg
│   │   └── ...
│   └── val/                  ← 20% ảnh validation
│       ├── img_201.jpg
│       └── ...
└── labels/
    ├── train/                ← YOLO labels (1 file/ảnh)
    │   ├── img_001.txt       ← "0 0.45 0.52 0.30 0.25"
    │   ├── img_002.txt       ←  class cx cy w h (normalized)
    │   └── ...
    └── val/
        ├── img_201.txt
        └── ...
```

**File `dataset.yaml`:**

```yaml
# data/poc/annotations/dataset.yaml
# YOLO dataset configuration for Vietnamese tableware detection

path: ../../data/poc/annotations  # Dataset root dir
train: images/train               # Train images (relative to path)
val: images/val                   # Val images (relative to path)

# Classes
names:
  0: bat_com
  1: bat_pho_m
  2: bat_pho_l
  3: dia_com
  4: thia
  5: dua

# Number of classes
nc: 6
```

**YOLO label format (mỗi file .txt):**

```
# class_id center_x center_y width height (normalized 0-1)
# Ví dụ: bát phở M ở giữa ảnh, chiếm ~40% width, ~35% height
1 0.50 0.48 0.40 0.35
# Thìa ở góc phải dưới
4 0.78 0.72 0.15 0.05
```

---

## Bước 2: Train/Fine-tune YOLO — Việt (2-3 giờ)

### 2.1 Chọn YOLO variant

```
┌─────────────────────────────────────────────────────────────────────┐
│  YOLO VARIANT SELECTION:                                             │
│                                                                     │
│  Model      | Params | Speed (GPU) | mAP   | Phù hợp              │
│  ──────────────────────────────────────────────────────────────────  │
│  YOLOv8n    | 3.2M   | ~2ms        | 37.3  | Mobile/Edge           │
│  YOLOv8s    | 11.2M  | ~4ms        | 44.9  | ✅ Cân bằng          │
│  YOLOv8m    | 25.9M  | ~8ms        | 50.2  | Server deploy         │
│                                                                     │
│  ✅ CHỌN: YOLOv8s (small) — fine-tune từ pretrained COCO          │
│                                                                     │
│  LÝ DO:                                                             │
│  • YOLOv8s đã pretrained trên COCO (có "bowl", "spoon")          │
│  • Fine-tune thêm classes VN → nhanh, accuracy cao                │
│  • Đủ nhẹ để chạy trên mobile (ONNX export)                      │
│  • Inference ~4ms trên GPU → không bottleneck pipeline            │
│                                                                     │
│  ALTERNATIVE: Nếu không đủ thời gian train                        │
│  → Dùng YOLOv8 pretrained COCO (có "bowl", "spoon" sẵn)          │
│  → Chỉ cần mapping class + thêm size lookup                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Cài đặt Ultralytics

```bash
# Cài YOLO (ultralytics)
pip install ultralytics>=8.0.0

# Verify
yolo version
# Kỳ vọng: Ultralytics YOLOv8.x.x
```

### 2.3 Script training

```python
# scripts/train_reference_detector.py
"""
Train YOLOv8 để nhận diện dụng cụ ăn VN (bát/thìa/đũa).
Fine-tune từ YOLOv8s pretrained trên COCO.

Chạy: python scripts/train_reference_detector.py
"""

from pathlib import Path
from ultralytics import YOLO


def train_reference_detector(
    dataset_yaml: str = "data/poc/annotations/dataset.yaml",
    model_variant: str = "yolov8s.pt",  # Pretrained COCO
    epochs: int = 100,
    img_size: int = 640,
    batch_size: int = 16,
    project: str = "runs/reference_detector",
    name: str = "v1",
):
    """
    Fine-tune YOLOv8 cho nhận diện dụng cụ ăn VN.
    
    Pretrained YOLOv8s đã biết detect "bowl" (COCO class 45) 
    và "spoon" (COCO class 44). Fine-tune thêm classes VN cụ thể.
    """
    print(f"🔄 Loading pretrained model: {model_variant}")
    model = YOLO(model_variant)

    print(f"🏋️ Starting training...")
    print(f"   Dataset: {dataset_yaml}")
    print(f"   Epochs: {epochs}")
    print(f"   Image size: {img_size}")
    print(f"   Batch size: {batch_size}")

    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        project=project,
        name=name,
        # Augmentation settings
        hsv_h=0.015,       # Hue augmentation
        hsv_s=0.7,         # Saturation augmentation
        hsv_v=0.4,         # Value augmentation
        degrees=10.0,      # Rotation
        translate=0.1,     # Translation
        scale=0.5,         # Scale augmentation
        fliplr=0.5,        # Horizontal flip
        mosaic=1.0,        # Mosaic augmentation
        # Training params
        patience=20,       # Early stopping patience
        save=True,
        save_period=10,    # Save checkpoint every 10 epochs
        val=True,
        plots=True,        # Generate training plots
        verbose=True,
    )

    # Best model path
    best_model = Path(project) / name / "weights" / "best.pt"
    print(f"\n✅ Training complete!")
    print(f"   Best model: {best_model}")
    print(f"   mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"   mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")

    return best_model


def evaluate_model(model_path: str, dataset_yaml: str):
    """Evaluate trained model trên validation set."""
    model = YOLO(model_path)
    results = model.val(data=dataset_yaml)
    
    print(f"\n📊 Evaluation Results:")
    print(f"   mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"   mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    print(f"   Precision: {results.results_dict.get('metrics/precision(B)', 'N/A')}")
    print(f"   Recall: {results.results_dict.get('metrics/recall(B)', 'N/A')}")

    return results


if __name__ == "__main__":
    best_model = train_reference_detector()
    evaluate_model(str(best_model), "data/poc/annotations/dataset.yaml")
```

### 2.4 Quick-start alternative: Dùng pretrained COCO

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚡ NẾU KHÔNG ĐỦ THỜI GIAN TRAIN (Plan B):                        │
│                                                                     │
│  YOLOv8 pretrained COCO đã nhận diện được:                        │
│  • Class 45: "bowl"  → mapping → bat_com / bat_pho                │
│  • Class 44: "spoon" → mapping → thia                             │
│  • Class 43: "fork"  → bỏ qua (ít dùng ở VN)                    │
│  • Class 42: "knife" → bỏ qua                                    │
│                                                                     │
│  → Dùng pretrained + heuristic phân loại size:                     │
│  - bowl bbox width < 15% image width → bát cơm nhỏ               │
│  - bowl bbox width 15-25% → bát/tô phở M                         │
│  - bowl bbox width > 25% → tô phở L                              │
│                                                                     │
│  Ưu điểm: Không cần annotate + train (tiết kiệm 4-5 giờ)         │
│  Nhược điểm: Không detect đũa, accuracy thấp hơn                  │
│                                                                     │
│  → Chọn Plan A (train) nếu Hoài annotate xong kịp                │
│  → Chọn Plan B (pretrained) nếu thiếu thời gian                  │
└─────────────────────────────────────────────────────────────────────┘
```

```python
# scripts/reference_detector_pretrained.py
"""
Plan B: Dùng YOLOv8 pretrained COCO để detect bowl/spoon.
Không cần training, chỉ cần mapping class.
"""

from ultralytics import YOLO
from PIL import Image


# COCO class mapping
COCO_REFERENCE_CLASSES = {
    45: {"name": "bowl", "vn_name": "Bát", "default_diameter_cm": 18.0},
    44: {"name": "spoon", "vn_name": "Thìa", "default_length_cm": 16.0},
}

# Size heuristic based on bbox width ratio
BOWL_SIZE_MAPPING = {
    "small": {"max_ratio": 0.20, "name": "bat_com", "diameter_cm": 11.5},
    "medium": {"max_ratio": 0.30, "name": "bat_pho_m", "diameter_cm": 19.0},
    "large": {"max_ratio": 1.00, "name": "bat_pho_l", "diameter_cm": 23.0},
}


def detect_reference_objects(image_path: str, confidence: float = 0.5):
    """
    Detect reference objects (bowls, spoons) using pretrained YOLOv8.
    
    Returns: list of detected reference objects with estimated real sizes.
    """
    model = YOLO("yolov8s.pt")  # Pretrained COCO
    
    results = model(image_path, conf=confidence)
    
    detections = []
    img = Image.open(image_path)
    img_width = img.size[0]
    
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            
            if cls_id not in COCO_REFERENCE_CLASSES:
                continue
            
            ref_info = COCO_REFERENCE_CLASSES[cls_id]
            bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            bbox_width = bbox[2] - bbox[0]
            width_ratio = bbox_width / img_width
            conf = float(box.conf[0])
            
            # Determine bowl size
            detected_type = ref_info["name"]
            real_size_cm = ref_info.get("default_diameter_cm", ref_info.get("default_length_cm"))
            
            if cls_id == 45:  # Bowl - classify by size
                for size_key, size_info in BOWL_SIZE_MAPPING.items():
                    if width_ratio <= size_info["max_ratio"]:
                        detected_type = size_info["name"]
                        real_size_cm = size_info["diameter_cm"]
                        break
            
            detections.append({
                "class": detected_type,
                "confidence": conf,
                "bbox": bbox,
                "bbox_width_px": bbox_width,
                "width_ratio": width_ratio,
                "real_size_cm": real_size_cm,
            })
    
    return detections


if __name__ == "__main__":
    import sys
    image_path = sys.argv[1] if len(sys.argv) > 1 else "data/poc/raw/poc_pho_bo_001_main.jpg"
    
    detections = detect_reference_objects(image_path)
    
    print(f"\n📊 Detected {len(detections)} reference objects:")
    for det in detections:
        print(f"  - {det['class']}: {det['confidence']:.2f} conf, "
              f"real size ~{det['real_size_cm']} cm, "
              f"bbox width ratio: {det['width_ratio']:.2f}")
```

---

## Bước 3: Integrate vào Vision Pipeline — Việt (1.5 giờ)

### 3.1 Reference Object Service

```python
# src/vision-service/services/reference_service.py
"""
Reference object detection service.
Nhận diện bát/thìa/đũa trong ảnh và trả về kích thước thực.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

logger = logging.getLogger(__name__)


@dataclass
class ReferenceObject:
    """Detected reference object with real-world dimensions."""
    class_name: str        # "bat_com", "bat_pho_m", "thia", "dua"
    confidence: float      # Detection confidence (0-1)
    bbox: List[float]      # [x1, y1, x2, y2] in pixels
    bbox_width_px: float   # Bounding box width in pixels  
    bbox_height_px: float  # Bounding box height in pixels
    real_width_cm: float   # Known real-world width/diameter (cm)
    real_height_cm: float  # Known real-world height (cm)
    pixels_per_cm: float   # Calculated scale factor


# Kích thước thực tế dụng cụ ăn VN (from market survey)
REFERENCE_DIMENSIONS = {
    "bat_com": {"width_cm": 11.5, "height_cm": 5.5, "description": "Bát cơm nhỏ"},
    "bat_pho_m": {"width_cm": 19.0, "height_cm": 7.5, "description": "Tô phở M"},
    "bat_pho_l": {"width_cm": 23.0, "height_cm": 8.5, "description": "Tô phở L"},
    "dia_com": {"width_cm": 21.0, "height_cm": 2.5, "description": "Đĩa cơm"},
    "thia": {"width_cm": 4.0, "height_cm": 16.0, "description": "Thìa inox"},
    "dua": {"width_cm": 0.5, "height_cm": 24.5, "description": "Đũa tre"},
}


class ReferenceDetector:
    """YOLO-based reference object detector."""

    def __init__(self, model_path: Optional[str] = None, confidence: float = 0.5):
        """
        Initialize detector.
        
        Args:
            model_path: Path to custom trained model. 
                        None = use pretrained COCO (Plan B).
            confidence: Minimum detection confidence.
        """
        self.confidence = confidence
        self.model_path = model_path
        self.model = None
        self._loaded = False

    def load(self) -> None:
        """Load YOLO model."""
        if self._loaded:
            return

        if self.model_path and Path(self.model_path).exists():
            logger.info(f"🔄 Loading custom YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
        else:
            logger.info("🔄 Loading pretrained YOLOv8s (COCO)...")
            self.model = YOLO("yolov8s.pt")
        
        self._loaded = True
        logger.info("✅ Reference detector loaded!")

    def detect(self, image: Image.Image) -> List[ReferenceObject]:
        """
        Detect reference objects in image.
        
        Args:
            image: PIL Image (RGB)
            
        Returns:
            List of ReferenceObject with real-world dimensions.
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        img_width, img_height = image.size
        results = self.model(image, conf=self.confidence, verbose=False)

        detections = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names[cls_id]
                conf = float(box.conf[0])
                bbox = box.xyxy[0].tolist()

                # Map detected class to reference dimensions
                ref_type = self._map_class(cls_name, bbox, img_width)
                if ref_type is None:
                    continue

                dims = REFERENCE_DIMENSIONS[ref_type]
                bbox_w = bbox[2] - bbox[0]
                bbox_h = bbox[3] - bbox[1]

                # Calculate pixels_per_cm (scale factor)
                # Dùng width (diameter) cho bát/đĩa, height (length) cho thìa/đũa
                if ref_type in ("thia", "dua"):
                    pixels_per_cm = bbox_h / dims["height_cm"]
                else:
                    pixels_per_cm = bbox_w / dims["width_cm"]

                detections.append(ReferenceObject(
                    class_name=ref_type,
                    confidence=conf,
                    bbox=bbox,
                    bbox_width_px=bbox_w,
                    bbox_height_px=bbox_h,
                    real_width_cm=dims["width_cm"],
                    real_height_cm=dims["height_cm"],
                    pixels_per_cm=pixels_per_cm,
                ))

        # Sort by confidence (cao nhất trước)
        detections.sort(key=lambda d: d.confidence, reverse=True)
        
        logger.info(f"📦 Detected {len(detections)} reference objects: "
                     f"{[d.class_name for d in detections]}")

        return detections

    def _map_class(self, cls_name: str, bbox: List[float], img_width: float) -> Optional[str]:
        """
        Map YOLO class name to InSight reference type.
        
        Nếu dùng custom model: class name trực tiếp.
        Nếu dùng pretrained COCO: mapping + heuristic.
        """
        # Custom model classes (trùng tên REFERENCE_DIMENSIONS)
        if cls_name in REFERENCE_DIMENSIONS:
            return cls_name

        # COCO pretrained mapping
        if cls_name == "bowl":
            bbox_w = bbox[2] - bbox[0]
            ratio = bbox_w / img_width
            if ratio < 0.20:
                return "bat_com"
            elif ratio < 0.30:
                return "bat_pho_m"
            else:
                return "bat_pho_l"
        
        if cls_name == "spoon":
            return "thia"

        return None  # Không phải reference object

    def get_best_scale_factor(self, detections: List[ReferenceObject]) -> Optional[float]:
        """
        Lấy scale factor tốt nhất từ các detected objects.
        Ưu tiên: bát (diện tích lớn, stable) > thìa > đũa
        """
        if not detections:
            return None

        # Priority order
        priority = {"bat_pho_m": 1, "bat_pho_l": 2, "bat_com": 3, 
                     "dia_com": 4, "thia": 5, "dua": 6}
        
        best = min(detections, key=lambda d: priority.get(d.class_name, 99))
        return best.pixels_per_cm

    @property 
    def is_loaded(self) -> bool:
        return self._loaded
```

### 3.2 Thêm API endpoint

```python
# Thêm vào src/vision-service/main.py

from services.reference_service import ReferenceDetector, ReferenceObject
from schemas.reference_schemas import ReferenceDetectionResponse, DetectedObject

# Initialize detector trong lifespan
ref_detector = ReferenceDetector(
    model_path="runs/reference_detector/v1/weights/best.pt",  # Custom model
    # model_path=None,  # Fallback: pretrained COCO
)

# Thêm load() trong lifespan startup:
# ref_detector.load()


@app.post("/api/vision/detect-reference", response_model=ReferenceDetectionResponse)
async def detect_reference(image: UploadFile = File(...)):
    """
    Detect reference objects (bowls, spoons, chopsticks) in food image.
    Returns bounding boxes + real-world dimensions for calibration.
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        detections = ref_detector.detect(pil_image)
        scale_factor = ref_detector.get_best_scale_factor(detections)
        
        return ReferenceDetectionResponse(
            objects=[
                DetectedObject(
                    class_name=d.class_name,
                    confidence=d.confidence,
                    bbox=d.bbox,
                    real_width_cm=d.real_width_cm,
                    real_height_cm=d.real_height_cm,
                    pixels_per_cm=d.pixels_per_cm,
                )
                for d in detections
            ],
            best_scale_factor=scale_factor,
            total_detected=len(detections),
        )
    except Exception as e:
        logger.error(f"Reference detection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.3 Response schemas

```python
# src/vision-service/schemas/reference_schemas.py
"""Pydantic schemas cho Reference Object Detection API."""

from pydantic import BaseModel, Field
from typing import List, Optional


class DetectedObject(BaseModel):
    """Thông tin 1 reference object được detect."""
    class_name: str = Field(..., description="Loại dụng cụ: bat_com, bat_pho_m, etc.")
    confidence: float = Field(..., description="Detection confidence (0-1)")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2] in pixels")
    real_width_cm: float = Field(..., description="Kích thước thực (chiều rộng/đường kính)")
    real_height_cm: float = Field(..., description="Kích thước thực (chiều cao/chiều dài)")
    pixels_per_cm: float = Field(..., description="Scale factor: pixels per centimeter")


class ReferenceDetectionResponse(BaseModel):
    """Response từ reference detection endpoint."""
    objects: List[DetectedObject] = Field(default_factory=list)
    best_scale_factor: Optional[float] = Field(None, description="Best pixels_per_cm from detected objects")
    total_detected: int = Field(0, description="Số lượng reference objects detected")
```

### 3.4 Sơ đồ pipeline tích hợp

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Vision Pipeline (sau Task 2.1 + 2.2)             │
│                                                                     │
│  Ảnh input (RGB)                                                    │
│    │                                                                │
│    ├──► POST /api/vision/depth                                     │
│    │    │ → Depth Anything V2                                      │
│    │    └ → depth_map (numpy H×W)                                  │
│    │                                                                │
│    ├──► POST /api/vision/detect-reference                          │
│    │    │ → YOLO detect bát/thìa/đũa                              │
│    │    └ → reference objects + pixels_per_cm                      │
│    │                                                                │
│    └──► (Sẽ implement ở Task 2.3-2.5)                              │
│         │                                                          │
│         │ depth_map + pixels_per_cm                                │
│         │ → Calibrate pixel → real cm                              │
│         │ → Segment food region                                    │
│         │ → V = ∫∫ depth(x,y) dA × scale³                         │
│         └ → Volume (ml) → Carb (g) → GL                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 4: Testing & Validation — Việt + Hoài (30 phút)

### 4.1 Test detection accuracy

```python
# src/vision-service/tests/test_reference_service.py
"""
Unit tests cho Reference Object Detection Service.
Chạy: pytest tests/test_reference_service.py -v
"""

import pytest
import numpy as np
from PIL import Image

from services.reference_service import (
    ReferenceDetector,
    ReferenceObject,
    REFERENCE_DIMENSIONS,
)


@pytest.fixture(scope="session")
def detector():
    """Load detector 1 lần cho session."""
    det = ReferenceDetector(confidence=0.3)
    det.load()
    return det


@pytest.fixture
def sample_image():
    """Tạo ảnh test."""
    arr = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return Image.fromarray(arr)


class TestReferenceDetector:
    """Tests cho ReferenceDetector."""

    def test_detector_loads(self, detector):
        """Detector phải load thành công."""
        assert detector.is_loaded

    def test_detect_returns_list(self, detector, sample_image):
        """detect() phải trả về list (có thể rỗng)."""
        result = detector.detect(sample_image)
        assert isinstance(result, list)

    def test_reference_dimensions_complete(self):
        """Tất cả reference types phải có dimensions."""
        required_keys = {"width_cm", "height_cm", "description"}
        for ref_type, dims in REFERENCE_DIMENSIONS.items():
            assert required_keys.issubset(dims.keys()), f"Missing keys for {ref_type}"

    def test_scale_factor_calculation(self):
        """Test tính toán pixels_per_cm."""
        # Giả sử bát phở M (19cm) chiếm 380px → 20px/cm
        obj = ReferenceObject(
            class_name="bat_pho_m",
            confidence=0.95,
            bbox=[130.0, 40.0, 510.0, 360.0],
            bbox_width_px=380.0,
            bbox_height_px=320.0,
            real_width_cm=19.0,
            real_height_cm=7.5,
            pixels_per_cm=20.0,  # 380 / 19 = 20
        )
        assert abs(obj.pixels_per_cm - (380.0 / 19.0)) < 0.1

    def test_get_best_scale_factor_priority(self, detector):
        """Scale factor phải ưu tiên bát phở > bát cơm > thìa."""
        detections = [
            ReferenceObject("thia", 0.9, [0,0,10,80], 10, 80, 4.0, 16.0, 5.0),
            ReferenceObject("bat_pho_m", 0.85, [100,50,480,370], 380, 320, 19.0, 7.5, 20.0),
        ]
        best = detector.get_best_scale_factor(detections)
        assert best == 20.0  # Bát phở priority cao hơn thìa

    def test_get_best_scale_factor_empty(self, detector):
        """Trả về None nếu không có detection."""
        assert detector.get_best_scale_factor([]) is None


class TestWithRealImages:
    """Tests với ảnh thực (chỉ chạy khi có ảnh POC)."""

    @pytest.mark.skipif(
        not Path("data/poc/raw").exists(),
        reason="POC images not available"
    )
    def test_detect_on_poc_images(self, detector):
        """Test detection trên ảnh POC (nếu có)."""
        from pathlib import Path
        
        poc_dir = Path("data/poc/raw")
        images = list(poc_dir.glob("*.jpg")) + list(poc_dir.glob("*.png"))
        
        if not images:
            pytest.skip("No POC images found")

        for img_path in images[:3]:  # Test tối đa 3 ảnh
            image = Image.open(img_path).convert("RGB")
            detections = detector.detect(image)
            # Chỉ cần chạy không lỗi
            assert isinstance(detections, list)
```

### 4.2 Validate trên ảnh thực

```bash
# Test detection trên ảnh VN demo
python -c "
from services.reference_service import ReferenceDetector
from PIL import Image

detector = ReferenceDetector(confidence=0.3)
detector.load()

# Test với ảnh POC
import glob
for img_path in glob.glob('data/poc/raw/*.jpg')[:5]:
    image = Image.open(img_path).convert('RGB')
    detections = detector.detect(image)
    print(f'{img_path}:')
    for d in detections:
        print(f'  {d.class_name}: {d.confidence:.2f}, {d.pixels_per_cm:.1f} px/cm')
    print()
"
```

### 4.3 Accuracy target

```
┌─────────────────────────────────────────────────────────────────────┐
│  ACCEPTANCE CRITERIA:                                                │
│                                                                     │
│  ✅ mAP50 ≥ 90% trên validation set (nếu custom train)            │
│  ✅ Hoặc: pretrained COCO detect "bowl" với conf ≥ 0.5            │
│     trên ≥ 90% ảnh có bát                                         │
│                                                                     │
│  Kiểm tra bằng:                                                    │
│  1. Chạy detector trên tất cả ảnh VN demo (5-10 ảnh)              │
│  2. Đếm: bao nhiêu ảnh detect đúng bát/thìa?                     │
│  3. Target: ≥ 90% (tức ≥ 9/10 ảnh detect đúng)                   │
│                                                                     │
│  NẾU CHƯA ĐẠT:                                                     │
│  - Hạ confidence threshold (0.5 → 0.3)                             │
│  - Thêm data augmentation                                         │
│  - Thêm ảnh annotate vào training set                              │
│  - Fallback: hỏi user "Bát loại gì?" (form UI)                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `No module named ultralytics` | Chưa cài YOLO | `pip install ultralytics` |
| Training accuracy thấp | Dataset nhỏ | Tăng augmentation, epochs, hoặc thêm data |
| Không detect được đũa | Đũa mỏng, khó detect | Chấp nhận — dùng bát/thìa làm reference |
| Detection chậm | Model lớn | Dùng YOLOv8n (nano) cho inference |
| "No reference object found" | Không có bát/thìa trong ảnh | Implement fallback: form hỏi user |

### Workflow tổng hợp cho team

```
┌─────────────────────────────────────────────────────────────────────┐
│  WORKFLOW SONG SONG:                                                 │
│                                                                     │
│  Hoài (annotate):                                                   │
│  Ngày 14/03:                                                       │
│  □ Chụp 50-80 ảnh (kết hợp Task 1.3.5 chụp món VN)              │
│  □ Upload lên Roboflow                                             │
│  □ Annotate bounding box (2-3 giờ)                                │
│  □ Export YOLO format → data/poc/annotations/                     │
│                                                                     │
│  Việt (train + integrate):                                          │
│  Ngày 14/03 (sáng): Setup YOLO, chờ dataset từ Hoài              │
│  Ngày 14/03 (chiều): Nhận dataset → train (1-2 giờ)              │
│  Ngày 15/03: Integrate vào pipeline + tests                       │
│                                                                     │
│  Hoàng (review):                                                    │
│  □ Review model accuracy                                           │
│  □ Review integration code                                         │
│  □ Quyết định: custom model hay pretrained COCO?                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Checklist hoàn thành

- [ ] Dataset annotated ≥ 200 ảnh (Hoài)
  - [ ] Ảnh tự chụp: ≥ 50 ảnh (đa dạng bát/thìa/đũa VN)
  - [ ] Ảnh open-source: ≥ 100 ảnh (COCO/Open Images/Roboflow)
  - [ ] Export YOLO format → `data/poc/annotations/`
- [ ] YOLO model trained hoặc pretrained ready (Việt)
  - [ ] Training script: `scripts/train_reference_detector.py`
  - [ ] mAP50 ≥ 90% trên validation set
  - [ ] Model weights saved: `runs/reference_detector/v1/weights/best.pt`
- [ ] Service integrated (Việt)
  - [ ] `services/reference_service.py` — ReferenceDetector class
  - [ ] `schemas/reference_schemas.py` — Pydantic response models
  - [ ] `main.py` — endpoint `POST /api/vision/detect-reference`
  - [ ] Kích thước thực tế mapping cho bát/thìa/đũa VN
- [ ] Tests pass (Việt)
  - [ ] `tests/test_reference_service.py` — Unit tests
  - [ ] Manual test trên ảnh VN demo (≥ 90% detect đúng)
- [ ] Hoàng reviewed — quyết định Plan A (custom) hay Plan B (pretrained)

---

> **Tạo**: 10/03/2026
> **Guide cho**: [TASK_2.2_REFERENCE_OBJECT.md](../Tasks/TASK_2.2_REFERENCE_OBJECT.md)

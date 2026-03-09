# 📖 HƯỚNG DẪN CHI TIẾT TASK 1.3: THU THẬP DỮ LIỆU MÓN ĂN (HYBRID APPROACH)

> **Assignee**: Hoàng (chính), Hoài
> **Thời gian**: 11/03 → 12/03/2026
> **Tiền đề**: Task 1.0 (Hoàng đã định nghĩa format), Task 1.2 (DB có seed data)
> **Tham chiếu**: [TASK_1.3](../Tasks/TASK_1.3_DATA_COLLECTION.md) | [plan.md](../plan.md)
> **Cập nhật**: 07/03/2026 — Chuyển sang Hybrid Approach

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 1.1  Environment ✅ | Task 1.2 Database ✅                    │
│                                                                     │
│  ► Task 1.3  THU THẬP DỮ LIỆU (HYBRID)  ◄◄◄  BẠN ĐANG Ở ĐÂY    │
│    │                                                                │
│    │  Mục tiêu: Benchmark dataset + VN demo samples                │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Hoàng: Schema + Nutrition5k parse + Nutrition DB import    │
│    │  •         + Density Factor (literature) + validate           │
│    │  • Hoài: Chụp 5-10 mẫu món Việt cho demo                     │
│    │                                                                │
│    │  ⚡ TẠI SAO HYBRID?                                           │
│    │  ① Tự thu thập 22 mẫu = 5-8h, N quá nhỏ, GT thủ công       │
│    │  ② Nutrition5k = 5,006 mẫu, lab-grade, RGB+depth+weight     │
│    │  ③ Kết hợp: validate N=500 (thuyết phục) + demo VN (thực tế)│
│    │                                                                │
│    │  Vision Engine (Phase 2) CẦN dataset này để:                  │
│    │  1. Develop & test pipeline trên Nutrition5k (N lớn)         │
│    │  2. Validate accuracy report cho bảo vệ luận văn             │
│    │  3. Demo thực tế trên món Việt Nam                            │
│    │                                                                │
│    └───► Phase 2: Vision Engine (dùng dataset để dev + validate)   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tại sao thay đổi cách tiếp cận?

```
┌─────────────────────────────────────────────────────────────────────┐
│  VẤN ĐỀ VỚI KẾ HOẠCH CŨ (Tự thu thập 100%):                      │
│                                                                     │
│  ❌ 22 mẫu × (chụp 3 góc + đo nước + cân + tra cứu + nhập JSON)  │
│     = 5-8 giờ → N=22 quá nhỏ, không có ý nghĩa thống kê          │
│  ❌ Ground truth thủ công (đổ nước, cốc đong) = sai số cao        │
│  ❌ Pipeline chưa chắc hoạt động → mất công vô ích                 │
│  ❌ Hội đồng hỏi "Accuracy?" → "Đo trên 22 mẫu tự làm" → yếu    │
│                                                                     │
│  ✅ HYBRID APPROACH:                                                │
│  Tầng 1: Nutrition5k benchmark (N=100-500, lab-grade GT)           │
│  Tầng 2: Bảng dinh dưỡng VN tự động import (USDA/TPDD VN)        │
│  Tầng 3: 5-10 mẫu VN chụp demo (estimated values từ literature)   │
│                                                                     │
│  KẾT QUẢ:                                                           │
│  "Validate trên Nutrition5k (N=500) đạt X% accuracy.               │
│   Demo trên 10 món Việt, đạt Y% accuracy."                         │
│  → THUYẾT PHỤC HƠN RẤT NHIỀU                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### So sánh 2 cách tiếp cận

| Tiêu chí             | Cũ (Tự thu thập)   | Mới (Hybrid)                      |
| -------------------- | ------------------ | --------------------------------- |
| Thời gian            | 5-8 giờ manual     | ~4 giờ (download + script)        |
| Số mẫu validation    | N = 22             | N = 100-500                       |
| Ý nghĩa thống kê     | Yếu                | Mạnh                              |
| Ground truth quality | Tự đo (sai số cao) | Lab-grade (Nutrition5k)           |
| Tính thuyết phục     | "22 mẫu tự làm"    | "500 mẫu benchmark + demo Việt"   |
| Rủi ro pipeline fail | Mất công → phí hết | Pipeline test nhanh trên data sẵn |
| Demo Việt            | 22 mẫu             | 5-10 mẫu (đủ gây ấn tượng)        |

---

## Bước 1: Định nghĩa JSON Schema — Hoàng (30 phút)

### 1.1 Schema cho mẫu InSight (dùng chung cho cả Nutrition5k parsed và VN samples)

```json
{
  "$schema": "insight-food-sample-v1",
  "food_info": {
    "name_vi": "Phở bò",
    "name_en": "Beef pho",
    "category": "noodle_soup",
    "gi_index": 46,
    "carb_per_100g": 15.0
  },
  "sample": {
    "sample_id": "pho_bo_001",
    "source": "vn_demo",
    "images": [
      { "angle": "top_down", "file": "pho_bo_001_top.jpg" },
      { "angle": "45_degree", "file": "pho_bo_001_45.jpg" }
    ]
  },
  "ground_truth": {
    "total_weight_g": 650,
    "measurement_method": "estimated_from_literature",
    "nutrition": {
      "calories": 350,
      "total_carb_g": 45.0,
      "protein_g": 25.0,
      "fat_g": 8.0
    },
    "density_factor": {
      "solid_ratio": 0.3,
      "effective_density": 1.02
    }
  },
  "nutrition_derived": {
    "glycemic_load": 20.7,
    "calculation": "45g carb × 46 GI / 100 = 20.7 GL"
  },
  "metadata": {
    "collected_by": "Hoài",
    "date": "2026-03-11",
    "source_dataset": "vn_demo",
    "notes": "Bát nhựa trắng, nước dùng trong"
  }
}
```

### 1.2 Schema cho Nutrition5k parsed samples

```json
{
  "$schema": "insight-food-sample-v1",
  "food_info": {
    "name_en": "Mixed plate - chicken rice",
    "category": "mixed",
    "carb_per_100g": null
  },
  "sample": {
    "sample_id": "n5k_dish_1560",
    "source": "nutrition5k",
    "images": [
      { "angle": "overhead", "file": "dish_1560/rgb_overhead.png" },
      { "angle": "side", "file": "dish_1560/rgb_side.png" }
    ],
    "depth_image": "dish_1560/depth_overhead.png"
  },
  "ground_truth": {
    "total_weight_g": 385,
    "measurement_method": "lab_scale",
    "nutrition": {
      "calories": 512,
      "total_carb_g": 52.0,
      "protein_g": 30.0,
      "fat_g": 18.0
    }
  },
  "metadata": {
    "source_dataset": "nutrition5k",
    "original_id": "dish_1560"
  }
}
```

### 1.3 Folder structure

```
data/
├── nutrition5k/                    ← Benchmark dataset (gitignored — lớn)
│   ├── README.md                   ← Hướng dẫn download + license
│   ├── raw/                        ← Download từ Google
│   │   ├── dish_1560/
│   │   │   ├── rgb_overhead.png
│   │   │   ├── rgb_side.png
│   │   │   ├── depth_overhead.png
│   │   │   └── metadata.csv
│   │   └── ...
│   └── parsed/
│       └── nutrition5k_subset.json ← Parsed sang InSight format
├── vn_demo/                        ← Mẫu Việt Nam cho demo
│   ├── pho_bo/
│   │   ├── pho_bo_001/
│   │   │   ├── pho_bo_001_top.jpg
│   │   │   ├── pho_bo_001_45.jpg
│   │   │   └── pho_bo_001.json
│   │   └── ...
│   └── ...
├── nutrition_db/                   ← Bảng dinh dưỡng tự động import
│   ├── vn_food_nutrition.json      ← Bảng TPDD Việt Nam
│   └── density_factors.json        ← Density Factor từ literature
├── processed/
│   └── dataset_v1.json             ← Tổng hợp (N5k subset + VN demo)
├── annotations/
│   └── ground_truth.json           ← Ground truth tổng hợp
└── README.md
```

---

## Bước 2: Download & Parse Nutrition5k — Hoàng (1 giờ)

### 2.1 Về Nutrition5k Dataset

```
┌─────────────────────────────────────────────────────────────────────┐
│  NUTRITION5K (Google Research, 2021)                                 │
│                                                                     │
│  • 5,006 món ăn với ground truth đo bằng lab equipment             │
│  • Mỗi món có: RGB overhead + side images, depth map               │
│  • Ground truth: total weight (g), calories, fat, carb, protein    │
│  • Đo bằng: cân điện tử lab-grade + calorimeter                   │
│  • Link: github.com/google-research-datasets/Nutrition5k           │
│  • License: Creative Commons BY 4.0                                 │
│                                                                     │
│  TẠI SAO PHÙ HỢP:                                                   │
│  ✅ Có cả RGB + depth map → test Depth Anything V2 pipeline        │
│  ✅ Ground truth weight chính xác → validate volume estimation     │
│  ✅ N=5006 → chọn subset 100-500 mẫu = đủ ý nghĩa thống kê      │
│  ✅ Có nutrition data → validate GL calculation                     │
│  ✅ License mở → dùng được cho đồ án                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Script download & parse

```python
# scripts/download_nutrition5k.py
"""Download Nutrition5k subset và parse sang InSight format."""
import json
import csv
from pathlib import Path

# Nutrition5k metadata file (download trước)
# https://github.com/google-research-datasets/Nutrition5k
N5K_METADATA = Path("data/nutrition5k/raw/metadata.csv")
OUTPUT_PATH = Path("data/nutrition5k/parsed/nutrition5k_subset.json")

def parse_nutrition5k(metadata_path, max_samples=500):
    """Parse Nutrition5k metadata sang InSight format."""
    samples = []

    with open(metadata_path) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_samples:
                break

            sample = {
                "food_info": {
                    "name_en": row.get("dish_name", f"dish_{row['dish_id']}"),
                    "category": "mixed",
                },
                "sample": {
                    "sample_id": f"n5k_{row['dish_id']}",
                    "source": "nutrition5k",
                    "images": [
                        {"angle": "overhead", "file": f"dish_{row['dish_id']}/rgb_overhead.png"},
                        {"angle": "side", "file": f"dish_{row['dish_id']}/rgb_side.png"},
                    ],
                    "depth_image": f"dish_{row['dish_id']}/depth_overhead.png",
                },
                "ground_truth": {
                    "total_weight_g": float(row.get("total_weight", 0)),
                    "measurement_method": "lab_scale",
                    "nutrition": {
                        "calories": float(row.get("total_calories", 0)),
                        "total_carb_g": float(row.get("total_carb", 0)),
                        "protein_g": float(row.get("total_protein", 0)),
                        "fat_g": float(row.get("total_fat", 0)),
                    },
                },
                "metadata": {
                    "source_dataset": "nutrition5k",
                    "original_id": row["dish_id"],
                },
            }
            samples.append(sample)

    return samples

if __name__ == "__main__":
    samples = parse_nutrition5k(N5K_METADATA, max_samples=500)

    output = {
        "version": "1.0",
        "source": "nutrition5k",
        "total_samples": len(samples),
        "samples": samples,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Parsed {len(samples)} Nutrition5k samples -> {OUTPUT_PATH}")
```

### 2.3 Các dataset bổ sung (tham khảo)

| Dataset                   | Mô tả                                        | Dùng cho                                |
| ------------------------- | -------------------------------------------- | --------------------------------------- |
| **Nutrition5k**           | 5,006 món, RGB + depth + weight/nutrition GT | Pipeline development & validation chính |
| **ECUST Food-512**        | 512 món Trung Quốc (nhiều trùng VN)          | Bổ sung nếu cần thêm diversity          |
| **USDA FoodData Central** | 370,000+ entries dinh dưỡng                  | Tra cứu carb/GI tự động                 |
| **Bảng TPDD Việt Nam**    | ~500 món Việt, macro nutrients               | Dinh dưỡng món Việt cụ thể              |

---

## Bước 3: Import bảng dinh dưỡng VN vào DB — Hoàng (1 giờ)

### 3.1 Nguồn dữ liệu dinh dưỡng

```
┌─────────────────────────────────────────────────────────────────────┐
│  THAY VÌ tra cứu thủ công từng món (3+ giờ)                        │
│  → IMPORT TỰ ĐỘNG từ bảng có sẵn (30 phút)                        │
│                                                                     │
│  Nguồn 1: USDA FoodData Central API                                │
│  - API: https://fdc.nal.usda.gov/fdc-app.html#/food-search         │
│  - Có endpoint REST, trả JSON                                      │
│  - 370,000+ items, có carb/protein/fat per 100g                    │
│                                                                     │
│  Nguồn 2: Bảng Thành phần Dinh dưỡng Thực phẩm Việt Nam          │
│  - Viện Dinh dưỡng Quốc gia                                        │
│  - ~500 món Việt phổ biến                                           │
│  - Có: Năng lượng, Protein, Lipid, Glucid per 100g                │
│                                                                     │
│  Nguồn 3: Published GI Tables                                      │
│  - International Tables of Glycemic Index (Foster-Powell et al.)   │
│  - Có GI cho 2,500+ thực phẩm                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Script import dinh dưỡng

```python
# scripts/import_nutrition_db.py
"""Import bảng dinh dưỡng VN vào JSON + seed vào PostgreSQL."""
import json
from pathlib import Path

# Dữ liệu tổng hợp từ USDA + Bảng TPDD VN + GI Tables
# Đây là curated data cho 10 món VN trong scope
VN_FOOD_NUTRITION = [
    {
        "food_name_vi": "Cơm trắng",
        "food_name_en": "White rice (cooked)",
        "category": "rice",
        "gi_index": 73,
        "carb_per_100g": 28.2,
        "protein_per_100g": 2.7,
        "fat_per_100g": 0.3,
        "calories_per_100g": 130,
        "source": "USDA #168878 + VN TPDD",
    },
    {
        "food_name_vi": "Phở bò (bánh phở)",
        "food_name_en": "Rice noodles (pho)",
        "category": "noodle_soup",
        "gi_index": 46,
        "carb_per_100g": 22.5,
        "protein_per_100g": 1.6,
        "fat_per_100g": 0.2,
        "calories_per_100g": 109,
        "source": "USDA #168921 + GI Tables",
    },
    {
        "food_name_vi": "Bún bò Huế (bún)",
        "food_name_en": "Rice vermicelli (bun)",
        "category": "noodle_soup",
        "gi_index": 58,
        "carb_per_100g": 25.1,
        "protein_per_100g": 2.0,
        "fat_per_100g": 0.1,
        "calories_per_100g": 108,
        "source": "USDA #168921 + VN TPDD",
    },
    {
        "food_name_vi": "Bánh mì",
        "food_name_en": "Vietnamese baguette",
        "category": "bread",
        "gi_index": 80,
        "carb_per_100g": 50.6,
        "protein_per_100g": 8.2,
        "fat_per_100g": 3.3,
        "calories_per_100g": 274,
        "source": "USDA #172686 + GI Tables",
    },
    {
        "food_name_vi": "Cơm tấm",
        "food_name_en": "Broken rice (cooked)",
        "category": "rice",
        "gi_index": 70,
        "carb_per_100g": 27.0,
        "protein_per_100g": 2.5,
        "fat_per_100g": 0.5,
        "calories_per_100g": 126,
        "source": "VN TPDD + GI Tables (similar to white rice)",
    },
    {
        "food_name_vi": "Bún thịt nướng (bún)",
        "food_name_en": "Rice vermicelli",
        "category": "noodle_dry",
        "gi_index": 58,
        "carb_per_100g": 25.1,
        "protein_per_100g": 2.0,
        "fat_per_100g": 0.1,
        "calories_per_100g": 108,
        "source": "USDA #168921",
    },
    {
        "food_name_vi": "Mì xào",
        "food_name_en": "Stir-fried egg noodles",
        "category": "noodle_dry",
        "gi_index": 52,
        "carb_per_100g": 23.0,
        "protein_per_100g": 4.5,
        "fat_per_100g": 6.0,
        "calories_per_100g": 168,
        "source": "USDA #168919 + GI Tables",
    },
    {
        "food_name_vi": "Cháo gạo",
        "food_name_en": "Rice porridge (congee)",
        "category": "porridge",
        "gi_index": 78,
        "carb_per_100g": 8.5,
        "protein_per_100g": 1.0,
        "fat_per_100g": 0.2,
        "calories_per_100g": 46,
        "source": "USDA #168870 + GI Tables",
    },
    {
        "food_name_vi": "Xôi (nếp)",
        "food_name_en": "Sticky rice (cooked)",
        "category": "rice",
        "gi_index": 87,
        "carb_per_100g": 36.7,
        "protein_per_100g": 3.5,
        "fat_per_100g": 0.3,
        "calories_per_100g": 169,
        "source": "USDA #168879 + GI Tables",
    },
    {
        "food_name_vi": "Trà sữa trân châu",
        "food_name_en": "Bubble tea (boba)",
        "category": "drink",
        "gi_index": 65,
        "carb_per_100g": 15.0,
        "protein_per_100g": 0.5,
        "fat_per_100g": 1.5,
        "calories_per_100g": 80,
        "source": "Estimated from commercial products + GI Tables",
    },
]

if __name__ == "__main__":
    output_path = Path("data/nutrition_db/vn_food_nutrition.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "version": "1.0",
        "description": "Vietnamese food nutrition database (curated from USDA + VN TPDD + GI Tables)",
        "total_items": len(VN_FOOD_NUTRITION),
        "items": VN_FOOD_NUTRITION,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(VN_FOOD_NUTRITION)} items -> {output_path}")
```

---

## Bước 4: Density Factor DB từ Literature — Hoàng (30 phút)

### 4.1 Giải thích Density Factor

```
┌─────────────────────────────────────────────────────────────────────┐
│  DENSITY FACTOR = Tỷ lệ phần ĂN ĐƯỢC trong tổng thể tích          │
│                                                                     │
│  Tại sao cần: Bát phở 500ml, nhưng chỉ 150ml là bánh phở + thịt  │
│  → Nếu tính 500ml × carb/ml → SAI (nước dùng ít carb)            │
│  → Cần nhân với solid_ratio = 0.30 → 150ml thực tế                │
│                                                                     │
│  Công thức:                                                         │
│  Weight_food = Volume × solid_ratio × density                      │
│  Carb = Weight_food × carb_per_100g / 100                         │
│  GL = Carb × GI / 100                                              │
│                                                                     │
│  ⚠️ THAY ĐỔI: Lấy từ food science literature thay vì tự đo       │
│  Nguồn: USDA food composition, food engineering research papers    │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Bảng Density Factor (từ literature)

| Món                  | Solid Ratio | Density (g/ml) | Nguồn                       | Ghi chú                 |
| -------------------- | ----------- | -------------- | --------------------------- | ----------------------- |
| Cơm trắng            | 1.00        | 1.08           | USDA food composition       | Hoàn toàn đặc           |
| Phở bò (standard)    | 0.30        | 1.02           | Food engineering estimates  | 30% đặc, 70% nước       |
| Phở bò (đặc biệt)    | 0.45        | 1.03           | Food engineering estimates  | Nhiều thịt, bánh phở    |
| Bún bò Huế           | 0.35        | 1.03           | Food engineering estimates  | Nước đặc hơn phở        |
| Bánh mì              | 1.00        | 0.35           | USDA #172686 bulk density   | Xốp, nhẹ                |
| Cơm tấm + đồ ăn kèm  | 0.90        | 1.10           | USDA food composition       | Gần đặc hoàn toàn       |
| Bún thịt nướng (khô) | 0.95        | 0.85           | Food engineering estimates  | Không nước, bún xốp     |
| Mì xào               | 1.00        | 0.90           | Food engineering estimates  | Đặc, dầu nhiều          |
| Cháo (loãng)         | 0.20        | 1.01           | USDA #168870                | 80% nước                |
| Cháo (đặc)           | 0.35        | 1.02           | USDA #168870                | 65% nước                |
| Xôi                  | 1.00        | 1.15           | USDA food composition       | Đặc, nếp nặng           |
| Trà sữa              | 0.10        | 1.05           | Commercial product analysis | 90% nước, 10% trân châu |

### 4.3 Script export Density Factor

```python
# scripts/export_density_factors.py
"""Export Density Factor DB sang JSON."""
import json
from pathlib import Path

DENSITY_FACTORS = [
    {"food": "com_trang", "name_vi": "Cơm trắng", "solid_ratio": 1.00, "density": 1.08, "source": "USDA food composition"},
    {"food": "pho_bo_standard", "name_vi": "Phở bò (standard)", "solid_ratio": 0.30, "density": 1.02, "source": "Food engineering estimates"},
    {"food": "pho_bo_special", "name_vi": "Phở bò (đặc biệt)", "solid_ratio": 0.45, "density": 1.03, "source": "Food engineering estimates"},
    {"food": "bun_bo_hue", "name_vi": "Bún bò Huế", "solid_ratio": 0.35, "density": 1.03, "source": "Food engineering estimates"},
    {"food": "banh_mi", "name_vi": "Bánh mì", "solid_ratio": 1.00, "density": 0.35, "source": "USDA #172686 bulk density"},
    {"food": "com_tam", "name_vi": "Cơm tấm + đồ ăn kèm", "solid_ratio": 0.90, "density": 1.10, "source": "USDA food composition"},
    {"food": "bun_thit_nuong", "name_vi": "Bún thịt nướng (khô)", "solid_ratio": 0.95, "density": 0.85, "source": "Food engineering estimates"},
    {"food": "mi_xao", "name_vi": "Mì xào", "solid_ratio": 1.00, "density": 0.90, "source": "Food engineering estimates"},
    {"food": "chao_loang", "name_vi": "Cháo (loãng)", "solid_ratio": 0.20, "density": 1.01, "source": "USDA #168870"},
    {"food": "chao_dac", "name_vi": "Cháo (đặc)", "solid_ratio": 0.35, "density": 1.02, "source": "USDA #168870"},
    {"food": "xoi", "name_vi": "Xôi", "solid_ratio": 1.00, "density": 1.15, "source": "USDA food composition"},
    {"food": "tra_sua", "name_vi": "Trà sữa", "solid_ratio": 0.10, "density": 1.05, "source": "Commercial product analysis"},
]

if __name__ == "__main__":
    output_path = Path("data/nutrition_db/density_factors.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "version": "1.0",
            "description": "Density factors for Vietnamese dishes (from published literature)",
            "total_items": len(DENSITY_FACTORS),
            "items": DENSITY_FACTORS,
        }, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(DENSITY_FACTORS)} density factors -> {output_path}")
```

---

## Bước 5: Chụp mẫu Việt Nam cho Demo — Hoài (1-2 giờ)

### 5.1 Danh sách 5-10 món (giảm scope — demo only)

| #   | Món        | Số mẫu | Ghi chú                 |
| --- | ---------- | ------ | ----------------------- |
| 1   | Cơm trắng  | 1-2    | Chén/bát — dễ chụp nhất |
| 2   | Phở bò     | 1-2    | Tô thường               |
| 3   | Bánh mì    | 1      | Nguyên ổ                |
| 4   | Cơm tấm    | 1      | Đĩa thường              |
| 5   | Bún bò Huế | 1      | Tô thường               |

**Tùy thời gian có thể thêm:** Mì xào, Cháo, Xôi, Bún thịt nướng, Trà sữa

**Tổng: 5-10 mẫu × 2 góc = 10-20 ảnh** (giảm từ 66 ảnh)

### 5.2 Checklist chụp ảnh (đơn giản hóa)

```
Cho mỗi mẫu:
□ 1. Đặt món ăn trên bàn có thìa/đũa bên cạnh (vật tham chiếu)
□ 2. Chụp 2 góc:
     - Top-down (nhìn thẳng từ trên)
     - 45 độ (góc nghiêng bình thường)
□ 3. Đảm bảo: ánh sáng đều, nền rõ ràng
□ 4. Tạo JSON mẫu với estimated values từ literature
     (KHÔNG cần đo nước hay cân)
```

### 5.3 Ground truth cho mẫu VN

```
┌─────────────────────────────────────────────────────────────────────┐
│  THAY ĐỔI QUAN TRỌNG:                                              │
│                                                                     │
│  CŨ: Đo nước + cân từng thành phần (3+ giờ cho 22 mẫu)           │
│  MỚI: Dùng estimated values từ literature + portion size chuẩn     │
│                                                                     │
│  VD: Bát phở M thường ~ 450-500ml, bánh phở ~200g, thịt ~80g      │
│  → Lấy giá trị trung bình từ USDA + VN TPDD                       │
│                                                                     │
│  LÝ DO: Validated pipeline accuracy CHÍNH trên Nutrition5k (N=500) │
│  Mẫu VN chỉ cần CHO THẤY app HOẠT ĐỘNG trên món Việt              │
│  → Không cần ground truth cực chính xác                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 6: Compile & Validate — Hoàng (30 phút)

### 6.1 Script tổng hợp dataset

```python
# scripts/compile_dataset.py
"""Tổng hợp Nutrition5k subset + VN demo samples."""
import json
from pathlib import Path

def load_samples(path):
    if path.exists():
        with open(path) as f:
            return json.load(f).get("samples", [])
    return []

# Load Nutrition5k parsed
n5k_samples = load_samples(Path("data/nutrition5k/parsed/nutrition5k_subset.json"))

# Load VN demo samples
vn_samples = []
vn_dir = Path("data/vn_demo")
if vn_dir.exists():
    for food_dir in sorted(vn_dir.iterdir()):
        if not food_dir.is_dir():
            continue
        for sample_dir in sorted(food_dir.iterdir()):
            json_files = list(sample_dir.glob("*.json"))
            if json_files:
                with open(json_files[0]) as f:
                    vn_samples.append(json.load(f))

output = {
    "version": "1.0",
    "description": "InSight dataset: Nutrition5k benchmark + Vietnamese demo samples",
    "nutrition5k_count": len(n5k_samples),
    "vn_demo_count": len(vn_samples),
    "total_samples": len(n5k_samples) + len(vn_samples),
    "samples": n5k_samples + vn_samples,
}

output_path = Path("data/processed/dataset_v1.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Dataset compiled:")
print(f"  Nutrition5k: {len(n5k_samples)} samples")
print(f"  VN demo: {len(vn_samples)} samples")
print(f"  Total: {len(n5k_samples) + len(vn_samples)} -> {output_path}")
```

### 6.2 Validation

```bash
# Compile
python scripts/compile_dataset.py
# Kỳ vọng: 100-500 Nutrition5k + 5-10 VN demo

# Validate structure
python scripts/validate_dataset.py
# Kỳ vọng: All samples have required fields
```

---

## Checklist hoàn thành

- [ ] JSON schema định nghĩa xong (InSight format + Nutrition5k format)
- [ ] Nutrition5k subset downloaded & parsed (≥ 100 mẫu)
- [ ] Bảng dinh dưỡng VN exported (`vn_food_nutrition.json`)
- [ ] Density Factor DB exported (`density_factors.json`)
- [ ] 5-10 mẫu VN demo chụp ảnh (≥ 2 góc)
- [ ] `dataset_v1.json` compiled + validated
- [ ] Hoàng reviewed

---

> **Tạo**: 06/03/2026
> **Cập nhật**: 07/03/2026 — Chuyển sang Hybrid Approach

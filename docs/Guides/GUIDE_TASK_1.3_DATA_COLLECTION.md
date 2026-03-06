# 📖 HƯỚNG DẪN CHI TIẾT TASK 1.3: THU THẬP DỮ LIỆU MÓN ĂN

> **Assignee**: Hoài (chính), Hoàng
> **Thời gian**: 11/03 → 12/03/2026
> **Tiền đề**: Task 1.0 (Hoàng đã định nghĩa format), Task 1.2 (DB có seed data)
> **Tham chiếu**: [TASK_1.3](../Tasks/TASK_1.3_DATA_COLLECTION.md) | [plan.md](../plan.md)

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 1.1  Environment ✅ | Task 1.2 Database ✅                    │
│                                                                     │
│  ► Task 1.3  THU THẬP DỮ LIỆU  ◄◄◄  BẠN ĐANG Ở ĐÂY              │
│    │                                                                │
│    │  Mục tiêu: Dataset 10 món VN + ground-truth thể tích          │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Hoàng: JSON schema + Density Factor DB + review            │
│    │  • Hoài: Chụp ảnh + đo thể tích + cân khối lượng + GI data  │
│    │                                                                │
│    │  ⚡ TẠI SAO QUAN TRỌNG:                                       │
│    │  Vision Engine (Phase 2) CẦN dataset này để:                  │
│    │  1. Test depth estimation có chính xác không                  │
│    │  2. Validate volume estimation (so sánh với đo thực tế)       │
│    │  3. Tính accuracy report cho bảo vệ luận văn                  │
│    │                                                                │
│    └───► Phase 2: Vision Engine (dùng dataset để train + test)     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tại sao cần Ground-Truth?

```
┌─────────────────────────────────────────────────────────────────────┐
│  BÀI TOÁN: App chụp ảnh → ước lượng thể tích V (ml)               │
│                                                                     │
│  ĐỂ BIẾT APP ƯỚC LƯỢNG ĐÚNG HAY SAI:                              │
│  Cần so sánh V_app vs V_thực = Ground Truth                        │
│                                                                     │
│  Ví dụ:                                                             │
│  - Bát phở: App nói 450ml, thực tế đổ nước = 480ml → sai 6.3% ✅ │
│  - Cơm tấm: App nói 300ml, thực tế = 250ml → sai 20% ❌          │
│                                                                     │
│  KPI: Sai số ≤ 15% trên 10 mẫu                                    │
│                                                                     │
│  ⚠️ Hội đồng CHẮC CHẮN HỎI:                                       │
│  "Accuracy bao nhiêu? Đo bằng cách nào?"                           │
│  → Có ground-truth = trả lời được                                  │
│  → Không có = bịa số = TRƯỢT                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 1: Định nghĩa JSON Schema — Hoàng (1 giờ)

### 1.1 Schema cho mỗi mẫu

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
    "bowl_type": "bát tô lớn",
    "bowl_diameter_cm": 20,
    "images": [
      {"angle": "top_down", "file": "pho_bo_001_top.jpg"},
      {"angle": "45_degree", "file": "pho_bo_001_45.jpg"},
      {"angle": "side", "file": "pho_bo_001_side.jpg"}
    ]
  },
  "ground_truth": {
    "total_volume_ml": 480,
    "measurement_method": "water_displacement",
    "components": {
      "noodle_g": 200,
      "beef_g": 80,
      "broth_ml": 350,
      "herbs_g": 20
    },
    "total_weight_g": 650,
    "density_factor": {
      "solid_ratio": 0.30,
      "effective_density": 1.02
    }
  },
  "nutrition": {
    "total_carb_g": 45.0,
    "glycemic_load": 20.7,
    "calculation": "200g noodle × 22.5g carb/100g = 45g carb"
  },
  "metadata": {
    "collected_by": "Hoài",
    "date": "2026-03-11",
    "location": "lab",
    "notes": "Bát nhựa trắng, nước dùng trong"
  }
}
```

### 1.2 Folder structure cho data

```
data/
├── raw/
│   ├── pho_bo/
│   │   ├── pho_bo_001/
│   │   │   ├── pho_bo_001_top.jpg
│   │   │   ├── pho_bo_001_45.jpg
│   │   │   ├── pho_bo_001_side.jpg
│   │   │   └── pho_bo_001.json
│   │   └── pho_bo_002/
│   ├── com_trang/
│   │   ├── com_trang_001/
│   │   └── ...
│   └── ...
└── processed/
    └── dataset_v1.json  ← File tổng hợp tất cả mẫu
```

---

## Bước 2: Chụp ảnh — Hoài (3 giờ)

### 2.1 Danh sách 10 món

| # | Món | Dụng cụ đựng | Số mẫu | Ghi chú |
|---|-----|-------------|--------|---------|
| 1 | Cơm trắng | Bát/Đĩa | 3 (S/M/L) | Dùng chén, bát nhỏ, bát to |
| 2 | Phở bò | Bát tô | 2 (M/L) | Tô thường + tô đặc biệt |
| 3 | Bún bò Huế | Bát tô | 2 | Nhiều nước + ít nước |
| 4 | Bánh mì | Khay/Tay | 2 | Nguyên ổ + cắt đôi |
| 5 | Cơm tấm | Đĩa | 2 | Đĩa nhỏ + đĩa to |
| 6 | Bún thịt nướng | Bát/Đĩa | 2 | Bát + đĩa |
| 7 | Mì xào | Đĩa | 2 | Ít + nhiều |
| 8 | Cháo | Bát/Tô | 2 | Loãng + đặc |
| 9 | Xôi | Hộp/Lá | 2 | Gói nhỏ + gói lớn |
| 10 | Trà sữa | Ly | 2 (M/L) | Size M + L |

**Tổng: ~22 mẫu × 3 góc = ~66 ảnh**

### 2.2 Checklist chụp ảnh cho MỖI mẫu

```
Cho mỗi mẫu ảnh:
□ 1. Đặt món ăn trên bàn có vật tham chiếu (thìa/đũa bên cạnh)
□ 2. Chụp 3 góc:
     - Top-down (nhìn thẳng từ trên xuống)
     - 45 độ (góc nghiêng người dùng thường chụp)
     - Side (ngang, để thấy chiều cao)
□ 3. Đảm bảo:
     - Ánh sáng đều, không bóng tối
     - Nền rõ ràng (bàn gỗ/trắng)
     - Vật tham chiếu (thìa/đũa) luôn trong khung hình
     - Resolution ≥ 1920x1080
```

### 2.3 Thiết bị cần chuẩn bị

| Thiết bị | Mục đích | Ghi chú |
|----------|---------|---------|
| Điện thoại | Chụp ảnh | ≥ 12MP, auto-focus |
| Cân điện tử | Cân khối lượng | Sai số ±1g |
| Cốc đong | Đo thể tích nước | 100ml, 250ml, 500ml |
| Thước kẻ | Đo đường kính bát | 30cm ruler |
| Thìa/Đũa tiêu chuẩn | Vật tham chiếu | Đo sẵn kích thước thực |
| Bát/Tô các cỡ | Đựng món ăn | S/M/L — đo sẵn đường kính |

---

## Bước 3: Đo Ground-Truth — Hoài (2 giờ)

### 3.1 Phương pháp đo thể tích: Đổ nước (Water Displacement)

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHƯƠNG PHÁP ĐỔ NƯỚC (Archimedes principle simplified)             │
│                                                                     │
│  1. Bát + Món ăn                  → Chụp ảnh xong                  │
│  2. Lấy món ăn ra                 → Bát trống                      │
│  3. Đổ nước đầy bát tới mép      → Ghi lại V_full (ml)            │
│  4. Múc nước ra                   → Đổ vào cốc đong               │
│  5. V_món = V_full - V_nước_còn_lại                                │
│                                                                     │
│  CHO MÓN NƯỚC (Phở, Bún):                                          │
│  1. Ghi V_total (toàn bộ món trong bát)                            │
│  2. Lọc riêng phần đặc (rây)     → Cân W_solid (g)                │
│  3. Đo V_nước_dùng               → V_liquid (ml)                  │
│  4. Solid ratio = W_solid / (W_solid + V_liquid × density_liquid)  │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Bảng ghi kết quả

| Mẫu | V_total (ml) | W_solid (g) | W_total (g) | V_bowl (ml) | Solid ratio |
|------|-------------|------------|-------------|------------|-------------|
| pho_bo_001 | 480 | 300 | 650 | 700 | 0.30 |
| com_trang_001 | 250 | 250 | 250 | 400 | 1.00 |
| ... | | | | | |

### 3.3 Tra cứu dữ liệu dinh dưỡng

Nguồn tra cứu:
1. **USDA FoodData Central**: https://fdc.nal.usda.gov/ (tiếng Anh)
2. **Bảng dinh dưỡng VN** (Viện Dinh dưỡng Quốc gia)
3. **Google "carb per 100g [tên món]"** → cross-check 2-3 nguồn

---

## Bước 4: Xây dựng Density Factor DB — Hoàng (1 giờ)

### 4.1 Bảng Density Factor

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
└─────────────────────────────────────────────────────────────────────┘
```

| Món | Solid Ratio | Density (g/ml) | Ghi chú |
|-----|------------|---------------|---------|
| Cơm trắng | 1.00 | 1.08 | Hoàn toàn đặc |
| Phở bò (standard) | 0.30 | 1.02 | 30% đặc, 70% nước |
| Phở bò (đặc biệt) | 0.45 | 1.03 | Nhiều thịt, bánh phở |
| Bún bò Huế | 0.35 | 1.03 | Nước đặc hơn phở |
| Bánh mì | 1.00 | 0.35 | Xốp, nhẹ |
| Cơm tấm + đồ ăn kèm | 0.90 | 1.10 | Gần đặc hoàn toàn |
| Bún thịt nướng (khô) | 0.95 | 0.85 | Không nước, bún xốp |
| Mì xào | 1.00 | 0.90 | Đặc, dầu nhiều |
| Cháo (loãng) | 0.20 | 1.01 | 80% nước |
| Cháo (đặc) | 0.35 | 1.02 | 65% nước |
| Xôi | 1.00 | 1.15 | Đặc, nếp nặng |
| Trà sữa | 0.10 | 1.05 | 90% nước, 10% trân châu |

---

## Bước 5: Validate & Export — Hoàng (1 giờ)

### 5.1 Script tổng hợp dataset

```python
# scripts/compile_dataset.py
"""Tổng hợp tất cả JSON mẫu thành 1 file dataset_v1.json"""
import json
from pathlib import Path

raw_dir = Path("data/raw")
all_samples = []

for food_dir in sorted(raw_dir.iterdir()):
    if not food_dir.is_dir():
        continue
    for sample_dir in sorted(food_dir.iterdir()):
        json_files = list(sample_dir.glob("*.json"))
        if json_files:
            with open(json_files[0]) as f:
                sample = json.load(f)
                all_samples.append(sample)

output = {
    "version": "1.0",
    "total_samples": len(all_samples),
    "samples": all_samples,
}

output_path = Path("data/processed/dataset_v1.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ Dataset compiled: {len(all_samples)} samples → {output_path}")
```

### 5.2 Validation checklist

```bash
python scripts/compile_dataset.py
# Kỳ vọng: ≥ 20 samples

# Check tất cả mẫu có đủ trường
python -c "
import json
with open('data/processed/dataset_v1.json') as f:
    ds = json.load(f)
for s in ds['samples']:
    assert 'ground_truth' in s, f'Missing ground_truth: {s[\"sample\"][\"sample_id\"]}'
    assert s['ground_truth']['total_volume_ml'] > 0
    assert len(s['sample']['images']) >= 3
print(f'✅ All {ds[\"total_samples\"]} samples validated!')
"
```

---

## Checklist hoàn thành

- [ ] JSON schema định nghĩa xong
- [ ] 10 món × ≥ 2 mẫu = ≥ 20 mẫu chụp ảnh
- [ ] Mỗi mẫu có ≥ 3 góc (top, 45°, side)
- [ ] Ground-truth thể tích đo bằng đổ nước
- [ ] Khối lượng thực tế cân xong
- [ ] Dữ liệu dinh dưỡng (Carb, GI) tra cứu xong
- [ ] Density Factor DB hoàn chỉnh
- [ ] `dataset_v1.json` compiled + validated
- [ ] Hoàng reviewed

---

> **Tạo**: 06/03/2026

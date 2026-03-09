# InSight Data Directory

## Structure

```
data/
├── schemas/                        ← JSON Schema definitions
│   └── insight_food_sample_v1.json ← Schema for food samples
├── nutrition5k/                    ← Benchmark dataset (gitignored — large files)
│   ├── README.md                   ← Download instructions + license
│   ├── raw/                        ← Raw Nutrition5k data (download from Google)
│   │   └── metadata.csv            ← Sample/real metadata
│   └── parsed/
│       └── nutrition5k_subset.json ← Parsed to InSight format
├── vn_demo/                        ← Vietnamese demo samples (by Hoài)
│   ├── com_trang/                  ← White rice
│   ├── pho_bo/                     ← Beef pho
│   ├── banh_mi/                    ← Vietnamese baguette
│   ├── com_tam/                    ← Broken rice
│   └── bun_bo_hue/                 ← Hue beef noodle
├── nutrition_db/                   ← Nutrition reference data
│   ├── vn_food_nutrition.json      ← Vietnamese food nutrition (USDA + VN TPDD)
│   └── density_factors.json        ← Density factors from literature
├── poc/                            ← Legacy POC data
│   ├── annotations/
│   │   └── ground_truth.json
│   └── raw/
├── processed/
│   └── dataset_v1.json             ← Compiled dataset (N5k + VN demo)
├── annotations/
│   └── ground_truth.json           ← Ground truth for validation
└── README.md                       ← This file
```

## Quick Start

```bash
# 1. Parse Nutrition5k metadata
python scripts/download_nutrition5k.py

# 2. Export Vietnamese nutrition database
python scripts/import_nutrition_db.py

# 3. Export density factors
python scripts/export_density_factors.py

# 4. Compile all data into unified dataset
python scripts/compile_dataset.py

# 5. Validate everything
python scripts/validate_dataset.py --validate-all
```

## Sources

| Source | Description | License |
|--------|------------|---------|
| **Nutrition5k** | 5,006 dishes, RGB + depth + weight/nutrition GT | CC BY 4.0 |
| **USDA FoodData Central** | 370,000+ nutrition entries | Public Domain |
| **Bảng TPDD Việt Nam** | ~500 Vietnamese dishes | Public |
| **GI Tables** | International Tables of Glycemic Index | Academic |

## Notes

- `nutrition5k/raw/` is gitignored (large binary files)
- `vn_demo/` photos taken by Hoài for demo purposes
- Ground truth for VN demo: estimated from literature (validated on Nutrition5k)

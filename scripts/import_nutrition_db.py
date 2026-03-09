"""
Import Vietnamese food nutrition data to JSON and generate SQL seed.

Sources:
- USDA FoodData Central (https://fdc.nal.usda.gov/)
- Bảng Thành phần Dinh dưỡng Thực phẩm Việt Nam (Viện Dinh dưỡng Quốc gia)
- International Tables of Glycemic Index (Foster-Powell et al.)

Usage:
    python scripts/import_nutrition_db.py
    python scripts/import_nutrition_db.py --output data/nutrition_db/vn_food_nutrition.json
    python scripts/import_nutrition_db.py --generate-sql
"""

import json
import argparse
from pathlib import Path

OUTPUT_JSON = Path("data/nutrition_db/vn_food_nutrition.json")
OUTPUT_SQL = Path("data/nutrition_db/seed_nutrition.sql")

# Curated nutrition data for 10 Vietnamese dishes in scope
# Sources: USDA FoodData Central + Bảng TPDD Việt Nam + GI Tables
VN_FOOD_NUTRITION = [
    {
        "food_id": "vn_com_trang",
        "food_name_vi": "Cơm trắng",
        "food_name_en": "White rice (cooked)",
        "category": "rice",
        "is_liquid": False,
        "gi_index": 73,
        "gi_category": "high",
        "carb_per_100g": 28.2,
        "protein_per_100g": 2.7,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 0.4,
        "calories_per_100g": 130,
        "typical_serving_g": 200,
        "source": "USDA #168878 + VN TPDD",
        "notes": "1 chén cơm ~200g",
    },
    {
        "food_id": "vn_pho_bo",
        "food_name_vi": "Phở bò (bánh phở)",
        "food_name_en": "Rice noodles (pho)",
        "category": "noodle_soup",
        "is_liquid": True,
        "gi_index": 46,
        "gi_category": "low",
        "carb_per_100g": 22.5,
        "protein_per_100g": 1.6,
        "fat_per_100g": 0.2,
        "fiber_per_100g": 0.9,
        "calories_per_100g": 109,
        "typical_serving_g": 450,
        "source": "USDA #168921 + GI Tables",
        "notes": "Carb tính cho bánh phở khô, tô M ~450g tổng",
    },
    {
        "food_id": "vn_bun_bo_hue",
        "food_name_vi": "Bún bò Huế (bún)",
        "food_name_en": "Rice vermicelli (bun)",
        "category": "noodle_soup",
        "is_liquid": True,
        "gi_index": 58,
        "gi_category": "medium",
        "carb_per_100g": 25.1,
        "protein_per_100g": 2.0,
        "fat_per_100g": 0.1,
        "fiber_per_100g": 0.8,
        "calories_per_100g": 108,
        "typical_serving_g": 500,
        "source": "USDA #168921 + VN TPDD",
        "notes": "Bún sợi to hơn bánh phở",
    },
    {
        "food_id": "vn_banh_mi",
        "food_name_vi": "Bánh mì",
        "food_name_en": "Vietnamese baguette",
        "category": "bread",
        "is_liquid": False,
        "gi_index": 80,
        "gi_category": "high",
        "carb_per_100g": 50.6,
        "protein_per_100g": 8.2,
        "fat_per_100g": 3.3,
        "fiber_per_100g": 2.4,
        "calories_per_100g": 274,
        "typical_serving_g": 150,
        "source": "USDA #172686 + GI Tables",
        "notes": "1 ổ bánh mì ~150g",
    },
    {
        "food_id": "vn_com_tam",
        "food_name_vi": "Cơm tấm",
        "food_name_en": "Broken rice (cooked)",
        "category": "rice",
        "is_liquid": False,
        "gi_index": 70,
        "gi_category": "high",
        "carb_per_100g": 27.0,
        "protein_per_100g": 2.5,
        "fat_per_100g": 0.5,
        "fiber_per_100g": 0.5,
        "calories_per_100g": 126,
        "typical_serving_g": 250,
        "source": "VN TPDD + GI Tables (similar to white rice)",
        "notes": "Đĩa cơm tấm ~250g cơm",
    },
    {
        "food_id": "vn_bun_thit_nuong",
        "food_name_vi": "Bún thịt nướng (bún)",
        "food_name_en": "Rice vermicelli",
        "category": "noodle_dry",
        "is_liquid": False,
        "gi_index": 58,
        "gi_category": "medium",
        "carb_per_100g": 25.1,
        "protein_per_100g": 2.0,
        "fat_per_100g": 0.1,
        "fiber_per_100g": 0.8,
        "calories_per_100g": 108,
        "typical_serving_g": 300,
        "source": "USDA #168921",
        "notes": "Bún khô (không nước), 1 tô ~300g bún",
    },
    {
        "food_id": "vn_mi_xao",
        "food_name_vi": "Mì xào",
        "food_name_en": "Stir-fried egg noodles",
        "category": "noodle_dry",
        "is_liquid": False,
        "gi_index": 52,
        "gi_category": "low",
        "carb_per_100g": 23.0,
        "protein_per_100g": 4.5,
        "fat_per_100g": 6.0,
        "fiber_per_100g": 1.2,
        "calories_per_100g": 168,
        "typical_serving_g": 350,
        "source": "USDA #168919 + GI Tables",
        "notes": "Mì xào với rau và thịt",
    },
    {
        "food_id": "vn_chao",
        "food_name_vi": "Cháo gạo",
        "food_name_en": "Rice porridge (congee)",
        "category": "porridge",
        "is_liquid": True,
        "gi_index": 78,
        "gi_category": "high",
        "carb_per_100g": 8.5,
        "protein_per_100g": 1.0,
        "fat_per_100g": 0.2,
        "fiber_per_100g": 0.1,
        "calories_per_100g": 46,
        "typical_serving_g": 400,
        "source": "USDA #168870 + GI Tables",
        "notes": "Cháo loãng tiêu chuẩn",
    },
    {
        "food_id": "vn_xoi",
        "food_name_vi": "Xôi (nếp)",
        "food_name_en": "Sticky rice (cooked)",
        "category": "rice",
        "is_liquid": False,
        "gi_index": 87,
        "gi_category": "high",
        "carb_per_100g": 36.7,
        "protein_per_100g": 3.5,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 1.7,
        "calories_per_100g": 169,
        "typical_serving_g": 200,
        "source": "USDA #168879 + GI Tables",
        "notes": "1 gói xôi ~200g",
    },
    {
        "food_id": "vn_tra_sua",
        "food_name_vi": "Trà sữa trân châu",
        "food_name_en": "Bubble tea (boba)",
        "category": "drink",
        "is_liquid": True,
        "gi_index": 65,
        "gi_category": "medium",
        "carb_per_100g": 15.0,
        "protein_per_100g": 0.5,
        "fat_per_100g": 1.5,
        "fiber_per_100g": 0.0,
        "calories_per_100g": 80,
        "typical_serving_g": 500,
        "source": "Estimated from commercial products + GI Tables",
        "notes": "Ly M ~500ml, đường 100%",
    },
]


def export_json(output_path: Path) -> None:
    """Export nutrition data to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "version": "1.0",
        "schema": "insight-nutrition-db-v1",
        "description": "Vietnamese food nutrition database (curated from USDA + VN TPDD + GI Tables)",
        "sources": [
            "USDA FoodData Central (https://fdc.nal.usda.gov/)",
            "Bảng Thành phần Dinh dưỡng Thực phẩm Việt Nam",
            "International Tables of Glycemic Index (Foster-Powell et al.)",
        ],
        "total_items": len(VN_FOOD_NUTRITION),
        "items": VN_FOOD_NUTRITION,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported {len(VN_FOOD_NUTRITION)} nutrition items -> {output_path}")


def generate_sql(output_path: Path) -> None:
    """Generate SQL INSERT statements for PostgreSQL foods table."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "-- Auto-generated Vietnamese food nutrition seed data",
        "-- Source: scripts/import_nutrition_db.py",
        f"-- Items: {len(VN_FOOD_NUTRITION)}",
        "",
        "INSERT INTO foods (name_vi, name_en, carb_per_100g, protein_per_100g, fat_per_100g, fiber_per_100g, gi_value, gi_category, category, is_liquid) VALUES",
    ]

    values = []
    for item in VN_FOOD_NUTRITION:
        val = (
            f"('{_escape_sql(item['food_name_vi'])}', "
            f"'{_escape_sql(item['food_name_en'])}', "
            f"{item['carb_per_100g']}, "
            f"{item['protein_per_100g']}, "
            f"{item['fat_per_100g']}, "
            f"{item['fiber_per_100g']}, "
            f"{item['gi_index']}, "
            f"'{item['gi_category']}', "
            f"'{item['category']}', "
            f"{str(item['is_liquid']).upper()})"
        )
        values.append(val)

    lines.append(",\n".join(values) + ";")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Generated SQL seed -> {output_path}")


def _escape_sql(value: str) -> str:
    """Escape single quotes for SQL."""
    return value.replace("'", "''")


def print_summary() -> None:
    """Print summary table of nutrition data."""
    print("\n📊 Vietnamese Food Nutrition Summary:")
    print(f"{'Món':<30} {'GI':>4} {'Carb/100g':>10} {'Cal/100g':>10} {'Category':<15}")
    print("-" * 75)
    for item in VN_FOOD_NUTRITION:
        print(
            f"{item['food_name_vi']:<30} "
            f"{item['gi_index']:>4} "
            f"{item['carb_per_100g']:>9.1f}g "
            f"{item['calories_per_100g']:>9} "
            f"{item['category']:<15}"
        )
    print(f"\nTotal: {len(VN_FOOD_NUTRITION)} items")


def main():
    parser = argparse.ArgumentParser(description="Import Vietnamese food nutrition database")
    parser.add_argument("--output", type=Path, default=OUTPUT_JSON, help="JSON output path")
    parser.add_argument("--generate-sql", action="store_true", help="Also generate SQL seed file")
    parser.add_argument("--sql-output", type=Path, default=OUTPUT_SQL, help="SQL output path")
    parser.add_argument("--summary", action="store_true", help="Print summary table")
    args = parser.parse_args()

    export_json(args.output)

    if args.generate_sql:
        generate_sql(args.sql_output)

    if args.summary:
        print_summary()


if __name__ == "__main__":
    main()

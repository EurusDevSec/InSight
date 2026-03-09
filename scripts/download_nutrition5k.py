"""
Download Nutrition5k subset and parse to InSight format.

Nutrition5k (Google Research, 2021):
- 5,006 dishes with lab-grade ground truth
- Each dish: RGB overhead + side images, depth map
- Ground truth: total weight (g), calories, fat, carb, protein
- License: Creative Commons BY 4.0
- Source: https://github.com/google-research-datasets/Nutrition5k

Usage:
    # Step 1: Download metadata CSV from Nutrition5k repo
    # Place at: data/nutrition5k/raw/metadata.csv

    # Step 2: Parse to InSight format
    python scripts/download_nutrition5k.py

    # With custom options
    python scripts/download_nutrition5k.py --max-samples 200 --metadata data/nutrition5k/raw/metadata.csv
"""

import json
import csv
import argparse
from pathlib import Path

# Default paths
DEFAULT_METADATA = Path("data/nutrition5k/raw/metadata.csv")
DEFAULT_OUTPUT = Path("data/nutrition5k/parsed/nutrition5k_subset.json")


def parse_nutrition5k(metadata_path: Path, max_samples: int = 500) -> list[dict]:
    """Parse Nutrition5k metadata CSV to InSight format.

    Expected CSV columns: dish_id, dish_name, total_weight, total_calories,
    total_fat, total_carb, total_protein
    """
    samples = []

    with open(metadata_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_samples:
                break

            dish_id = row.get("dish_id", "").strip()
            if not dish_id:
                continue

            total_weight = _safe_float(row.get("total_weight", 0))
            calories = _safe_float(row.get("total_calories", 0))
            carb = _safe_float(row.get("total_carb", 0))
            protein = _safe_float(row.get("total_protein", 0))
            fat = _safe_float(row.get("total_fat", 0))

            # Skip invalid entries
            if total_weight <= 0:
                continue

            sample = {
                "food_info": {
                    "name_en": row.get("dish_name", f"dish_{dish_id}").strip(),
                    "category": "mixed",
                    "gi_index": None,
                    "carb_per_100g": round(carb / total_weight * 100, 2) if total_weight > 0 else None,
                },
                "sample": {
                    "sample_id": f"n5k_{dish_id}",
                    "source": "nutrition5k",
                    "images": [
                        {"angle": "overhead", "file": f"dish_{dish_id}/rgb_overhead.png"},
                        {"angle": "side", "file": f"dish_{dish_id}/rgb_side.png"},
                    ],
                    "depth_image": f"dish_{dish_id}/depth_overhead.png",
                },
                "ground_truth": {
                    "total_weight_g": total_weight,
                    "measurement_method": "lab_scale",
                    "nutrition": {
                        "calories": calories,
                        "total_carb_g": carb,
                        "protein_g": protein,
                        "fat_g": fat,
                    },
                },
                "metadata": {
                    "source_dataset": "nutrition5k",
                    "original_id": dish_id,
                },
            }
            samples.append(sample)

    return samples


def _safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def generate_sample_metadata(output_path: Path) -> None:
    """Generate a sample metadata.csv for testing when no real data available."""
    sample_csv = output_path.parent / "metadata.csv"
    if sample_csv.exists():
        return

    sample_csv.parent.mkdir(parents=True, exist_ok=True)
    print(f"ℹ️  No metadata.csv found. Generating sample at {sample_csv}")
    print("   Replace this with real Nutrition5k metadata from:")
    print("   https://github.com/google-research-datasets/Nutrition5k")

    # Sample entries for development/testing
    sample_data = [
        {"dish_id": "1556", "dish_name": "Chicken rice bowl", "total_weight": "385", "total_calories": "512", "total_fat": "18.0", "total_carb": "52.0", "total_protein": "30.0"},
        {"dish_id": "1560", "dish_name": "Mixed plate salad", "total_weight": "290", "total_calories": "320", "total_fat": "12.0", "total_carb": "38.0", "total_protein": "15.0"},
        {"dish_id": "1570", "dish_name": "Pasta with sauce", "total_weight": "420", "total_calories": "580", "total_fat": "20.0", "total_carb": "65.0", "total_protein": "22.0"},
        {"dish_id": "1575", "dish_name": "Grilled fish plate", "total_weight": "350", "total_calories": "410", "total_fat": "15.0", "total_carb": "30.0", "total_protein": "35.0"},
        {"dish_id": "1580", "dish_name": "Beef stew with bread", "total_weight": "450", "total_calories": "620", "total_fat": "22.0", "total_carb": "55.0", "total_protein": "40.0"},
    ]

    with open(sample_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["dish_id", "dish_name", "total_weight", "total_calories", "total_fat", "total_carb", "total_protein"])
        writer.writeheader()
        writer.writerows(sample_data)

    print(f"   Generated {len(sample_data)} sample entries for development.\n")


def main():
    parser = argparse.ArgumentParser(description="Parse Nutrition5k metadata to InSight format")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA, help="Path to Nutrition5k metadata CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path")
    parser.add_argument("--max-samples", type=int, default=500, help="Max samples to parse (default: 500)")
    args = parser.parse_args()

    # Ensure directories exist
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Generate sample if metadata doesn't exist
    if not args.metadata.exists():
        generate_sample_metadata(args.metadata)

    if not args.metadata.exists():
        print(f"❌ Metadata file not found: {args.metadata}")
        print("   Download from: https://github.com/google-research-datasets/Nutrition5k")
        return

    # Parse
    print(f"📥 Parsing Nutrition5k metadata from {args.metadata}...")
    samples = parse_nutrition5k(args.metadata, max_samples=args.max_samples)

    if not samples:
        print("❌ No valid samples found in metadata.")
        return

    # Write output
    output = {
        "version": "1.0",
        "schema": "insight-food-sample-v1",
        "source": "nutrition5k",
        "description": "Nutrition5k benchmark dataset parsed to InSight format",
        "total_samples": len(samples),
        "samples": samples,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Parsed {len(samples)} Nutrition5k samples -> {args.output}")

    # Stats
    weights = [s["ground_truth"]["total_weight_g"] for s in samples]
    carbs = [s["ground_truth"]["nutrition"]["total_carb_g"] for s in samples]
    print(f"   Weight range: {min(weights):.0f}g - {max(weights):.0f}g (avg: {sum(weights)/len(weights):.0f}g)")
    print(f"   Carb range: {min(carbs):.1f}g - {max(carbs):.1f}g (avg: {sum(carbs)/len(carbs):.1f}g)")


if __name__ == "__main__":
    main()

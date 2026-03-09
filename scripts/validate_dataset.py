"""
Validate InSight dataset integrity.

Supports two formats:
- Legacy POC format (data/poc/annotations/ground_truth.json)
- InSight v1 format (data/processed/dataset_v1.json)

Usage:
    python scripts/validate_dataset.py
    python scripts/validate_dataset.py --path data/processed/dataset_v1.json
    python scripts/validate_dataset.py --path data/poc/annotations/ground_truth.json
    python scripts/validate_dataset.py --validate-all
"""

import json
import argparse
from pathlib import Path

REQUIRED_FIELDS_V1 = ["food_info", "sample", "ground_truth", "metadata"]
VALID_SOURCES = ["nutrition5k", "vn_demo", "ecust"]
VALID_CATEGORIES = ["rice", "noodle_soup", "noodle_dry", "bread", "porridge", "drink", "mixed", "other"]


def detect_format(data: dict) -> str:
    """Detect dataset format: 'v1' (InSight) or 'legacy' (POC)."""
    samples = data.get("samples", [])
    if not samples:
        entries = data.get("entries", [])
        if entries:
            return "ground_truth_v1"
        return "unknown"

    first = samples[0]
    if "food_info" in first and "sample" in first:
        return "v1"
    if "image_file" in first and "food_category" in first:
        return "legacy"
    return "unknown"


def validate_v1_dataset(data_path: Path) -> bool:
    """Validate InSight v1 format dataset."""
    errors = []
    warnings = []

    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    samples = data.get("samples", [])
    fmt = detect_format(data)

    if fmt == "ground_truth_v1":
        return validate_ground_truth_v1(data_path, data)

    if fmt != "v1":
        print(f"⚠️  Unknown format in {data_path}, trying legacy validation...")
        return validate_legacy_dataset(str(data_path))

    print(f"📊 Validating {len(samples)} samples from {data_path} (InSight v1 format)...\n")

    categories = {}
    sources = {}
    sample_ids = set()

    for i, sample in enumerate(samples):
        sid = sample.get("sample", {}).get("sample_id", f"unknown_{i}")

        # Check required fields
        for field in REQUIRED_FIELDS_V1:
            if field not in sample:
                errors.append(f"[{sid}] Missing required field: {field}")

        # Check duplicate IDs
        if sid in sample_ids:
            errors.append(f"[{sid}] Duplicate sample_id")
        sample_ids.add(sid)

        # Check source
        source = sample.get("sample", {}).get("source", "unknown")
        sources[source] = sources.get(source, 0) + 1
        if source not in VALID_SOURCES:
            warnings.append(f"[{sid}] Unknown source: {source}")

        # Check category
        category = sample.get("food_info", {}).get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1
        if category not in VALID_CATEGORIES:
            warnings.append(f"[{sid}] Unknown category: {category}")

        # Check ground truth
        gt = sample.get("ground_truth", {})
        weight = gt.get("total_weight_g", 0)
        if weight <= 0:
            errors.append(f"[{sid}] total_weight_g <= 0")

        nutrition = gt.get("nutrition", {})
        if not nutrition:
            errors.append(f"[{sid}] Missing nutrition data")
        else:
            for key in ["calories", "total_carb_g", "protein_g", "fat_g"]:
                if key not in nutrition:
                    warnings.append(f"[{sid}] Missing nutrition.{key}")

        # Check images (for VN demo samples)
        if source == "vn_demo":
            images = sample.get("sample", {}).get("images", [])
            if len(images) < 2:
                warnings.append(f"[{sid}] VN demo sample should have ≥ 2 images, has {len(images)}")

    _print_report(samples, errors, warnings, categories, sources)
    return len(errors) == 0


def validate_ground_truth_v1(data_path: Path, data: dict) -> bool:
    """Validate ground_truth.json (v1 format)."""
    entries = data.get("entries", [])
    errors = []

    print(f"📊 Validating {len(entries)} ground truth entries from {data_path}...\n")

    for entry in entries:
        sid = entry.get("sample_id", "unknown")
        if entry.get("total_weight_g", 0) <= 0:
            errors.append(f"[{sid}] total_weight_g <= 0")

    print("=" * 50)
    if errors:
        print(f"❌ {len(errors)} errors:")
        for e in errors:
            print(f"   - {e}")
    else:
        print(f"✅ All {len(entries)} entries valid!")
    print("=" * 50)
    return len(errors) == 0


def validate_legacy_dataset(gt_path: str = "data/annotations/ground_truth.json") -> bool:
    """Validate legacy POC format dataset."""
    errors = []
    warnings = []

    gt_file = Path(gt_path)
    if not gt_file.exists():
        print(f"❌ File not found: {gt_path}")
        return False

    with open(gt_file, encoding="utf-8") as f:
        data = json.load(f)

    samples = data.get("samples", [])
    base_dir = gt_file.parent.parent

    print(f"📊 Validating {len(samples)} samples from {gt_path} (legacy format)...\n")

    categories = {}

    for sample in samples:
        sample_id = sample.get("id", "unknown")
        category = sample.get("food_category", "unknown")
        categories[category] = categories.get(category, 0) + 1

        # Check image exists
        img_file = sample.get("image_file", "")
        if img_file:
            img_path = base_dir / img_file
            if not img_path.exists():
                errors.append(f"[{sample_id}] Missing image: {img_path}")

        # Check ground truth
        gt = sample.get("ground_truth", {})
        if gt.get("total_weight_g", 0) <= 0:
            errors.append(f"[{sample_id}] total_weight_g <= 0")

        if gt.get("is_liquid") and gt.get("liquid_volume_ml", 0) <= 0:
            warnings.append(f"[{sample_id}] Liquid dish missing liquid_volume_ml")

        # Check metadata
        if not sample.get("metadata", {}).get("restaurant"):
            warnings.append(f"[{sample_id}] Missing restaurant info")

        # Check file extension
        if img_file and not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
            warnings.append(f"[{sample_id}] Not an image file: {img_file}")

    _print_report(samples, errors, warnings, categories)
    return len(errors) == 0


def validate_nutrition_db(path: Path = Path("data/nutrition_db/vn_food_nutrition.json")) -> bool:
    """Validate nutrition database JSON."""
    if not path.exists():
        print(f"⚠️  Nutrition DB not found: {path}")
        return False

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    errors = []

    print(f"📊 Validating nutrition DB ({len(items)} items)...\n")

    for item in items:
        name = item.get("food_name_vi", "unknown")
        if item.get("carb_per_100g", 0) < 0:
            errors.append(f"[{name}] Negative carb_per_100g")
        if item.get("gi_index", 0) < 0 or item.get("gi_index", 0) > 100:
            errors.append(f"[{name}] GI index out of range (0-100)")
        if item.get("calories_per_100g", 0) <= 0:
            errors.append(f"[{name}] Invalid calories_per_100g")

    if errors:
        print(f"❌ {len(errors)} errors:")
        for e in errors:
            print(f"   - {e}")
    else:
        print(f"✅ Nutrition DB: {len(items)} items valid!")

    return len(errors) == 0


def validate_density_factors(path: Path = Path("data/nutrition_db/density_factors.json")) -> bool:
    """Validate density factors JSON."""
    if not path.exists():
        print(f"⚠️  Density factors not found: {path}")
        return False

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    errors = []

    print(f"📊 Validating density factors ({len(items)} items)...\n")

    for item in items:
        name = item.get("name_vi", "unknown")
        sr = item.get("solid_ratio", -1)
        if sr < 0 or sr > 1:
            errors.append(f"[{name}] solid_ratio out of range (0-1): {sr}")
        density = item.get("density_g_per_ml", -1)
        if density <= 0:
            errors.append(f"[{name}] Invalid density: {density}")

    if errors:
        print(f"❌ {len(errors)} errors:")
        for e in errors:
            print(f"   - {e}")
    else:
        print(f"✅ Density factors: {len(items)} items valid!")

    return len(errors) == 0


def _print_report(samples, errors, warnings, categories, sources=None):
    """Print validation report."""
    print("=" * 50)

    print("📊 Category distribution:")
    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count}")
    print()

    if sources:
        print("📊 Source distribution:")
        for src, count in sorted(sources.items()):
            print(f"   - {src}: {count}")
        print()

    if errors:
        print(f"❌ {len(errors)} ERRORS:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ No errors found!")

    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNINGS:")
        for w in warnings:
            print(f"   - {w}")

    print("=" * 50)
    valid = len(samples) - len(errors)
    print(f"📈 Result: {valid}/{len(samples)} samples valid")


def main():
    parser = argparse.ArgumentParser(description="Validate InSight dataset")
    parser.add_argument(
        "--path",
        default="data/processed/dataset_v1.json",
        help="Path to dataset JSON (v1 or legacy format)",
    )
    parser.add_argument(
        "--validate-all",
        action="store_true",
        help="Validate all data files (dataset + nutrition DB + density factors)",
    )
    args = parser.parse_args()

    all_valid = True

    if args.validate_all:
        print("🔍 Validating all InSight data files...\n")

        # Dataset (if exists)
        dataset_path = Path("data/processed/dataset_v1.json")
        if dataset_path.exists():
            if not validate_v1_dataset(dataset_path):
                all_valid = False
            print()

        # Legacy POC
        poc_path = Path("data/poc/annotations/ground_truth.json")
        if poc_path.exists():
            if not validate_legacy_dataset(str(poc_path)):
                all_valid = False
            print()

        # Nutrition DB
        if not validate_nutrition_db():
            all_valid = False
        print()

        # Density factors
        if not validate_density_factors():
            all_valid = False

        print("\n" + "=" * 50)
        if all_valid:
            print("✅ ALL VALIDATIONS PASSED!")
        else:
            print("❌ SOME VALIDATIONS FAILED!")
        print("=" * 50)
    else:
        path = Path(args.path)
        if not path.exists():
            print(f"❌ File not found: {path}")
            exit(1)

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        fmt = detect_format(data)
        if fmt in ("v1", "ground_truth_v1"):
            all_valid = validate_v1_dataset(path)
        elif fmt == "legacy":
            all_valid = validate_legacy_dataset(str(path))
        else:
            print(f"❌ Unknown dataset format in {path}")
            all_valid = False

    exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()

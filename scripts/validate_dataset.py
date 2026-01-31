"""
Kiểm tra tính toàn vẹn của dataset
Chạy: python scripts/validate_dataset.py [--path <path_to_ground_truth>]
"""

import json
import argparse
from pathlib import Path


def validate_dataset(gt_path: str = "data/annotations/ground_truth.json"):
    errors = []
    warnings = []

    # Load ground truth
    gt_file = Path(gt_path)
    if not gt_file.exists():
        print(f"❌ Không tìm thấy {gt_path}")
        return False
    # mo ft_file
    with open(gt_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = data["samples"]
    base_dir = gt_file.parent.parent  # data/poc/ hoặc data/

    print(f"📊 Kiểm tra {len(samples)} mẫu từ {gt_path}...\n")

    # Thống kê theo category
    categories = {}

    for sample in samples:
        sample_id = sample["id"]
        category = sample.get("food_category", "unknown")
        categories[category] = categories.get(category, 0) + 1

        # 1. Kiểm tra ảnh tồn tại
        img_path = base_dir / sample["image_file"]
        if not img_path.exists():
            errors.append(f"[{sample_id}] Thiếu ảnh: {img_path}")

        # 2. Kiểm tra ground truth hợp lệ
        gt = sample["ground_truth"]
        if gt["total_weight_g"] <= 0:
            errors.append(f"[{sample_id}] Trọng lượng <= 0")

        if gt["is_liquid"] and gt["liquid_volume_ml"] <= 0:
            warnings.append(f"[{sample_id}] Món nước nhưng không có thể tích nước")

        # 3. Kiểm tra metadata
        if not sample["metadata"].get("restaurant"):
            warnings.append(f"[{sample_id}] Thiếu thông tin quán")

        # 4. Kiểm tra image file extension
        img_file = sample["image_file"]
        if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
            warnings.append(f"[{sample_id}] File không phải ảnh: {img_file}")

    # Report
    print("=" * 50)

    # Thống kê category
    print("📊 Thống kê theo loại:")
    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count} mẫu")
    print()

    if errors:
        print(f"❌ {len(errors)} LỖI:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ Không có lỗi nghiêm trọng!")

    if warnings:
        print(f"\n⚠️  {len(warnings)} CẢNH BÁO:")
        for w in warnings:
            print(f"   - {w}")

    print("=" * 50)
    valid = len(samples) - len(errors)
    print(f"📈 Kết quả: {valid}/{len(samples)} mẫu hợp lệ")

    return len(errors) == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate InSight dataset")
    parser.add_argument(
        "--path",
        default="data/annotations/ground_truth.json",
        help="Path to ground_truth.json",
    )
    args = parser.parse_args()

    success = validate_dataset(args.path)
    exit(0 if success else 1)

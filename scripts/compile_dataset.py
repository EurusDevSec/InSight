"""
Compile Nutrition5k subset + VN demo samples into a unified dataset.

Usage:
    python scripts/compile_dataset.py
    python scripts/compile_dataset.py --n5k-path data/nutrition5k/parsed/nutrition5k_subset.json
"""

import json
import argparse
from pathlib import Path

N5K_PATH = Path("data/nutrition5k/parsed/nutrition5k_subset.json")
VN_DEMO_DIR = Path("data/vn_demo")
OUTPUT_PATH = Path("data/processed/dataset_v1.json")
GT_OUTPUT = Path("data/annotations/ground_truth.json")


def load_json_samples(path: Path) -> list[dict]:
    """Load samples from a JSON dataset file."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("samples", [])


def load_vn_demo_samples(vn_dir: Path) -> list[dict]:
    """Load VN demo samples from individual JSON files."""
    samples = []
    if not vn_dir.exists():
        return samples

    for food_dir in sorted(vn_dir.iterdir()):
        if not food_dir.is_dir():
            continue
        for sample_dir in sorted(food_dir.iterdir()):
            if not sample_dir.is_dir():
                continue
            json_files = list(sample_dir.glob("*.json"))
            if json_files:
                with open(json_files[0], encoding="utf-8") as f:
                    samples.append(json.load(f))

    return samples


def compile_ground_truth(samples: list[dict]) -> dict:
    """Extract ground truth from all samples for validation."""
    gt_entries = []
    for s in samples:
        gt = s.get("ground_truth", {})
        entry = {
            "sample_id": s.get("sample", {}).get("sample_id", "unknown"),
            "source": s.get("sample", {}).get("source", "unknown"),
            "total_weight_g": gt.get("total_weight_g", 0),
            "measurement_method": gt.get("measurement_method", "unknown"),
            "nutrition": gt.get("nutrition", {}),
        }
        gt_entries.append(entry)

    return {
        "version": "1.0",
        "description": "Ground truth annotations for InSight dataset",
        "total_entries": len(gt_entries),
        "entries": gt_entries,
    }


def main():
    parser = argparse.ArgumentParser(description="Compile InSight dataset")
    parser.add_argument("--n5k-path", type=Path, default=N5K_PATH, help="Nutrition5k parsed JSON")
    parser.add_argument("--vn-dir", type=Path, default=VN_DEMO_DIR, help="VN demo samples directory")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output dataset path")
    parser.add_argument("--gt-output", type=Path, default=GT_OUTPUT, help="Ground truth output path")
    args = parser.parse_args()

    # Load samples
    print("📥 Loading samples...")
    n5k_samples = load_json_samples(args.n5k_path)
    print(f"   Nutrition5k: {len(n5k_samples)} samples")

    vn_samples = load_vn_demo_samples(args.vn_dir)
    print(f"   VN demo: {len(vn_samples)} samples")

    all_samples = n5k_samples + vn_samples
    total = len(all_samples)

    if total == 0:
        print("⚠️  No samples found. Run these scripts first:")
        print("   python scripts/download_nutrition5k.py")
        print("   (VN demo photos will be added by Hoài)")
        return

    # Compile dataset
    output = {
        "version": "1.0",
        "schema": "insight-food-sample-v1",
        "description": "InSight dataset: Nutrition5k benchmark + Vietnamese demo samples",
        "nutrition5k_count": len(n5k_samples),
        "vn_demo_count": len(vn_samples),
        "total_samples": total,
        "samples": all_samples,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Compile ground truth
    gt = compile_ground_truth(all_samples)
    args.gt_output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.gt_output, "w", encoding="utf-8") as f:
        json.dump(gt, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Dataset compiled:")
    print(f"   Nutrition5k: {len(n5k_samples)} samples")
    print(f"   VN demo: {len(vn_samples)} samples")
    print(f"   Total: {total} -> {args.output}")
    print(f"   Ground truth: {args.gt_output}")

    # Stats
    if all_samples:
        weights = [s.get("ground_truth", {}).get("total_weight_g", 0) for s in all_samples if s.get("ground_truth", {}).get("total_weight_g", 0) > 0]
        if weights:
            print(f"\n📊 Stats:")
            print(f"   Weight: {min(weights):.0f}g - {max(weights):.0f}g (avg: {sum(weights)/len(weights):.0f}g)")

        sources = {}
        for s in all_samples:
            src = s.get("sample", {}).get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1
        print(f"   Sources: {sources}")


if __name__ == "__main__":
    main()

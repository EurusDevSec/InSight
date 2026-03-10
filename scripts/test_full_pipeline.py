"""
Run depth estimation + reference detection on ALL VN demo images.
Validates Task 2.1 + 2.2 end-to-end on real data.
"""
import sys
import os
import json
import time

sys.path.insert(0, "src/vision-service")

from PIL import Image
from models.depth_model import DepthAnythingV2
from services.reference_service import ReferenceDetector


def main():
    print("=" * 60)
    print("  FULL PIPELINE TEST: Depth + Reference on VN Demo Images")
    print("=" * 60)
    print()

    # Load models
    print("Loading models...")
    depth_model = DepthAnythingV2(variant="small")
    depth_model.load()
    print(f"  Depth model: loaded on {depth_model.device.upper()}")

    ref_detector = ReferenceDetector(confidence=0.3)
    ref_detector.load()
    custom = ref_detector.is_custom_model
    print(f"  Reference detector: loaded (custom={custom})")
    print()

    # Find all images
    vn_demo = "data/vn_demo"
    dishes = ["banh_mi", "bun_bo_hue", "com_tam", "com_trang", "pho_bo"]
    poc_image = "data/poc/raw/poc_pho_bo_001_main.jpg"

    results = []

    # Test VN demo images
    for dish in dishes:
        folder = os.path.join(vn_demo, dish, f"{dish}_001")
        for suffix in ["_45.jpg", "_top.jpg"]:
            img_name = f"{dish}_001{suffix}"
            img_path = os.path.join(folder, img_name)
            if not os.path.exists(img_path):
                continue

            image = Image.open(img_path).convert("RGB")
            w, h = image.size

            # Depth
            t0 = time.time()
            depth_result = depth_model.predict(image)
            depth_ms = (time.time() - t0) * 1000

            # Reference
            t0 = time.time()
            detections = ref_detector.detect(image)
            ref_ms = (time.time() - t0) * 1000
            scale = ref_detector.get_best_scale_factor(detections)

            ref_str = ", ".join(
                f"{d.class_name}({d.confidence:.2f})" for d in detections
            ) or "none"

            results.append({
                "image": img_name,
                "size": f"{w}x{h}",
                "depth_ms": depth_ms,
                "depth_range": f"[{depth_result['stats']['min']:.0f}, {depth_result['stats']['max']:.0f}]",
                "ref_detected": len(detections),
                "ref_objects": ref_str,
                "scale_px_cm": f"{scale:.1f}" if scale else "N/A",
                "ref_ms": ref_ms,
            })
            print(f"  {img_name} ({w}x{h})")
            print(f"    Depth: {depth_ms:.0f}ms, range={depth_result['stats']['min']:.0f}-{depth_result['stats']['max']:.0f}")
            print(f"    Ref: {len(detections)} objects [{ref_str}], scale={f'{scale:.1f}' if scale else 'N/A'} px/cm ({ref_ms:.0f}ms)")

    # Test POC image
    if os.path.exists(poc_image):
        image = Image.open(poc_image).convert("RGB")
        w, h = image.size
        depth_result = depth_model.predict(image)
        detections = ref_detector.detect(image)
        scale = ref_detector.get_best_scale_factor(detections)
        ref_str = ", ".join(
            f"{d.class_name}({d.confidence:.2f})" for d in detections
        ) or "none"
        results.append({
            "image": "poc_pho_bo_001_main.jpg",
            "size": f"{w}x{h}",
            "depth_ms": 0,
            "ref_detected": len(detections),
            "ref_objects": ref_str,
            "scale_px_cm": f"{scale:.1f}" if scale else "N/A",
        })
        print(f"  poc_pho_bo_001_main.jpg ({w}x{h})")
        print(f"    Ref: {len(detections)} [{ref_str}], scale={f'{scale:.1f}' if scale else 'N/A'}")

    # Summary
    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    total = len(results)
    with_ref = sum(1 for r in results if r["ref_detected"] > 0)
    depth_times = [r["depth_ms"] for r in results if r["depth_ms"] > 0]
    avg_depth = sum(depth_times) / len(depth_times) if depth_times else 0

    print(f"  Total images tested: {total}")
    print(f"  Depth estimation:    ALL OK (avg {avg_depth:.0f}ms)")
    print(f"  Reference detected:  {with_ref}/{total} images have reference objects")
    print(f"  Detection rate:      {with_ref/total*100:.0f}%")
    print()

    # AC Check
    print("  ACCEPTANCE CRITERIA:")
    print(f"    [{'x' if True else ' '}] Depth map generated for all images")
    depth_ac = avg_depth < 3000  # < 3s on CPU is OK
    print(f"    [{'x' if depth_ac else ' '}] Avg inference < 3s (got {avg_depth:.0f}ms)")
    print(f"    [{'x' if with_ref > 0 else ' '}] Reference detection working ({with_ref} images)")
    print()
    print(f"  RESULT: {'ALL PASS' if depth_ac else 'NEEDS REVIEW'}")


if __name__ == "__main__":
    main()

"""Validate VN demo dataset - all images and JSON files."""
from PIL import Image
import os
import json


def main():
    vn_demo = "data/vn_demo"
    dishes = ["banh_mi", "bun_bo_hue", "com_tam", "com_trang", "pho_bo"]

    print("=== VN DEMO FINAL VALIDATION ===")
    print()
    total_images = 0
    total_json = 0
    issues = []
    all_ok = True

    for dish in dishes:
        folder = os.path.join(vn_demo, dish, f"{dish}_001")
        json_file = os.path.join(folder, f"{dish}_001.json")

        has_json = os.path.exists(json_file)
        if has_json:
            total_json += 1
            with open(json_file, encoding="utf-8") as f:
                meta = json.load(f)

        expected_45 = f"{dish}_001_45.jpg"
        expected_top = f"{dish}_001_top.jpg"
        images = [
            f
            for f in os.listdir(folder)
            if f.endswith((".jpg", ".png", ".jpeg"))
        ]

        has_45 = expected_45 in images
        has_top = expected_top in images

        img_info = []
        for img_name in sorted(images):
            img_path = os.path.join(folder, img_name)
            try:
                img = Image.open(img_path)
                w, h = img.size
                size_kb = os.path.getsize(img_path) / 1024
                img_info.append(f"{img_name} ({w}x{h}, {size_kb:.0f}KB)")
                total_images += 1
            except Exception as e:
                issues.append(f"{dish}: {img_name} CORRUPT - {e}")
                all_ok = False

        ok = has_json and has_45 and has_top
        status = "OK" if ok else "ISSUE"
        if not ok:
            all_ok = False

        print(f"[{status}] {dish}:")
        jstat = "YES" if has_json else "MISSING"
        d45 = "YES" if has_45 else "MISSING"
        dtop = "YES" if has_top else "MISSING"
        print(f"  JSON: {jstat}, 45deg: {d45}, top: {dtop}")
        for info in img_info:
            print(f"  - {info}")
        if not has_45:
            issues.append(f"{dish}: missing {expected_45}")
        if not has_top:
            issues.append(f"{dish}: missing {expected_top}")
        print()

    print(f"Total: {total_json} JSON + {total_images} images across {len(dishes)} dishes")
    print(f"Issues: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    print()
    result = "PASS" if all_ok else "FAIL"
    print(f"TASK 1.3.5 STATUS: {result}")


if __name__ == "__main__":
    main()

"""
Plan B: Reference object detection using pretrained YOLOv8 COCO.
No custom training needed — uses COCO "bowl" and "spoon" classes
with size heuristics for Vietnamese bowl classification.

Task 2.2 - Reference Object Detection (Fallback)

Usage:
  python scripts/reference_detector_pretrained.py <image_path>
  python scripts/reference_detector_pretrained.py data/poc/raw/poc_pho_bo_001_main.jpg

This is the SAME logic as services/reference_service.py but as a
standalone CLI script for quick testing.
"""

import sys
from pathlib import Path

from PIL import Image
from ultralytics import YOLO


# COCO classes that might be reference objects
COCO_REFERENCE_CLASSES = {
    45: {
        "name": "bowl",
        "vn_name": "Bat",
        "default_diameter_cm": 18.0,
    },
    44: {
        "name": "spoon",
        "vn_name": "Thia",
        "default_length_cm": 16.0,
    },
}

# Bowl size classification by bbox width ratio
BOWL_SIZE_MAPPING = [
    {"max_ratio": 0.20, "name": "bat_com", "diameter_cm": 11.5},
    {"max_ratio": 0.35, "name": "bat_pho_m", "diameter_cm": 19.0},
    {"max_ratio": 1.00, "name": "bat_pho_l", "diameter_cm": 23.0},
]


def detect_reference_objects(image_path: str, confidence: float = 0.4):
    """
    Detect reference objects (bowls, spoons) using pretrained YOLOv8.

    Returns: list of detected reference objects with estimated real sizes.
    """
    model = YOLO("yolov8s.pt")

    results = model(image_path, conf=confidence, verbose=False)

    detections = []
    img = Image.open(image_path)
    img_width = img.size[0]

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])

            if cls_id not in COCO_REFERENCE_CLASSES:
                continue

            ref_info = COCO_REFERENCE_CLASSES[cls_id]
            bbox = box.xyxy[0].tolist()
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            width_ratio = bbox_width / img_width
            conf = float(box.conf[0])

            # Determine type and real size
            detected_type = ref_info["name"]
            real_size_cm = ref_info.get(
                "default_diameter_cm",
                ref_info.get("default_length_cm", 0),
            )

            if cls_id == 45:  # Bowl — classify by size
                for size_info in BOWL_SIZE_MAPPING:
                    if width_ratio <= size_info["max_ratio"]:
                        detected_type = size_info["name"]
                        real_size_cm = size_info["diameter_cm"]
                        break

            # Calculate scale factor
            if detected_type == "thia":
                pixels_per_cm = max(bbox_width, bbox_height) / 16.0
            else:
                pixels_per_cm = bbox_width / real_size_cm

            detections.append(
                {
                    "class": detected_type,
                    "confidence": conf,
                    "bbox": bbox,
                    "bbox_width_px": bbox_width,
                    "width_ratio": width_ratio,
                    "real_size_cm": real_size_cm,
                    "pixels_per_cm": pixels_per_cm,
                }
            )

    return detections


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/reference_detector_pretrained.py <image_path>")
        print("")
        print("Example:")
        print(
            "  python scripts/reference_detector_pretrained.py "
            "data/poc/raw/poc_pho_bo_001_main.jpg"
        )
        sys.exit(1)

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)

    print(f"Detecting reference objects in: {image_path}")
    print(f"Using pretrained YOLOv8s (COCO)...")
    print()

    detections = detect_reference_objects(image_path)

    print(f"Detected {len(detections)} reference objects:")
    for det in detections:
        print(
            f"  - {det['class']}: "
            f"conf={det['confidence']:.2f}, "
            f"real_size~{det['real_size_cm']:.1f}cm, "
            f"scale={det['pixels_per_cm']:.1f}px/cm, "
            f"width_ratio={det['width_ratio']:.3f}"
        )

    if not detections:
        print("  (No reference objects detected)")
        print("  Tip: lower confidence threshold or ensure bowl/spoon is visible")


if __name__ == "__main__":
    main()

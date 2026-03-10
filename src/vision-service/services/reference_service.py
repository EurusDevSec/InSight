"""
Reference object detection service.
Detect bowls/spoons/chopsticks in food images for size calibration.

Task 2.2 - Reference Object Detection

Supports two modes:
  - Plan A: Custom-trained YOLO on Vietnamese tableware
  - Plan B: Pretrained YOLOv8 COCO with heuristic class mapping
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from PIL import Image

logger = logging.getLogger(__name__)


# ============================================================
# Reference object real-world dimensions (Vietnamese standard)
# Source: Vietnamese market survey + USDA food composition
# ============================================================

REFERENCE_DIMENSIONS = {
    "bat_com": {
        "width_cm": 11.5,
        "height_cm": 5.5,
        "description": "Small rice bowl (bat com)",
    },
    "bat_pho_m": {
        "width_cm": 19.0,
        "height_cm": 7.5,
        "description": "Medium pho bowl (to pho M)",
    },
    "bat_pho_l": {
        "width_cm": 23.0,
        "height_cm": 8.5,
        "description": "Large pho bowl (to pho L)",
    },
    "dia_com": {
        "width_cm": 21.0,
        "height_cm": 2.5,
        "description": "Rice plate (dia com)",
    },
    "thia": {
        "width_cm": 4.0,
        "height_cm": 16.0,
        "description": "Stainless steel spoon (thia inox)",
    },
    "dua": {
        "width_cm": 0.5,
        "height_cm": 24.5,
        "description": "Bamboo chopsticks (dua tre)",
    },
}

# COCO classes that map to reference objects
COCO_REFERENCE_MAPPING = {
    "bowl": "bowl",   # COCO class 45
    "spoon": "thia",  # COCO class 44
}

# Size heuristic for bowls based on bbox width ratio
BOWL_SIZE_THRESHOLDS = {
    "bat_com": {"max_ratio": 0.20},
    "bat_pho_m": {"max_ratio": 0.35},
    "bat_pho_l": {"max_ratio": 1.00},
}


@dataclass
class ReferenceObject:
    """Detected reference object with real-world dimensions."""

    class_name: str          # "bat_com", "bat_pho_m", "thia", "dua", etc.
    confidence: float        # Detection confidence (0-1)
    bbox: List[float]        # [x1, y1, x2, y2] in pixels
    bbox_width_px: float     # Bounding box width in pixels
    bbox_height_px: float    # Bounding box height in pixels
    real_width_cm: float     # Known real-world width/diameter (cm)
    real_height_cm: float    # Known real-world height (cm)
    pixels_per_cm: float     # Calculated scale factor


class ReferenceDetector:
    """YOLO-based reference object detector."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence: float = 0.5,
    ):
        """
        Initialize detector.

        Args:
            model_path: Path to custom trained YOLO model weights.
                        If None or not found, falls back to pretrained COCO.
            confidence: Minimum detection confidence threshold.
        """
        self.confidence = confidence
        self.model_path = model_path
        self.model = None
        self._loaded = False
        self._is_custom = False

    def load(self) -> None:
        """Load YOLO model."""
        if self._loaded:
            return

        from ultralytics import YOLO

        if self.model_path and Path(self.model_path).exists():
            logger.info(f"Loading custom YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            self._is_custom = True
        else:
            logger.info("Loading pretrained YOLOv8s (COCO) as fallback...")
            self.model = YOLO("yolov8s.pt")
            self._is_custom = False

        self._loaded = True
        logger.info(
            f"Reference detector loaded! "
            f"(custom={self._is_custom})"
        )

    def detect(self, image: Image.Image) -> List[ReferenceObject]:
        """
        Detect reference objects in image.

        Args:
            image: PIL Image (RGB)

        Returns:
            List of ReferenceObject with real-world dimensions,
            sorted by confidence (highest first).
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        img_width, img_height = image.size
        results = self.model(image, conf=self.confidence, verbose=False)

        detections = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names[cls_id]
                conf = float(box.conf[0])
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

                # Map detected class to reference type
                ref_type = self._map_class(cls_name, bbox, img_width)
                if ref_type is None:
                    continue

                dims = REFERENCE_DIMENSIONS[ref_type]
                bbox_w = bbox[2] - bbox[0]
                bbox_h = bbox[3] - bbox[1]

                # Calculate pixels_per_cm (scale factor)
                # Use width (diameter) for bowls/plates,
                # height (length) for spoons/chopsticks
                if ref_type in ("thia", "dua"):
                    pixels_per_cm = max(bbox_w, bbox_h) / dims["height_cm"]
                else:
                    pixels_per_cm = bbox_w / dims["width_cm"]

                detections.append(
                    ReferenceObject(
                        class_name=ref_type,
                        confidence=conf,
                        bbox=bbox,
                        bbox_width_px=bbox_w,
                        bbox_height_px=bbox_h,
                        real_width_cm=dims["width_cm"],
                        real_height_cm=dims["height_cm"],
                        pixels_per_cm=pixels_per_cm,
                    )
                )

        # Sort by confidence (highest first)
        detections.sort(key=lambda d: d.confidence, reverse=True)

        logger.info(
            f"Detected {len(detections)} reference objects: "
            f"{[d.class_name for d in detections]}"
        )

        return detections

    def _map_class(
        self,
        cls_name: str,
        bbox: List[float],
        img_width: float,
    ) -> Optional[str]:
        """
        Map YOLO class name to InSight reference type.

        If using custom model: class name maps directly.
        If using pretrained COCO: uses mapping + size heuristic.
        """
        # Custom model classes (match REFERENCE_DIMENSIONS keys)
        if cls_name in REFERENCE_DIMENSIONS:
            return cls_name

        # COCO pretrained mapping
        if cls_name == "bowl":
            bbox_w = bbox[2] - bbox[0]
            ratio = bbox_w / img_width
            for bowl_type, threshold in BOWL_SIZE_THRESHOLDS.items():
                if ratio <= threshold["max_ratio"]:
                    return bowl_type
            return "bat_pho_l"  # Default to large if very big

        if cls_name == "spoon":
            return "thia"

        return None  # Not a reference object

    def get_best_scale_factor(
        self, detections: List[ReferenceObject]
    ) -> Optional[float]:
        """
        Get the best scale factor (pixels_per_cm) from detected objects.

        Priority: bowls (larger area, more stable) > spoons > chopsticks
        """
        if not detections:
            return None

        # Priority order (lower = higher priority)
        priority = {
            "bat_pho_m": 1,
            "bat_pho_l": 2,
            "bat_com": 3,
            "dia_com": 4,
            "thia": 5,
            "dua": 6,
        }

        best = min(
            detections, key=lambda d: priority.get(d.class_name, 99)
        )
        return best.pixels_per_cm

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded

    @property
    def is_custom_model(self) -> bool:
        """Check if using custom trained model."""
        return self._is_custom

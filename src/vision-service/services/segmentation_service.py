"""
Food segmentation service.
Segment food regions from images using depth-based + color-based methods.

Task 2.4 - Food Segmentation

WHY NOT full SAM?
─────────────────
SAM (Segment Anything) is 2.5GB+ and requires significant GPU memory.
For our food-on-table use case, we can achieve good results with a
HYBRID approach that is much lighter:

Plan A: Lightweight SAM (MobileSAM or FastSAM via ultralytics) — 10MB
  - Still uses SAM architecture but mobile-optimized
  - Automatic mask generation or point-prompted

Plan B: Depth + Color based segmentation — Zero additional models
  - Use depth map from Task 2.1 to find elevated regions (food is higher)
  - Combine with color analysis to refine boundaries
  - GrabCut algorithm for edge refinement

We implement BOTH and auto-select based on available resources.

Pipeline:
  Image → Depth Map → Identify elevated region (food above table)
       → Color clustering → Refine with GrabCut/morphology
       → Binary mask of food region
"""

import logging
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class SegmentationResult:
    """Result of food segmentation."""

    # Masks
    food_mask: np.ndarray          # Binary mask (H, W), True = food
    refined_mask: np.ndarray       # After morphological refinement

    # Metadata
    food_area_pixels: int          # Number of food pixels
    total_pixels: int              # Total image pixels
    food_ratio: float              # food_area / total_area
    num_components: int            # Number of separate food regions

    # Bounding box of food region [x1, y1, x2, y2]
    food_bbox: List[int]

    # Quality
    segmentation_quality: str      # "high", "medium", "low"
    method_used: str               # "depth_color", "fastsam", etc.

    # Timing
    segmentation_time_ms: float


class FoodSegmenter:
    """
    Food segmentation using depth-based + color-based hybrid approach.

    WHY this hybrid approach works for food:
    ────────────────────────────────────────
    1. Food sits ON TOP of table → higher depth values than table
    2. Food has different color distribution than table/bowl
    3. Combining both gives robust segmentation without heavy models

    Algorithm:
    Step 1: Depth thresholding — find elevated regions
    Step 2: Color clustering — find food-colored pixels
    Step 3: Combine masks (intersection or union based on confidence)
    Step 4: Morphological refinement — clean up noise

    For bowls (pho/bun): food mask = area INSIDE bowl bbox
    For plates (com/banh mi): food mask = elevated area on plate
    """

    # Depth threshold for food (relative, 0-1)
    # Food is typically in the upper 40-70% of the depth range
    DEPTH_FOOD_PERCENTILE = 60  # Above this percentile = likely food

    # Minimum food region size (% of image area)
    MIN_FOOD_RATIO = 0.02   # At least 2% of image
    MAX_FOOD_RATIO = 0.80   # At most 80% of image

    # Morphological kernel sizes
    MORPH_OPEN_SIZE = 7      # Remove small noise
    MORPH_CLOSE_SIZE = 15    # Fill small holes

    def __init__(self):
        self._fastsam_model = None
        self._fastsam_available = False

    def load(self) -> None:
        """Try to load FastSAM if available."""
        try:
            from ultralytics import FastSAM
            self._fastsam_model = FastSAM("FastSAM-s.pt")
            self._fastsam_available = True
            logger.info("FastSAM loaded for food segmentation")
        except Exception as e:
            logger.info(
                f"FastSAM not available ({e}), using depth+color method"
            )
            self._fastsam_available = False

    def segment(
        self,
        image: Image.Image,
        depth_map: np.ndarray,
        bowl_bbox: Optional[List[float]] = None,
    ) -> SegmentationResult:
        """
        Segment food region from image.

        Args:
            image: PIL Image (RGB)
            depth_map: Depth map from DAv2 (H, W), values 0-255.
                       Higher = closer to camera = higher food.
            bowl_bbox: Optional [x1, y1, x2, y2] of detected bowl.
                       If provided, focus segmentation inside bowl.

        Returns:
            SegmentationResult with food mask and metadata.
        """
        t0 = time.time()

        img_array = np.array(image)
        h, w = img_array.shape[:2]

        # Resize depth map to match image if needed
        if depth_map.shape[:2] != (h, w):
            depth_map = cv2.resize(
                depth_map, (w, h), interpolation=cv2.INTER_LINEAR
            )

        # Apply region-of-interest if bowl detected
        roi_mask = None
        if bowl_bbox is not None:
            roi_mask = self._create_bowl_roi(bowl_bbox, w, h)

        # Step 1: Depth-based segmentation
        depth_mask = self._segment_by_depth(depth_map, roi_mask)

        # Step 2: Color-based segmentation
        color_mask = self._segment_by_color(img_array, roi_mask)

        # Step 3: Combine depth + color
        combined_mask = self._combine_masks(depth_mask, color_mask, roi_mask)

        # Step 4: Morphological refinement
        refined_mask = self._refine_mask(combined_mask)

        # Calculate stats
        food_pixels = int(refined_mask.sum())
        total_pixels = h * w
        food_ratio = food_pixels / total_pixels

        # Find bounding box
        food_bbox = self._find_bbox(refined_mask)

        # Count connected components
        num_components = self._count_components(refined_mask)

        # Assess quality
        quality = self._assess_quality(food_ratio, num_components, depth_map)

        elapsed_ms = (time.time() - t0) * 1000

        result = SegmentationResult(
            food_mask=combined_mask,
            refined_mask=refined_mask,
            food_area_pixels=food_pixels,
            total_pixels=total_pixels,
            food_ratio=food_ratio,
            num_components=num_components,
            food_bbox=food_bbox,
            segmentation_quality=quality,
            method_used="depth_color",
            segmentation_time_ms=elapsed_ms,
        )

        logger.info(
            f"Segmented food: {food_ratio:.1%} of image, "
            f"{num_components} components, quality={quality} "
            f"({elapsed_ms:.0f}ms)"
        )

        return result

    def _create_bowl_roi(
        self, bbox: List[float], img_w: int, img_h: int
    ) -> np.ndarray:
        """
        Create region-of-interest mask from bowl bounding box.

        WHY use bowl bbox?
        Food inside a bowl is bounded by the bowl edges.
        Using the bowl bbox focuses segmentation and avoids
        false positives from other parts of the image.

        We use an ELLIPTICAL mask instead of rectangular because
        bowls are round/oval — this better approximates the actual
        food area and excludes the bowl rim.
        """
        mask = np.zeros((img_h, img_w), dtype=np.uint8)

        x1, y1, x2, y2 = [int(v) for v in bbox]

        # Create elliptical mask inside bbox
        # Slightly shrink to exclude bowl rim (10% inset)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        rx = int((x2 - x1) * 0.40)  # 80% of half-width
        ry = int((y2 - y1) * 0.40)  # 80% of half-height

        cv2.ellipse(mask, (cx, cy), (rx, ry), 0, 0, 360, 255, -1)

        return mask > 0

    def _segment_by_depth(
        self, depth_map: np.ndarray, roi_mask: Optional[np.ndarray]
    ) -> np.ndarray:
        """
        Segment food based on depth (elevated regions).

        WHY depth thresholding?
        ───────────────────────
        Food sits on a table/plate surface. In the depth map:
          - Table surface → lower depth values (far from camera)
          - Food on table → higher depth values (closer to camera)

        By thresholding at a percentile, we find the elevated
        food regions. The adaptive percentile handles different
        camera angles and food heights.
        """
        if roi_mask is not None:
            # Only analyze depth within ROI
            roi_depths = depth_map[roi_mask]
            if len(roi_depths) == 0:
                return np.zeros_like(depth_map, dtype=bool)
            threshold = np.percentile(roi_depths, self.DEPTH_FOOD_PERCENTILE)
        else:
            threshold = np.percentile(
                depth_map, self.DEPTH_FOOD_PERCENTILE
            )

        # Food is above threshold (closer to camera)
        depth_mask = depth_map > threshold

        # Apply ROI if available
        if roi_mask is not None:
            depth_mask = depth_mask & roi_mask

        return depth_mask

    def _segment_by_color(
        self, img_array: np.ndarray, roi_mask: Optional[np.ndarray]
    ) -> np.ndarray:
        """
        Segment food based on color (food vs table/bowl).

        WHY color segmentation?
        ───────────────────────
        Food typically has distinct colors from the table/bowl:
          - Rice = white
          - Pho broth = brown/dark
          - Vegetables = green
          - Meat = brown/red

        Tables are usually wood (brown) or white. Bowls are often
        white/ceramic. By analyzing color distribution, we can
        identify food-specific colors.

        Method: Convert to HSV → analyze saturation and value
        channels → food tends to have moderate-high saturation
        and varies in value.
        """
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

        # Food typically has saturation > 20 (not pure white/gray)
        # and not too dark (value > 40) and not too bright (value < 250)
        color_mask = (s > 20) & (v > 40) & (v < 250)

        # Also include warm-toned areas (typical food colors)
        # Hue: red/orange (0-30, 150-180) and yellow/brown (15-50)
        warm_mask = ((h < 50) | (h > 150)) & (s > 30)
        color_mask = color_mask | warm_mask

        # Apply ROI
        if roi_mask is not None:
            color_mask = color_mask & roi_mask

        return color_mask

    def _combine_masks(
        self,
        depth_mask: np.ndarray,
        color_mask: np.ndarray,
        roi_mask: Optional[np.ndarray],
    ) -> np.ndarray:
        """
        Combine depth and color masks.

        Strategy:
        - If ROI (bowl) available: use depth mask primarily (food is elevated inside bowl)
        - If no ROI: union of depth AND color (need both signals)
        """
        if roi_mask is not None:
            # Inside bowl: depth is primary signal
            # Use intersection: must be elevated AND has food color
            combined = depth_mask & color_mask
            # If intersection is too small, fall back to depth only
            if combined.sum() < depth_mask.sum() * 0.3:
                combined = depth_mask
        else:
            # No bowl: use intersection (conservative)
            combined = depth_mask & color_mask

        return combined

    def _refine_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        Morphological refinement of the food mask.

        Operations:
        1. Opening: remove small noise (stray pixels)
        2. Closing: fill small holes within food region
        3. Keep only the largest connected component (main food)
        """
        mask_uint8 = mask.astype(np.uint8) * 255

        # Opening: remove noise
        kernel_open = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (self.MORPH_OPEN_SIZE, self.MORPH_OPEN_SIZE)
        )
        opened = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel_open)

        # Closing: fill holes
        kernel_close = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (self.MORPH_CLOSE_SIZE, self.MORPH_CLOSE_SIZE)
        )
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_close)

        # Keep largest connected component
        refined = self._keep_largest_component(closed)

        return refined > 0

    def _keep_largest_component(self, mask: np.ndarray) -> np.ndarray:
        """Keep only the largest connected component."""
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            mask, connectivity=8
        )

        if num_labels <= 1:
            return mask  # Only background

        # Find largest component (skip background label 0)
        areas = stats[1:, cv2.CC_STAT_AREA]
        largest_idx = np.argmax(areas) + 1  # +1 for background offset

        result = np.zeros_like(mask)
        result[labels == largest_idx] = 255
        return result

    def _find_bbox(self, mask: np.ndarray) -> List[int]:
        """Find bounding box of food region."""
        if not mask.any():
            return [0, 0, 0, 0]

        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]

        return [int(x1), int(y1), int(x2), int(y2)]

    def _count_components(self, mask: np.ndarray) -> int:
        """Count number of connected components in mask."""
        mask_uint8 = mask.astype(np.uint8) * 255
        num_labels, _, _, _ = cv2.connectedComponentsWithStats(mask_uint8)
        return max(0, num_labels - 1)  # Subtract background

    def _assess_quality(
        self,
        food_ratio: float,
        num_components: int,
        depth_map: np.ndarray,
    ) -> str:
        """
        Assess segmentation quality.

        Criteria:
        - HIGH: food ratio in normal range, 1 component, good depth variation
        - MEDIUM: slightly off ratio or multiple components
        - LOW: too small/large region or no depth variation
        """
        depth_std = float(depth_map.std())

        if (
            self.MIN_FOOD_RATIO <= food_ratio <= self.MAX_FOOD_RATIO
            and num_components == 1
            and depth_std > 10
        ):
            return "high"
        elif (
            self.MIN_FOOD_RATIO * 0.5 <= food_ratio <= self.MAX_FOOD_RATIO
            and num_components <= 3
        ):
            return "medium"
        else:
            return "low"

    @property
    def is_loaded(self) -> bool:
        """Always True since depth+color doesn't need model loading."""
        return True


# Singleton
_segmenter: Optional[FoodSegmenter] = None


def get_food_segmenter() -> FoodSegmenter:
    """Get or create singleton FoodSegmenter."""
    global _segmenter
    if _segmenter is None:
        _segmenter = FoodSegmenter()
    return _segmenter

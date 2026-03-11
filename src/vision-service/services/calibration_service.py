"""
Pixel-to-Real calibration service.
Convert pixel measurements to real-world dimensions (cm) using
depth map + reference object scale factor.

Task 2.3 - Pixel-to-Real Mapping

WHY this approach?
──────────────────
Depth Anything V2 produces RELATIVE depth (0-255), not absolute depth in cm.
To convert pixel distances to real-world cm, we need a "ruler" in the image.
Reference objects (bowls, spoons) detected in Task 2.2 provide that ruler:
  - We know the real diameter of a pho bowl (19cm)
  - We detect its pixel width in the image (380px)
  - Scale factor = 380px / 19cm = 20 px/cm

This scale factor is then applied to the depth map to convert ALL pixels
to real-world dimensions. The depth map provides Z-axis (height/distance),
while the scale factor provides X/Y-axis calibration.

The calibration combines:
  1. Reference-based scale (px → cm for X/Y axes)
  2. Depth normalization (relative depth → proportional height for Z axis)
  3. Depth gradient analysis (identify food vs flat surfaces)
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class CalibrationResult:
    """Result of pixel-to-real calibration."""

    # Scale factors
    pixels_per_cm: float           # From reference object (X/Y scale)
    cm_per_pixel: float            # Inverse: 1 / pixels_per_cm

    # Calibrated depth map
    depth_map_cm: np.ndarray       # Depth map in relative cm units (H, W)

    # Image metadata
    image_width_cm: float          # Image width in real cm
    image_height_cm: float         # Image height in real cm

    # Reference info
    reference_class: str           # Which reference was used (bat_pho_m, etc.)
    reference_confidence: float    # Detection confidence

    # Quality metrics
    calibration_quality: str       # "high", "medium", "low"
    quality_reason: str            # Why this quality rating

    # Timing
    calibration_time_ms: float


@dataclass
class DepthRegionStats:
    """Statistics for a region in the depth map."""
    mean_depth: float
    max_depth: float
    min_depth: float
    std_depth: float
    area_pixels: int
    area_cm2: float               # Area in cm^2 after calibration


class CalibrationService:
    """
    Pixel-to-Real calibration service.

    Combines depth map (Task 2.1) + reference detection (Task 2.2)
    to produce calibrated real-world measurements.

    Pipeline:
      1. Get scale factor from reference detector (px/cm)
      2. Normalize depth map to proportional scale
      3. Apply scale factor to convert depth to relative cm
      4. Provide utility methods for measurement
    """

    # Depth map normalization range
    # Depth Anything V2 outputs 0-255, where higher = closer to camera
    # We need to decide a reference depth scale
    # For food on a table, typical depth range is 2-15cm
    DEPTH_RANGE_CM = (0.0, 15.0)  # Min/max food height in cm

    def __init__(self):
        self._last_calibration: Optional[CalibrationResult] = None

    def calibrate(
        self,
        depth_map: np.ndarray,
        pixels_per_cm: float,
        reference_class: str = "unknown",
        reference_confidence: float = 0.0,
        image_size: Optional[Tuple[int, int]] = None,
    ) -> CalibrationResult:
        """
        Calibrate depth map using reference object scale factor.

        Args:
            depth_map: Raw depth map from DAv2 (H, W), values 0-255.
                       Higher value = closer to camera.
            pixels_per_cm: Scale factor from reference detector.
            reference_class: Which reference object was used.
            reference_confidence: Detection confidence of reference.
            image_size: (width, height) of original image.

        Returns:
            CalibrationResult with calibrated depth map and measurements.

        WHY normalize depth like this?
        ──────────────────────────────
        DAv2 depth is RELATIVE — "pixel A is 2x closer than pixel B".
        We can't get absolute distance, but we CAN:
        1. Use reference scale for X/Y (px → cm horizontal)
        2. Map depth range to typical food heights (0-15cm)
        3. The relative proportions are preserved, which is what
           matters for volume estimation (Task 2.5)
        """
        t0 = time.time()

        if pixels_per_cm <= 0:
            raise ValueError(f"Invalid scale factor: {pixels_per_cm}")

        cm_per_pixel = 1.0 / pixels_per_cm

        # Step 1: Normalize depth map to 0-1 range
        depth_min = float(depth_map.min())
        depth_max = float(depth_map.max())
        depth_range = depth_max - depth_min

        if depth_range < 1e-6:
            # Flat depth — no meaningful depth variation
            depth_normalized = np.zeros_like(depth_map, dtype=np.float64)
        else:
            depth_normalized = (depth_map.astype(np.float64) - depth_min) / depth_range

        # Step 2: Map to physical depth range (cm)
        # DAv2: higher value = closer = higher food surface
        # We want: higher normalized = taller food
        depth_cm_range = self.DEPTH_RANGE_CM[1] - self.DEPTH_RANGE_CM[0]
        depth_map_cm = depth_normalized * depth_cm_range

        # Step 3: Calculate image real dimensions
        h, w = depth_map.shape[:2]
        if image_size:
            img_w, img_h = image_size
        else:
            img_w, img_h = w, h

        image_width_cm = img_w * cm_per_pixel
        image_height_cm = img_h * cm_per_pixel

        # Step 4: Assess calibration quality
        quality, reason = self._assess_quality(
            pixels_per_cm, reference_confidence, depth_range
        )

        elapsed_ms = (time.time() - t0) * 1000

        result = CalibrationResult(
            pixels_per_cm=pixels_per_cm,
            cm_per_pixel=cm_per_pixel,
            depth_map_cm=depth_map_cm,
            image_width_cm=image_width_cm,
            image_height_cm=image_height_cm,
            reference_class=reference_class,
            reference_confidence=reference_confidence,
            calibration_quality=quality,
            quality_reason=reason,
            calibration_time_ms=elapsed_ms,
        )

        self._last_calibration = result

        logger.info(
            f"Calibrated: {pixels_per_cm:.1f} px/cm, "
            f"image={image_width_cm:.1f}x{image_height_cm:.1f}cm, "
            f"quality={quality} ({elapsed_ms:.1f}ms)"
        )

        return result

    def measure_region(
        self,
        calibration: CalibrationResult,
        mask: np.ndarray,
    ) -> DepthRegionStats:
        """
        Measure a specific region using calibrated depth map.

        Args:
            calibration: CalibrationResult from calibrate()
            mask: Boolean mask (H, W) — True for region of interest

        Returns:
            DepthRegionStats with mean depth, area in cm², etc.
        """
        depth_cm = calibration.depth_map_cm

        # Ensure mask matches depth map shape
        if mask.shape != depth_cm.shape:
            raise ValueError(
                f"Mask shape {mask.shape} != depth map shape {depth_cm.shape}"
            )

        # Extract region depths
        region_depths = depth_cm[mask]

        if len(region_depths) == 0:
            return DepthRegionStats(
                mean_depth=0.0,
                max_depth=0.0,
                min_depth=0.0,
                std_depth=0.0,
                area_pixels=0,
                area_cm2=0.0,
            )

        # Calculate area in cm²
        pixel_area_cm2 = calibration.cm_per_pixel ** 2
        area_cm2 = int(mask.sum()) * pixel_area_cm2

        return DepthRegionStats(
            mean_depth=float(region_depths.mean()),
            max_depth=float(region_depths.max()),
            min_depth=float(region_depths.min()),
            std_depth=float(region_depths.std()),
            area_pixels=int(mask.sum()),
            area_cm2=area_cm2,
        )

    def pixels_to_cm(self, pixels: float) -> float:
        """Convert pixel distance to cm using last calibration."""
        if self._last_calibration is None:
            raise RuntimeError("No calibration available. Call calibrate() first.")
        return pixels * self._last_calibration.cm_per_pixel

    def cm_to_pixels(self, cm: float) -> float:
        """Convert cm to pixel distance using last calibration."""
        if self._last_calibration is None:
            raise RuntimeError("No calibration available. Call calibrate() first.")
        return cm * self._last_calibration.pixels_per_cm

    def _assess_quality(
        self,
        pixels_per_cm: float,
        confidence: float,
        depth_range: float,
    ) -> Tuple[str, str]:
        """
        Assess calibration quality based on multiple factors.

        Quality criteria:
        - HIGH: confident reference (>0.8) + good scale (10-50 px/cm)
                + meaningful depth range (>30)
        - MEDIUM: moderate confidence + acceptable scale
        - LOW: low confidence or extreme scale or flat depth
        """
        reasons = []

        # Reference confidence
        if confidence >= 0.8:
            conf_score = 3
        elif confidence >= 0.5:
            conf_score = 2
            reasons.append(f"moderate reference confidence ({confidence:.2f})")
        else:
            conf_score = 1
            reasons.append(f"low reference confidence ({confidence:.2f})")

        # Scale factor reasonableness
        # Typical food images: 10-50 px/cm
        if 10 <= pixels_per_cm <= 50:
            scale_score = 3
        elif 5 <= pixels_per_cm <= 80:
            scale_score = 2
            reasons.append(f"unusual scale ({pixels_per_cm:.1f} px/cm)")
        else:
            scale_score = 1
            reasons.append(f"extreme scale ({pixels_per_cm:.1f} px/cm)")

        # Depth variation
        if depth_range > 30:
            depth_score = 3
        elif depth_range > 10:
            depth_score = 2
            reasons.append("low depth variation")
        else:
            depth_score = 1
            reasons.append("very flat depth (no 3D info)")

        # Overall quality
        total = conf_score + scale_score + depth_score
        if total >= 8:
            quality = "high"
        elif total >= 5:
            quality = "medium"
        else:
            quality = "low"

        reason = "; ".join(reasons) if reasons else "good calibration"
        return quality, reason


# Singleton instance
_calibration_service: Optional[CalibrationService] = None


def get_calibration_service() -> CalibrationService:
    """Get or create singleton CalibrationService."""
    global _calibration_service
    if _calibration_service is None:
        _calibration_service = CalibrationService()
    return _calibration_service

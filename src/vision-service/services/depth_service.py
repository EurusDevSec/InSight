"""
Depth estimation service — business logic layer.
Handles: receive image -> generate depth map -> normalize -> return result.

Task 2.1 - Depth Estimation
"""

import base64
import io
import logging
from typing import Optional

import numpy as np
from PIL import Image

from models.depth_model import DepthAnythingV2

logger = logging.getLogger(__name__)

# Singleton model instance
_model: Optional[DepthAnythingV2] = None


def get_model(variant: str = "small") -> DepthAnythingV2:
    """Get or create singleton model instance."""
    global _model
    if _model is None:
        _model = DepthAnythingV2(variant=variant)
        _model.load()
    return _model


def estimate_depth(image_bytes: bytes) -> dict:
    """
    Estimate depth from image bytes.

    Args:
        image_bytes: Raw image bytes (JPEG/PNG)

    Returns:
        dict with depth estimation results:
          - depth_map_base64: base64 encoded depth map PNG
          - inference_time_ms: float
          - image_size: [width, height]
          - depth_stats: {min, max, mean, std}
    """
    # Decode image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    logger.info(f"Processing image: {width}x{height}")

    # Run depth estimation
    model = get_model()
    result = model.predict(image)

    # Encode depth map to base64 PNG for API response
    depth_image = result["depth_image"]
    buffer = io.BytesIO()
    depth_image.save(buffer, format="PNG")
    depth_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "depth_map_base64": depth_base64,
        "inference_time_ms": result["inference_time_ms"],
        "image_size": [width, height],
        "depth_stats": result["stats"],
    }


def estimate_depth_raw(image: Image.Image) -> np.ndarray:
    """
    Get raw depth map as numpy array.
    Used for internal pipeline (Task 2.3 calibration, Task 2.5 volume).

    Args:
        image: PIL Image (RGB)

    Returns:
        numpy array (H, W) with depth values
    """
    model = get_model()
    result = model.predict(image)
    return result["depth_map"]


def estimate_depth_full(image: Image.Image) -> dict:
    """
    Get full depth estimation result including raw numpy array.
    Used for internal pipeline when both depth map and metadata are needed.

    Args:
        image: PIL Image (RGB)

    Returns:
        Full result dict from model.predict()
    """
    model = get_model()
    return model.predict(image)

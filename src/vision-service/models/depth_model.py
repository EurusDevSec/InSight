"""
Depth Anything V2 model wrapper.
Encapsulate model loading and inference logic.

Task 2.1 - Depth Estimation
Reference: POC validated at scripts/poc_depth_test.py
"""

import logging
import time
from typing import Optional

import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)


class DepthAnythingV2:
    """Wrapper for Depth Anything V2 model inference."""

    # Supported model variants
    MODELS = {
        "small": "depth-anything/Depth-Anything-V2-Small-hf",
        "base": "depth-anything/Depth-Anything-V2-Base-hf",
        "large": "depth-anything/Depth-Anything-V2-Large-hf",
    }

    def __init__(self, variant: str = "small", device: Optional[str] = None):
        """
        Initialize Depth Anything V2 model.

        Args:
            variant: Model size - "small", "base", or "large"
            device: "cuda" or "cpu". Auto-detect if None.
        """
        self.variant = variant
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipe = None
        self._loaded = False

    def load(self) -> None:
        """Load model weights. Called once at startup."""
        if self._loaded:
            logger.info("Model already loaded, skipping...")
            return

        model_id = self.MODELS.get(self.variant)
        if not model_id:
            raise ValueError(
                f"Unknown variant: {self.variant}. "
                f"Choose from: {list(self.MODELS.keys())}"
            )

        logger.info(
            f"Loading Depth Anything V2 ({self.variant}) on {self.device}..."
        )
        start = time.time()

        # Import here to avoid slow import at module level
        from transformers import pipeline as hf_pipeline

        self.pipe = hf_pipeline(
            task="depth-estimation",
            model=model_id,
            device=self.device,
        )

        elapsed = time.time() - start
        self._loaded = True
        logger.info(
            f"Model loaded in {elapsed:.1f}s on {self.device.upper()}"
        )

    def predict(self, image: Image.Image) -> dict:
        """
        Run depth estimation on a single image.

        Args:
            image: PIL Image (RGB)

        Returns:
            dict with:
              - "depth_map": numpy array (H, W) with depth values 0-255
              - "depth_image": PIL Image (grayscale depth visualization)
              - "inference_time_ms": float
              - "stats": dict with min, max, mean, std depth values
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Run inference
        start = time.time()
        result = self.pipe(image)
        inference_ms = (time.time() - start) * 1000

        # Extract depth map
        depth_image = result["depth"]  # PIL Image (grayscale)
        depth_array = np.array(depth_image)

        # Compute statistics
        stats = {
            "min": float(depth_array.min()),
            "max": float(depth_array.max()),
            "mean": float(depth_array.mean()),
            "std": float(depth_array.std()),
        }

        logger.info(
            f"Depth estimated in {inference_ms:.0f}ms | "
            f"Range: [{stats['min']:.0f}, {stats['max']:.0f}] | "
            f"Mean: {stats['mean']:.1f}"
        )

        return {
            "depth_map": depth_array,
            "depth_image": depth_image,
            "inference_time_ms": inference_ms,
            "stats": stats,
        }

    @property
    def is_loaded(self) -> bool:
        """Check if model has been loaded."""
        return self._loaded

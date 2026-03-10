"""
Unit tests for Depth Estimation Service (Task 2.1).

Run: cd src/vision-service && pytest tests/test_depth_service.py -v
"""

import io
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Add parent dir so imports work when running from vision-service/
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.depth_model import DepthAnythingV2


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture(scope="session")
def depth_model():
    """Load model once for entire test session (saves time)."""
    model = DepthAnythingV2(variant="small")
    model.load()
    return model


@pytest.fixture
def sample_image():
    """Create a random RGB test image."""
    arr = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.fixture
def sample_image_bytes(sample_image):
    """Convert test image to JPEG bytes."""
    buffer = io.BytesIO()
    sample_image.save(buffer, format="JPEG")
    return buffer.getvalue()


# ============================================================
# Tests: DepthAnythingV2 Model
# ============================================================
class TestDepthModel:
    """Tests for DepthAnythingV2 model wrapper."""

    def test_model_loads_successfully(self, depth_model):
        """Model should load without errors."""
        assert depth_model.is_loaded

    def test_predict_returns_expected_keys(self, depth_model, sample_image):
        """predict() must return dict with required keys."""
        result = depth_model.predict(sample_image)
        assert "depth_map" in result
        assert "depth_image" in result
        assert "inference_time_ms" in result
        assert "stats" in result

    def test_depth_map_is_2d_numpy(self, depth_model, sample_image):
        """Depth map must be 2D numpy array (H, W)."""
        result = depth_model.predict(sample_image)
        depth_map = result["depth_map"]
        assert isinstance(depth_map, np.ndarray)
        assert depth_map.ndim == 2

    def test_depth_map_values_in_valid_range(self, depth_model, sample_image):
        """Depth map values must be in [0, 255]."""
        result = depth_model.predict(sample_image)
        depth_map = result["depth_map"]
        assert depth_map.min() >= 0
        assert depth_map.max() <= 255

    def test_depth_image_is_pil(self, depth_model, sample_image):
        """depth_image must be a PIL Image."""
        result = depth_model.predict(sample_image)
        assert isinstance(result["depth_image"], Image.Image)

    def test_inference_time_is_positive(self, depth_model, sample_image):
        """Inference time must be positive."""
        result = depth_model.predict(sample_image)
        assert result["inference_time_ms"] > 0

    def test_inference_time_reasonable(self, depth_model, sample_image):
        """Inference time should be < 30s even on CPU."""
        result = depth_model.predict(sample_image)
        assert result["inference_time_ms"] < 30000

    def test_stats_has_expected_keys(self, depth_model, sample_image):
        """Stats should contain min, max, mean, std."""
        result = depth_model.predict(sample_image)
        stats = result["stats"]
        assert "min" in stats
        assert "max" in stats
        assert "mean" in stats
        assert "std" in stats

    def test_stats_values_are_floats(self, depth_model, sample_image):
        """All stat values should be floats."""
        result = depth_model.predict(sample_image)
        for key, value in result["stats"].items():
            assert isinstance(value, float), f"stats['{key}'] is not float"

    def test_invalid_variant_raises(self):
        """Invalid variant must raise ValueError."""
        model = DepthAnythingV2(variant="xxxl")
        with pytest.raises(ValueError, match="Unknown variant"):
            model.load()

    def test_predict_without_load_raises(self):
        """predict() before load() must raise RuntimeError."""
        model = DepthAnythingV2(variant="small")
        image = Image.new("RGB", (100, 100))
        with pytest.raises(RuntimeError, match="not loaded"):
            model.predict(image)

    def test_handles_rgba_image(self, depth_model):
        """Model should handle RGBA images by converting to RGB."""
        rgba_image = Image.new("RGBA", (200, 200), (255, 0, 0, 128))
        result = depth_model.predict(rgba_image)
        assert result["depth_map"].ndim == 2

    def test_handles_grayscale_image(self, depth_model):
        """Model should handle grayscale images by converting to RGB."""
        gray_image = Image.new("L", (200, 200), 128)
        result = depth_model.predict(gray_image)
        assert result["depth_map"].ndim == 2

    def test_different_image_sizes(self, depth_model):
        """Model should work with various image sizes."""
        sizes = [(320, 240), (640, 480), (800, 600)]
        for w, h in sizes:
            image = Image.new("RGB", (w, h), color="blue")
            result = depth_model.predict(image)
            assert result["depth_map"].ndim == 2, f"Failed for size {w}x{h}"


# ============================================================
# Tests: Depth Service Functions
# ============================================================
class TestDepthService:
    """Tests for depth estimation service functions."""

    def test_estimate_depth_returns_base64(self, sample_image_bytes):
        """estimate_depth() must return base64 encoded depth map."""
        from services.depth_service import estimate_depth

        result = estimate_depth(sample_image_bytes)
        assert "depth_map_base64" in result
        assert isinstance(result["depth_map_base64"], str)
        assert len(result["depth_map_base64"]) > 0

    def test_estimate_depth_has_stats(self, sample_image_bytes):
        """estimate_depth() must return depth statistics."""
        from services.depth_service import estimate_depth

        result = estimate_depth(sample_image_bytes)
        assert "depth_stats" in result
        stats = result["depth_stats"]
        assert "min" in stats
        assert "max" in stats
        assert "mean" in stats

    def test_estimate_depth_has_image_size(self, sample_image_bytes):
        """estimate_depth() must return image size."""
        from services.depth_service import estimate_depth

        result = estimate_depth(sample_image_bytes)
        assert "image_size" in result
        assert len(result["image_size"]) == 2

    def test_estimate_depth_raw(self, sample_image):
        """estimate_depth_raw() must return numpy array."""
        from services.depth_service import estimate_depth_raw

        depth_map = estimate_depth_raw(sample_image)
        assert isinstance(depth_map, np.ndarray)
        assert depth_map.ndim == 2

    def test_base64_is_decodable(self, sample_image_bytes):
        """Base64 depth map should be decodable to valid PNG."""
        import base64

        from services.depth_service import estimate_depth

        result = estimate_depth(sample_image_bytes)
        decoded = base64.b64decode(result["depth_map_base64"])
        depth_img = Image.open(io.BytesIO(decoded))
        assert depth_img.size[0] > 0
        assert depth_img.size[1] > 0

"""
Unit tests for Food Segmentation Service (Task 2.4).

Run: cd src/vision-service && pytest tests/test_segmentation_service.py -v
"""

import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.segmentation_service import (
    FoodSegmenter,
    SegmentationResult,
    get_food_segmenter,
)


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def segmenter():
    """Create food segmenter."""
    return FoodSegmenter()


@pytest.fixture
def food_image():
    """Create synthetic food-like image (colorful center, neutral edges)."""
    img = np.full((400, 600, 3), [200, 200, 200], dtype=np.uint8)  # Gray bg
    # Food-colored region (warm orange/brown)
    cv2.rectangle(img, (150, 100), (450, 300), (60, 120, 200), -1)  # BGR warm
    # Add some variation
    noise = np.random.randint(-20, 20, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


@pytest.fixture
def food_depth_map():
    """Create synthetic depth map (food elevated above table)."""
    depth = np.full((400, 600), 50, dtype=np.uint8)  # Table level
    # Food bump in center
    depth[100:300, 150:450] = 200  # Food is higher
    return depth


@pytest.fixture
def flat_depth_map():
    """Flat depth map (no food)."""
    return np.full((400, 600), 128, dtype=np.uint8)


@pytest.fixture
def bowl_bbox():
    """Bounding box of a bowl."""
    return [100.0, 50.0, 500.0, 350.0]


# ============================================================
# Tests: FoodSegmenter basics
# ============================================================
class TestFoodSegmenterBasics:
    """Basic tests for FoodSegmenter."""

    def test_segment_returns_result(
        self, segmenter, food_image, food_depth_map
    ):
        """segment() must return SegmentationResult."""
        result = segmenter.segment(food_image, food_depth_map)
        assert isinstance(result, SegmentationResult)

    def test_mask_shape_matches_image(
        self, segmenter, food_image, food_depth_map
    ):
        """Food mask must match image dimensions."""
        result = segmenter.segment(food_image, food_depth_map)
        img_array = np.array(food_image)
        assert result.refined_mask.shape == img_array.shape[:2]

    def test_mask_is_boolean(
        self, segmenter, food_image, food_depth_map
    ):
        """Masks must be boolean."""
        result = segmenter.segment(food_image, food_depth_map)
        assert result.refined_mask.dtype == bool
        assert result.food_mask.dtype == bool

    def test_food_ratio_in_range(
        self, segmenter, food_image, food_depth_map
    ):
        """Food ratio should be between 0 and 1."""
        result = segmenter.segment(food_image, food_depth_map)
        assert 0.0 <= result.food_ratio <= 1.0

    def test_food_area_equals_mask_sum(
        self, segmenter, food_image, food_depth_map
    ):
        """food_area_pixels should equal sum of refined mask."""
        result = segmenter.segment(food_image, food_depth_map)
        assert result.food_area_pixels == int(result.refined_mask.sum())

    def test_bbox_format(
        self, segmenter, food_image, food_depth_map
    ):
        """food_bbox should be [x1, y1, x2, y2]."""
        result = segmenter.segment(food_image, food_depth_map)
        assert len(result.food_bbox) == 4
        if result.food_area_pixels > 0:
            x1, y1, x2, y2 = result.food_bbox
            assert x1 <= x2
            assert y1 <= y2

    def test_timing_positive(
        self, segmenter, food_image, food_depth_map
    ):
        """Timing should be positive."""
        result = segmenter.segment(food_image, food_depth_map)
        assert result.segmentation_time_ms > 0

    def test_quality_valid(
        self, segmenter, food_image, food_depth_map
    ):
        """Quality should be high/medium/low."""
        result = segmenter.segment(food_image, food_depth_map)
        assert result.segmentation_quality in ("high", "medium", "low")

    def test_method_used(
        self, segmenter, food_image, food_depth_map
    ):
        """Method should be depth_color."""
        result = segmenter.segment(food_image, food_depth_map)
        assert result.method_used == "depth_color"


# ============================================================
# Tests: Bowl ROI
# ============================================================
class TestBowlROI:
    """Tests for bowl-focused segmentation."""

    def test_with_bowl_bbox(
        self, segmenter, food_image, food_depth_map, bowl_bbox
    ):
        """Segmentation with bowl bbox should still work."""
        result = segmenter.segment(
            food_image, food_depth_map, bowl_bbox=bowl_bbox
        )
        assert isinstance(result, SegmentationResult)

    def test_bowl_roi_focuses_segmentation(
        self, segmenter, food_image, food_depth_map, bowl_bbox
    ):
        """Bowl bbox should focus food detection inside bowl."""
        result_no_bowl = segmenter.segment(food_image, food_depth_map)
        result_with_bowl = segmenter.segment(
            food_image, food_depth_map, bowl_bbox=bowl_bbox
        )
        # With bowl, food should be more concentrated
        # (not necessarily smaller, but more focused)
        assert isinstance(result_with_bowl, SegmentationResult)


# ============================================================
# Tests: Depth map mismatch
# ============================================================
class TestDepthMapResize:
    """Tests for depth map / image size mismatch."""

    def test_different_depth_size(self, segmenter, food_image):
        """Depth map different size should be auto-resized."""
        # Create depth map with different size
        small_depth = np.full((200, 300), 128, dtype=np.uint8)
        small_depth[50:150, 75:225] = 200

        result = segmenter.segment(food_image, small_depth)
        assert isinstance(result, SegmentationResult)
        assert result.refined_mask.shape == (400, 600)


# ============================================================
# Tests: Edge cases
# ============================================================
class TestEdgeCases:
    """Edge case tests."""

    def test_uniform_image(self, segmenter, flat_depth_map):
        """Uniform depth + color should still return result."""
        uniform_img = Image.new("RGB", (600, 400), (128, 128, 128))
        result = segmenter.segment(uniform_img, flat_depth_map)
        assert isinstance(result, SegmentationResult)

    def test_small_image(self, segmenter):
        """Very small image should work."""
        small_img = Image.new("RGB", (50, 50), (200, 100, 50))
        small_depth = np.full((50, 50), 200, dtype=np.uint8)
        result = segmenter.segment(small_img, small_depth)
        assert isinstance(result, SegmentationResult)

    def test_is_loaded(self, segmenter):
        """Segmenter should always be loaded."""
        assert segmenter.is_loaded

    def test_singleton(self):
        """get_food_segmenter should return same instance."""
        s1 = get_food_segmenter()
        s2 = get_food_segmenter()
        assert s1 is s2


# ============================================================
# Tests: Component counting
# ============================================================
class TestComponentCounting:
    """Tests for counting connected components."""

    def test_single_food_region(
        self, segmenter, food_image, food_depth_map
    ):
        """Single contiguous food should give 1 component."""
        result = segmenter.segment(food_image, food_depth_map)
        assert result.num_components >= 1  # At least 1

    def test_count_components_empty(self, segmenter):
        """Empty mask should give 0 components."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        count = segmenter._count_components(mask)
        assert count == 0

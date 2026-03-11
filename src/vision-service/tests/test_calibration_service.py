"""
Unit tests for Calibration Service (Task 2.3).

Run: cd src/vision-service && pytest tests/test_calibration_service.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.calibration_service import (
    CalibrationResult,
    CalibrationService,
    DepthRegionStats,
    get_calibration_service,
)


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def cal_service():
    """Create calibration service."""
    return CalibrationService()


@pytest.fixture
def sample_depth_map():
    """Create a sample depth map with food-like pattern."""
    # 200x300 depth map: table (low depth) + food bump (high depth)
    depth = np.zeros((200, 300), dtype=np.uint8)
    # Table background at depth 50
    depth[:, :] = 50
    # Food region at depth 180 (elevated)
    depth[60:140, 80:220] = 180
    # Some gradient at food edges
    depth[50:150, 70:230] = np.clip(depth[50:150, 70:230] + 30, 0, 255)
    return depth


@pytest.fixture
def flat_depth_map():
    """Depth map with no variation (flat table, no food)."""
    return np.full((200, 300), 128, dtype=np.uint8)


@pytest.fixture
def food_mask():
    """Binary mask for food region."""
    mask = np.zeros((200, 300), dtype=bool)
    mask[60:140, 80:220] = True
    return mask


# ============================================================
# Tests: CalibrationService
# ============================================================
class TestCalibrationService:
    """Tests for CalibrationService."""

    def test_calibrate_returns_result(self, cal_service, sample_depth_map):
        """calibrate() must return CalibrationResult."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=20.0,
            reference_class="bat_pho_m",
            reference_confidence=0.9,
        )
        assert isinstance(result, CalibrationResult)

    def test_scale_factors_consistent(self, cal_service, sample_depth_map):
        """cm_per_pixel should be inverse of pixels_per_cm."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=20.0,
        )
        assert abs(result.cm_per_pixel - 1.0 / 20.0) < 1e-6

    def test_image_dimensions_cm(self, cal_service, sample_depth_map):
        """Image dimensions in cm should match pixel dimensions / scale."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=20.0,
            image_size=(300, 200),
        )
        assert abs(result.image_width_cm - 15.0) < 0.1   # 300/20
        assert abs(result.image_height_cm - 10.0) < 0.1  # 200/20

    def test_depth_map_cm_shape(self, cal_service, sample_depth_map):
        """Calibrated depth map must have same shape as input."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=20.0,
        )
        assert result.depth_map_cm.shape == sample_depth_map.shape

    def test_depth_map_cm_range(self, cal_service, sample_depth_map):
        """Calibrated depth map values should be in DEPTH_RANGE_CM."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=20.0,
        )
        assert result.depth_map_cm.min() >= 0.0
        assert result.depth_map_cm.max() <= cal_service.DEPTH_RANGE_CM[1]

    def test_invalid_scale_factor_raises(self, cal_service, sample_depth_map):
        """Zero or negative scale factor must raise ValueError."""
        with pytest.raises(ValueError, match="Invalid scale factor"):
            cal_service.calibrate(
                depth_map=sample_depth_map,
                pixels_per_cm=0.0,
            )
        with pytest.raises(ValueError):
            cal_service.calibrate(
                depth_map=sample_depth_map,
                pixels_per_cm=-5.0,
            )

    def test_flat_depth_gives_zero(self, cal_service, flat_depth_map):
        """Flat depth map should produce all-zero calibrated depth."""
        result = cal_service.calibrate(
            depth_map=flat_depth_map,
            pixels_per_cm=20.0,
        )
        assert result.depth_map_cm.max() == 0.0

    def test_high_quality_calibration(self, cal_service, sample_depth_map):
        """Good conditions should give high quality."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=25.0,
            reference_class="bat_pho_m",
            reference_confidence=0.95,
        )
        assert result.calibration_quality == "high"

    def test_low_confidence_reduces_quality(self, cal_service, sample_depth_map):
        """Low reference confidence should reduce quality."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=25.0,
            reference_confidence=0.3,
        )
        assert result.calibration_quality in ("medium", "low")

    def test_extreme_scale_reduces_quality(self, cal_service, sample_depth_map):
        """Extreme scale factor should reduce quality."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=200.0,  # Very extreme
            reference_confidence=0.9,
        )
        assert result.calibration_quality in ("medium", "low")

    def test_calibration_time_non_negative(self, cal_service, sample_depth_map):
        """Calibration time should be non-negative."""
        result = cal_service.calibrate(
            depth_map=sample_depth_map,
            pixels_per_cm=20.0,
        )
        assert result.calibration_time_ms >= 0


# ============================================================
# Tests: Region measurement
# ============================================================
class TestMeasureRegion:
    """Tests for measure_region()."""

    def test_measure_region_returns_stats(
        self, cal_service, sample_depth_map, food_mask
    ):
        """measure_region() must return DepthRegionStats."""
        cal = cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        stats = cal_service.measure_region(cal, food_mask)
        assert isinstance(stats, DepthRegionStats)

    def test_area_cm2_positive(
        self, cal_service, sample_depth_map, food_mask
    ):
        """Area in cm² should be positive for non-empty mask."""
        cal = cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        stats = cal_service.measure_region(cal, food_mask)
        assert stats.area_cm2 > 0

    def test_area_cm2_calculation(
        self, cal_service, sample_depth_map, food_mask
    ):
        """Area in cm² should be = pixels * (cm/px)²."""
        cal = cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        stats = cal_service.measure_region(cal, food_mask)
        expected = int(food_mask.sum()) * (1.0 / 20.0) ** 2
        assert abs(stats.area_cm2 - expected) < 0.01

    def test_empty_mask_returns_zero(self, cal_service, sample_depth_map):
        """Empty mask should return zeros."""
        cal = cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        empty_mask = np.zeros((200, 300), dtype=bool)
        stats = cal_service.measure_region(cal, empty_mask)
        assert stats.area_pixels == 0
        assert stats.area_cm2 == 0.0

    def test_mismatched_mask_raises(self, cal_service, sample_depth_map):
        """Mismatched mask shape should raise ValueError."""
        cal = cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        wrong_mask = np.zeros((100, 100), dtype=bool)
        with pytest.raises(ValueError, match="Mask shape"):
            cal_service.measure_region(cal, wrong_mask)

    def test_food_region_has_higher_depth(
        self, cal_service, sample_depth_map, food_mask
    ):
        """Food region should have higher mean depth than background."""
        cal = cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        food_stats = cal_service.measure_region(cal, food_mask)
        bg_stats = cal_service.measure_region(cal, ~food_mask)
        assert food_stats.mean_depth > bg_stats.mean_depth


# ============================================================
# Tests: Utility methods
# ============================================================
class TestUtilities:
    """Tests for pixels_to_cm and cm_to_pixels."""

    def test_pixels_to_cm(self, cal_service, sample_depth_map):
        """pixels_to_cm should use correct scale."""
        cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        assert abs(cal_service.pixels_to_cm(100) - 5.0) < 0.01

    def test_cm_to_pixels(self, cal_service, sample_depth_map):
        """cm_to_pixels should be inverse of pixels_to_cm."""
        cal_service.calibrate(
            depth_map=sample_depth_map, pixels_per_cm=20.0
        )
        assert abs(cal_service.cm_to_pixels(5.0) - 100.0) < 0.01

    def test_no_calibration_raises(self, cal_service):
        """Using utility without calibration should raise RuntimeError."""
        with pytest.raises(RuntimeError, match="No calibration"):
            cal_service.pixels_to_cm(100)

    def test_singleton(self):
        """get_calibration_service should return same instance."""
        s1 = get_calibration_service()
        s2 = get_calibration_service()
        assert s1 is s2

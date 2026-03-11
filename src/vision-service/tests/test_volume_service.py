"""
Unit tests for Volume Estimation Service (Task 2.5).

Tests cover:
  - Core volume formula correctness
  - Empty/zero mask handling
  - Weight, carb, GL calculation chain
  - Density factor application (solid vs liquid dishes)
  - Food ID resolution (full ID, short ID, unknown, None)
  - Quality assessment (high/medium/low)
  - Singleton pattern
  - Edge cases (shape mismatch, near-zero heights)

Run: cd src/vision-service && pytest tests/test_volume_service.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.volume_service import (
    VolumeEstimator,
    VolumeResult,
    get_volume_estimator,
)


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def estimator():
    """Fresh VolumeEstimator with real data files."""
    return VolumeEstimator()


@pytest.fixture
def flat_depth_food():
    """
    Controlled geometry for exact volume checks.

    Layout (100×100 pixel image, cm_per_pixel=0.1):
      - Entire image: depth_map_cm = 2.0 cm  (table level)
      - Center 50×50 pixels: depth_map_cm = 7.0 cm  (food)

    Expected:
      - table_level ≈ 2.0 cm  (10th percentile of non-food pixels)
      - height per food pixel = 7.0 - 2.0 = 5.0 cm
      - pixel_area = 0.1² = 0.01 cm²
      - volume = 50×50 × 5.0 × 0.01 = 125.0 cm³
    """
    depth = np.full((100, 100), 2.0, dtype=np.float64)
    depth[25:75, 25:75] = 7.0  # Elevated food region

    mask = np.zeros((100, 100), dtype=bool)
    mask[25:75, 25:75] = True

    return depth, mask


@pytest.fixture
def sample_depth_mask():
    """Realistic-looking depth + mask (no exact geometry guarantee)."""
    rng = np.random.default_rng(42)
    # 200×200 image
    depth = np.full((200, 200), 3.0, dtype=np.float64)   # table background
    depth[60:140, 60:140] = 8.0 + rng.uniform(0, 1, (80, 80))  # food with noise
    mask = np.zeros((200, 200), dtype=bool)
    mask[60:140, 60:140] = True
    return depth, mask


# ============================================================
# Tests: Core volume formula
# ============================================================
class TestVolumeFormula:
    """Test the discrete integral V = Σ height × pixel_area."""

    def test_estimate_returns_volume_result(self, estimator, flat_depth_food):
        """estimate() must return VolumeResult instance."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert isinstance(result, VolumeResult)

    def test_exact_volume_known_geometry(self, estimator, flat_depth_food):
        """
        With known geometry: 50×50 food at height 5cm above table,
        pixel_area=0.01 cm², expected V = 125 cm³.

        Tolerance: ±5% to account for percentile estimator of table_level.
        """
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        expected = 125.0
        assert abs(result.volume_cm3 - expected) / expected < 0.05

    def test_volume_equals_volume_ml(self, estimator, flat_depth_food):
        """volume_cm3 and volume_ml must be identical (1 cm³ = 1 mL)."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.volume_cm3 == result.volume_ml

    def test_empty_mask_gives_zero_volume(self, estimator):
        """Empty mask → volume = 0, quality = 'low'."""
        depth = np.full((100, 100), 5.0)
        mask = np.zeros((100, 100), dtype=bool)
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.volume_cm3 == 0.0
        assert result.weight_g == 0.0
        assert result.carb_g == 0.0
        assert result.glycemic_load == 0.0
        assert result.estimation_quality == "low"

    def test_volume_positive_for_elevated_food(self, estimator, sample_depth_mask):
        """Volume must be positive when food is elevated above background."""
        depth, mask = sample_depth_mask
        result = estimator.estimate(depth, mask, cm_per_pixel=0.05)
        assert result.volume_cm3 > 0

    def test_food_area_cm2_correct(self, estimator, flat_depth_food):
        """food_area_cm2 = food_pixels × cm_per_pixel²."""
        depth, mask = flat_depth_food
        cm_per_pixel = 0.1
        result = estimator.estimate(depth, mask, cm_per_pixel=cm_per_pixel)
        expected_area = mask.sum() * (cm_per_pixel ** 2)   # 2500 × 0.01 = 25 cm²
        assert abs(result.food_area_cm2 - expected_area) < 0.01

    def test_larger_cm_per_pixel_gives_larger_volume(self, estimator, flat_depth_food):
        """Bigger pixels → larger area per pixel → larger volume."""
        depth, mask = flat_depth_food
        r1 = estimator.estimate(depth, mask, cm_per_pixel=0.05)
        r2 = estimator.estimate(depth, mask, cm_per_pixel=0.10)
        assert r2.volume_cm3 > r1.volume_cm3

    def test_shape_mismatch_raises(self, estimator):
        """Mismatched depth and mask shapes must raise ValueError."""
        depth = np.ones((100, 100))
        mask = np.zeros((200, 200), dtype=bool)
        with pytest.raises(ValueError, match="shape"):
            estimator.estimate(depth, mask, cm_per_pixel=0.1)


# ============================================================
# Tests: GL calculation chain
# ============================================================
class TestGLCalculation:
    """Test weight → carb → GL formula chain."""

    def test_gl_formula_white_rice(self, estimator, flat_depth_food):
        """
        GL = carb_g × GI / 100, where carb_g = weight_g × carb_per_100g / 100.
        White rice: GI=73, carb_per_100g=28.2, density=1.08, solid_ratio=1.0.
        """
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_com_trang")

        expected_weight = result.volume_ml * result.solid_ratio * result.density_g_per_ml
        expected_carb = expected_weight * 28.2 / 100.0
        expected_gl = expected_carb * 73 / 100.0

        assert abs(result.weight_g - expected_weight) < 0.01
        assert abs(result.carb_g - expected_carb) < 0.01
        assert abs(result.glycemic_load - expected_gl) < 0.01

    def test_gi_is_73_for_white_rice(self, estimator, flat_depth_food):
        """White rice GI must be 73."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_com_trang")
        assert result.glycemic_index == 73

    def test_gl_positive_for_nonempty_mask(self, estimator, flat_depth_food):
        """GL must be positive when there are food pixels."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.glycemic_load > 0

    def test_empty_mask_gives_zero_gl(self, estimator):
        """No food → GL = 0."""
        depth = np.full((100, 100), 5.0)
        mask = np.zeros((100, 100), dtype=bool)
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.glycemic_load == 0.0

    def test_timing_non_negative(self, estimator, flat_depth_food):
        """Estimation time must be >= 0."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.estimation_time_ms >= 0.0


# ============================================================
# Tests: Density factor — liquid vs solid dishes
# ============================================================
class TestDensityFactor:
    """
    Task 2.5.2 (Hoàng): Verify density factors are applied correctly
    for liquid dishes (phở, bún bò) vs solid dishes (cơm tấm, bánh mì).
    """

    def test_solid_dish_solid_ratio_is_one(self, estimator, flat_depth_food):
        """Cơm trắng is fully solid: solid_ratio = 1.0."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_com_trang")
        assert result.solid_ratio == 1.0
        assert result.is_liquid_dish is False

    def test_pho_solid_ratio_less_than_one(self, estimator, flat_depth_food):
        """Phở bò is a soup: solid_ratio < 1 (broth volume is excluded)."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo")
        assert result.solid_ratio < 1.0
        assert result.is_liquid_dish is True

    def test_pho_weight_less_than_rice_same_volume(self, estimator, flat_depth_food):
        """
        Same volume, same depth map → pho should weigh LESS than rice because
        solid_ratio(pho) = 0.3 << solid_ratio(rice) = 1.0.
        """
        depth, mask = flat_depth_food
        rice_result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_com_trang"
        )
        pho_result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo"
        )
        assert pho_result.weight_g < rice_result.weight_g

    def test_bun_bo_hue_is_liquid(self, estimator, flat_depth_food):
        """Bún bò Huế must be classified as liquid dish."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_bun_bo_hue")
        assert result.is_liquid_dish is True
        assert result.solid_ratio < 1.0

    def test_weight_formula_manual_check(self, estimator, flat_depth_food):
        """
        Manual check: volume=125mL, pho solid_ratio=0.3, density=1.02
        weight = 125 × 0.3 × 1.02 = 38.25 g (within 5% tolerance).
        """
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo")
        # Volume ≈ 125 mL (verified in test_exact_volume_known_geometry)
        expected_weight = result.volume_ml * 0.3 * 1.02
        assert abs(result.weight_g - expected_weight) < 0.01


# ============================================================
# Tests: Food ID resolution
# ============================================================
class TestFoodIDResolution:
    """Test that food IDs are resolved correctly from various input formats."""

    def test_full_id_resolved(self, estimator, flat_depth_food):
        """Full nutrition DB ID 'vn_com_trang' should resolve correctly."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_com_trang")
        assert result.food_id == "vn_com_trang"
        assert result.food_name_en != ""

    def test_short_id_resolved(self, estimator, flat_depth_food):
        """Short ID 'pho_bo' (without 'vn_') should auto-resolve to 'vn_pho_bo'."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="pho_bo")
        assert result.food_id == "vn_pho_bo"

    def test_none_food_id_defaults_to_com_trang(self, estimator, flat_depth_food):
        """food_id=None should default to vn_com_trang."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id=None)
        assert result.food_id == "vn_com_trang"

    def test_unknown_food_id_defaults_to_com_trang(self, estimator, flat_depth_food):
        """Unknown food_id should warn (logged) and default to vn_com_trang."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="unknown_xyz")
        assert result.food_id == "vn_com_trang"

    def test_all_nutrition_ids_resolvable(self, estimator, flat_depth_food):
        """Every food in the nutrition DB must be callable without fallback."""
        depth, mask = flat_depth_food
        for food_id in estimator.get_available_foods():
            result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id=food_id)
            assert result.food_id == food_id, f"ID mismatch for {food_id}"
            assert result.glycemic_index > 0


# ============================================================
# Tests: Quality assessment
# ============================================================
class TestQualityAssessment:
    """Test quality scoring logic for volume estimates."""

    def test_high_quality_realistic_food(self, estimator, flat_depth_food):
        """
        125 mL volume with decent food area and height should yield 'high'.
        """
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.estimation_quality == "high"

    def test_low_quality_empty_mask(self, estimator):
        """Empty mask returns quality='low' with descriptive reason."""
        depth = np.full((100, 100), 5.0)
        mask = np.zeros((100, 100), dtype=bool)
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.estimation_quality == "low"
        assert "empty" in result.quality_reason.lower()

    def test_low_quality_flat_depth(self, estimator):
        """
        Food pixels at same depth as table (flat depth) → mean_height ≈ 0
        → quality should be 'low' or 'medium' (not 'high').
        """
        depth = np.full((100, 100), 5.0)   # Uniformly flat
        mask = np.zeros((100, 100), dtype=bool)
        mask[25:75, 25:75] = True          # 25% food coverage
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.estimation_quality in ("low", "medium")

    def test_quality_reason_not_empty(self, estimator, flat_depth_food):
        """quality_reason must always be a non-empty string."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert isinstance(result.quality_reason, str)
        assert len(result.quality_reason) > 0


# ============================================================
# Tests: Singleton
# ============================================================
class TestSingleton:
    def test_singleton_returns_same_instance(self):
        """get_volume_estimator() must return the same instance each time."""
        a = get_volume_estimator()
        b = get_volume_estimator()
        assert a is b

    def test_available_foods_non_empty(self, estimator):
        """Loaded nutrition DB should have foods available."""
        foods = estimator.get_available_foods()
        assert len(foods) >= 10   # We have 10 VN foods

    def test_available_foods_contains_rice(self, estimator):
        """vn_com_trang must be in the food list."""
        assert "vn_com_trang" in estimator.get_available_foods()

    def test_available_foods_contains_pho(self, estimator):
        """vn_pho_bo must be in the food list."""
        assert "vn_pho_bo" in estimator.get_available_foods()

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
        pixel_area=0.01 cm², raw V = 125 cm³.
        After DAv2 correction factor (0.35): expected V = 43.75 cm³.

        Tolerance: ±5% to account for percentile estimator of table_level.
        """
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        expected = 125.0 * 0.35  # raw volume × DAv2 correction factor
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

    def test_pho_weight_less_than_rice_per_ml(self, estimator, flat_depth_food):
        """
        Per-mL effective weight of pho should be less than rice because
        solid_ratio(pho) = 0.3 << solid_ratio(rice) = 1.0.
        Note: Pho uses bowl volume prior, rice uses depth integral,
        so absolute volumes differ.
        """
        depth, mask = flat_depth_food
        rice_result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_com_trang"
        )
        pho_result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo"
        )
        # Effective density (g per mL) should be lower for soup
        rice_gpm = rice_result.weight_g / rice_result.volume_ml
        pho_gpm = pho_result.weight_g / pho_result.volume_ml
        assert pho_gpm < rice_gpm

    def test_bun_bo_hue_is_liquid(self, estimator, flat_depth_food):
        """Bún bò Huế must be classified as liquid dish."""
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_bun_bo_hue")
        assert result.is_liquid_dish is True
        assert result.solid_ratio < 1.0

    def test_weight_formula_manual_check(self, estimator, flat_depth_food):
        """
        Manual check for phở: bowl prior = 500 mL,
        solid_ratio=0.3, density=1.02.
        weight = 500 × 0.3 × 1.02 = 153 g.
        """
        depth, mask = flat_depth_food
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo")
        # Phở uses bowl volume prior (500 mL)
        assert abs(result.volume_ml - 500.0) < 1.0
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

    def test_low_seg_override_quality(self, estimator):
        """
        Food mask covering < 5% of image should force quality='low' with
        segmentation warning, even if other criteria are OK.
        """
        depth = np.full((200, 200), 2.0, dtype=np.float64)
        mask = np.zeros((200, 200), dtype=bool)
        # ~2% food coverage (< 5% threshold)
        mask[95:105, 95:105] = True  # 100 pixels out of 40000 = 0.25%
        depth[95:105, 95:105] = 7.0
        result = estimator.estimate(depth, mask, cm_per_pixel=0.1)
        assert result.estimation_quality == "low"
        assert "segmentation" in result.quality_reason.lower()


# ============================================================
# Tests: Dynamic bowl-fill estimation for soup dishes
# ============================================================
class TestBowlFillEstimation:
    """Test that liquid dishes scale bowl prior by fill ratio from depth map."""

    @pytest.fixture
    def full_bowl_scene(self):
        """
        200×200 image simulating a FULL bowl seen from above.

        Layout:
          - Table (background): depth = 1.0 cm (low, far from camera)
          - Bowl rim (ring): depth = 4.0 cm (high, close to camera)
          - Bowl interior (liquid surface): depth = 3.8 cm (near rim = full)
          - Food mask covers center 80×80 pixels

        Bowl bbox: [40, 40, 160, 160] (centered, 120×120 px)
        """
        depth = np.full((200, 200), 1.0, dtype=np.float64)  # table

        yy, xx = np.ogrid[:200, :200]
        cx, cy, hw, hh = 100.0, 100.0, 60.0, 60.0
        dist_sq = ((xx - cx) / hw) ** 2 + ((yy - cy) / hh) ** 2

        # Rim ring (85-100% of half-widths)
        rim = (dist_sq > 0.85 ** 2) & (dist_sq <= 1.0)
        depth[rim] = 4.0

        # Interior (< 65% of half-widths) — full bowl, liquid near rim
        interior = dist_sq <= 0.65 ** 2
        depth[interior] = 3.8

        # Transition zone
        mid = (dist_sq > 0.65 ** 2) & (dist_sq <= 0.85 ** 2)
        depth[mid] = 3.5

        mask = np.zeros((200, 200), dtype=bool)
        mask[60:140, 60:140] = True  # food in center

        bowl_bbox = [40.0, 40.0, 160.0, 160.0]
        return depth, mask, bowl_bbox

    @pytest.fixture
    def half_bowl_scene(self):
        """
        200×200 image simulating a HALF-EMPTY bowl.

        Same as full_bowl but interior liquid surface is much lower.
          - Interior depth = 2.0 cm (between table=1.0 and rim=4.0)
        """
        depth = np.full((200, 200), 1.0, dtype=np.float64)  # table

        yy, xx = np.ogrid[:200, :200]
        cx, cy, hw, hh = 100.0, 100.0, 60.0, 60.0
        dist_sq = ((xx - cx) / hw) ** 2 + ((yy - cy) / hh) ** 2

        rim = (dist_sq > 0.85 ** 2) & (dist_sq <= 1.0)
        depth[rim] = 4.0

        # Interior — half-empty, liquid surface much lower
        interior = dist_sq <= 0.65 ** 2
        depth[interior] = 2.0

        mid = (dist_sq > 0.65 ** 2) & (dist_sq <= 0.85 ** 2)
        depth[mid] = 2.5

        mask = np.zeros((200, 200), dtype=bool)
        mask[60:140, 60:140] = True

        bowl_bbox = [40.0, 40.0, 160.0, 160.0]
        return depth, mask, bowl_bbox

    def test_full_bowl_near_prior(self, estimator, full_bowl_scene):
        """Full bowl of phở should give volume close to the bowl prior (500mL)."""
        depth, mask, bbox = full_bowl_scene
        result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo", bowl_bbox=bbox,
        )
        # fill_ratio should be ~0.93 (3.8-1.0)/(4.0-1.0) ≈ 0.93
        assert result.volume_ml > 400.0, f"Full bowl too low: {result.volume_ml}"
        assert result.fill_ratio > 0.85

    def test_half_bowl_much_less(self, estimator, half_bowl_scene):
        """Half-empty bowl should give significantly less volume."""
        depth, mask, bbox = half_bowl_scene
        result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo", bowl_bbox=bbox,
        )
        # fill_ratio should be ~0.33 (2.0-1.0)/(4.0-1.0) ≈ 0.33
        assert result.volume_ml < 300.0, f"Half bowl too high: {result.volume_ml}"
        assert result.fill_ratio < 0.5

    def test_full_vs_half_differ(self, estimator, full_bowl_scene, half_bowl_scene):
        """Full bowl must produce higher volume than half bowl."""
        d_full, m_full, bb_full = full_bowl_scene
        d_half, m_half, bb_half = half_bowl_scene
        r_full = estimator.estimate(
            d_full, m_full, cm_per_pixel=0.1, food_id="vn_bun_bo_hue", bowl_bbox=bb_full,
        )
        r_half = estimator.estimate(
            d_half, m_half, cm_per_pixel=0.1, food_id="vn_bun_bo_hue", bowl_bbox=bb_half,
        )
        assert r_full.volume_ml > r_half.volume_ml * 1.5, (
            f"Full ({r_full.volume_ml:.0f}mL) should be >1.5× half ({r_half.volume_ml:.0f}mL)"
        )

    def test_no_bowl_bbox_falls_back_to_prior(self, estimator, full_bowl_scene):
        """Without bowl_bbox, liquid dish should use full bowl prior (fallback)."""
        depth, mask, _ = full_bowl_scene
        result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo",
            # No bowl_bbox → fill_ratio = 1.0
        )
        assert abs(result.volume_ml - 500.0) < 1.0
        assert result.fill_ratio == 1.0

    def test_solid_food_ignores_bowl_bbox(self, estimator, full_bowl_scene):
        """Solid dish should use depth integral, not bowl prior, even with bbox."""
        depth, mask, bbox = full_bowl_scene
        result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_com_trang", bowl_bbox=bbox,
        )
        assert result.volume_ml < 200  # depth integral, not bowl prior
        assert result.fill_ratio == 1.0  # fill_ratio stays 1.0 for solid

    def test_rim_too_low_defaults_to_full(self, estimator):
        """When rim height <= 0.1 cm (bbox on table), fill_ratio should be 1.0."""
        # Everything at table level — no rim contrast
        depth = np.full((200, 200), 1.0, dtype=np.float64)
        depth[60:140, 60:140] = 1.05  # barely above table

        mask = np.zeros((200, 200), dtype=bool)
        mask[60:140, 60:140] = True

        bbox = [40.0, 40.0, 160.0, 160.0]
        result = estimator.estimate(
            depth, mask, cm_per_pixel=0.1, food_id="vn_pho_bo", bowl_bbox=bbox,
        )
        # fill_ratio should fall back to 1.0 (rim_height ≈ 0.0 ≤ 0.1)
        assert result.fill_ratio == 1.0
        assert abs(result.volume_ml - 500.0) < 1.0


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

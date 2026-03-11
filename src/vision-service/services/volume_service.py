"""
Volume estimation service.
Compute food volume from calibrated depth map + food segmentation mask,
then convert volume → weight → carbohydrates → Glycemic Load.

Task 2.5 - Volume Estimation

WHY V = ∫∫ depth(x,y) dA?
───────────────────────────
Imagine looking at a bowl of pho from above. Each pixel covers a tiny
square patch of food (dA = pixel_area_cm²). The food column at that
patch has height = depth_map_cm[y,x] − table_level in centimeters.
Summing all columns gives the total volume.

Discrete form:
  V = Σ height(x,y) × pixel_area_cm²   for all (x,y) in food_mask

where:
  height(x,y)  = max(0,  depth_map_cm[y,x] − table_level)
  table_level  = 10th percentile of non-food pixel depths
  pixel_area   = cm_per_pixel²

WHY subtract table_level?
──────────────────────────
The calibrated depth_map_cm is mapped to the range [0, 15cm] but
the ABSOLUTE camera distance is unknown. The table surface is our
"floor". Without subtracting table_level every pixel would erroneously
accumulate the full camera-to-table distance instead of just the food's
own height above the table.

WHY 10th percentile (not minimum)?
────────────────────────────────────
Minimum pixel values may be noisy outliers from shadowed corners or
lens vignette. The 10th percentile of non-food pixels robustly
represents the true table/bowl surface while ignoring noise.

WHY Density Factor for soups?
──────────────────────────────
A pho bowl estimated at 500 mL contains ~70% broth (water, near-zero
carbs) and ~30% noodles + meat. Applying solid_ratio = 0.3 means we
only count the carbohydrate-bearing solid mass:
  Weight_solid = 500 × 0.3 × 1.02 = 153 g
  Carb = 153 × 22.5 / 100 = 34 g   (vs naively 500 × density = 510 g)

This is the critical correction that makes GL estimates clinically
meaningful for Vietnamese soup dishes.
"""

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ============================================================
# Paths (relative to project root)
# ============================================================
_DATA_ROOT = Path(__file__).parents[3] / "data" / "nutrition_db"
_DENSITY_FACTORS_PATH = _DATA_ROOT / "density_factors.json"
_NUTRITION_DB_PATH = _DATA_ROOT / "vn_food_nutrition.json"

# Mapping: nutrition DB food_id → density factor food_id
# Needed because the two JSONs use slightly different naming conventions.
_NUTRITION_TO_DENSITY: Dict[str, str] = {
    "vn_com_trang":      "com_trang",
    "vn_pho_bo":         "pho_bo_standard",
    "vn_bun_bo_hue":     "bun_bo_hue",
    "vn_banh_mi":        "banh_mi",
    "vn_com_tam":        "com_tam",
    "vn_bun_thit_nuong": "bun_thit_nuong",
    "vn_mi_xao":         "mi_xao",
    "vn_chao":           "chao_loang",
    "vn_xoi":            "xoi",
    "vn_tra_sua":        "tra_sua",
}

_DEFAULT_FOOD_ID = "vn_com_trang"    # Fallback when food_id unknown


# ============================================================
# Data classes
# ============================================================
@dataclass
class NutritionInfo:
    """Nutrition data for one food item (from vn_food_nutrition.json)."""
    food_id: str
    food_name_vi: str
    food_name_en: str
    gi_index: int
    gi_category: str
    carb_per_100g: float
    is_liquid: bool


@dataclass
class DensityFactor:
    """Density factor for one food item (from density_factors.json)."""
    food_id: str
    name_vi: str
    solid_ratio: float          # Fraction of volume that is solid food (0-1)
    density_g_per_ml: float     # Density of the solid portion


@dataclass
class VolumeResult:
    """Full result of volume estimation + GL computation."""

    # Volume (cm³ ≡ mL because 1 cm³ = 1 mL)
    volume_cm3: float
    volume_ml: float

    # Weight
    weight_g: float             # weight_g = volume_ml × solid_ratio × density

    # Nutrition
    carb_g: float               # carb_g = weight_g × carb_per_100g / 100
    glycemic_load: float        # GL = carb_g × gi_index / 100
    glycemic_index: int

    # Food identity
    food_id: str
    food_name_vi: str
    food_name_en: str
    is_liquid_dish: bool

    # Density details
    solid_ratio: float
    density_g_per_ml: float

    # Geometry
    food_area_cm2: float            # Footprint area of food in cm²
    mean_food_height_cm: float      # Average height of food above table (cm)

    # Quality
    estimation_quality: str         # "high" / "medium" / "low"
    quality_reason: str

    # Timing
    estimation_time_ms: float


# ============================================================
# VolumeEstimator
# ============================================================
class VolumeEstimator:
    """
    Estimate food volume using discrete integral over segmented food region.

    Pipeline:
      1. Detect table level (background) from non-food pixel depths
      2. Compute per-pixel food height = depth_food − table_level
      3. Integrate: V = Σ height × pixel_area_cm²
      4. Lookup density factor to get weight = V × solid_ratio × density
      5. Compute carb = weight × carb_per_100g / 100
      6. Compute GL = carb × GI / 100
    """

    def __init__(
        self,
        density_factors_path: Optional[Path] = None,
        nutrition_db_path: Optional[Path] = None,
    ):
        self._density_factors: Dict[str, DensityFactor] = {}
        self._nutrition_db: Dict[str, NutritionInfo] = {}

        self._load_density_factors(density_factors_path or _DENSITY_FACTORS_PATH)
        self._load_nutrition_db(nutrition_db_path or _NUTRITION_DB_PATH)

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------
    def estimate(
        self,
        depth_map_cm: np.ndarray,
        food_mask: np.ndarray,
        cm_per_pixel: float,
        food_id: Optional[str] = None,
    ) -> VolumeResult:
        """
        Estimate food volume and compute GL.

        Args:
            depth_map_cm: Calibrated depth map (H, W) in cm from
                          CalibrationResult.depth_map_cm.
                          Higher value = closer to camera = higher food surface.
            food_mask:    Binary mask (H, W), True = food pixel,
                          from SegmentationResult.refined_mask.
            cm_per_pixel: Real-world size of one pixel in cm,
                          from CalibrationResult.cm_per_pixel.
            food_id:      Nutrition DB food ID (e.g. "vn_com_trang").
                          Defaults to "vn_com_trang" if None or not found.

        Returns:
            VolumeResult containing volume, weight, carb, GL, and metadata.

        Raises:
            ValueError: If depth_map_cm and food_mask shapes do not match.
        """
        t0 = time.time()

        mask = food_mask.astype(bool)
        if depth_map_cm.shape[:2] != mask.shape[:2]:
            raise ValueError(
                f"depth_map_cm shape {depth_map_cm.shape} != "
                f"food_mask shape {mask.shape}"
            )

        # ── Step 1: Detect table (background) level ──────────────────────
        # Use the 10th percentile of non-food pixel depths as the floor
        # reference. This is more robust than simple minimum (noise-resistant).
        non_food = depth_map_cm[~mask]
        if len(non_food) >= 10:
            table_level = float(np.percentile(non_food, 10))
        else:
            # Edge case: mask covers almost the entire image
            table_level = float(np.percentile(depth_map_cm, 5))

        # ── Step 2: Per-pixel food height above table ─────────────────────
        food_depths = depth_map_cm[mask]
        if len(food_depths) == 0:
            # Empty mask → no food detected
            return self._zero_result(
                food_id=self._resolve_food_id(food_id),
                elapsed_ms=(time.time() - t0) * 1000,
            )

        heights = np.maximum(food_depths - table_level, 0.0)

        # ── Step 3: Discrete integral V = Σ height × dA ──────────────────
        pixel_area_cm2 = cm_per_pixel ** 2
        food_area_cm2 = float(mask.sum()) * pixel_area_cm2
        volume_cm3 = float(np.sum(heights) * pixel_area_cm2)
        mean_height = float(np.mean(heights))

        # ── Step 4: Lookup food data ──────────────────────────────────────
        resolved_id = self._resolve_food_id(food_id)
        nutrition = self._get_nutrition(resolved_id)
        density = self._get_density(resolved_id)

        # ── Step 5: Weight → Carb → GL ───────────────────────────────────
        volume_ml = volume_cm3                                          # 1 cm³ = 1 mL
        weight_g = volume_ml * density.solid_ratio * density.density_g_per_ml
        carb_g = weight_g * nutrition.carb_per_100g / 100.0
        glycemic_load = carb_g * nutrition.gi_index / 100.0

        # ── Step 6: Quality assessment ────────────────────────────────────
        quality, reason = self._assess_quality(
            volume_cm3=volume_cm3,
            food_mask=mask,
            mean_height=mean_height,
        )

        elapsed_ms = (time.time() - t0) * 1000

        result = VolumeResult(
            volume_cm3=volume_cm3,
            volume_ml=volume_ml,
            weight_g=weight_g,
            carb_g=carb_g,
            glycemic_load=glycemic_load,
            glycemic_index=nutrition.gi_index,
            food_id=resolved_id,
            food_name_vi=nutrition.food_name_vi,
            food_name_en=nutrition.food_name_en,
            is_liquid_dish=nutrition.is_liquid,
            solid_ratio=density.solid_ratio,
            density_g_per_ml=density.density_g_per_ml,
            food_area_cm2=food_area_cm2,
            mean_food_height_cm=mean_height,
            estimation_quality=quality,
            quality_reason=reason,
            estimation_time_ms=elapsed_ms,
        )

        logger.info(
            f"Volume: {volume_cm3:.1f}cm³ → {weight_g:.1f}g → "
            f"carb={carb_g:.1f}g, GL={glycemic_load:.1f} "
            f"[{nutrition.food_name_en}] quality={quality} ({elapsed_ms:.1f}ms)"
        )

        return result

    def get_available_foods(self) -> List[str]:
        """Return list of all available food IDs in the nutrition database."""
        return list(self._nutrition_db.keys())

    # ----------------------------------------------------------
    # Private: data loaders
    # ----------------------------------------------------------
    def _load_density_factors(self, path: Path) -> None:
        """Load density factors from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data["items"]:
                factor = DensityFactor(
                    food_id=item["food_id"],
                    name_vi=item["name_vi"],
                    solid_ratio=float(item["solid_ratio"]),
                    density_g_per_ml=float(item["density_g_per_ml"]),
                )
                self._density_factors[item["food_id"]] = factor
            logger.info(f"Loaded {len(self._density_factors)} density factors")
        except Exception as e:
            logger.warning(f"Could not load density factors from {path}: {e}")

    def _load_nutrition_db(self, path: Path) -> None:
        """Load nutrition database from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data["items"]:
                info = NutritionInfo(
                    food_id=item["food_id"],
                    food_name_vi=item["food_name_vi"],
                    food_name_en=item["food_name_en"],
                    gi_index=int(item["gi_index"]),
                    gi_category=item["gi_category"],
                    carb_per_100g=float(item["carb_per_100g"]),
                    is_liquid=bool(item.get("is_liquid", False)),
                )
                self._nutrition_db[item["food_id"]] = info
            logger.info(f"Loaded {len(self._nutrition_db)} nutrition entries")
        except Exception as e:
            logger.warning(f"Could not load nutrition DB from {path}: {e}")

    # ----------------------------------------------------------
    # Private: helpers
    # ----------------------------------------------------------
    def _resolve_food_id(self, food_id: Optional[str]) -> str:
        """
        Resolve food_id to a known nutrition DB entry.

        Accepts:
          - Full IDs like "vn_com_trang"
          - Short IDs like "com_trang" (auto-prepends "vn_")
          - None → defaults to vn_com_trang
          - Unknown → warns and defaults to vn_com_trang
        """
        if food_id is None:
            return _DEFAULT_FOOD_ID
        if food_id in self._nutrition_db:
            return food_id
        # Try with "vn_" prefix
        with_prefix = f"vn_{food_id}" if not food_id.startswith("vn_") else food_id
        if with_prefix in self._nutrition_db:
            return with_prefix
        logger.warning(
            f"Unknown food_id '{food_id}', defaulting to {_DEFAULT_FOOD_ID}"
        )
        return _DEFAULT_FOOD_ID

    def _get_nutrition(self, food_id: str) -> NutritionInfo:
        """Get NutritionInfo, falling back to white rice defaults."""
        info = self._nutrition_db.get(food_id)
        if info is not None:
            return info
        # Fallback (should rarely happen since _resolve_food_id already defaults)
        return NutritionInfo(
            food_id=food_id,
            food_name_vi="Cơm trắng (default)",
            food_name_en="White rice (default)",
            gi_index=73,
            gi_category="high",
            carb_per_100g=28.2,
            is_liquid=False,
        )

    def _get_density(self, food_id: str) -> DensityFactor:
        """Get DensityFactor, falling back to white rice defaults."""
        density_id = _NUTRITION_TO_DENSITY.get(food_id)
        if density_id:
            factor = self._density_factors.get(density_id)
            if factor is not None:
                return factor
        return DensityFactor(
            food_id="com_trang",
            name_vi="Cơm trắng (default)",
            solid_ratio=1.0,
            density_g_per_ml=1.08,
        )

    def _assess_quality(
        self,
        volume_cm3: float,
        food_mask: np.ndarray,
        mean_height: float,
    ) -> Tuple[str, str]:
        """
        Assess volume estimation quality based on three criteria:

        1. Volume plausibility: realistic food volume 10–1500 mL
        2. Food coverage: food_ratio ≥ 5% (enough pixels for stable estimate)
        3. Height presence: mean_height ≥ 0.5 cm (non-flat depth)

        Each criterion contributes 1–3 points → total 3–9 → high/medium/low.
        """
        if volume_cm3 <= 0:
            return "low", "zero or negative volume — check segmentation mask"

        reasons: list = []
        score = 0

        # ── Criterion 1: Volume range ─────────────────────────────────────
        if 10 <= volume_cm3 <= 1500:
            score += 3
        elif 1 <= volume_cm3 <= 3000:
            score += 2
            reasons.append(f"unusual volume ({volume_cm3:.0f}mL)")
        else:
            score += 1
            reasons.append(f"extreme volume ({volume_cm3:.0f}mL)")

        # ── Criterion 2: Food mask coverage ───────────────────────────────
        food_ratio = food_mask.sum() / food_mask.size
        if food_ratio >= 0.05:
            score += 3
        elif food_ratio >= 0.02:
            score += 2
            reasons.append(f"small food area ({food_ratio:.1%})")
        else:
            score += 1
            reasons.append(f"very small food area ({food_ratio:.1%})")

        # ── Criterion 3: Height check ──────────────────────────────────────
        if mean_height >= 0.5:
            score += 3
        elif mean_height >= 0.1:
            score += 2
            reasons.append(f"shallow food height ({mean_height:.2f}cm)")
        else:
            score += 1
            reasons.append("nearly flat food — possible calibration issue")

        quality = "high" if score >= 8 else ("medium" if score >= 5 else "low")
        reason = "; ".join(reasons) if reasons else "good estimation"
        return quality, reason

    def _zero_result(self, food_id: str, elapsed_ms: float) -> VolumeResult:
        """Return a zero-volume result for empty masks."""
        nutrition = self._get_nutrition(food_id)
        density = self._get_density(food_id)
        return VolumeResult(
            volume_cm3=0.0,
            volume_ml=0.0,
            weight_g=0.0,
            carb_g=0.0,
            glycemic_load=0.0,
            glycemic_index=nutrition.gi_index,
            food_id=food_id,
            food_name_vi=nutrition.food_name_vi,
            food_name_en=nutrition.food_name_en,
            is_liquid_dish=nutrition.is_liquid,
            solid_ratio=density.solid_ratio,
            density_g_per_ml=density.density_g_per_ml,
            food_area_cm2=0.0,
            mean_food_height_cm=0.0,
            estimation_quality="low",
            quality_reason="empty food mask",
            estimation_time_ms=elapsed_ms,
        )


# ============================================================
# Singleton
# ============================================================
_volume_estimator: Optional[VolumeEstimator] = None


def get_volume_estimator() -> VolumeEstimator:
    """Get or create singleton VolumeEstimator."""
    global _volume_estimator
    if _volume_estimator is None:
        _volume_estimator = VolumeEstimator()
    return _volume_estimator

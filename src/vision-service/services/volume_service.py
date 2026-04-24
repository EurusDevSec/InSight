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

# ============================================================
# Bowl volume priors for liquid/soup dishes (mL)
# ============================================================
# Depth estimation CANNOT reliably measure bowl interior depth because
# the camera only sees the liquid surface. For soup/liquid dishes we
# use typical Vietnamese serving volumes as priors instead of the
# depth integral.  These values represent a standard single serving.
_BOWL_VOLUME_PRIOR: Dict[str, float] = {
    "vn_pho_bo":      500.0,   # standard phở bowl
    "vn_pho_ga":      500.0,
    "vn_bun_bo_hue":  550.0,   # slightly larger bowl
    "vn_bun_rieu":    500.0,
    "vn_bun_mam":     500.0,
    "vn_hu_tieu":     450.0,
    "vn_banh_canh":   450.0,
    "vn_chao":        350.0,   # smaller porridge bowl
    "vn_tra_sua":     400.0,   # typical cup/glass
}
_DEFAULT_BOWL_VOLUME_ML = 450.0  # fallback for unknown liquid dishes

# Volume correction for solid foods (depth integral).
# DAv2 systematically overestimates due to plate margins, non-linear
# depth gradients, and top-down angle compression.
_SOLID_VOLUME_CORRECTION = 0.35

# Minimum food segmentation ratio — below this, results are unreliable
# and the user should be advised to retake the photo from above.
_MIN_FOOD_SEG_RATIO = 0.05

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
    # New items
    "vn_com_rang":       "com_rang",
    "vn_bun_cha":        "bun_cha",
    "vn_hu_tieu":        "hu_tieu",
    "vn_bun_rieu":       "bun_rieu",
    "vn_banh_cuon":      "banh_cuon",
    "vn_com_ga":         "com_ga",
    "vn_banh_canh":      "banh_canh",
    "vn_bun_mam":        "bun_mam",
    "vn_pho_ga":         "pho_ga",
    "vn_banh_xeo":       "banh_xeo",
    "vn_goi_cuon":       "goi_cuon",
    "vn_mi_quang":       "mi_quang",
    "vn_cao_lau":        "cao_lau",
    "vn_bot_chien":      "bot_chien",
    "vn_com_binh_dan":   "com_binh_dan",
}

_DEFAULT_FOOD_ID = "vn_com_trang"    # Fallback when food_id unknown

# Mapping: Vietnamese display names → nutrition DB food_id
_VN_NAME_TO_FOOD_ID: dict[str, str] = {
    # Exact display names used in Flutter FoodFormScreen
    "Cơm tấm":          "vn_com_tam",
    "Cơm trắng":        "vn_com_trang",
    "Cơm":              "vn_com_trang",
    "Phở":              "vn_pho_bo",
    "Phở bò":           "vn_pho_bo",
    "Phở gà":           "vn_pho_ga",
    "Bún bò":           "vn_bun_bo_hue",
    "Bún thịt nướng":   "vn_bun_thit_nuong",
    "Bún chả":          "vn_bun_cha",
    "Bún riêu":         "vn_bun_rieu",
    "Bún mắm":          "vn_bun_mam",
    "Bún":              "vn_bun_bo_hue",
    "Cháo":             "vn_chao",
    "Bánh mì":          "vn_banh_mi",
    "Bánh cuốn":       "vn_banh_cuon",
    "Bánh xèo":         "vn_banh_xeo",
    "Bánh canh":        "vn_banh_canh",
    "Xôi":              "vn_xoi",
    "Miến":             "vn_com_trang",   # closest fallback
    "Mì xào":           "vn_mi_xao",
    "Mì Quảng":         "vn_mi_quang",
    "Mì":               "vn_mi_xao",
    "Hủ tiếu":         "vn_hu_tieu",
    "Cơm gà":           "vn_com_ga",
    "Cơm chiên":       "vn_com_rang",
    "Cơm rang":         "vn_com_rang",
    "Cơm bình dân":    "vn_com_binh_dan",
    "Gỏi cuốn":        "vn_goi_cuon",
    "Cao lầu":          "vn_cao_lau",
    "Bột chiên":       "vn_bot_chien",
    "Khác":             "vn_com_binh_dan",  # better fallback than plain rice
    # Common short names / variants (lowercase)
    "com tam":          "vn_com_tam",
    "com trang":        "vn_com_trang",
    "com ga":           "vn_com_ga",
    "com rang":         "vn_com_rang",
    "com chien":        "vn_com_rang",
    "com binh dan":     "vn_com_binh_dan",
    "pho":              "vn_pho_bo",
    "pho bo":           "vn_pho_bo",
    "pho ga":           "vn_pho_ga",
    "com":              "vn_com_trang",
    "bun":              "vn_bun_bo_hue",
    "bun cha":          "vn_bun_cha",
    "bun rieu":         "vn_bun_rieu",
    "bun mam":          "vn_bun_mam",
    "banh mi":          "vn_banh_mi",
    "banh cuon":        "vn_banh_cuon",
    "banh xeo":         "vn_banh_xeo",
    "banh canh":        "vn_banh_canh",
    "hu tieu":          "vn_hu_tieu",
    "chao":             "vn_chao",
    "xoi":              "vn_xoi",
    "mi xao":           "vn_mi_xao",
    "mi quang":         "vn_mi_quang",
    "cao lau":          "vn_cao_lau",
    "goi cuon":         "vn_goi_cuon",
    "bot chien":        "vn_bot_chien",
}

# Mapping: reference object class → likely food_id
# Used when user does not specify food_id (auto-detection from bowl type)
_REFERENCE_TO_FOOD_ID: dict[str, str] = {
    "bat_pho_l":  "vn_pho_bo",
    "bat_pho_m":  "vn_pho_bo",
    "bat_com":    "vn_com_trang",
    "dia_com":    "vn_com_tam",
}


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

    # ── Uncertainty range (addresses professor feedback) ──────────────
    # Instead of reporting a single GL number, we provide a plausible
    # range based on accumulated error sources:
    #   - Depth estimation: +/-20% (DAv2 monocular)
    #   - Segmentation: +/-15%
    #   - Density factor: +/-10%
    # Combined (RSS): +/-27%
    carb_range_low: float = 0.0     # Lower bound carb estimate (g)
    carb_range_high: float = 0.0    # Upper bound carb estimate (g)
    gl_range_low: float = 0.0       # Lower bound GL estimate
    gl_range_high: float = 0.0      # Upper bound GL estimate
    confidence_pct: int = 60        # Confidence level for the range (%)

    # Bowl fill (liquid dishes only)
    fill_ratio: float = 1.0         # Bowl fill level 0.15-1.0 (1.0 = full)

    # Debug
    table_level_cm: float = 0.0     # Table surface depth used as baseline


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
        bowl_bbox: Optional[List[float]] = None,
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
            bowl_bbox:    Bowl bounding box [x1, y1, x2, y2] in pixels
                          from reference detection. Used for liquid dishes
                          to estimate bowl fill level.

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

        # ── Step 3: Resolve food data (moved up to enable category logic) ─
        resolved_id = self._resolve_food_id(food_id)
        nutrition = self._get_nutrition(resolved_id)
        density = self._get_density(resolved_id)

        # ── Step 3a: Food segmentation quality check ──────────────────────
        food_seg_ratio = float(mask.sum()) / float(mask.size)
        seg_warning: Optional[str] = None
        if food_seg_ratio < _MIN_FOOD_SEG_RATIO:
            seg_warning = (
                f"food segmentation too sparse ({food_seg_ratio:.1%} < 5%) "
                "— Hãy chụp lại từ trên xuống (top-down) để có kết quả chính xác hơn"
            )
            logger.warning("Low food segmentation: %.1f%% — results may be inaccurate",
                           food_seg_ratio * 100)

        # ── Step 4: Category-specific volume estimation ───────────────────
        pixel_area_cm2 = cm_per_pixel ** 2
        food_area_cm2 = float(mask.sum()) * pixel_area_cm2
        volume_raw = float(np.sum(heights) * pixel_area_cm2)
        mean_height = float(np.mean(heights))

        fill_ratio = 1.0  # Default: assume full serving

        if nutrition.is_liquid:
            # SOUP / LIQUID DISHES: scale bowl volume prior by fill ratio.
            # The prior represents a FULL bowl. We estimate how full the
            # bowl actually is by comparing interior vs rim depth.
            bowl_prior = _BOWL_VOLUME_PRIOR.get(resolved_id, _DEFAULT_BOWL_VOLUME_ML)
            depth_volume = volume_raw * _SOLID_VOLUME_CORRECTION

            fill_ratio = self._estimate_bowl_fill_ratio(
                depth_map_cm, bowl_bbox, table_level,
            )
            volume_cm3 = bowl_prior * fill_ratio

            logger.info(
                "Liquid dish '%s': bowl_prior=%.0f mL × fill_ratio=%.2f "
                "→ volume=%.0f mL (depth integral was %.0f raw, %.0f corrected)",
                resolved_id, bowl_prior, fill_ratio, volume_cm3,
                volume_raw, depth_volume,
            )
        else:
            # SOLID DISHES: apply empirical correction to depth integral.
            volume_cm3 = volume_raw * _SOLID_VOLUME_CORRECTION
            logger.info(
                "Solid dish '%s': volume raw=%.0f cm³, corrected=%.0f cm³ "
                "(factor=%.2f, area=%.0f cm², mean_h=%.2f cm)",
                resolved_id, volume_raw, volume_cm3,
                _SOLID_VOLUME_CORRECTION, food_area_cm2, mean_height,
            )

        # Safety clamp: cap at 800 mL (largest reasonable single serving)
        # A generous plate of com tam ~400 mL, large pho bowl ~600-700 mL.
        _MAX_VOLUME_ML = 800.0
        if volume_cm3 > _MAX_VOLUME_ML:
            logger.warning(
                "Corrected volume %.0f cm³ still exceeds max %.0f — clamping.",
                volume_cm3, _MAX_VOLUME_ML,
            )
            volume_cm3 = _MAX_VOLUME_ML

        # ── Step 5: Weight → Carb → GL ───────────────────────────────────
        volume_ml = volume_cm3                                          # 1 cm³ = 1 mL
        weight_g = volume_ml * density.solid_ratio * density.density_g_per_ml
        carb_g = weight_g * nutrition.carb_per_100g / 100.0
        glycemic_load = carb_g * nutrition.gi_index / 100.0

        # ── Step 5a: Uncertainty estimation ───────────────────────────────
        # Error sources (root-sum-square combination):
        #   - Depth estimation: +/-20% (DAv2 monocular, per Ranftl et al.)
        #   - Food segmentation: +/-15% (mask boundary uncertainty)
        #   - Density/solid_ratio: +/-10% (lookup table vs actual)
        # Combined uncertainty: sqrt(0.20^2 + 0.15^2 + 0.10^2) ~ 0.27 (27%)
        #
        # For liquid dishes (bowl prior), uncertainty is lower:
        #   - Bowl volume prior: +/-15% (VN standard bowl size variation)
        #   - Fill ratio estimation: +/-10%
        #   - Combined: sqrt(0.15^2 + 0.10^2) ~ 0.18 (18%)
        import math
        if nutrition.is_liquid:
            uncertainty_pct = math.sqrt(0.15**2 + 0.10**2)  # ~18%
            confidence_pct = 70  # Higher for liquid (fewer error sources)
        else:
            uncertainty_pct = math.sqrt(0.20**2 + 0.15**2 + 0.10**2)  # ~27%
            confidence_pct = 60

        carb_range_low = max(0.0, carb_g * (1 - uncertainty_pct))
        carb_range_high = carb_g * (1 + uncertainty_pct)
        gl_range_low = max(0.0, glycemic_load * (1 - uncertainty_pct))
        gl_range_high = glycemic_load * (1 + uncertainty_pct)

        # ── Step 6: Quality assessment ────────────────────────────────────
        quality, reason = self._assess_quality(
            volume_cm3=volume_cm3,
            food_mask=mask,
            mean_height=mean_height,
        )
        # Override quality to "low" if food segmentation was too sparse
        if seg_warning:
            quality = "low"
            reason = seg_warning

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
            carb_range_low=round(carb_range_low, 1),
            carb_range_high=round(carb_range_high, 1),
            gl_range_low=round(gl_range_low, 1),
            gl_range_high=round(gl_range_high, 1),
            confidence_pct=confidence_pct,
            fill_ratio=fill_ratio,
            table_level_cm=table_level,
            estimation_time_ms=elapsed_ms,
        )

        logger.info(
            f"Volume: {volume_cm3:.1f}cm3 -> {weight_g:.1f}g -> "
            f"carb={carb_g:.1f}g ({carb_range_low:.0f}-{carb_range_high:.0f}), "
            f"GL={glycemic_load:.1f} ({gl_range_low:.0f}-{gl_range_high:.0f}) "
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
          - Vietnamese display names like "Phở", "Cơm", "Bánh mì"
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
        # Try Vietnamese display name mapping (case-insensitive)
        vn_lookup = _VN_NAME_TO_FOOD_ID.get(food_id) or _VN_NAME_TO_FOOD_ID.get(food_id.lower())
        if vn_lookup and vn_lookup in self._nutrition_db:
            return vn_lookup
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

    def _estimate_bowl_fill_ratio(
        self,
        depth_map_cm: np.ndarray,
        bowl_bbox: Optional[List[float]],
        table_level: float,
    ) -> float:
        """
        Estimate how full a bowl is using rim-vs-interior depth contrast.

        Compares the average depth of the bowl interior (liquid surface)
        against the bowl rim depth. A full bowl has liquid near the rim;
        a half-empty bowl has liquid surface much lower.

        Returns fill_ratio in [0.15, 1.0].  Falls back to 1.0 when
        bowl_bbox is unavailable or rim depth is too low (YOLO box
        extends to table surface).
        """
        if bowl_bbox is None:
            return 1.0

        h, w = depth_map_cm.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in bowl_bbox]

        # Bowl center and half-widths
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        hw = (x2 - x1) / 2.0  # half-width in pixels
        hh = (y2 - y1) / 2.0  # half-height in pixels

        if hw < 5 or hh < 5:
            return 1.0  # bbox too small to be meaningful

        # Build elliptical distance map (normalized: 1.0 = on bbox edge)
        yy, xx = np.ogrid[:h, :w]
        dist_sq = ((xx - cx) / hw) ** 2 + ((yy - cy) / hh) ** 2

        # Interior ellipse: center 65% — where liquid surface is visible
        interior_mask = dist_sq <= 0.65 ** 2
        # Rim ring: 85-100% of half-widths — the bowl rim band
        rim_mask = (dist_sq > 0.85 ** 2) & (dist_sq <= 1.0 ** 2)

        interior_depths = depth_map_cm[interior_mask]
        rim_depths = depth_map_cm[rim_mask]

        if len(interior_depths) < 10 or len(rim_depths) < 10:
            return 1.0  # Not enough pixels for reliable estimation

        # Heights above table
        interior_height = float(np.mean(interior_depths)) - table_level
        rim_height = float(np.percentile(rim_depths, 80)) - table_level

        # Edge case: rim barely above table (YOLO box too wide)
        if rim_height <= 0.1:
            logger.debug(
                "Bowl rim height %.3f cm ≤ 0.1 — bbox may extend to table, "
                "defaulting fill_ratio=1.0",
                rim_height,
            )
            return 1.0

        ratio = interior_height / rim_height
        fill_ratio = float(np.clip(ratio, 0.15, 1.0))

        logger.info(
            "Bowl fill estimation: interior_h=%.2f cm, rim_h=%.2f cm, "
            "raw_ratio=%.3f, clamped=%.2f",
            interior_height, rim_height, ratio, fill_ratio,
        )

        return fill_ratio

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

"""
Pydantic schemas for Volume Estimation endpoint (Task 2.5).
"""
from pydantic import BaseModel, Field


class VolumeEstimationResponse(BaseModel):
    """Response for POST /api/vision/estimate-volume."""

    # ── Volume ────────────────────────────────────────────────────────────
    volume_cm3: float = Field(
        ..., description="Food volume in cm³ (equivalent to mL)"
    )
    volume_ml: float = Field(
        ..., description="Food volume in milliliters (same as volume_cm3)"
    )

    # ── Weight ────────────────────────────────────────────────────────────
    weight_g: float = Field(
        ...,
        description=(
            "Estimated food weight in grams. "
            "Formula: volume_ml × solid_ratio × density_g_per_ml"
        ),
    )

    # ── Nutrition ─────────────────────────────────────────────────────────
    carb_g: float = Field(
        ..., description="Estimated carbohydrates in grams"
    )
    glycemic_load: float = Field(
        ...,
        description=(
            "Glycemic Load = (glycemic_index × carb_g) / 100. "
            "GL < 10: low, 10–20: medium, > 20: high"
        ),
    )
    glycemic_index: int = Field(
        ..., description="Glycemic Index of the food used in GL calculation"
    )

    # ── Food metadata ─────────────────────────────────────────────────────
    food_id: str = Field(
        ..., description="Food ID resolved from request (e.g. 'vn_com_trang')"
    )
    food_name_vi: str = Field(..., description="Vietnamese food name")
    food_name_en: str = Field(..., description="English food name")
    is_liquid_dish: bool = Field(
        ...,
        description="True if the dish contains significant liquid (soup, porridge)",
    )

    # ── Density details ───────────────────────────────────────────────────
    solid_ratio: float = Field(
        ...,
        description=(
            "Fraction of total volume that is solid food (0–1). "
            "E.g. pho: 0.30 (30% noodles+meat, 70% broth)"
        ),
    )
    density_g_per_ml: float = Field(
        ..., description="Density of the solid food fraction (g/mL)"
    )

    # ── Geometry ──────────────────────────────────────────────────────────
    food_area_cm2: float = Field(
        ..., description="Footprint area of detected food region in cm²"
    )
    mean_food_height_cm: float = Field(
        ...,
        description=(
            "Average height of food above table surface in cm, "
            "derived from calibrated depth map"
        ),
    )

    # ── Quality ───────────────────────────────────────────────────────────
    estimation_quality: str = Field(
        ..., description="Volume estimation quality: 'high' / 'medium' / 'low'"
    )
    quality_reason: str = Field(
        ..., description="Human-readable explanation of the quality rating"
    )

    # ── Uncertainty range ─────────────────────────────────────────────────
    carb_range_low: float = Field(
        default=0.0,
        description="Lower bound carb estimate (g), based on RSS error propagation",
    )
    carb_range_high: float = Field(
        default=0.0,
        description="Upper bound carb estimate (g), based on RSS error propagation",
    )
    gl_range_low: float = Field(
        default=0.0,
        description=(
            "Lower bound GL estimate. "
            "Use this + gl_range_high to display a range, e.g. 'GL ~ 10-18'"
        ),
    )
    gl_range_high: float = Field(
        default=0.0,
        description=(
            "Upper bound GL estimate. "
            "Combined uncertainty from depth (+/-20%), segmentation (+/-15%), density (+/-10%)"
        ),
    )
    confidence_pct: int = Field(
        default=60,
        description=(
            "Confidence level for the GL/carb range (%). "
            "60% for solid dishes (3 error sources), 70% for liquid (2 error sources)"
        ),
    )

    # ── Timing ────────────────────────────────────────────────────────────
    volume_time_ms: float = Field(
        ..., description="Time for volume+GL computation only (ms)"
    )
    total_pipeline_time_ms: float = Field(
        ...,
        description=(
            "Total pipeline time including depth estimation, "
            "reference detection, calibration, segmentation, and volume (ms)"
        ),
    )

    # ── Debug / Developer Mode ────────────────────────────────────────────
    debug_depth_preview: str | None = Field(
        default=None,
        description="Base64-encoded depth map thumbnail (256px wide, PNG)",
    )
    debug_food_mask_preview: str | None = Field(
        default=None,
        description="Base64-encoded food mask thumbnail (256px wide, PNG)",
    )
    debug_reference_objects: list[dict] | None = Field(
        default=None,
        description="Detected reference objects [{class, confidence, bbox}]",
    )
    debug_scale_px_per_cm: float | None = Field(
        default=None,
        description="Calibrated scale factor (pixels per cm)",
    )
    debug_table_level_cm: float | None = Field(
        default=None,
        description="Estimated table surface depth (cm) used as baseline",
    )
    debug_formula: str | None = Field(
        default=None,
        description="Human-readable formula breakdown for volume computation",
    )

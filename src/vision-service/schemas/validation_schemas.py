"""
Pydantic response schemas for validation endpoints.
Task 2.6 — Validation & Benchmark
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SingleValidationResponse(BaseModel):
    """
    Response for POST /api/vision/validate — single image compare vs GT.

    The caller provides ground-truth values; the endpoint runs the full
    pipeline and returns APE for weight and carb.
    """

    # Sample identity
    sample_id: Optional[str] = Field(
        None,
        description="Optional label for this comparison (e.g. 'pho_bo_001')",
    )
    food_id: Optional[str] = Field(
        None, description="Food ID used for density lookup"
    )

    # Ground truth (provided by caller)
    gt_weight_g: float = Field(..., description="Ground truth weight [g]")
    gt_carb_g: float = Field(..., description="Ground truth carbohydrate [g]")

    # Predictions (pipeline output)
    pred_weight_g: float = Field(..., description="Predicted weight [g]")
    pred_carb_g: float = Field(..., description="Predicted carbohydrate [g]")
    pred_volume_ml: float = Field(..., description="Predicted volume [mL]")
    pred_glycemic_load: float = Field(..., description="Predicted Glycemic Load")
    pred_quality: str = Field(..., description="Estimation quality tier")

    # Accuracy
    weight_ape_pct: float = Field(
        ..., description="Weight Absolute Percentage Error [%]"
    )
    carb_ape_pct: float = Field(
        ..., description="Carb Absolute Percentage Error [%]"
    )
    passes_15pct_threshold: bool = Field(
        ..., description="True if weight_ape ≤ 15%"
    )

    # Pipeline timing
    pipeline_time_ms: float = Field(
        ..., description="Total pipeline time [ms]"
    )


class CategoryStatsResponse(BaseModel):
    """Aggregated accuracy stats per food category or dataset source."""

    category_name: str
    n_samples: int
    mape_weight_pct: float
    mape_carb_pct: float
    max_weight_ape_pct: float
    pass_rate_15pct: float = Field(
        ..., description="% samples with weight_ape ≤ 15"
    )


class ValidationReportResponse(BaseModel):
    """
    Response for POST /api/vision/validate-batch — full validation report.

    Also the schema used when loading a saved JSON report.
    """

    run_date: str
    n_total: int
    n_n5k: int
    n_vn_demo: int

    # Overall metrics
    mape_weight_pct: float = Field(
        ..., description="Mean Absolute Percentage Error for weight [%]"
    )
    mape_carb_pct: float = Field(
        ..., description="Mean Absolute Percentage Error for carbohydrate [%]"
    )
    pass_rate_15pct: float = Field(
        ..., description="% of samples with weight APE ≤ 15%"
    )
    passes_threshold: bool = Field(
        ..., description="True if overall MAPE_weight ≤ 15%"
    )

    # Breakdown
    by_category: List[CategoryStatsResponse] = Field(
        default_factory=list,
        description="Per-category breakdown",
    )

    # Per-sample detail
    per_sample: List[SingleValidationResponse] = Field(
        default_factory=list,
        description="Per-sample comparison results",
    )

    notes: str = ""

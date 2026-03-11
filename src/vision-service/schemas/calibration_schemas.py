"""Pydantic schemas for calibration API (Task 2.3)."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CalibrationResponse(BaseModel):
    """Response from pixel-to-real calibration endpoint."""

    pixels_per_cm: float = Field(
        ..., description="Scale factor: pixels per centimeter"
    )
    cm_per_pixel: float = Field(
        ..., description="Inverse scale factor: cm per pixel"
    )
    image_width_cm: float = Field(
        ..., description="Image width in real-world cm"
    )
    image_height_cm: float = Field(
        ..., description="Image height in real-world cm"
    )
    reference_class: str = Field(
        ..., description="Reference object used for calibration"
    )
    reference_confidence: float = Field(
        ..., description="Detection confidence of reference"
    )
    calibration_quality: str = Field(
        ..., description="Quality rating: high, medium, low"
    )
    quality_reason: str = Field(
        ..., description="Explanation for quality rating"
    )
    depth_stats: dict = Field(
        ..., description="Depth map statistics"
    )
    calibration_time_ms: float = Field(
        ..., description="Calibration time in ms"
    )


class MeasurementRequest(BaseModel):
    """Request to measure distance/size in calibrated image."""

    point1: List[int] = Field(
        ..., description="[x, y] start point in pixels"
    )
    point2: List[int] = Field(
        ..., description="[x, y] end point in pixels"
    )


class MeasurementResponse(BaseModel):
    """Response with real-world measurement."""

    pixel_distance: float = Field(
        ..., description="Distance in pixels"
    )
    real_distance_cm: float = Field(
        ..., description="Estimated real distance in cm"
    )
    pixels_per_cm: float = Field(
        ..., description="Scale factor used"
    )

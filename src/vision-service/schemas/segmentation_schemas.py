"""Pydantic schemas for food segmentation API (Task 2.4)."""

from typing import List

from pydantic import BaseModel, Field


class SegmentationResponse(BaseModel):
    """Response from food segmentation endpoint."""

    food_mask_base64: str = Field(
        ..., description="Base64 encoded food mask PNG (white=food, black=bg)"
    )
    food_area_pixels: int = Field(
        ..., description="Number of pixels classified as food"
    )
    food_ratio: float = Field(
        ..., description="Ratio of food area to total image area"
    )
    num_components: int = Field(
        ..., description="Number of separate food regions"
    )
    food_bbox: List[int] = Field(
        ..., description="Bounding box [x1, y1, x2, y2] of food region"
    )
    segmentation_quality: str = Field(
        ..., description="Quality: high, medium, low"
    )
    method_used: str = Field(
        ..., description="Method: depth_color, fastsam"
    )
    segmentation_time_ms: float = Field(
        ..., description="Segmentation time in ms"
    )

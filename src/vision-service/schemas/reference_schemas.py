"""Pydantic schemas for Reference Object Detection API responses."""

from typing import List, Optional

from pydantic import BaseModel, Field


class DetectedObject(BaseModel):
    """Information about one detected reference object."""

    class_name: str = Field(
        ...,
        description="Object type: bat_com, bat_pho_m, bat_pho_l, dia_com, thia, dua",
    )
    confidence: float = Field(
        ..., description="Detection confidence (0-1)"
    )
    bbox: List[float] = Field(
        ..., description="Bounding box [x1, y1, x2, y2] in pixels"
    )
    real_width_cm: float = Field(
        ..., description="Known real-world width/diameter in cm"
    )
    real_height_cm: float = Field(
        ..., description="Known real-world height/length in cm"
    )
    pixels_per_cm: float = Field(
        ..., description="Scale factor: pixels per centimeter"
    )


class ReferenceDetectionResponse(BaseModel):
    """Response from reference detection endpoint."""

    objects: List[DetectedObject] = Field(default_factory=list)
    best_scale_factor: Optional[float] = Field(
        None, description="Best pixels_per_cm from highest-priority detected object"
    )
    total_detected: int = Field(
        0, description="Total number of reference objects detected"
    )
    model_type: str = Field(
        "unknown",
        description="Model type used: 'custom' or 'pretrained_coco'",
    )

"""Pydantic schemas for Depth Estimation API responses."""

from typing import List

from pydantic import BaseModel, Field


class DepthStats(BaseModel):
    """Statistics of the depth map."""

    min: float = Field(..., description="Minimum depth value")
    max: float = Field(..., description="Maximum depth value")
    mean: float = Field(..., description="Mean depth value")
    std: float = Field(..., description="Standard deviation of depth values")


class DepthEstimationResponse(BaseModel):
    """Response from depth estimation endpoint."""

    depth_map_base64: str = Field(
        ..., description="Base64 encoded depth map PNG"
    )
    inference_time_ms: float = Field(
        ..., description="Inference time in milliseconds"
    )
    image_size: List[int] = Field(
        ..., description="[width, height] of input image"
    )
    depth_stats: DepthStats = Field(..., description="Depth map statistics")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    model_loaded: bool
    device: str

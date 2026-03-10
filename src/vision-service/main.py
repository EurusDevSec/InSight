"""
InSight Vision Service — FastAPI application.

Provides endpoints for:
  - Depth estimation (Task 2.1)
  - Reference object detection (Task 2.2)
  - Volume estimation (placeholder for Task 2.5)

Run: python main.py
Swagger: http://localhost:8000/docs
"""

import io
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image

from schemas.depth_schemas import DepthEstimationResponse, HealthResponse
from schemas.reference_schemas import (
    DetectedObject,
    ReferenceDetectionResponse,
)
from services.depth_service import estimate_depth, get_model
from services.reference_service import ReferenceDetector

# ============================================================
# Logging configuration
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================
# Reference detector (global instance)
# ============================================================
# Plan A: custom model path (set when model is trained)
# Plan B: None -> falls back to pretrained COCO
CUSTOM_MODEL_PATH = "runs/reference_detector/v1/weights/best.pt"

ref_detector = ReferenceDetector(
    model_path=CUSTOM_MODEL_PATH,
    confidence=0.4,
)


# ============================================================
# Application lifespan (startup / shutdown)
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup, cleanup on shutdown."""
    logger.info("Starting InSight Vision Service...")

    # Pre-load depth model (warm up)
    depth_model = get_model()
    logger.info(f"Depth model ready on {depth_model.device.upper()}")

    # Pre-load reference detector
    ref_detector.load()
    logger.info(
        f"Reference detector ready "
        f"(custom={ref_detector.is_custom_model})"
    )

    yield  # App is running

    logger.info("Shutting down InSight Vision Service...")


# ============================================================
# FastAPI app
# ============================================================
app = FastAPI(
    title="InSight Vision Service",
    version="0.2.0",
    description=(
        "Computer Vision service for food depth estimation, "
        "reference object detection, and volume calculation."
    ),
    lifespan=lifespan,
)


# ============================================================
# Endpoints
# ============================================================
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    depth_model = get_model()
    return HealthResponse(
        status="UP",
        service="insight-vision-service",
        model_loaded=depth_model.is_loaded,
        device=depth_model.device,
    )


@app.post(
    "/api/vision/depth",
    response_model=DepthEstimationResponse,
    summary="Generate depth map from food image",
)
async def depth_estimation(image: UploadFile = File(...)):
    """
    Generate depth map from food image using Depth Anything V2.

    - **Input**: Image file (JPEG/PNG)
    - **Output**: Base64 encoded depth map + statistics
    - **Target**: <= 500ms inference time on GPU
    """
    _validate_image_upload(image)

    try:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        result = estimate_depth(image_bytes)
        return DepthEstimationResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Depth estimation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Depth estimation failed: {str(e)}",
        )


@app.post(
    "/api/vision/detect-reference",
    response_model=ReferenceDetectionResponse,
    summary="Detect reference objects (bowls, spoons, chopsticks)",
)
async def detect_reference(image: UploadFile = File(...)):
    """
    Detect reference objects (bowls, spoons, chopsticks) in food image.

    Returns bounding boxes + real-world dimensions for pixel-to-real
    calibration (used by Task 2.3).

    - **Input**: Image file (JPEG/PNG)
    - **Output**: List of detected objects + best scale factor
    """
    _validate_image_upload(image)

    try:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        detections = ref_detector.detect(pil_image)
        scale_factor = ref_detector.get_best_scale_factor(detections)

        return ReferenceDetectionResponse(
            objects=[
                DetectedObject(
                    class_name=d.class_name,
                    confidence=d.confidence,
                    bbox=d.bbox,
                    real_width_cm=d.real_width_cm,
                    real_height_cm=d.real_height_cm,
                    pixels_per_cm=d.pixels_per_cm,
                )
                for d in detections
            ],
            best_scale_factor=scale_factor,
            total_detected=len(detections),
            model_type=(
                "custom" if ref_detector.is_custom_model else "pretrained_coco"
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reference detection failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Reference detection failed: {str(e)}",
        )


@app.post("/api/vision/estimate-volume")
async def estimate_volume(image: UploadFile = File(...)):
    """
    Estimate food volume from image.

    **Not implemented** — placeholder for Task 2.5.
    Will combine depth map + reference calibration + food segmentation.
    """
    return {
        "volume_ml": 0.0,
        "message": "Not implemented — see Task 2.5",
    }


# ============================================================
# Helpers
# ============================================================
def _validate_image_upload(image: UploadFile) -> None:
    """Validate uploaded file is an image."""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {image.content_type}. Expected image/*",
        )


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

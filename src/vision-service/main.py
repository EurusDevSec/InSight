"""
InSight Vision Service — FastAPI application.

Provides endpoints for:
  - Depth estimation (Task 2.1)
  - Reference object detection (Task 2.2)
  - Pixel-to-Real calibration (Task 2.3)
  - Food segmentation (Task 2.4)
  - Volume + GL estimation (Task 2.5)
  - Validation against ground truth (Task 2.6)

Run: python main.py
Swagger: http://localhost:8000/docs
"""

import base64
import io
import logging
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image, ImageOps

from schemas.calibration_schemas import CalibrationResponse
from schemas.depth_schemas import DepthEstimationResponse, HealthResponse
from schemas.reference_schemas import (
    DetectedObject,
    ReferenceDetectionResponse,
)
from schemas.segmentation_schemas import SegmentationResponse
from schemas.validation_schemas import SingleValidationResponse
from schemas.volume_schemas import VolumeEstimationResponse
from services.calibration_service import get_calibration_service
from services.depth_service import estimate_depth, estimate_depth_full, get_model
from services.reference_service import ReferenceDetector
from services.segmentation_service import get_food_segmenter
from services.validation_service import MetricComputer
from services.volume_service import get_volume_estimator

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

    # Initialize calibration service (no model to load)
    cal_svc = get_calibration_service()
    logger.info("Calibration service ready")

    # Initialize food segmenter
    segmenter = get_food_segmenter()
    logger.info("Food segmenter ready")

    # Initialize volume estimator (loads JSON data files)
    vol_estimator = get_volume_estimator()
    logger.info(
        f"Volume estimator ready "
        f"({len(vol_estimator.get_available_foods())} foods loaded)"
    )

    yield  # App is running

    logger.info("Shutting down InSight Vision Service...")


# ============================================================
# FastAPI app
# ============================================================
app = FastAPI(
    title="InSight Vision Service",
    version="0.6.0",
    description=(
        "Computer Vision service for food depth estimation, "
        "reference object detection, pixel-to-real calibration, "
        "food segmentation, volume + Glycemic Load calculation, "
        "and pipeline accuracy validation."
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
    Detect reference objects in food image for size calibration.

    - **Input**: Image file (JPEG/PNG)
    - **Output**: List of detected objects + best scale factor
    """
    _validate_image_upload(image)

    try:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        pil_image = _open_image(image_bytes)

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


@app.post(
    "/api/vision/calibrate",
    response_model=CalibrationResponse,
    summary="Calibrate pixel-to-real mapping (Task 2.3)",
)
async def calibrate(image: UploadFile = File(...)):
    """
    Calibrate pixel-to-real mapping using depth map + reference object.

    Combines Task 2.1 (depth) + Task 2.2 (reference) to produce
    calibrated measurements in centimeters.

    - **Input**: Image file (JPEG/PNG)
    - **Output**: Scale factors + calibration quality
    """
    _validate_image_upload(image)

    try:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        pil_image = _open_image(image_bytes)

        # Step 1: Get depth map
        depth_result = estimate_depth_full(pil_image)
        depth_map = depth_result["depth_map"]

        # Step 2: Detect reference objects
        detections = ref_detector.detect(pil_image)
        scale_factor = ref_detector.get_best_scale_factor(detections)

        if scale_factor is None:
            raise HTTPException(
                status_code=422,
                detail="No reference object detected. "
                "Ensure a bowl or spoon is visible in the image.",
            )

        # Step 3: Calibrate
        best_ref = max(detections, key=lambda d: d.confidence)
        cal_svc = get_calibration_service()
        cal_result = cal_svc.calibrate(
            depth_map=depth_map,
            pixels_per_cm=scale_factor,
            reference_class=best_ref.class_name,
            reference_confidence=best_ref.confidence,
            image_size=pil_image.size,
        )

        return CalibrationResponse(
            pixels_per_cm=cal_result.pixels_per_cm,
            cm_per_pixel=cal_result.cm_per_pixel,
            image_width_cm=cal_result.image_width_cm,
            image_height_cm=cal_result.image_height_cm,
            reference_class=cal_result.reference_class,
            reference_confidence=cal_result.reference_confidence,
            calibration_quality=cal_result.calibration_quality,
            quality_reason=cal_result.quality_reason,
            depth_stats=depth_result["stats"],
            calibration_time_ms=cal_result.calibration_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calibration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Calibration failed: {str(e)}",
        )


@app.post(
    "/api/vision/segment-food",
    response_model=SegmentationResponse,
    summary="Segment food region from image (Task 2.4)",
)
async def segment_food(image: UploadFile = File(...)):
    """
    Segment food region from image using depth + color analysis.

    Combines depth map (elevated regions) with color analysis
    to identify food pixels. Optionally uses bowl detection
    to focus segmentation.

    - **Input**: Image file (JPEG/PNG)
    - **Output**: Base64 food mask + statistics
    """
    _validate_image_upload(image)

    try:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        pil_image = _open_image(image_bytes)

        # Step 1: Get depth map
        depth_result = estimate_depth_full(pil_image)
        depth_map = depth_result["depth_map"]

        # Step 2: Detect bowl for ROI (optional, improves segmentation)
        detections = ref_detector.detect(pil_image)
        bowl_bbox = None
        for det in detections:
            if det.class_name.startswith("bat_") or det.class_name == "dia_com":
                bowl_bbox = det.bbox
                break

        # Step 3: Segment food
        segmenter = get_food_segmenter()
        seg_result = segmenter.segment(
            image=pil_image,
            depth_map=depth_map,
            bowl_bbox=bowl_bbox,
        )

        # Encode mask to base64 PNG
        mask_img = Image.fromarray(
            seg_result.refined_mask.astype(np.uint8) * 255
        )
        buffer = io.BytesIO()
        mask_img.save(buffer, format="PNG")
        mask_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return SegmentationResponse(
            food_mask_base64=mask_base64,
            food_area_pixels=seg_result.food_area_pixels,
            food_ratio=seg_result.food_ratio,
            num_components=seg_result.num_components,
            food_bbox=seg_result.food_bbox,
            segmentation_quality=seg_result.segmentation_quality,
            method_used=seg_result.method_used,
            segmentation_time_ms=seg_result.segmentation_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Segmentation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Food segmentation failed: {str(e)}",
        )


@app.post(
    "/api/vision/estimate-volume",
    response_model=VolumeEstimationResponse,
    summary="Estimate food volume + Glycemic Load (Task 2.5)",
)
async def estimate_volume(
    image: UploadFile = File(...),
    food_id: Optional[str] = Form(
        None,
        description=(
            "Nutrition DB food ID (e.g. 'vn_com_trang', 'vn_pho_bo'). "
            "Defaults to 'vn_com_trang' if omitted or unrecognised."
        ),
    ),
):
    """
    Full pipeline: image → depth → calibrate → segment → volume → GL.

    Combines all previous tasks:
    - Task 2.1: Depth estimation (Depth Anything V2)
    - Task 2.2: Reference object detection (scale factor)
    - Task 2.3: Pixel-to-real calibration
    - Task 2.4: Food segmentation (depth + color hybrid)
    - Task 2.5: Volume integral + Glycemic Load computation

    - **Input**: Image file (JPEG/PNG) + optional food_id form field
    - **Output**: Volume (mL), weight (g), carbohydrates (g), GL
    """
    _validate_image_upload(image)

    try:
        t_total_start = __import__("time").time()

        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        pil_image = _open_image(image_bytes)

        # ── Step 1: Depth map ─────────────────────────────────────────────
        depth_result = estimate_depth_full(pil_image)
        depth_map = depth_result["depth_map"]

        # ── Step 2: Reference detection → scale factor ────────────────────
        detections = ref_detector.detect(pil_image)
        scale_factor = ref_detector.get_best_scale_factor(detections)

        if scale_factor is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No reference object detected. "
                    "Ensure a bowl or spoon is visible in the image."
                ),
            )

        # ── Step 3: Calibration ───────────────────────────────────────────
        best_ref = max(detections, key=lambda d: d.confidence)
        cal_svc = get_calibration_service()
        cal_result = cal_svc.calibrate(
            depth_map=depth_map,
            pixels_per_cm=scale_factor,
            reference_class=best_ref.class_name,
            reference_confidence=best_ref.confidence,
            image_size=pil_image.size,
        )

        # ── Step 4: Food segmentation ─────────────────────────────────────
        bowl_bbox = None
        for det in detections:
            if det.class_name.startswith("bat_") or det.class_name == "dia_com":
                bowl_bbox = det.bbox
                break

        segmenter = get_food_segmenter()
        seg_result = segmenter.segment(
            image=pil_image,
            depth_map=depth_map,
            bowl_bbox=bowl_bbox,
        )

        # ── Step 5: Volume estimation + GL ────────────────────────────────
        # Auto-infer food_id from reference object if user didn't specify
        effective_food_id = food_id
        if not effective_food_id:
            from services.volume_service import _REFERENCE_TO_FOOD_ID
            for det in detections:
                inferred = _REFERENCE_TO_FOOD_ID.get(det.class_name)
                if inferred:
                    effective_food_id = inferred
                    logger.info("Auto-inferred food_id='%s' from reference '%s'", inferred, det.class_name)
                    break

        vol_estimator = get_volume_estimator()
        vol_result = vol_estimator.estimate(
            depth_map_cm=cal_result.depth_map_cm,
            food_mask=seg_result.refined_mask,
            cm_per_pixel=cal_result.cm_per_pixel,
            food_id=effective_food_id,
        )

        total_ms = (__import__("time").time() - t_total_start) * 1000

        return VolumeEstimationResponse(
            volume_cm3=vol_result.volume_cm3,
            volume_ml=vol_result.volume_ml,
            weight_g=vol_result.weight_g,
            carb_g=vol_result.carb_g,
            glycemic_load=vol_result.glycemic_load,
            glycemic_index=vol_result.glycemic_index,
            food_id=vol_result.food_id,
            food_name_vi=vol_result.food_name_vi,
            food_name_en=vol_result.food_name_en,
            is_liquid_dish=vol_result.is_liquid_dish,
            solid_ratio=vol_result.solid_ratio,
            density_g_per_ml=vol_result.density_g_per_ml,
            food_area_cm2=vol_result.food_area_cm2,
            mean_food_height_cm=vol_result.mean_food_height_cm,
            estimation_quality=vol_result.estimation_quality,
            quality_reason=vol_result.quality_reason,
            volume_time_ms=vol_result.estimation_time_ms,
            total_pipeline_time_ms=total_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Volume estimation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Volume estimation failed: {str(e)}",
        )


@app.post(
    "/api/vision/validate",
    response_model=SingleValidationResponse,
    summary="Run pipeline and compare result against ground-truth (Task 2.6)",
)
async def validate_single(
    image: UploadFile = File(...),
    food_id: Optional[str] = Form(
        None,
        description="Food ID for density lookup (e.g. 'vn_pho_bo')",
    ),
    gt_weight_g: float = Form(
        ...,
        description="Ground-truth total weight [g]",
    ),
    gt_carb_g: float = Form(
        ...,
        description="Ground-truth total carbohydrate [g]",
    ),
    sample_id: Optional[str] = Form(
        None,
        description="Optional label for this sample (e.g. 'pho_bo_001')",
    ),
):
    """
    Run the full pipeline on an image and compare against provided GT.

    This endpoint is used by ``scripts/validate_pipeline.py`` to
    benchmark Vision Engine accuracy against reference datasets.

    Runs the same pipeline as ``/api/vision/estimate-volume``, then
    computes Absolute Percentage Error (APE) against the provided
    ground-truth weight and carbohydrate values.

    **Accuracy target**: MAPE ≤ 15% for both weight and carb.

    - **Input**: Image + food_id (optional) + gt_weight_g + gt_carb_g
    - **Output**: Predicted values + APE per metric + pass/fail flag
    """
    _validate_image_upload(image)

    try:
        t_start = __import__("time").time()

        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        pil_image = _open_image(image_bytes)

        # ── Full pipeline (same as /estimate-volume) ───────────────────────
        depth_result = estimate_depth_full(pil_image)
        depth_map = depth_result["depth_map"]

        detections = ref_detector.detect(pil_image)
        scale_factor = ref_detector.get_best_scale_factor(detections)

        if scale_factor is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No reference object detected. "
                    "Ensure a bowl or spoon is visible in the image."
                ),
            )

        best_ref = max(detections, key=lambda d: d.confidence)
        cal_svc = get_calibration_service()
        cal_result = cal_svc.calibrate(
            depth_map=depth_map,
            pixels_per_cm=scale_factor,
            reference_class=best_ref.class_name,
            reference_confidence=best_ref.confidence,
            image_size=pil_image.size,
        )

        bowl_bbox = None
        for det in detections:
            if det.class_name.startswith("bat_") or det.class_name == "dia_com":
                bowl_bbox = det.bbox
                break

        segmenter = get_food_segmenter()
        seg_result = segmenter.segment(
            image=pil_image,
            depth_map=depth_map,
            bowl_bbox=bowl_bbox,
        )

        vol_estimator = get_volume_estimator()
        vol_result = vol_estimator.estimate(
            depth_map_cm=cal_result.depth_map_cm,
            food_mask=seg_result.refined_mask,
            cm_per_pixel=cal_result.cm_per_pixel,
            food_id=food_id,
        )

        pipeline_ms = (__import__("time").time() - t_start) * 1000

        # ── Compare against ground truth ───────────────────────────────────
        weight_ape = MetricComputer.ape(vol_result.weight_g, gt_weight_g)
        carb_ape = MetricComputer.ape(vol_result.carb_g, gt_carb_g)

        return SingleValidationResponse(
            sample_id=sample_id,
            food_id=vol_result.food_id,
            gt_weight_g=gt_weight_g,
            gt_carb_g=gt_carb_g,
            pred_weight_g=round(vol_result.weight_g, 1),
            pred_carb_g=round(vol_result.carb_g, 1),
            pred_volume_ml=round(vol_result.volume_ml, 1),
            pred_glycemic_load=round(vol_result.glycemic_load, 1),
            pred_quality=vol_result.estimation_quality,
            weight_ape_pct=round(weight_ape, 1),
            carb_ape_pct=round(carb_ape, 1),
            passes_15pct_threshold=weight_ape <= 15.0,
            pipeline_time_ms=round(pipeline_ms, 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}",
        )


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


def _open_image(raw_bytes: bytes) -> Image.Image:
    """
    Open image bytes as RGB PIL Image with EXIF orientation applied.

    WHY apply EXIF transpose here?
    ────────────────────────────────
    Phone photos are often stored in portrait orientation with an EXIF
    rotation flag (e.g. rotation=90°). The HuggingFace depth pipeline
    internally auto-applies this EXIF correction, but PIL's
    Image.open() alone does NOT. Without this correction, the depth
    model outputs a landscape array while numpy indexing of the PIL
    image still sees portrait dimensions — causing shape mismatches
    in the segmentation and volume services (bug observed on
    com_trang_001 landscape photo).

    Applying exif_transpose() normalises the pixel matrix so every
    downstream service sees the same (H, W) layout.
    """
    pil_image = Image.open(io.BytesIO(raw_bytes))
    pil_image = ImageOps.exif_transpose(pil_image)
    return pil_image.convert("RGB")


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

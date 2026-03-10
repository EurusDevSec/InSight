# 📖 HƯỚNG DẪN CHI TIẾT TASK 2.1: TRIỂN KHAI DEPTH ESTIMATION

> **Assignee**: Việt (chính), Hoàng (review)
> **Thời gian**: 13/03 → 14/03/2026
> **Tiền đề**: Task 1.1 (Vision Service skeleton ✅ — `src/vision-service/main.py` FastAPI), Task 1.3 (Dataset ✅ — Nutrition5k parsed + VN demo JSON)
> **Tham chiếu**: [TASK_2.1](../Tasks/TASK_2.1_DEPTH_ESTIMATION.md) | [plan.md](../plan.md)
> **Cập nhật**: 10/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 1.1  Environment ✅ | Task 1.3 Data Collection 🔄            │
│  (FastAPI skeleton ready)   (Nutrition5k parsed, VN JSON ready)    │
│                                                                     │
│  ► Task 2.1  DEPTH ESTIMATION  ◄◄◄  BẠN ĐANG Ở ĐÂY               │
│    │                                                                │
│    │  Mục tiêu: Service inference Depth Anything V2                │
│    │  Input: Ảnh 2D món ăn (RGB) → Output: Depth map              │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Việt: Setup model + inference pipeline + deploy + tests    │
│    │  • Hoàng: Review code + hướng dẫn kỹ thuật                   │
│    │                                                                │
│    │  ⚡ TẠI SAO DEPTH ANYTHING V2?                                │
│    │  ① Zero-shot monocular depth estimation (không cần train)    │
│    │  ② Pretrained tốt trên nhiều loại ảnh (bao gồm food)       │
│    │  ③ Có sẵn trên HuggingFace → dễ tích hợp                   │
│    │  ④ POC đã test thành công (scripts/poc_depth_test.py ✅)     │
│    │                                                                │
│    │  Phase 2 pipeline CẦN depth map để:                           │
│    │  1. Task 2.2: Nhận diện vật tham chiếu (bát/thìa)           │
│    │  2. Task 2.3: Pixel-to-Real calibration                      │
│    │  3. Task 2.5: Tính thể tích V = ∫∫ depth(x,y) dA           │
│    │                                                                │
│    └───► Task 2.2 → 2.3 → 2.5: Cần depth map làm đầu vào         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Nền tảng đã có sẵn (từ Phase 1)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ĐÃ CÓ TỪ PHASE 1:                                                │
│                                                                     │
│  ✅ FastAPI skeleton:  src/vision-service/main.py                   │
│     - GET /health                                                   │
│     - POST /api/vision/estimate-volume (stub, return 0.0)          │
│                                                                     │
│  ✅ requirements.txt:  fastapi, uvicorn, torch, pillow, numpy      │
│                                                                     │
│  ✅ POC depth test:    scripts/poc_depth_test.py                    │
│     - Đã test thành công Depth Anything V2 Small qua HuggingFace  │
│     - Pipeline: load model → load image → pipe(image) → depth map │
│     - Output: depth PNG + statistics (min/max/mean)                │
│                                                                     │
│  ✅ gRPC proto:        src/vision-service/api/insight_pb2.py       │
│     - Đã generate Python proto files                               │
│                                                                     │
│  ✅ Dataset ready:     data/nutrition5k/parsed/ + data/vn_demo/    │
│     - Có ảnh để test pipeline                                      │
│                                                                     │
│  → TASK 2.1 xây dựng TRÊN nền tảng này, biến POC → production     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 1: Setup Depth Anything V2 Model — Việt (45 phút)

### 1.1 Cài đặt dependencies bổ sung

```bash
# Từ thư mục root InSight/
cd src/vision-service

# Cài thêm dependencies cần thiết (ngoài requirements.txt hiện tại)
pip install transformers>=4.35.0
pip install accelerate>=0.25.0
pip install scipy>=1.11.0
pip install opencv-python>=4.8.0
```

### 1.2 Update requirements.txt

```txt
# src/vision-service/requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
torch>=2.0.0
pillow>=10.0.0
numpy>=1.24.0

# === Thêm cho Task 2.1 ===
transformers>=4.35.0
accelerate>=0.25.0
scipy>=1.11.0
opencv-python>=4.8.0
```

### 1.3 Download model weights

```
┌─────────────────────────────────────────────────────────────────────┐
│  DEPTH ANYTHING V2 — Chọn variant nào?                              │
│                                                                     │
│  Model              | Params | Speed (GPU) | Accuracy | RAM        │
│  ─────────────────────────────────────────────────────────────────  │
│  DAv2-Small (vits)  | 24.8M  | ~45ms       | Tốt      | ~2GB      │
│  DAv2-Base (vitb)   | 97.5M  | ~80ms       | Rất tốt  | ~4GB      │
│  DAv2-Large (vitl)  | 335.3M | ~150ms      | Xuất sắc | ~8GB      │
│                                                                     │
│  ✅ CHỌN: DAv2-Small cho development (nhanh, nhẹ)                  │
│  📌 Sau này có thể upgrade lên Base/Large nếu cần accuracy hơn    │
│                                                                     │
│  HuggingFace model ID:                                              │
│  "depth-anything/Depth-Anything-V2-Small-hf"                       │
│  (Giống POC đã test thành công ✅)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

```python
# Cách download + cache model (chạy 1 lần)
# Model sẽ được cache tại ~/.cache/huggingface/
from transformers import pipeline

pipe = pipeline(
    task="depth-estimation",
    model="depth-anything/Depth-Anything-V2-Small-hf",
)
print("✅ Model downloaded and cached!")
```

### 1.4 Folder structure cho service

```
src/vision-service/
├── main.py                          ← FastAPI app (đã có, sẽ update)
├── requirements.txt                 ← Dependencies (update)
├── api/
│   ├── insight_pb2.py               ← gRPC proto (đã có)
│   └── insight_pb2_grpc.py          ← gRPC proto (đã có)
├── models/                          ← Thêm mới
│   ├── __init__.py
│   └── depth_model.py               ← ⭐ Depth Anything V2 wrapper
├── services/                        ← Thêm mới
│   ├── __init__.py
│   └── depth_service.py             ← ⭐ Business logic service
├── schemas/                         ← Thêm mới
│   ├── __init__.py
│   └── depth_schemas.py             ← ⭐ Pydantic response models
└── tests/                           ← Thêm mới
    ├── __init__.py
    └── test_depth_service.py        ← ⭐ Unit tests
```

---

## Bước 2: Implement Inference Pipeline — Việt (1.5 giờ)

### 2.1 Depth Model Wrapper

```python
# src/vision-service/models/depth_model.py
"""
Depth Anything V2 model wrapper.
Encapsulate model loading và inference logic.

Reference: POC thành công tại scripts/poc_depth_test.py
"""

import logging
import time
from typing import Optional

import numpy as np
import torch
from PIL import Image
from transformers import pipeline

logger = logging.getLogger(__name__)


class DepthAnythingV2:
    """Wrapper cho Depth Anything V2 model inference."""

    # Supported model variants
    MODELS = {
        "small": "depth-anything/Depth-Anything-V2-Small-hf",
        "base": "depth-anything/Depth-Anything-V2-Base-hf",
        "large": "depth-anything/Depth-Anything-V2-Large-hf",
    }

    def __init__(self, variant: str = "small", device: Optional[str] = None):
        """
        Initialize Depth Anything V2 model.

        Args:
            variant: Model size - "small", "base", or "large"
            device: "cuda" or "cpu". Auto-detect if None.
        """
        self.variant = variant
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipe = None
        self._loaded = False

    def load(self) -> None:
        """Load model weights. Gọi 1 lần khi startup."""
        if self._loaded:
            logger.info("Model already loaded, skipping...")
            return

        model_id = self.MODELS.get(self.variant)
        if not model_id:
            raise ValueError(f"Unknown variant: {self.variant}. Choose from: {list(self.MODELS.keys())}")

        logger.info(f"🔄 Loading Depth Anything V2 ({self.variant}) on {self.device}...")
        start = time.time()

        self.pipe = pipeline(
            task="depth-estimation",
            model=model_id,
            device=self.device,
        )

        elapsed = time.time() - start
        self._loaded = True
        logger.info(f"✅ Model loaded in {elapsed:.1f}s on {self.device.upper()}")

    def predict(self, image: Image.Image) -> dict:
        """
        Run depth estimation on a single image.

        Args:
            image: PIL Image (RGB)

        Returns:
            dict with:
              - "depth_map": numpy array (H, W) with depth values 0-255
              - "depth_image": PIL Image (grayscale depth visualization)
              - "inference_time_ms": float
              - "stats": dict with min, max, mean depth values
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Run inference
        start = time.time()
        result = self.pipe(image)
        inference_ms = (time.time() - start) * 1000

        # Extract depth map
        depth_image = result["depth"]  # PIL Image
        depth_array = np.array(depth_image)

        # Statistics
        stats = {
            "min": float(depth_array.min()),
            "max": float(depth_array.max()),
            "mean": float(depth_array.mean()),
            "std": float(depth_array.std()),
        }

        logger.info(
            f"📊 Depth estimated in {inference_ms:.0f}ms | "
            f"Range: [{stats['min']:.0f}, {stats['max']:.0f}] | "
            f"Mean: {stats['mean']:.1f}"
        )

        return {
            "depth_map": depth_array,
            "depth_image": depth_image,
            "inference_time_ms": inference_ms,
            "stats": stats,
        }

    @property
    def is_loaded(self) -> bool:
        return self._loaded
```

### 2.2 Depth Service (Business Logic)

```python
# src/vision-service/services/depth_service.py
"""
Depth estimation service — business logic layer.
Xử lý: nhận ảnh → tạo depth map → normalize → trả kết quả.
"""

import io
import base64
import logging
from typing import Optional

import numpy as np
from PIL import Image

from models.depth_model import DepthAnythingV2

logger = logging.getLogger(__name__)

# Singleton model instance
_model: Optional[DepthAnythingV2] = None


def get_model() -> DepthAnythingV2:
    """Get or create singleton model instance."""
    global _model
    if _model is None:
        _model = DepthAnythingV2(variant="small")
        _model.load()
    return _model


def estimate_depth(image_bytes: bytes) -> dict:
    """
    Estimate depth from image bytes.

    Args:
        image_bytes: Raw image bytes (JPEG/PNG)

    Returns:
        dict with depth estimation results:
          - depth_map_base64: base64 encoded depth map PNG
          - inference_time_ms: float
          - image_size: [width, height]
          - depth_stats: min, max, mean, std
    """
    # Decode image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    logger.info(f"📷 Processing image: {width}x{height}")

    # Run depth estimation
    model = get_model()
    result = model.predict(image)

    # Encode depth map to base64 PNG for API response
    depth_image = result["depth_image"]
    buffer = io.BytesIO()
    depth_image.save(buffer, format="PNG")
    depth_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "depth_map_base64": depth_base64,
        "inference_time_ms": result["inference_time_ms"],
        "image_size": [width, height],
        "depth_stats": result["stats"],
    }


def estimate_depth_raw(image: Image.Image) -> np.ndarray:
    """
    Get raw depth map as numpy array.
    Dùng cho internal pipeline (Task 2.3, 2.5).

    Args:
        image: PIL Image (RGB)

    Returns:
        numpy array (H, W) with depth values
    """
    model = get_model()
    result = model.predict(image)
    return result["depth_map"]
```

### 2.3 Pydantic Response Schemas

```python
# src/vision-service/schemas/depth_schemas.py
"""Pydantic schemas cho Depth Estimation API responses."""

from pydantic import BaseModel, Field
from typing import List


class DepthStats(BaseModel):
    """Statistics của depth map."""
    min: float = Field(..., description="Minimum depth value")
    max: float = Field(..., description="Maximum depth value") 
    mean: float = Field(..., description="Mean depth value")
    std: float = Field(..., description="Standard deviation of depth values")


class DepthEstimationResponse(BaseModel):
    """Response từ depth estimation endpoint."""
    depth_map_base64: str = Field(..., description="Base64 encoded depth map PNG")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    image_size: List[int] = Field(..., description="[width, height] of input image")
    depth_stats: DepthStats = Field(..., description="Depth map statistics")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    model_loaded: bool
    device: str
```

---

## Bước 3: Deploy via FastAPI Endpoint — Việt (1 giờ)

### 3.1 Update main.py

```python
# src/vision-service/main.py
"""
InSight Vision Service — FastAPI application.
Cung cấp endpoints cho depth estimation và volume estimation.

Updated: Task 2.1 — Thêm depth estimation endpoint.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from services.depth_service import get_model, estimate_depth
from schemas.depth_schemas import DepthEstimationResponse, HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown."""
    logger.info("🚀 Starting InSight Vision Service...")
    
    # Pre-load model (warm up)
    model = get_model()
    logger.info(f"✅ Model ready on {model.device.upper()}")
    
    yield  # App is running
    
    logger.info("👋 Shutting down InSight Vision Service...")


app = FastAPI(
    title="InSight Vision Service",
    version="0.2.0",
    description="Computer Vision service for food depth estimation and volume calculation",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    model = get_model()
    return HealthResponse(
        status="UP",
        service="insight-vision-service",
        model_loaded=model.is_loaded,
        device=model.device,
    )


@app.post("/api/vision/depth", response_model=DepthEstimationResponse)
async def depth_estimation(image: UploadFile = File(...)):
    """
    Generate depth map from food image.
    
    - Input: Image file (JPEG/PNG)
    - Output: Base64 encoded depth map + statistics
    - Target: ≤ 500ms inference time on GPU
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {image.content_type}. Expected image/*"
        )

    try:
        # Read image bytes
        image_bytes = await image.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Run depth estimation
        result = estimate_depth(image_bytes)
        
        return DepthEstimationResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Depth estimation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Depth estimation failed: {str(e)}")


@app.post("/api/vision/estimate-volume")
async def estimate_volume(image: UploadFile = File(...)):
    """
    Estimate food volume from image (placeholder for Task 2.5).
    
    TODO: Implement in Task 2.5 using depth map + calibration
    """
    return {"volume_ml": 0.0, "message": "Not implemented — see Task 2.5"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
```

### 3.2 Kiểm tra service chạy được

```bash
# Từ src/vision-service/
python main.py

# Terminal output kỳ vọng:
# 🚀 Starting InSight Vision Service...
# 🔄 Loading Depth Anything V2 (small) on cpu...
# ✅ Model loaded in X.Xs on CPU
# ✅ Model ready on CPU
# INFO:     Uvicorn running on http://0.0.0.0:8000

# Test health check
curl http://localhost:8000/health
# Kỳ vọng: {"status":"UP","service":"insight-vision-service","model_loaded":true,"device":"cpu"}
```

### 3.3 Test depth estimation endpoint

```bash
# Dùng ảnh từ POC hoặc VN demo
curl -X POST http://localhost:8000/api/vision/depth \
  -F "image=@data/poc/raw/poc_pho_bo_001_main.jpg" \
  | python -m json.tool

# Kỳ vọng:
# {
#   "depth_map_base64": "iVBORw0KGgo...",
#   "inference_time_ms": 450.5,
#   "image_size": [640, 480],
#   "depth_stats": {
#     "min": 0.0,
#     "max": 255.0,
#     "mean": 128.5,
#     "std": 45.2
#   }
# }
```

### 3.4 Sơ đồ API flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API Flow                                     │
│                                                                     │
│  Client                                                             │
│    │                                                                │
│    │  POST /api/vision/depth                                       │
│    │  Content-Type: multipart/form-data                            │
│    │  Body: image file (JPEG/PNG)                                  │
│    │                                                                │
│    ▼                                                                │
│  FastAPI (main.py)                                                  │
│    │ Validate file type                                            │
│    │ Read image bytes                                              │
│    │                                                                │
│    ▼                                                                │
│  DepthService (services/depth_service.py)                          │
│    │ Decode bytes → PIL Image                                      │
│    │ Call model.predict()                                          │
│    │                                                                │
│    ▼                                                                │
│  DepthAnythingV2 (models/depth_model.py)                           │
│    │ HuggingFace pipeline inference                                │
│    │ Return: depth_map (numpy) + depth_image (PIL) + stats         │
│    │                                                                │
│    ▼                                                                │
│  DepthService                                                       │
│    │ Encode depth_image → base64 PNG                               │
│    │ Build response dict                                           │
│    │                                                                │
│    ▼                                                                │
│  Client receives DepthEstimationResponse (JSON)                    │
│    - depth_map_base64 (string)                                     │
│    - inference_time_ms (float)                                     │
│    - image_size [w, h]                                             │
│    - depth_stats {min, max, mean, std}                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Bước 4: Unit Tests — Việt (45 phút)

### 4.1 Test file

```python
# src/vision-service/tests/test_depth_service.py
"""
Unit tests cho Depth Estimation Service.
Chạy: pytest tests/ -v
"""

import io
import pytest
import numpy as np
from PIL import Image

from models.depth_model import DepthAnythingV2
from services.depth_service import estimate_depth, estimate_depth_raw


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def depth_model():
    """Load model 1 lần cho toàn bộ test session (tiết kiệm thời gian)."""
    model = DepthAnythingV2(variant="small")
    model.load()
    return model


@pytest.fixture
def sample_image():
    """Tạo ảnh test RGB ngẫu nhiên."""
    arr = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.fixture
def sample_image_bytes(sample_image):
    """Convert ảnh test sang bytes (JPEG)."""
    buffer = io.BytesIO()
    sample_image.save(buffer, format="JPEG")
    return buffer.getvalue()


# ============================================================
# Tests: Model
# ============================================================

class TestDepthModel:
    """Tests cho DepthAnythingV2 model wrapper."""

    def test_model_loads(self, depth_model):
        """Model phải load thành công."""
        assert depth_model.is_loaded

    def test_predict_returns_dict(self, depth_model, sample_image):
        """predict() phải trả về dict với đúng keys."""
        result = depth_model.predict(sample_image)
        assert "depth_map" in result
        assert "depth_image" in result
        assert "inference_time_ms" in result
        assert "stats" in result

    def test_depth_map_shape(self, depth_model, sample_image):
        """Depth map phải có 2 chiều (H, W)."""
        result = depth_model.predict(sample_image)
        depth_map = result["depth_map"]
        assert isinstance(depth_map, np.ndarray)
        assert depth_map.ndim == 2  # Grayscale

    def test_depth_map_values(self, depth_model, sample_image):
        """Depth map values phải trong khoảng hợp lệ."""
        result = depth_model.predict(sample_image)
        depth_map = result["depth_map"]
        assert depth_map.min() >= 0
        assert depth_map.max() <= 255

    def test_inference_time(self, depth_model, sample_image):
        """Inference time phải hợp lý (< 10 giây cho CPU, < 500ms cho GPU)."""
        result = depth_model.predict(sample_image)
        # Cho phép tối đa 10s trên CPU (test environment)
        assert result["inference_time_ms"] < 10000

    def test_invalid_variant(self):
        """Variant không hợp lệ phải raise ValueError."""
        model = DepthAnythingV2(variant="xxxl")
        with pytest.raises(ValueError):
            model.load()

    def test_predict_without_load(self):
        """predict() khi chưa load phải raise RuntimeError."""
        model = DepthAnythingV2(variant="small")
        image = Image.new("RGB", (100, 100))
        with pytest.raises(RuntimeError):
            model.predict(image)


# ============================================================
# Tests: Service
# ============================================================

class TestDepthService:
    """Tests cho depth estimation service functions."""

    def test_estimate_depth_returns_base64(self, sample_image_bytes):
        """estimate_depth() phải trả về base64 encoded depth map."""
        result = estimate_depth(sample_image_bytes)
        assert "depth_map_base64" in result
        assert isinstance(result["depth_map_base64"], str)
        assert len(result["depth_map_base64"]) > 0

    def test_estimate_depth_stats(self, sample_image_bytes):
        """estimate_depth() phải trả về depth statistics."""
        result = estimate_depth(sample_image_bytes)
        stats = result["depth_stats"]
        assert "min" in stats
        assert "max" in stats
        assert "mean" in stats

    def test_estimate_depth_raw(self, sample_image):
        """estimate_depth_raw() phải trả về numpy array."""
        depth_map = estimate_depth_raw(sample_image)
        assert isinstance(depth_map, np.ndarray)
        assert depth_map.ndim == 2

    def test_different_image_sizes(self):
        """Model phải xử lý được nhiều kích thước ảnh khác nhau."""
        sizes = [(320, 240), (640, 480), (1280, 720)]
        for w, h in sizes:
            image = Image.new("RGB", (w, h), color="blue")
            depth_map = estimate_depth_raw(image)
            assert depth_map.ndim == 2, f"Failed for size {w}x{h}"
```

### 4.2 Chạy tests

```bash
# Cài pytest
pip install pytest pytest-cov

# Chạy tests (từ src/vision-service/)
pytest tests/ -v

# Kỳ vọng output:
# tests/test_depth_service.py::TestDepthModel::test_model_loads PASSED
# tests/test_depth_service.py::TestDepthModel::test_predict_returns_dict PASSED
# tests/test_depth_service.py::TestDepthModel::test_depth_map_shape PASSED
# tests/test_depth_service.py::TestDepthModel::test_depth_map_values PASSED
# tests/test_depth_service.py::TestDepthModel::test_inference_time PASSED
# tests/test_depth_service.py::TestDepthModel::test_invalid_variant PASSED
# tests/test_depth_service.py::TestDepthModel::test_predict_without_load PASSED
# tests/test_depth_service.py::TestDepthService::test_estimate_depth_returns_base64 PASSED
# tests/test_depth_service.py::TestDepthService::test_estimate_depth_stats PASSED
# tests/test_depth_service.py::TestDepthService::test_estimate_depth_raw PASSED
# tests/test_depth_service.py::TestDepthService::test_different_image_sizes PASSED

# Chạy với coverage
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## Bước 5: Verify End-to-End — Việt + Hoàng (15 phút)

### 5.1 Manual E2E test

```bash
# 1. Start service
cd src/vision-service
python main.py

# 2. (Terminal khác) Test với ảnh thực
# Dùng ảnh POC đã có
curl -X POST http://localhost:8000/api/vision/depth \
  -F "image=@../../data/poc/raw/poc_pho_bo_001_main.jpg" \
  -o depth_result.json

# 3. Kiểm tra kết quả
python -c "
import json, base64
from PIL import Image
import io

with open('depth_result.json') as f:
    data = json.load(f)

print(f'Inference time: {data[\"inference_time_ms\"]:.0f}ms')
print(f'Image size: {data[\"image_size\"]}')
print(f'Depth stats: {data[\"depth_stats\"]}')

# Decode và save depth map
depth_bytes = base64.b64decode(data['depth_map_base64'])
depth_img = Image.open(io.BytesIO(depth_bytes))
depth_img.save('depth_output.png')
print(f'Depth map saved: depth_output.png ({depth_img.size})')
"
```

### 5.2 Swagger UI test

```
Mở browser: http://localhost:8000/docs

1. Expand POST /api/vision/depth
2. Click "Try it out"
3. Upload ảnh món ăn
4. Execute → kiểm tra response 200 OK
```

### 5.3 Performance check

```
┌─────────────────────────────────────────────────────────────────────┐
│  KIỂM TRA HIỆU NĂNG:                                               │
│                                                                     │
│  Target: ≤ 500ms trên GPU                                          │
│                                                                     │
│  Nếu trên CPU (dev machine):                                       │
│  • Small model: ~1-3 giây → OK cho development                    │
│  • Sẽ nhanh hơn nhiều trên GPU khi deploy                         │
│                                                                     │
│  Nếu trên GPU:                                                     │
│  • Small model: ~30-50ms → ✅ Excess                               │
│  • Base model: ~60-100ms → ✅ OK                                   │
│  • Large model: ~150-250ms → ✅ OK                                 │
│                                                                     │
│  ⚠️ Lần đầu tiên inference sẽ chậm hơn (warmup)                  │
│  → Đã xử lý bằng lifespan startup                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `CUDA out of memory` | Model quá lớn cho GPU | Chuyển sang variant "small" hoặc dùng CPU |
| `ModuleNotFoundError: transformers` | Chưa cài dependencies | `pip install transformers accelerate` |
| Inference > 10s trên CPU | Bình thường cho CPU | Chấp nhận, sẽ nhanh hơn trên GPU |
| `RuntimeError: Model not loaded` | Chưa gọi `model.load()` | App startup sẽ tự load qua lifespan |
| Import error `models.depth_model` | Thiếu `__init__.py` | Tạo file `__init__.py` trống trong mỗi folder |

### Tips

```
┌─────────────────────────────────────────────────────────────────────┐
│  💡 TIPS CHO VIỆT:                                                  │
│                                                                     │
│  1. Có thể reuse code từ POC:                                      │
│     scripts/poc_depth_test.py đã verify model hoạt động            │
│     → Chỉ cần refactor thành production structure                  │
│                                                                     │
│  2. Model caching:                                                  │
│     HuggingFace tự cache tại ~/.cache/huggingface/                 │
│     → Lần đầu download ~350MB, sau đó load từ cache               │
│                                                                     │
│  3. Nếu không có GPU:                                               │
│     Develop trên CPU OK, inference ~1-3s cho Small model           │
│     Production deploy sẽ dùng GPU → ≤ 500ms                       │
│                                                                     │
│  4. Depth map output:                                               │
│     Giá trị 0-255, LIGHTER = CLOSER, DARKER = FARTHER             │
│     Task 2.3 sẽ convert sang real-world dimensions                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Checklist hoàn thành

- [ ] Depth Anything V2 model loaded thành công (download weights, verify)
- [ ] `models/depth_model.py` — Model wrapper class `DepthAnythingV2`
- [ ] `services/depth_service.py` — Service layer với `estimate_depth()` và `estimate_depth_raw()`
- [ ] `schemas/depth_schemas.py` — Pydantic response models
- [ ] `main.py` updated — endpoint `POST /api/vision/depth` hoạt động
- [ ] `requirements.txt` updated — thêm transformers, accelerate, scipy, opencv-python
- [ ] `tests/test_depth_service.py` — Unit tests pass
- [ ] Health check trả `model_loaded: true`
- [ ] Manual test với ảnh POC/VN demo thành công
- [ ] Inference time ghi nhận (CPU: ~1-3s, GPU: ≤ 500ms)
- [ ] Hoàng reviewed code

---

> **Tạo**: 10/03/2026
> **Guide cho**: [TASK_2.1_DEPTH_ESTIMATION.md](../Tasks/TASK_2.1_DEPTH_ESTIMATION.md)

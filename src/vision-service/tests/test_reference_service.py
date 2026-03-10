"""
Unit tests for Reference Object Detection Service (Task 2.2).

Run: cd src/vision-service && pytest tests/test_reference_service.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Add parent dir so imports work when running from vision-service/
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.reference_service import (
    REFERENCE_DIMENSIONS,
    ReferenceDetector,
    ReferenceObject,
)


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture(scope="session")
def detector():
    """Load reference detector once for session."""
    det = ReferenceDetector(confidence=0.3)
    det.load()
    return det


@pytest.fixture
def sample_image():
    """Create a random RGB test image."""
    arr = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.fixture
def sample_bowl_detection():
    """Create a mock ReferenceObject for testing."""
    return ReferenceObject(
        class_name="bat_pho_m",
        confidence=0.92,
        bbox=[100.0, 50.0, 480.0, 350.0],
        bbox_width_px=380.0,
        bbox_height_px=300.0,
        real_width_cm=19.0,
        real_height_cm=7.5,
        pixels_per_cm=20.0,  # 380 / 19 = 20
    )


@pytest.fixture
def sample_spoon_detection():
    """Create a mock ReferenceObject for spoon."""
    return ReferenceObject(
        class_name="thia",
        confidence=0.85,
        bbox=[500.0, 200.0, 530.0, 360.0],
        bbox_width_px=30.0,
        bbox_height_px=160.0,
        real_width_cm=4.0,
        real_height_cm=16.0,
        pixels_per_cm=10.0,  # 160 / 16 = 10
    )


# ============================================================
# Tests: Reference Dimensions
# ============================================================
class TestReferenceDimensions:
    """Tests for reference object dimension definitions."""

    def test_all_types_have_required_fields(self):
        """Every reference type must have width_cm, height_cm, description."""
        required = {"width_cm", "height_cm", "description"}
        for ref_type, dims in REFERENCE_DIMENSIONS.items():
            assert required.issubset(
                dims.keys()
            ), f"Missing keys for {ref_type}: {required - dims.keys()}"

    def test_dimensions_are_positive(self):
        """All dimensions must be positive."""
        for ref_type, dims in REFERENCE_DIMENSIONS.items():
            assert dims["width_cm"] > 0, f"{ref_type} width_cm <= 0"
            assert dims["height_cm"] > 0, f"{ref_type} height_cm <= 0"

    def test_expected_types_exist(self):
        """Expected Vietnamese tableware types must be defined."""
        expected = ["bat_com", "bat_pho_m", "bat_pho_l", "dia_com", "thia", "dua"]
        for t in expected:
            assert t in REFERENCE_DIMENSIONS, f"Missing type: {t}"

    def test_bowl_sizes_consistent(self):
        """Bowl sizes should be: bat_com < bat_pho_m < bat_pho_l."""
        bat_com = REFERENCE_DIMENSIONS["bat_com"]["width_cm"]
        bat_pho_m = REFERENCE_DIMENSIONS["bat_pho_m"]["width_cm"]
        bat_pho_l = REFERENCE_DIMENSIONS["bat_pho_l"]["width_cm"]
        assert bat_com < bat_pho_m < bat_pho_l


# ============================================================
# Tests: ReferenceObject dataclass
# ============================================================
class TestReferenceObject:
    """Tests for ReferenceObject data structure."""

    def test_scale_factor_calculation(self, sample_bowl_detection):
        """Scale factor should be bbox_width / real_width."""
        expected = 380.0 / 19.0
        assert abs(sample_bowl_detection.pixels_per_cm - expected) < 0.1

    def test_spoon_scale_uses_height(self, sample_spoon_detection):
        """Spoon scale factor should use height (length)."""
        expected = 160.0 / 16.0
        assert abs(sample_spoon_detection.pixels_per_cm - expected) < 0.1

    def test_dataclass_fields(self, sample_bowl_detection):
        """ReferenceObject must have all required fields."""
        assert hasattr(sample_bowl_detection, "class_name")
        assert hasattr(sample_bowl_detection, "confidence")
        assert hasattr(sample_bowl_detection, "bbox")
        assert hasattr(sample_bowl_detection, "pixels_per_cm")


# ============================================================
# Tests: ReferenceDetector
# ============================================================
class TestReferenceDetector:
    """Tests for ReferenceDetector class."""

    def test_detector_loads(self, detector):
        """Detector must load successfully."""
        assert detector.is_loaded

    def test_detect_returns_list(self, detector, sample_image):
        """detect() must return a list (may be empty for random images)."""
        result = detector.detect(sample_image)
        assert isinstance(result, list)

    def test_detections_are_reference_objects(self, detector, sample_image):
        """All detections must be ReferenceObject instances."""
        result = detector.detect(sample_image)
        for det in result:
            assert isinstance(det, ReferenceObject)

    def test_detections_sorted_by_confidence(self, detector, sample_image):
        """Detections should be sorted by confidence (highest first)."""
        result = detector.detect(sample_image)
        if len(result) >= 2:
            for i in range(len(result) - 1):
                assert result[i].confidence >= result[i + 1].confidence

    def test_predict_without_load_raises(self):
        """detect() before load() must raise RuntimeError."""
        det = ReferenceDetector()
        image = Image.new("RGB", (100, 100))
        with pytest.raises(RuntimeError, match="not loaded"):
            det.detect(image)

    def test_get_best_scale_factor_empty(self, detector):
        """Should return None for empty detections list."""
        assert detector.get_best_scale_factor([]) is None

    def test_get_best_scale_factor_priority(
        self, detector, sample_bowl_detection, sample_spoon_detection
    ):
        """Scale factor should prioritize bowls over spoons."""
        detections = [sample_spoon_detection, sample_bowl_detection]
        best = detector.get_best_scale_factor(detections)
        # bat_pho_m has higher priority than thia
        assert best == sample_bowl_detection.pixels_per_cm

    def test_get_best_scale_factor_single(self, detector, sample_spoon_detection):
        """Should return single detection's scale factor."""
        best = detector.get_best_scale_factor([sample_spoon_detection])
        assert best == sample_spoon_detection.pixels_per_cm


# ============================================================
# Tests: Class Mapping
# ============================================================
class TestClassMapping:
    """Tests for COCO → InSight class mapping."""

    def test_bowl_mapping_small(self, detector):
        """Small bowl (width ratio < 0.20) should map to bat_com."""
        bbox = [0, 0, 100, 100]  # width 100 / img_width 640 = 0.156
        result = detector._map_class("bowl", bbox, 640)
        assert result == "bat_com"

    def test_bowl_mapping_medium(self, detector):
        """Medium bowl (0.20 < ratio < 0.35) should map to bat_pho_m."""
        bbox = [0, 0, 200, 200]  # width 200 / img_width 640 = 0.3125
        result = detector._map_class("bowl", bbox, 640)
        assert result == "bat_pho_m"

    def test_bowl_mapping_large(self, detector):
        """Large bowl (ratio > 0.35) should map to bat_pho_l."""
        bbox = [0, 0, 400, 400]  # width 400 / img_width 640 = 0.625
        result = detector._map_class("bowl", bbox, 640)
        assert result == "bat_pho_l"

    def test_spoon_mapping(self, detector):
        """COCO 'spoon' should map to 'thia'."""
        result = detector._map_class("spoon", [0, 0, 50, 100], 640)
        assert result == "thia"

    def test_irrelevant_class_returns_none(self, detector):
        """Non-reference classes should return None."""
        assert detector._map_class("car", [0, 0, 50, 50], 640) is None
        assert detector._map_class("person", [0, 0, 50, 50], 640) is None
        assert detector._map_class("cat", [0, 0, 50, 50], 640) is None

    def test_custom_class_direct_mapping(self, detector):
        """Custom model class names should map directly."""
        assert detector._map_class("bat_com", [0, 0, 50, 50], 640) == "bat_com"
        assert detector._map_class("bat_pho_m", [0, 0, 50, 50], 640) == "bat_pho_m"
        assert detector._map_class("dua", [0, 0, 50, 50], 640) == "dua"

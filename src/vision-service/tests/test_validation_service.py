"""
Unit tests for Validation Service (Task 2.6).

Tests cover:
  - MetricComputer.ape() — exact and edge cases
  - MetricComputer.mape() — mean across samples
  - MetricComputer.pass_rate() — threshold counting
  - MetricComputer.compute_sample_result() — full result object
  - DataLoader.load_vn_demo() — parses real JSON files
  - DataLoader.load_n5k_subset() — parses real N5k JSON
  - DataLoader error handling — missing / invalid paths
  - ReportGenerator.generate() — aggregate metrics
  - ReportGenerator._category_breakdown() — group by source
  - ValidationReport.to_dict() — serialisation contract
  - ValidationReport.save() — writes valid JSON to disk
  - Singleton get_data_loader() — stable identity across calls
  - Integration: load → compare → report loop with real GT data

Run: cd src/vision-service && pytest tests/test_validation_service.py -v
"""

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.validation_service import (
    DataLoader,
    GroundTruth,
    MetricComputer,
    ReportGenerator,
    SampleResult,
    ValidationReport,
    get_data_loader,
)

# Project root for path helpers
_PROJECT_ROOT = Path(__file__).parents[3]
_VN_DEMO_ROOT = _PROJECT_ROOT / "data" / "vn_demo"
_N5K_PATH = _PROJECT_ROOT / "data" / "nutrition5k" / "parsed" / "nutrition5k_subset.json"


# ============================================================
# Helpers
# ============================================================
def _make_gt(
    sample_id="test_01",
    source="vn_demo",
    weight_g=200.0,
    carb_g=40.0,
    food_id="vn_com_trang",
    food_name_en="White rice",
    method="estimated_from_literature",
    gt_gl=None,
) -> GroundTruth:
    return GroundTruth(
        sample_id=sample_id,
        source=source,
        food_id=food_id,
        food_name_en=food_name_en,
        total_weight_g=weight_g,
        total_carb_g=carb_g,
        gt_gl=gt_gl,
        measurement_method=method,
        image_path=None,
    )


def _make_result(
    sample_id="test_01",
    source="vn_demo",
    gt_weight=200.0,
    gt_carb=40.0,
    pred_weight=180.0,
    pred_carb=36.0,
    pred_volume=167.0,
    pred_gl=26.3,
    quality="medium",
    food_id="vn_com_trang",
    ms=900.0,
) -> SampleResult:
    weight_ape = MetricComputer.ape(pred_weight, gt_weight)
    carb_ape = MetricComputer.ape(pred_carb, gt_carb)
    return SampleResult(
        sample_id=sample_id,
        source=source,
        food_name_en="White rice",
        measurement_method="estimated_from_literature",
        gt_weight_g=gt_weight,
        gt_carb_g=gt_carb,
        pred_weight_g=pred_weight,
        pred_carb_g=pred_carb,
        pred_volume_ml=pred_volume,
        pred_gl=pred_gl,
        pred_quality=quality,
        weight_ape=weight_ape,
        carb_ape=carb_ape,
        food_id_used=food_id,
        pipeline_time_ms=ms,
    )


# ============================================================
# 1. MetricComputer — APE
# ============================================================
class TestAPE:
    """MetricComputer.ape() — absolute percentage error."""

    def test_exact_match_is_zero(self):
        """Perfect prediction → 0% error."""
        assert MetricComputer.ape(100.0, 100.0) == 0.0

    def test_10pct_over(self):
        """Prediction 10% above actual → APE 10%."""
        assert abs(MetricComputer.ape(110.0, 100.0) - 10.0) < 1e-9

    def test_10pct_under(self):
        """Prediction 10% below actual → APE 10% (absolute)."""
        assert abs(MetricComputer.ape(90.0, 100.0) - 10.0) < 1e-9

    def test_zero_actual_returns_zero(self):
        """Division by zero guard: actual=0 → APE=0.0."""
        assert MetricComputer.ape(50.0, 0.0) == 0.0

    def test_zero_predicted(self):
        """All-wrong prediction → APE=100%."""
        assert abs(MetricComputer.ape(0.0, 100.0) - 100.0) < 1e-9

    def test_large_overprediction(self):
        """3× overprediction → APE=200%."""
        assert abs(MetricComputer.ape(300.0, 100.0) - 200.0) < 1e-9

    def test_symmetric_around_actual(self):
        """
        APE is NOT symmetric: +50g vs -50g give different raw errors
        but the same PERCENTAGE when actual is the same.
        Pred=150, actual=100 → 50%; pred=50, actual=100 → 50%.
        """
        ape_over = MetricComputer.ape(150.0, 100.0)
        ape_under = MetricComputer.ape(50.0, 100.0)
        assert abs(ape_over - 50.0) < 1e-9
        assert abs(ape_under - 50.0) < 1e-9

    def test_realistic_weight_error(self):
        """Pred=380g, actual=450g (phở bò) → ~15.6%."""
        ape = MetricComputer.ape(380.0, 450.0)
        assert abs(ape - (70.0 / 450.0 * 100.0)) < 1e-6


# ============================================================
# 2. MetricComputer — MAPE
# ============================================================
class TestMAPE:
    """MetricComputer.mape() — mean APE."""

    def test_empty_list_returns_zero(self):
        assert MetricComputer.mape([]) == 0.0

    def test_single_element(self):
        assert abs(MetricComputer.mape([12.5]) - 12.5) < 1e-9

    def test_all_zero(self):
        assert MetricComputer.mape([0.0, 0.0, 0.0]) == 0.0

    def test_mean_of_known_values(self):
        """MAPE([10, 20, 30]) = 20.0."""
        assert abs(MetricComputer.mape([10.0, 20.0, 30.0]) - 20.0) < 1e-9

    def test_five_samples_below_15(self):
        """5 samples all ≤ 15 → MAPE ≤ 15."""
        apes = [5.0, 8.0, 12.0, 14.0, 15.0]
        assert MetricComputer.mape(apes) <= 15.0


# ============================================================
# 3. MetricComputer — pass_rate
# ============================================================
class TestPassRate:
    """MetricComputer.pass_rate() — fraction within threshold."""

    def test_empty_returns_zero(self):
        assert MetricComputer.pass_rate([]) == 0.0

    def test_all_pass(self):
        assert MetricComputer.pass_rate([5.0, 10.0, 14.9]) == 100.0

    def test_none_pass(self):
        assert MetricComputer.pass_rate([16.0, 20.0, 30.0]) == 0.0

    def test_half_pass(self):
        result = MetricComputer.pass_rate([5.0, 20.0])
        assert abs(result - 50.0) < 1e-9

    def test_exactly_threshold_passes(self):
        """APE == 15.0% is considered passing."""
        assert MetricComputer.pass_rate([15.0], threshold_pct=15.0) == 100.0

    def test_custom_threshold(self):
        """Custom threshold=10 → tighter requirement."""
        apes = [9.0, 11.0, 5.0, 12.0]
        # 9 and 5 pass (<= 10); 11 and 12 fail
        result = MetricComputer.pass_rate(apes, threshold_pct=10.0)
        assert abs(result - 50.0) < 1e-9


# ============================================================
# 4. MetricComputer — compute_sample_result
# ============================================================
class TestComputeSampleResult:
    """MetricComputer.compute_sample_result() — full SampleResult."""

    def test_ape_computed_from_gt(self):
        """APE values are computed, not passed directly."""
        gt = _make_gt(weight_g=200.0, carb_g=40.0)
        sr = MetricComputer.compute_sample_result(
            gt=gt,
            pred_weight_g=220.0,   # 10% over
            pred_carb_g=44.0,      # 10% over
            pred_volume_ml=200.0,
            pred_gl=32.0,
            pred_quality="high",
            food_id_used="vn_com_trang",
            pipeline_time_ms=800.0,
        )
        assert abs(sr.weight_ape - 10.0) < 1e-6
        assert abs(sr.carb_ape - 10.0) < 1e-6

    def test_perfect_prediction(self):
        gt = _make_gt(weight_g=150.0, carb_g=75.0)
        sr = MetricComputer.compute_sample_result(
            gt=gt,
            pred_weight_g=150.0,
            pred_carb_g=75.0,
            pred_volume_ml=428.0,
            pred_gl=60.0,
            pred_quality="high",
            food_id_used="vn_banh_mi",
            pipeline_time_ms=950.0,
        )
        assert sr.weight_ape == 0.0
        assert sr.carb_ape == 0.0

    def test_sample_id_preserved(self):
        gt = _make_gt(sample_id="pho_bo_001")
        sr = MetricComputer.compute_sample_result(
            gt=gt,
            pred_weight_g=400.0,
            pred_carb_g=40.0,
            pred_volume_ml=390.0,
            pred_gl=18.0,
            pred_quality="medium",
            food_id_used="vn_pho_bo",
            pipeline_time_ms=1050.0,
        )
        assert sr.sample_id == "pho_bo_001"
        assert sr.source == "vn_demo"


# ============================================================
# 5. DataLoader — VN demo
# ============================================================
class TestDataLoaderVNDemo:
    """DataLoader.load_vn_demo() parsing real JSON files."""

    @pytest.fixture(autouse=True)
    def skip_if_missing(self):
        if not _VN_DEMO_ROOT.exists():
            pytest.skip("VN demo data not available")

    def test_loads_expected_count(self):
        """Should load exactly 5 VN demo samples."""
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        assert len(samples) == 5

    def test_all_have_positive_weight(self):
        """All ground truth weights must be > 0."""
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        for s in samples:
            assert s.total_weight_g > 0, f"{s.sample_id}: weight={s.total_weight_g}"

    def test_all_have_positive_carb(self):
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        for s in samples:
            assert s.total_carb_g > 0, f"{s.sample_id}: carb={s.total_carb_g}"

    def test_source_is_vn_demo(self):
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        for s in samples:
            assert s.source == "vn_demo", f"{s.sample_id}: source={s.source}"

    def test_image_paths_exist(self):
        """Top-down image files must exist on disk."""
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        images_found = [s for s in samples if s.image_path and s.image_path.exists()]
        assert len(images_found) == len(samples), (
            f"Expected all {len(samples)} samples to have images, "
            f"but only {len(images_found)} have local image paths."
        )

    def test_pho_bo_weight_is_450(self):
        """VN demo phở bò GT weight = 450g (from JSON)."""
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        pho = next((s for s in samples if "pho" in s.sample_id), None)
        assert pho is not None, "pho_bo_001 sample not found"
        assert abs(pho.total_weight_g - 450.0) < 0.1

    def test_pho_bo_carb_is_45(self):
        """VN demo phở bò GT carb = 45.0g (from JSON)."""
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        pho = next((s for s in samples if "pho" in s.sample_id), None)
        assert pho is not None
        assert abs(pho.total_carb_g - 45.0) < 0.1

    def test_invalid_root_returns_empty(self):
        """Non-existent root returns empty list (no exception)."""
        samples = DataLoader.load_vn_demo(Path("/does/not/exist"))
        assert samples == []


# ============================================================
# 6. DataLoader — N5k
# ============================================================
class TestDataLoaderN5k:
    """DataLoader.load_n5k_subset() parsing N5k parsed JSON."""

    @pytest.fixture(autouse=True)
    def skip_if_missing(self):
        if not _N5K_PATH.exists():
            pytest.skip("N5k subset JSON not available")

    def test_loads_five_samples(self):
        """Subset JSON has 5 N5k entries."""
        samples = DataLoader.load_n5k_subset(_N5K_PATH)
        assert len(samples) == 5

    def test_all_source_is_n5k(self):
        samples = DataLoader.load_n5k_subset(_N5K_PATH)
        for s in samples:
            assert s.source == "nutrition5k"

    def test_all_weights_positive(self):
        samples = DataLoader.load_n5k_subset(_N5K_PATH)
        for s in samples:
            assert s.total_weight_g > 0

    def test_measurement_method_is_lab_scale(self):
        samples = DataLoader.load_n5k_subset(_N5K_PATH)
        for s in samples:
            assert s.measurement_method == "lab_scale"

    def test_n5k_1556_weight_is_385(self):
        """First N5k sample weight = 385g (from JSON)."""
        samples = DataLoader.load_n5k_subset(_N5K_PATH)
        s1556 = next((s for s in samples if s.sample_id == "n5k_1556"), None)
        assert s1556 is not None
        assert abs(s1556.total_weight_g - 385.0) < 0.1

    def test_invalid_path_returns_empty(self):
        samples = DataLoader.load_n5k_subset(Path("/does/not/exist.json"))
        assert samples == []


# ============================================================
# 7. ReportGenerator
# ============================================================
class TestReportGenerator:
    """ReportGenerator.generate() — aggregate report structure."""

    def test_empty_results_returns_zeros(self):
        report = ReportGenerator.generate([])
        assert report.n_total == 0
        assert report.mape_weight == 0.0
        assert report.mape_carb == 0.0
        assert report.pass_rate_15pct == 0.0

    def test_single_perfect_result(self):
        sr = _make_result(gt_weight=200.0, pred_weight=200.0,
                          gt_carb=40.0, pred_carb=40.0)
        report = ReportGenerator.generate([sr])
        assert report.n_total == 1
        assert report.mape_weight == 0.0
        assert report.mape_carb == 0.0
        assert report.pass_rate_15pct == 100.0
        assert report.passes_threshold is True

    def test_single_result_above_threshold(self):
        """20% weight error → MAPE=20% → fails threshold."""
        sr = _make_result(gt_weight=200.0, pred_weight=240.0,
                          gt_carb=40.0, pred_carb=40.0)
        report = ReportGenerator.generate([sr])
        assert report.mape_weight > 15.0
        assert report.passes_threshold is False

    def test_mixed_pass_fail(self):
        """3 passing + 1 failing → 75% pass rate."""
        results = [
            _make_result(f"s{i}", gt_weight=200.0, pred_weight=200.0 + i * 5)
            for i in range(4)
        ]
        # i=0: 0%, i=1: 2.5%, i=2: 5%, i=3: 7.5% weight APE
        report = ReportGenerator.generate(results)
        # All ≤ 15% → 100% pass rate
        assert report.pass_rate_15pct == 100.0

    def test_category_breakdown_by_source(self):
        """Results from 2 sources → 2 categories in breakdown."""
        vn_r = _make_result("vn_01", source="vn_demo")
        n5k_r = _make_result("n5_02", source="nutrition5k")
        report = ReportGenerator.generate([vn_r, n5k_r])
        assert len(report.by_category) == 2
        cats = {c.category_name for c in report.by_category}
        assert "vn_demo" in cats
        assert "nutrition5k" in cats

    def test_n_n5k_n_vn_demo_counts(self):
        results = [
            _make_result("v1", source="vn_demo"),
            _make_result("v2", source="vn_demo"),
            _make_result("n1", source="nutrition5k"),
        ]
        report = ReportGenerator.generate(results)
        assert report.n_vn_demo == 2
        assert report.n_n5k == 1

    def test_run_date_recorded(self):
        from datetime import date
        sr = _make_result()
        report = ReportGenerator.generate([sr])
        assert report.run_date == date.today().isoformat()

    def test_custom_run_date(self):
        sr = _make_result()
        report = ReportGenerator.generate([sr], run_date="2026-06-01")
        assert report.run_date == "2026-06-01"

    def test_notes_preserved(self):
        sr = _make_result()
        report = ReportGenerator.generate([sr], notes="pilot run")
        assert "pilot run" in report.notes


# ============================================================
# 8. ValidationReport — serialisation and persistence
# ============================================================
class TestValidationReport:
    """ValidationReport.to_dict() and .save() contract."""

    def test_to_dict_has_required_keys(self):
        sr = _make_result()
        report = ReportGenerator.generate([sr])
        d = report.to_dict()
        assert "run_date" in d
        assert "overall_metrics" in d
        assert "per_sample_results" in d
        assert "category_breakdown" in d

    def test_overall_metrics_structure(self):
        sr = _make_result(gt_weight=200.0, pred_weight=210.0)
        report = ReportGenerator.generate([sr])
        m = report.to_dict()["overall_metrics"]
        assert "mape_weight_pct" in m
        assert "mape_carb_pct" in m
        assert "pass_rate_15pct" in m
        assert "passes_threshold_15pct" in m

    def test_per_sample_has_ape_fields(self):
        sr = _make_result()
        report = ReportGenerator.generate([sr])
        sample = report.to_dict()["per_sample_results"][0]
        assert "weight_ape_pct" in sample
        assert "carb_ape_pct" in sample

    def test_save_writes_valid_json(self, tmp_path):
        """save() creates a parsable JSON file at the given path."""
        sr = _make_result()
        report = ReportGenerator.generate([sr])
        out = tmp_path / "report.json"
        report.save(out)
        assert out.exists()
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert "overall_metrics" in loaded

    def test_save_creates_parent_dirs(self, tmp_path):
        """save() creates intermediate directories if needed."""
        sr = _make_result()
        report = ReportGenerator.generate([sr])
        out = tmp_path / "nested" / "deep" / "report.json"
        report.save(out)
        assert out.exists()

    def test_serialised_mape_is_rounded(self):
        """MAPE in dict is rounded to 2 decimal places."""
        sr = _make_result(gt_weight=100.0, pred_weight=113.456789)
        report = ReportGenerator.generate([sr])
        d = report.to_dict()
        mape = d["overall_metrics"]["mape_weight_pct"]
        # Check it's a float and has at most 2 decimal places when formatted
        assert isinstance(mape, float)
        assert mape == round(mape, 2)


# ============================================================
# 9. Singleton
# ============================================================
class TestSingleton:
    """get_data_loader() returns the same instance every time."""

    def test_same_object(self):
        a = get_data_loader()
        b = get_data_loader()
        assert a is b

    def test_returns_data_loader_instance(self):
        from services.validation_service import DataLoader
        instance = get_data_loader()
        assert isinstance(instance, DataLoader)


# ============================================================
# 10. Integration — load VN demo → generate report
# ============================================================
class TestIntegrationVNDemoReport:
    """End-to-end: load GT → simulate predictions → generate report."""

    @pytest.fixture(autouse=True)
    def skip_if_missing(self):
        if not _VN_DEMO_ROOT.exists():
            pytest.skip("VN demo data not available")

    def test_report_from_gt_with_10pct_error(self):
        """
        Simulate pipeline with 10% weight error on all 5 VN demo samples.

        MAPE should be ~10% → passes threshold.
        """
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        assert len(samples) == 5

        results = []
        for gt in samples:
            sr = MetricComputer.compute_sample_result(
                gt=gt,
                pred_weight_g=gt.total_weight_g * 0.90,   # 10% under
                pred_carb_g=gt.total_carb_g * 0.90,       # 10% under
                pred_volume_ml=gt.total_weight_g * 0.90,
                pred_gl=10.0,
                pred_quality="medium",
                food_id_used=gt.food_id or "vn_com_trang",
                pipeline_time_ms=900.0,
            )
            results.append(sr)

        report = ReportGenerator.generate(results, notes="simulated 10% error")
        assert abs(report.mape_weight - 10.0) < 1e-6
        assert report.passes_threshold is True
        assert report.pass_rate_15pct == 100.0

    def test_report_fails_when_error_exceeds_15(self):
        """
        Simulate 20% weight error on all 5 samples → MAPE=20% → fails.
        """
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        results = []
        for gt in samples:
            sr = MetricComputer.compute_sample_result(
                gt=gt,
                pred_weight_g=gt.total_weight_g * 1.20,   # 20% over
                pred_carb_g=gt.total_carb_g * 1.20,
                pred_volume_ml=gt.total_weight_g * 1.20,
                pred_gl=10.0,
                pred_quality="low",
                food_id_used=gt.food_id or "vn_com_trang",
                pipeline_time_ms=900.0,
            )
            results.append(sr)

        report = ReportGenerator.generate(results)
        assert report.passes_threshold is False

    def test_all_five_samples_have_results(self):
        """Generate report should have n_total=5 for VN demo only."""
        samples = DataLoader.load_vn_demo(_VN_DEMO_ROOT)
        results = [
            MetricComputer.compute_sample_result(
                gt=gt,
                pred_weight_g=gt.total_weight_g,
                pred_carb_g=gt.total_carb_g,
                pred_volume_ml=gt.total_weight_g,
                pred_gl=15.0,
                pred_quality="high",
                food_id_used=gt.food_id or "vn_com_trang",
                pipeline_time_ms=850.0,
            )
            for gt in samples
        ]
        report = ReportGenerator.generate(results)
        assert report.n_total == 5
        assert report.n_vn_demo == 5
        assert report.n_n5k == 0

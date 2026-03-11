"""
Validation service for Vision Engine accuracy benchmarking.
Compare pipeline estimates against ground-truth weight, carb, and GL.

Task 2.6 - Validation & Benchmark

WHY a separate validation service?
────────────────────────────────────
The validation service is intentionally MODEL-FREE: it only computes
comparison metrics and loads data files. This lets it run instantly
(no GPU needed) and makes every metric function unit-testable in
isolation from the pipeline.

Actual pipeline calls happen in scripts/validate_pipeline.py which
calls the running FastAPI service and records results here.

Metrics used:
  APE  (Absolute Percentage Error) = |predicted - actual| / actual × 100
  MAPE (Mean APE) = mean(APE) across N samples

WHY MAPE instead of RMSE?
──────────────────────────
RMSE penalises large absolute errors, which would unfairly favour
lighter dishes (bánh mì 150g = small absolute error) over heavier
ones (phở 450g = large absolute error even at the same %).
MAPE treats all dishes equally on a relative scale, which is what
matters for a GL-estimation system: a 10% error on a pho bowl is
just as acceptable as a 10% error on a rice plate.

Accuracy target: MAPE ≤ 15% for weight and carb.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).parents[3]
_VN_DEMO_ROOT = _PROJECT_ROOT / "data" / "vn_demo"
_N5K_SUBSET_PATH = _PROJECT_ROOT / "data" / "nutrition5k" / "parsed" / "nutrition5k_subset.json"
_ANNOTATIONS_PATH = _PROJECT_ROOT / "data" / "annotations" / "ground_truth.json"

# ── Map food category/name to our nutrition DB food_id ────────────────────
# Used when loading VN demo samples so the pipeline endpoint gets the
# correct food_id for density factor lookup.
_CATEGORY_TO_FOOD_ID: Dict[str, str] = {
    "noodle_soup": "vn_pho_bo",          # default for soup noodles
    "bread":       "vn_banh_mi",
    "rice":        "vn_com_trang",
    "rice_broken": "vn_com_tam",
    "porridge":    "vn_chao",
    "noodle_dry":  "vn_bun_thit_nuong",
    "drink":       "vn_tra_sua",
    "mixed":       "vn_com_trang",       # fallback
}

_SAMPLE_ID_TO_FOOD_ID: Dict[str, str] = {
    "pho_bo_001":     "vn_pho_bo",
    "bun_bo_hue_001": "vn_bun_bo_hue",
    "banh_mi_001":    "vn_banh_mi",
    "com_tam_001":    "vn_com_tam",
    "com_trang_001":  "vn_com_trang",
}


# ============================================================
# Data classes
# ============================================================
@dataclass
class GroundTruth:
    """Ground truth label for one food sample."""
    sample_id: str
    source: str                       # "nutrition5k" | "vn_demo"
    food_id: Optional[str]            # Our nutrition DB ID
    food_name_en: str

    total_weight_g: float
    total_carb_g: float
    gt_gl: Optional[float]            # Ground-truth Glycemic Load (if available)
    measurement_method: str           # "lab_scale" | "estimated_from_literature"

    image_path: Optional[Path] = None  # Path to image file (if available)


@dataclass
class SampleResult:
    """Comparison between one pipeline prediction and ground truth."""
    sample_id: str
    source: str
    food_name_en: str
    measurement_method: str

    # Ground truth
    gt_weight_g: float
    gt_carb_g: float

    # Predictions
    pred_weight_g: float
    pred_carb_g: float
    pred_volume_ml: float
    pred_gl: float
    pred_quality: str

    # Errors (APE = absolute percentage error)
    weight_ape: float       # |pred - gt| / gt × 100
    carb_ape: float

    # Pipeline info
    food_id_used: str
    pipeline_time_ms: float

    # GL error (computed from pred_gl vs gt_carb-derived GL if available)
    # Optional, set by compute_sample_result when gt_gl is provided
    gl_ape: float = 0.0


@dataclass
class CategoryStats:
    """Aggregated stats for one food category."""
    category_name: str
    n_samples: int
    mean_weight_ape: float
    mean_carb_ape: float
    max_weight_ape: float
    max_carb_ape: float
    pass_rate_15pct: float          # % of samples with weight_ape ≤ 15


@dataclass
class ValidationReport:
    """Full validation report for the Vision Engine."""
    # Run info
    run_date: str
    n_total: int
    n_n5k: int
    n_vn_demo: int

    # Overall metrics
    mape_weight: float          # Mean APE for weight across all samples
    mape_carb: float            # Mean APE for carb across all samples
    mape_gl: float              # Mean APE for GL
    pass_rate_15pct: float      # % of samples with weight_ape ≤ 15

    # Per-sample results
    results: List[SampleResult]

    # Category breakdown
    by_category: List[CategoryStats] = field(default_factory=list)

    # Conclusion
    passes_threshold: bool = False   # True if mape_weight ≤ 15%
    notes: str = ""

    def to_dict(self) -> dict:
        """Serialize to plain dict for JSON export."""
        return {
            "run_date": self.run_date,
            "n_total": self.n_total,
            "n_n5k": self.n_n5k,
            "n_vn_demo": self.n_vn_demo,
            "overall_metrics": {
                "mape_weight_pct": round(self.mape_weight, 2),
                "mape_carb_pct": round(self.mape_carb, 2),
                "mape_gl_pct": round(self.mape_gl, 2),
                "pass_rate_15pct": round(self.pass_rate_15pct, 1),
                "passes_threshold_15pct": self.passes_threshold,
            },
            "category_breakdown": [
                {
                    "category": c.category_name,
                    "n_samples": c.n_samples,
                    "mape_weight_pct": round(c.mean_weight_ape, 2),
                    "mape_carb_pct": round(c.mean_carb_ape, 2),
                    "max_weight_ape_pct": round(c.max_weight_ape, 2),
                    "pass_rate_15pct": round(c.pass_rate_15pct, 1),
                }
                for c in self.by_category
            ],
            "per_sample_results": [
                {
                    "sample_id": r.sample_id,
                    "source": r.source,
                    "food": r.food_name_en,
                    "measurement_method": r.measurement_method,
                    "gt_weight_g": r.gt_weight_g,
                    "pred_weight_g": round(r.pred_weight_g, 1),
                    "weight_ape_pct": round(r.weight_ape, 1),
                    "gt_carb_g": r.gt_carb_g,
                    "pred_carb_g": round(r.pred_carb_g, 1),
                    "carb_ape_pct": round(r.carb_ape, 1),
                    "gl_ape_pct": round(r.gl_ape, 1),
                    "pred_volume_ml": round(r.pred_volume_ml, 1),
                    "pred_gl": round(r.pred_gl, 1),
                    "quality": r.pred_quality,
                    "pipeline_ms": round(r.pipeline_time_ms, 0),
                }
                for r in self.results
            ],
            "notes": self.notes,
        }

    def save(self, path: Path) -> None:
        """Save report to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info(f"Validation report saved: {path}")


# ============================================================
# MetricComputer — pure math, no model deps
# ============================================================
class MetricComputer:
    """
    Stateless metric computation.

    All methods are static — easy to unit test in isolation.
    """

    @staticmethod
    def ape(predicted: float, actual: float) -> float:
        """
        Absolute Percentage Error (APE).

        APE = |predicted - actual| / |actual| × 100

        Args:
            predicted: pipeline estimate
            actual:    ground truth value

        Returns:
            APE [%]. Returns 0.0 if actual == 0.

        WHY return 0 for zero actual?
        ──────────────────────────────
        Dividing by zero gives inf. For samples where GT carb = 0
        (e.g. pure water) the dish is not interesting for GL anyway.
        """
        if abs(actual) < 1e-9:
            return 0.0
        return abs(predicted - actual) / abs(actual) * 100.0

    @staticmethod
    def mape(ape_values: List[float]) -> float:
        """
        Mean Absolute Percentage Error.

        Returns 0.0 for empty list.
        """
        if not ape_values:
            return 0.0
        return sum(ape_values) / len(ape_values)

    @staticmethod
    def pass_rate(ape_values: List[float], threshold_pct: float = 15.0) -> float:
        """
        Fraction of samples with APE ≤ threshold_pct.

        Returns percentage (0-100).
        """
        if not ape_values:
            return 0.0
        passing = sum(1 for x in ape_values if x <= threshold_pct)
        return passing / len(ape_values) * 100.0

    @staticmethod
    def compute_sample_result(
        gt: GroundTruth,
        pred_weight_g: float,
        pred_carb_g: float,
        pred_volume_ml: float,
        pred_gl: float,
        pred_quality: str,
        food_id_used: str,
        pipeline_time_ms: float,
        gt_gl: Optional[float] = None,
    ) -> SampleResult:
        """
        Create a SampleResult from GT + pipeline predictions.

        Computes APE for weight and carb automatically.
        If gt_gl is provided, also computes GL APE.
        """
        weight_ape = MetricComputer.ape(pred_weight_g, gt.total_weight_g)
        carb_ape = MetricComputer.ape(pred_carb_g, gt.total_carb_g)
        gl_ape = MetricComputer.ape(pred_gl, gt_gl) if gt_gl is not None else 0.0

        return SampleResult(
            sample_id=gt.sample_id,
            source=gt.source,
            food_name_en=gt.food_name_en,
            measurement_method=gt.measurement_method,
            gt_weight_g=gt.total_weight_g,
            gt_carb_g=gt.total_carb_g,
            pred_weight_g=pred_weight_g,
            pred_carb_g=pred_carb_g,
            pred_volume_ml=pred_volume_ml,
            pred_gl=pred_gl,
            pred_quality=pred_quality,
            weight_ape=weight_ape,
            carb_ape=carb_ape,
            food_id_used=food_id_used,
            pipeline_time_ms=pipeline_time_ms,
            gl_ape=gl_ape,
        )


# ============================================================
# DataLoader — loads ground truth from JSON assets
# ============================================================
class DataLoader:
    """Loads GroundTruth objects from data files."""

    @staticmethod
    def load_vn_demo(root: Optional[Path] = None) -> List[GroundTruth]:
        """
        Load all VN demo samples from data/vn_demo/*.json.

        Schema assumed:
          food_info.name_en
          food_info.category
          sample.sample_id
          ground_truth.total_weight_g
          ground_truth.nutrition.total_carb_g
          ground_truth.measurement_method
          sample.images[*] — for image path resolution

        Returns sorted list by sample_id.
        """
        root = root or _VN_DEMO_ROOT
        results: List[GroundTruth] = []

        for json_path in sorted(root.rglob("*.json")):
            if "_template" in json_path.name:
                continue
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                fi = data["food_info"]
                sp = data["sample"]
                gt = data["ground_truth"]

                sample_id = sp["sample_id"]
                food_id = _SAMPLE_ID_TO_FOOD_ID.get(
                    sample_id,
                    _CATEGORY_TO_FOOD_ID.get(fi.get("category", ""), None),
                )

                # Resolve image path (prefer top_down / overhead angle)
                image_path: Optional[Path] = None
                for img in sp.get("images", []):
                    if img.get("angle") in ("top_down", "overhead"):
                        candidate = json_path.parent / img["file"]
                        if candidate.exists():
                            image_path = candidate
                            break
                # Fallback: any image
                if image_path is None:
                    for img in sp.get("images", []):
                        candidate = json_path.parent / img["file"]
                        if candidate.exists():
                            image_path = candidate
                            break

                results.append(
                    GroundTruth(
                        sample_id=sample_id,
                        source="vn_demo",
                        food_id=food_id,
                        food_name_en=fi.get("name_en", sample_id),
                        total_weight_g=float(gt["total_weight_g"]),
                        total_carb_g=float(gt["nutrition"]["total_carb_g"]),
                        gt_gl=float(data.get("nutrition_derived", {}).get("glycemic_load", 0) or 0) or None,
                        measurement_method=gt.get(
                            "measurement_method", "estimated_from_literature"
                        ),
                        image_path=image_path,
                    )
                )
            except Exception as e:
                logger.warning(f"Could not load VN demo sample {json_path}: {e}")

        logger.info(f"Loaded {len(results)} VN demo ground truth samples")
        return results

    @staticmethod
    def load_n5k_subset(path: Optional[Path] = None) -> List[GroundTruth]:
        """
        Load Nutrition5k subset from data/nutrition5k/parsed/nutrition5k_subset.json.

        N5k samples have lab-scale ground truth (highest quality).
        We use them to validate the weight + carb estimation methodology.

        Note: actual N5k images require the full dataset download.
        When images are unavailable, image_path=None and the sample is
        used for offline metric estimation only (via known-GT simulation).
        """
        path = path or _N5K_SUBSET_PATH
        results: List[GroundTruth] = []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Could not load N5k subset from {path}: {e}")
            return results

        for item in data.get("samples", []):
            try:
                fi = item["food_info"]
                sp = item["sample"]
                gt = item["ground_truth"]

                # N5k images not available locally — record path as None
                image_path = None
                n5k_images_root = path.parents[1] / "raw"
                for img in sp.get("images", []):
                    if img.get("angle") in ("overhead",):
                        candidate = n5k_images_root / img["file"]
                        if candidate.exists():
                            image_path = candidate
                            break

                # For N5k mixed dishes, use com_trang as default food_id
                category = fi.get("category", "mixed")
                food_id = _CATEGORY_TO_FOOD_ID.get(category, "vn_com_trang")

                results.append(
                    GroundTruth(
                        sample_id=sp["sample_id"],
                        source="nutrition5k",
                        food_id=food_id,
                        food_name_en=fi.get("name_en", sp["sample_id"]),
                        total_weight_g=float(gt["total_weight_g"]),
                        total_carb_g=float(gt["nutrition"]["total_carb_g"]),
                        gt_gl=None,  # N5k doesn't have pre-computed GL
                        measurement_method=gt.get(
                            "measurement_method", "lab_scale"
                        ),
                        image_path=image_path,
                    )
                )
            except Exception as e:
                logger.warning(f"Could not parse N5k sample: {e}")

        logger.info(f"Loaded {len(results)} Nutrition5k ground truth samples")
        return results


# ============================================================
# ReportGenerator
# ============================================================
class ReportGenerator:
    """
    Assemble a ValidationReport from a list of SampleResult objects.

    Separates metric computation from pipeline execution so each
    part can be tested independently.
    """

    @staticmethod
    def generate(
        results: List[SampleResult],
        run_date: str = "",
        notes: str = "",
    ) -> ValidationReport:
        """
        Build a ValidationReport from per-sample results.

        Args:
            results:   List of SampleResult (pipeline output vs GT).
            run_date:  ISO date string, e.g. "2026-03-11".
            notes:     Free-text notes for the report.

        Returns:
            ValidationReport with overall and per-category metrics.
        """
        if not run_date:
            from datetime import date
            run_date = date.today().isoformat()

        n5k = [r for r in results if r.source == "nutrition5k"]
        vn = [r for r in results if r.source == "vn_demo"]

        weight_apes = [r.weight_ape for r in results]
        carb_apes = [r.carb_ape for r in results]
        gl_apes = [r.gl_ape for r in results]

        mape_w = MetricComputer.mape(weight_apes)
        mape_c = MetricComputer.mape(carb_apes)
        mape_gl = MetricComputer.mape(gl_apes)
        pass_rate = MetricComputer.pass_rate(weight_apes, 15.0)
        passes = mape_w <= 15.0

        # Category breakdown — group by food_name_en prefix or source
        by_cat = ReportGenerator._category_breakdown(results)

        return ValidationReport(
            run_date=run_date,
            n_total=len(results),
            n_n5k=len(n5k),
            n_vn_demo=len(vn),
            mape_weight=mape_w,
            mape_carb=mape_c,
            mape_gl=mape_gl,
            pass_rate_15pct=pass_rate,
            results=results,
            by_category=by_cat,
            passes_threshold=passes,
            notes=notes,
        )

    @staticmethod
    def _category_breakdown(results: List[SampleResult]) -> List[CategoryStats]:
        """Group results by source (nutrition5k vs vn_demo) and compute stats."""
        groups: Dict[str, List[SampleResult]] = {}
        for r in results:
            groups.setdefault(r.source, []).append(r)

        stats = []
        for cat, group in sorted(groups.items()):
            wapes = [r.weight_ape for r in group]
            capes = [r.carb_ape for r in group]
            stats.append(
                CategoryStats(
                    category_name=cat,
                    n_samples=len(group),
                    mean_weight_ape=MetricComputer.mape(wapes),
                    mean_carb_ape=MetricComputer.mape(capes),
                    max_weight_ape=max(wapes) if wapes else 0.0,
                    max_carb_ape=max(capes) if capes else 0.0,
                    pass_rate_15pct=MetricComputer.pass_rate(wapes, 15.0),
                )
            )
        return stats


# ============================================================
# Singleton accessor
# ============================================================
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """Return (or create) singleton DataLoader."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader

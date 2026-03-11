#!/usr/bin/env python3
"""
validate_pipeline.py — Batch validation script for InSight Vision Engine.

Task 2.6: Runs the full pipeline on VN demo images and compares predictions
against ground-truth labels. Saves an accuracy report.

Usage:
    # Start the Vision Service first:
    #   cd src/vision-service && python main.py
    #
    # Then in a separate terminal:
    python scripts/validate_pipeline.py
    python scripts/validate_pipeline.py --host http://localhost:8000
    python scripts/validate_pipeline.py --output data/annotations/my_report.json

Dependencies: requests (pip install requests)
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path
from typing import Optional

# ── Handle running from project root ─────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src" / "vision-service"
sys.path.insert(0, str(SRC_PATH))

from services.validation_service import (
    DataLoader,
    GroundTruth,
    MetricComputer,
    ReportGenerator,
    SampleResult,
    ValidationReport,
)

try:
    import requests
except ImportError:
    print("[ERROR] requests not installed. Run: pip install requests")
    sys.exit(1)


# ── Constants ─────────────────────────────────────────────────────────────
DEFAULT_HOST = "http://localhost:8000"
DEFAULT_OUTPUT = str(
    PROJECT_ROOT / "data" / "annotations" / "validation_report.json"
)
VALIDATE_ENDPOINT = "/api/vision/validate"
HEALTH_ENDPOINT = "/health"


# ============================================================
# Pipeline caller
# ============================================================
def call_validate(
    host: str,
    image_path: Path,
    food_id: Optional[str],
    gt_weight_g: float,
    gt_carb_g: float,
    sample_id: str,
    timeout: float = 120.0,
) -> dict:
    """
    POST image + GT to /api/vision/validate.

    Returns the parsed JSON response dict.

    Raises:
        RuntimeError: if the request fails or returns non-200.
    """
    url = host.rstrip("/") + VALIDATE_ENDPOINT
    with open(image_path, "rb") as f:
        data = {
            "gt_weight_g": str(gt_weight_g),
            "gt_carb_g": str(gt_carb_g),
            "sample_id": sample_id,
        }
        if food_id:
            data["food_id"] = food_id

        resp = requests.post(
            url,
            files={"image": (image_path.name, f, "image/jpeg")},
            data=data,
            timeout=timeout,
        )

    if resp.status_code != 200:
        raise RuntimeError(
            f"HTTP {resp.status_code} from {url}: {resp.text[:400]}"
        )
    return resp.json()


# ============================================================
# Main validation loop
# ============================================================
def run_validation(
    host: str,
    output_path: Path,
    include_n5k: bool = False,
) -> ValidationReport:
    """
    Run batch validation on VN demo samples (and optionally N5k subset).

    VN demo: 5 real images with literature-based ground truth.
    N5k:     5 parsed entries — only run if images are available locally.

    Returns the completed ValidationReport.
    """
    print(f"\n{'='*60}")
    print(f"  InSight Vision Engine — Batch Validation")
    print(f"  Host  : {host}")
    print(f"  Output: {output_path}")
    print(f"{'='*60}\n")

    # ── Health check ──────────────────────────────────────────────────────
    try:
        r = requests.get(host.rstrip("/") + HEALTH_ENDPOINT, timeout=10)
        if r.status_code != 200:
            print(f"[ERROR] Service not healthy: {r.text}")
            sys.exit(1)
        health = r.json()
        print(
            f"[OK] Service UP — model={health.get('model_loaded')}, "
            f"device={health.get('device')}\n"
        )
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot reach {host}.")
        print(
            "       Start the service first: "
            "cd src/vision-service && python main.py"
        )
        sys.exit(1)

    # ── Load ground truth ─────────────────────────────────────────────────
    print("[...] Loading VN demo ground truth samples...")
    vn_samples = DataLoader.load_vn_demo()
    print(f"      Found {len(vn_samples)} VN demo samples")

    n5k_samples: list[GroundTruth] = []
    if include_n5k:
        print("[...] Loading Nutrition5k ground truth samples...")
        n5k_samples = DataLoader.load_n5k_subset()
        n5k_runnable = [s for s in n5k_samples if s.image_path is not None]
        print(
            f"      Found {len(n5k_samples)} N5k samples, "
            f"{len(n5k_runnable)} have local images"
        )
        n5k_samples = n5k_runnable  # only run those with images

    all_samples = vn_samples + n5k_samples
    runnable = [s for s in all_samples if s.image_path is not None]

    print(
        f"\n[...] Running pipeline on {len(runnable)} samples "
        f"({len(all_samples) - len(runnable)} skipped — no local image)\n"
    )

    # ── Per-sample pipeline run ───────────────────────────────────────────
    results: list[SampleResult] = []
    skipped: list[str] = []

    header = (
        f"{'Sample':<22} {'GT-W':>7} {'Pred-W':>7} {'W-APE%':>7} "
        f"{'GT-C':>7} {'Pred-C':>7} {'C-APE%':>7} {'Pass?':>6} {'ms':>6}"
    )
    sep = "-" * len(header)
    print(header)
    print(sep)

    for gt in runnable:
        if gt.image_path is None or not gt.image_path.exists():
            skipped.append(gt.sample_id)
            continue
        try:
            t0 = time.time()
            resp = call_validate(
                host=host,
                image_path=gt.image_path,
                food_id=gt.food_id,
                gt_weight_g=gt.total_weight_g,
                gt_carb_g=gt.total_carb_g,
                sample_id=gt.sample_id,
            )
            elapsed_ms = (time.time() - t0) * 1000

            sr = SampleResult(
                sample_id=resp["sample_id"] or gt.sample_id,
                source=gt.source,
                food_name_en=gt.food_name_en,
                measurement_method=gt.measurement_method,
                gt_weight_g=gt.total_weight_g,
                gt_carb_g=gt.total_carb_g,
                pred_weight_g=resp["pred_weight_g"],
                pred_carb_g=resp["pred_carb_g"],
                pred_volume_ml=resp["pred_volume_ml"],
                pred_gl=resp["pred_glycemic_load"],
                pred_quality=resp["pred_quality"],
                weight_ape=resp["weight_ape_pct"],
                carb_ape=resp["carb_ape_pct"],
                food_id_used=resp.get("food_id") or (gt.food_id or ""),
                pipeline_time_ms=resp.get("pipeline_time_ms", elapsed_ms),
                gl_ape=(
                    MetricComputer.ape(resp["pred_glycemic_load"], gt.gt_gl)
                    if gt.gt_gl is not None else 0.0
                ),
            )
            results.append(sr)

            pass_flag = "PASS" if resp["passes_15pct_threshold"] else "FAIL"
            print(
                f"{gt.sample_id:<22} "
                f"{gt.total_weight_g:>7.1f} "
                f"{resp['pred_weight_g']:>7.1f} "
                f"{resp['weight_ape_pct']:>7.1f} "
                f"{gt.total_carb_g:>7.1f} "
                f"{resp['pred_carb_g']:>7.1f} "
                f"{resp['carb_ape_pct']:>7.1f} "
                f"{pass_flag:>6} "
                f"{resp.get('pipeline_time_ms', elapsed_ms):>6.0f}"
            )

        except Exception as e:
            print(f"  [WARN] {gt.sample_id}: {e}")
            skipped.append(gt.sample_id)

    print(sep)

    if not results:
        print("[ERROR] No samples completed. Check service logs.")
        sys.exit(1)

    # ── Generate report ───────────────────────────────────────────────────
    report = ReportGenerator.generate(
        results=results,
        run_date=date.today().isoformat(),
        notes=(
            f"Batch run on {len(results)} samples. "
            f"Skipped: {skipped if skipped else 'none'}."
        ),
    )

    # ── Print summary ─────────────────────────────────────────────────────
    verdict = "PASS ✓" if report.passes_threshold else "FAIL ✗"
    print(f"\n  Overall MAPE weight : {report.mape_weight:.1f}%")
    print(f"  Overall MAPE carb   : {report.mape_carb:.1f}%")
    print(f"  Pass rate (≤15%)    : {report.pass_rate_15pct:.0f}%")
    print(f"  Threshold (≤15%)    : {verdict}")

    if report.by_category:
        print("\n  Per-category breakdown:")
        for cat in report.by_category:
            print(
                f"    {cat.category_name:<15} "
                f"n={cat.n_samples}  "
                f"MAPE_W={cat.mean_weight_ape:.1f}%  "
                f"MAPE_C={cat.mean_carb_ape:.1f}%  "
                f"pass_rate={cat.pass_rate_15pct:.0f}%"
            )

    # ── Save report ───────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.save(output_path)
    print(f"\n[OK] Report saved: {output_path}")

    return report


# ============================================================
# CLI entry point
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="InSight Vision Engine — Batch validation script"
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"FastAPI service URL (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output JSON report path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--include-n5k",
        action="store_true",
        default=False,
        help="Include Nutrition5k samples that have local images",
    )
    args = parser.parse_args()

    report = run_validation(
        host=args.host,
        output_path=Path(args.output),
        include_n5k=args.include_n5k,
    )

    # Exit code 0 if passes threshold, 1 if not
    sys.exit(0 if report.passes_threshold else 1)


if __name__ == "__main__":
    main()

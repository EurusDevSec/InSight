#!/usr/bin/env python3
"""
Benchmark all Vietnamese demo dishes through the full Gateway pipeline.

Sends each vn_demo image through POST /api/gateway/analyze and compares
predicted values against ground-truth annotations.

Usage:
    python scripts/benchmark_vn_dishes.py [--gateway http://localhost:8080]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────

VN_DEMO_DIR = Path(__file__).parent.parent / "data" / "vn_demo"

# Food ID mapping (sample folder name → nutrition DB id)
FOOD_ID_MAP = {
    "pho_bo": "vn_pho_bo",
    "com_trang": "vn_com_trang",
    "com_tam": "vn_com_tam",
    "bun_bo_hue": "vn_bun_bo_hue",
    "banh_mi": "vn_banh_mi",
}

# Default patient context for benchmark (consistent across dishes)
PATIENT_CTX = {
    "glucose_level": 120,
    "diabetes_type": "type_2",
    "insulin_carb_ratio": 10,
    "correction_factor": 50,
    "target_glucose": 100,
}


def ape(predicted: float, actual: float) -> float:
    """Absolute Percentage Error."""
    if actual == 0:
        return 0.0 if predicted == 0 else 100.0
    return abs(predicted - actual) / actual * 100


def discover_samples() -> list[dict]:
    """Discover all sample folders under vn_demo."""
    samples = []
    for food_dir in sorted(VN_DEMO_DIR.iterdir()):
        if not food_dir.is_dir() or food_dir.name.startswith("_"):
            continue
        for sample_dir in sorted(food_dir.iterdir()):
            if not sample_dir.is_dir():
                continue
            json_file = sample_dir / f"{sample_dir.name}.json"
            top_img = sample_dir / f"{sample_dir.name}_top.jpg"
            if json_file.exists() and top_img.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    gt = json.load(f)
                samples.append({
                    "sample_id": sample_dir.name,
                    "food_dir": food_dir.name,
                    "food_id": FOOD_ID_MAP.get(food_dir.name),
                    "image_path": top_img,
                    "gt": gt,
                })
    return samples


def run_benchmark(gateway_url: str) -> None:
    """Run full pipeline benchmark against Gateway."""
    samples = discover_samples()
    if not samples:
        print("No samples found in", VN_DEMO_DIR)
        sys.exit(1)

    print(f"\n{'='*80}")
    print(f"InSight Full-Pipeline Benchmark — {len(samples)} dishes")
    print(f"Gateway: {gateway_url}")
    print(f"{'='*80}\n")

    results = []
    total_time = 0

    for s in samples:
        gt = s["gt"]
        gt_weight = gt["ground_truth"]["total_weight_g"]
        gt_carb = gt["ground_truth"]["nutrition"]["total_carb_g"]
        gt_gl = gt["nutrition_derived"]["glycemic_load"]
        food_name_vi = gt["food_info"]["name_vi"]

        print(f"  ▸ {s['sample_id']:20s} ({food_name_vi}) ...", end=" ", flush=True)

        with open(s["image_path"], "rb") as img:
            files = {"image": (s["image_path"].name, img, "image/jpeg")}
            data = {**PATIENT_CTX}
            if s["food_id"]:
                data["food_id"] = s["food_id"]

            t0 = time.time()
            try:
                resp = requests.post(
                    f"{gateway_url}/api/gateway/analyze",
                    files=files,
                    data=data,
                    timeout=30,
                )
                elapsed = (time.time() - t0) * 1000
                total_time += elapsed

                if resp.status_code != 200:
                    print(f"FAIL ({resp.status_code})")
                    results.append({**s, "status": "error", "error": resp.text[:100]})
                    continue

                r = resp.json()
                pred_weight = r.get("weight_g", 0)
                pred_carb = r.get("carbs_g", 0)
                pred_gl = r.get("glycemic_load", 0)
                pred_vol = r.get("volume_ml", 0)
                advice = r.get("advice", "")
                insulin = r.get("insulin_suggestion", "")
                pipeline_ms = r.get("pipeline_time_ms", elapsed)

                w_ape = ape(pred_weight, gt_weight)
                c_ape = ape(pred_carb, gt_carb)
                gl_ape = ape(pred_gl, gt_gl)

                results.append({
                    "sample_id": s["sample_id"],
                    "food_vi": food_name_vi,
                    "status": "ok",
                    "gt_weight": gt_weight,
                    "pred_weight": pred_weight,
                    "weight_ape": w_ape,
                    "gt_carb": gt_carb,
                    "pred_carb": pred_carb,
                    "carb_ape": c_ape,
                    "gt_gl": gt_gl,
                    "pred_gl": pred_gl,
                    "gl_ape": gl_ape,
                    "volume_ml": pred_vol,
                    "pipeline_ms": pipeline_ms,
                    "has_advice": bool(advice),
                    "has_insulin": bool(insulin),
                    "confidence": r.get("confidence", 0),
                })

                status = "✓" if w_ape <= 15 and c_ape <= 15 else "✗"
                print(f"{status}  W:{pred_weight:.0f}g(APE={w_ape:.0f}%)  "
                      f"C:{pred_carb:.1f}g(APE={c_ape:.0f}%)  "
                      f"GL:{pred_gl:.1f}(APE={gl_ape:.0f}%)  {pipeline_ms:.0f}ms")

            except requests.exceptions.ConnectionError:
                print("FAIL (connection refused)")
                results.append({**s, "status": "error", "error": "connection refused"})
            except Exception as e:
                print(f"FAIL ({e})")
                results.append({**s, "status": "error", "error": str(e)[:100]})

    # ── Summary ────────────────────────────────────────────────────
    ok_results = [r for r in results if r.get("status") == "ok"]
    if not ok_results:
        print("\n  No successful results to summarize.")
        return

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"  Dishes tested:    {len(samples)}")
    print(f"  Successful:       {len(ok_results)}")
    print(f"  Failed:           {len(results) - len(ok_results)}")

    avg_w = sum(r["weight_ape"] for r in ok_results) / len(ok_results)
    avg_c = sum(r["carb_ape"] for r in ok_results) / len(ok_results)
    avg_gl = sum(r["gl_ape"] for r in ok_results) / len(ok_results)
    avg_ms = sum(r["pipeline_ms"] for r in ok_results) / len(ok_results)
    p95_ms = sorted(r["pipeline_ms"] for r in ok_results)[int(len(ok_results) * 0.95)]
    has_rag = sum(1 for r in ok_results if r["has_advice"])

    print(f"\n  MAPE Weight:      {avg_w:.1f}%  (target ≤15%)")
    print(f"  MAPE Carb:        {avg_c:.1f}%  (target ≤15%)")
    print(f"  MAPE GL:          {avg_gl:.1f}%")
    print(f"  Avg latency:      {avg_ms:.0f}ms")
    print(f"  P95 latency:      {p95_ms:.0f}ms  (target ≤2000ms)")
    print(f"  RAG advice:       {has_rag}/{len(ok_results)} dishes")
    w_pass = "PASS ✓" if avg_w <= 15 else "FAIL ✗"
    c_pass = "PASS ✓" if avg_c <= 15 else "FAIL ✗"
    lat_pass = "PASS ✓" if p95_ms <= 2000 else "FAIL ✗"
    print(f"\n  KPI Weight MAPE:  {w_pass}")
    print(f"  KPI Carb MAPE:    {c_pass}")
    print(f"  KPI P95 Latency:  {lat_pass}")

    # ── Detail table ──────────────────────────────────────────────
    print(f"\n{'─'*80}")
    print(f"  {'Dish':<20} {'GT_W':>6} {'Pred_W':>7} {'W_APE':>6} "
          f"{'GT_C':>6} {'Pred_C':>7} {'C_APE':>6} "
          f"{'GT_GL':>6} {'Pred_GL':>8} {'GL_APE':>7} {'ms':>6}")
    print(f"  {'─'*20} {'─'*6} {'─'*7} {'─'*6} {'─'*6} {'─'*7} {'─'*6} {'─'*6} {'─'*8} {'─'*7} {'─'*6}")
    for r in ok_results:
        print(f"  {r['food_vi']:<20} {r['gt_weight']:>6.0f} {r['pred_weight']:>7.1f} "
              f"{r['weight_ape']:>5.1f}% {r['gt_carb']:>6.1f} {r['pred_carb']:>7.1f} "
              f"{r['carb_ape']:>5.1f}% {r['gt_gl']:>6.1f} {r['pred_gl']:>8.1f} "
              f"{r['gl_ape']:>6.1f}% {r['pipeline_ms']:>6.0f}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark VN dishes")
    parser.add_argument("--gateway", default="http://localhost:8080",
                        help="Gateway base URL")
    args = parser.parse_args()
    run_benchmark(args.gateway)

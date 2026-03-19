#!/usr/bin/env python3
"""
Real-world patient scenario testing for InSight.

Tests the FULL pipeline (Gateway → Vision → RAG) with:
1. All 5 demo dishes × 2 angles = 10 image tests
2. Different patient contexts (high/normal glucose, type 1/2)
3. Custom food ("Khác") feature
4. Compares against ground truth
5. Generates accuracy report

Usage:
    python scripts/test_patient_scenarios.py
    python scripts/test_patient_scenarios.py --dish com_tam
    python scripts/test_patient_scenarios.py --scenario high_glucose
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass

import requests

GATEWAY_URL = "http://localhost:8080"
DATA_DIR = "data/vn_demo"

# ── Ground truth for each demo dish ──────────────────────────────
GROUND_TRUTH = {
    "com_tam": {
        "food_id": "Cơm tấm",
        "weight_g": 250,
        "carbs_g": 67.5,
        "gl": 47.3,
        "tolerance": {"weight": 0.40, "carbs": 0.40, "gl": 0.40},
    },
    "com_trang": {
        "food_id": "Cơm trắng",
        "weight_g": 200,
        "carbs_g": 56.4,
        "gl": 41.2,
        "tolerance": {"weight": 0.40, "carbs": 0.40, "gl": 0.40},
    },
    "pho_bo": {
        "food_id": "Phở bò",
        "weight_g": 450,
        "carbs_g": 45.0,
        "gl": 20.7,
        "tolerance": {"weight": 0.50, "carbs": 0.50, "gl": 0.50},
    },
    "bun_bo_hue": {
        "food_id": "Bún bò",
        "weight_g": 500,
        "carbs_g": 50.0,
        "gl": 29.0,
        "tolerance": {"weight": 0.50, "carbs": 0.50, "gl": 0.50},
    },
    "banh_mi": {
        "food_id": "Bánh mì",
        "weight_g": 150,
        "carbs_g": 75.9,
        "gl": 60.7,
        "tolerance": {"weight": 0.50, "carbs": 0.50, "gl": 0.50},
    },
}

# ── Patient scenarios ────────────────────────────────────────────
PATIENT_SCENARIOS = {
    "normal": {
        "name": "Bệnh nhân Type 2 — glucose bình thường",
        "params": {
            "glucose_level": "120",
            "diabetes_type": "type_2",
            "insulin_carb_ratio": "10",
            "correction_factor": "50",
            "target_glucose": "100",
        },
    },
    "high_glucose": {
        "name": "Bệnh nhân Type 2 — glucose CAO (cần correction)",
        "params": {
            "glucose_level": "250",
            "diabetes_type": "type_2",
            "insulin_carb_ratio": "10",
            "correction_factor": "50",
            "target_glucose": "100",
        },
    },
    "type1": {
        "name": "Bệnh nhân Type 1 — ICR nhạy",
        "params": {
            "glucose_level": "140",
            "diabetes_type": "type_1",
            "insulin_carb_ratio": "8",
            "correction_factor": "40",
            "target_glucose": "110",
        },
    },
    "low_glucose": {
        "name": "Bệnh nhân Type 2 — glucose THẤP (hạ đường huyết)",
        "params": {
            "glucose_level": "60",
            "diabetes_type": "type_2",
            "insulin_carb_ratio": "10",
            "correction_factor": "50",
            "target_glucose": "100",
        },
    },
}


@dataclass
class TestResult:
    dish: str
    angle: str
    scenario: str
    food_id_sent: str
    food_name_returned: str
    volume_ml: float
    weight_g: float
    carbs_g: float
    gl: float
    gl_level: str
    confidence: float
    insulin: str
    advice_snippet: str
    warnings: list
    pipeline_ms: int
    vision_ms: int
    rag_ms: int
    # Accuracy vs ground truth
    weight_error_pct: float | None
    carbs_error_pct: float | None
    gl_error_pct: float | None
    weight_pass: bool | None
    carbs_pass: bool | None
    gl_pass: bool | None
    error: str | None = None


def call_pipeline(image_path: str, food_id: str | None, custom_food_name: str | None,
                  patient_params: dict) -> dict:
    """Call the Gateway pipeline endpoint."""
    with open(image_path, "rb") as f:
        files = {"image": ("test.jpg", f, "image/jpeg")}
        data = {**patient_params, "debug": "false"}
        if food_id:
            data["food_id"] = food_id
        if custom_food_name:
            data["custom_food_name"] = custom_food_name
        resp = requests.post(f"{GATEWAY_URL}/api/gateway/analyze",
                             files=files, data=data, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json()


def evaluate(dish: str, angle: str, scenario: str, result: dict,
             food_id_sent: str) -> TestResult:
    """Compare pipeline result against ground truth."""
    gt = GROUND_TRUTH.get(dish)

    weight_g = result.get("weight_g", 0)
    carbs_g = result.get("carbs_g", 0)
    gl = result.get("glycemic_load", 0)

    weight_err = carbs_err = gl_err = None
    weight_pass = carbs_pass = gl_pass = None

    if gt:
        if gt["weight_g"] > 0:
            weight_err = abs(weight_g - gt["weight_g"]) / gt["weight_g"]
            weight_pass = weight_err <= gt["tolerance"]["weight"]
        if gt["carbs_g"] > 0:
            carbs_err = abs(carbs_g - gt["carbs_g"]) / gt["carbs_g"]
            carbs_pass = carbs_err <= gt["tolerance"]["carbs"]
        if gt["gl"] > 0:
            gl_err = abs(gl - gt["gl"]) / gt["gl"]
            gl_pass = gl_err <= gt["tolerance"]["gl"]

    advice = result.get("advice") or ""
    advice_snippet = advice[:100] + "..." if len(advice) > 100 else advice

    return TestResult(
        dish=dish,
        angle=angle,
        scenario=scenario,
        food_id_sent=food_id_sent,
        food_name_returned=result.get("food_name", "?"),
        volume_ml=result.get("volume_ml", 0),
        weight_g=weight_g,
        carbs_g=carbs_g,
        gl=gl,
        gl_level=result.get("gl_level", "?"),
        confidence=result.get("confidence", 0),
        insulin=result.get("insulin_suggestion") or "N/A",
        advice_snippet=advice_snippet,
        warnings=result.get("warnings", []),
        pipeline_ms=result.get("pipeline_time_ms", 0),
        vision_ms=result.get("vision_time_ms", 0),
        rag_ms=result.get("rag_time_ms", 0),
        weight_error_pct=weight_err,
        carbs_error_pct=carbs_err,
        gl_error_pct=gl_err,
        weight_pass=weight_pass,
        carbs_pass=carbs_pass,
        gl_pass=gl_pass,
    )


def run_dish_test(dish: str, scenario_key: str, results: list) -> None:
    """Test one dish with both angles."""
    gt = GROUND_TRUTH[dish]
    scenario = PATIENT_SCENARIOS[scenario_key]
    folder = os.path.join(DATA_DIR, dish, f"{dish}_001")

    for suffix, angle in [("_45.jpg", "45°"), ("_top.jpg", "top")]:
        img_path = os.path.join(folder, f"{dish}_001{suffix}")
        if not os.path.exists(img_path):
            print(f"  ⚠ Skipped: {img_path} not found")
            continue

        try:
            print(f"  📸 {dish} ({angle}) + {scenario_key}...", end=" ", flush=True)
            t0 = time.time()
            result = call_pipeline(img_path, gt["food_id"], None, scenario["params"])
            elapsed = time.time() - t0

            tr = evaluate(dish, angle, scenario_key, result, gt["food_id"])
            results.append(tr)

            status = "✅" if all(x is not False for x in [tr.weight_pass, tr.carbs_pass, tr.gl_pass]) else "⚠️"
            print(f"{status} {elapsed:.1f}s | Vol={tr.volume_ml:.0f}mL Weight={tr.weight_g:.0f}g "
                  f"Carbs={tr.carbs_g:.0f}g GL={tr.gl:.1f} ({tr.gl_level})")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(TestResult(
                dish=dish, angle=angle, scenario=scenario_key,
                food_id_sent=gt["food_id"], food_name_returned="?",
                volume_ml=0, weight_g=0, carbs_g=0, gl=0, gl_level="?",
                confidence=0, insulin="?", advice_snippet="", warnings=[],
                pipeline_ms=0, vision_ms=0, rag_ms=0,
                weight_error_pct=None, carbs_error_pct=None, gl_error_pct=None,
                weight_pass=None, carbs_pass=None, gl_pass=None,
                error=str(e),
            ))


def run_custom_food_test(results: list) -> None:
    """Test 'Khác' with custom food name."""
    print("\n" + "=" * 70)
    print("  TEST: Custom Food ('Khác' + tên món tùy chỉnh)")
    print("=" * 70)

    # Use com_tam image but pretend it's "Bún đậu mắm tôm"
    img_path = os.path.join(DATA_DIR, "com_tam/com_tam_001/com_tam_001_45.jpg")
    scenario = PATIENT_SCENARIOS["normal"]

    custom_foods = [
        "Bún đậu mắm tôm",
        "Bánh tráng trộn",
        "Cơm gà Hải Nam",
    ]

    for custom_name in custom_foods:
        try:
            print(f"  🆕 Khác → '{custom_name}'...", end=" ", flush=True)
            t0 = time.time()
            result = call_pipeline(img_path, "Khác", custom_name, scenario["params"])
            elapsed = time.time() - t0

            food_name = result.get("food_name", "?")
            gl = result.get("glycemic_load", 0)
            advice = result.get("advice") or ""
            has_custom_name = custom_name.lower() in advice.lower() or custom_name in food_name

            print(f"{'✅' if has_custom_name else '⚠️'} {elapsed:.1f}s | "
                  f"food_name='{food_name}' GL={gl:.1f}")
            if has_custom_name:
                print(f"    ✅ Custom name '{custom_name}' appears in advice/response")
            else:
                print(f"    ⚠️ Custom name '{custom_name}' NOT found in response — "
                      f"food_name returned: '{food_name}'")
            print(f"    Advice: {advice[:120]}...")

        except Exception as e:
            print(f"❌ ERROR: {e}")


def run_safety_tests(results: list) -> None:
    """Verify safety checks work properly."""
    print("\n" + "=" * 70)
    print("  TEST: Safety Checks")
    print("=" * 70)

    img_path = os.path.join(DATA_DIR, "com_tam/com_tam_001/com_tam_001_45.jpg")

    # Test 1: Very high glucose → should trigger correction dose
    print("  🔴 High glucose (250 mg/dL) — expect correction dose...", end=" ", flush=True)
    try:
        result = call_pipeline(img_path, "Cơm tấm", None, {
            "glucose_level": "250",
            "diabetes_type": "type_2",
            "insulin_carb_ratio": "10",
            "correction_factor": "50",
            "target_glucose": "100",
        })
        insulin = result.get("insulin_suggestion") or ""
        warnings = result.get("warnings", [])
        has_correction = "correction" in insulin.lower() or float(insulin.split(" ")[0]) > 3 if insulin not in ("N/A", "") else False
        print(f"{'✅' if has_correction else '⚠️'} Insulin: {insulin[:80]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Test 2: Very low glucose → should NOT suggest insulin or warn
    print("  🟡 Low glucose (60 mg/dL) — expect low glucose warning...", end=" ", flush=True)
    try:
        result = call_pipeline(img_path, "Cơm tấm", None, {
            "glucose_level": "60",
            "diabetes_type": "type_2",
            "insulin_carb_ratio": "10",
            "correction_factor": "50",
            "target_glucose": "100",
        })
        advice = result.get("advice") or ""
        warnings = result.get("warnings", [])
        has_hypo_warning = any(kw in advice.lower() for kw in ["hạ đường", "hypo", "thấp", "nguy hiểm", "60"])
        print(f"{'✅' if has_hypo_warning else '⚠️'}")
        if has_hypo_warning:
            print(f"    ✅ Low glucose addressed in advice")
        else:
            print(f"    ⚠️ Advice may not address hypoglycemia risk")
        print(f"    Advice: {advice[:120]}...")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def print_report(results: list[TestResult]) -> None:
    """Print summary report."""
    print("\n" + "=" * 70)
    print("  📊 ACCURACY REPORT")
    print("=" * 70)

    valid = [r for r in results if r.error is None]
    if not valid:
        print("  No valid results.")
        return

    # Per-dish accuracy
    print(f"\n  {'Dish':<15} {'Angle':<6} {'Scenario':<14} "
          f"{'Weight':>8} {'Carbs':>8} {'GL':>8} {'Time':>7}")
    print("  " + "-" * 68)

    for r in valid:
        def fmt_err(err, passed):
            if err is None:
                return "  N/A  "
            symbol = "✅" if passed else "❌"
            return f"{symbol}{err*100:5.1f}%"

        print(f"  {r.dish:<15} {r.angle:<6} {r.scenario:<14} "
              f"{fmt_err(r.weight_error_pct, r.weight_pass):>8} "
              f"{fmt_err(r.carbs_error_pct, r.carbs_pass):>8} "
              f"{fmt_err(r.gl_error_pct, r.gl_pass):>8} "
              f"{r.pipeline_ms:>5}ms")

    # Summary stats
    weight_tests = [r for r in valid if r.weight_pass is not None]
    carbs_tests = [r for r in valid if r.carbs_pass is not None]
    gl_tests = [r for r in valid if r.gl_pass is not None]

    print("\n  ── Summary ──")
    if weight_tests:
        w_pass = sum(1 for r in weight_tests if r.weight_pass)
        w_avg_err = sum(r.weight_error_pct for r in weight_tests) / len(weight_tests)
        print(f"  Weight: {w_pass}/{len(weight_tests)} passed | avg error {w_avg_err*100:.1f}%")
    if carbs_tests:
        c_pass = sum(1 for r in carbs_tests if r.carbs_pass)
        c_avg_err = sum(r.carbs_error_pct for r in carbs_tests) / len(carbs_tests)
        print(f"  Carbs:  {c_pass}/{len(carbs_tests)} passed | avg error {c_avg_err*100:.1f}%")
    if gl_tests:
        g_pass = sum(1 for r in gl_tests if r.gl_pass)
        g_avg_err = sum(r.gl_error_pct for r in gl_tests) / len(gl_tests)
        print(f"  GL:     {g_pass}/{len(gl_tests)} passed | avg error {g_avg_err*100:.1f}%")

    # Performance
    avg_pipeline = sum(r.pipeline_ms for r in valid) / len(valid)
    avg_vision = sum(r.vision_ms for r in valid) / len(valid)
    avg_rag = sum(r.rag_ms for r in valid) / len(valid)
    print(f"\n  ── Performance ──")
    print(f"  Avg pipeline: {avg_pipeline:.0f}ms (vision={avg_vision:.0f}ms, rag={avg_rag:.0f}ms)")

    # Warnings summary
    all_warnings = []
    for r in valid:
        all_warnings.extend(r.warnings)
    if all_warnings:
        print(f"\n  ── Warnings ({len(all_warnings)} total) ──")
        for w in set(all_warnings):
            count = all_warnings.count(w)
            print(f"  [{count}x] {w[:100]}")


def main():
    parser = argparse.ArgumentParser(description="Patient scenario testing")
    parser.add_argument("--dish", help="Test specific dish only (e.g. com_tam)")
    parser.add_argument("--scenario", default="normal",
                        help="Patient scenario: normal, high_glucose, type1, low_glucose, all")
    parser.add_argument("--skip-custom", action="store_true", help="Skip custom food test")
    parser.add_argument("--skip-safety", action="store_true", help="Skip safety tests")
    args = parser.parse_args()

    # Health check
    try:
        resp = requests.get(f"{GATEWAY_URL}/api/health", timeout=5)
        if resp.status_code != 200:
            print("❌ Gateway not healthy!")
            sys.exit(1)
    except requests.ConnectionError:
        print("❌ Gateway not reachable at", GATEWAY_URL)
        sys.exit(1)

    print("=" * 70)
    print("  🏥 InSight Patient Scenario Testing")
    print("=" * 70)
    print(f"  Gateway: {GATEWAY_URL}")
    print()

    dishes = [args.dish] if args.dish else list(GROUND_TRUTH.keys())
    scenarios = list(PATIENT_SCENARIOS.keys()) if args.scenario == "all" else [args.scenario]

    results: list[TestResult] = []

    for scenario_key in scenarios:
        scenario = PATIENT_SCENARIOS[scenario_key]
        print(f"\n{'=' * 70}")
        print(f"  🧑‍⚕️ Scenario: {scenario['name']}")
        print(f"  Params: glucose={scenario['params']['glucose_level']}mg/dL, "
              f"type={scenario['params']['diabetes_type']}, "
              f"ICR=1:{scenario['params']['insulin_carb_ratio']}")
        print("=" * 70)

        for dish in dishes:
            run_dish_test(dish, scenario_key, results)

    if not args.skip_custom:
        run_custom_food_test(results)

    if not args.skip_safety:
        run_safety_tests(results)

    print_report(results)

    # Suggest improvements based on results
    valid = [r for r in results if r.error is None]
    issues = []
    for r in valid:
        if r.weight_pass is False:
            issues.append(f"{r.dish} ({r.angle}): weight error {r.weight_error_pct*100:.0f}%")
        if r.carbs_pass is False:
            issues.append(f"{r.dish} ({r.angle}): carbs error {r.carbs_error_pct*100:.0f}%")
        if r.gl_pass is False:
            issues.append(f"{r.dish} ({r.angle}): GL error {r.gl_error_pct*100:.0f}%")

    if issues:
        print(f"\n  ⚠️ Issues to investigate ({len(issues)}):")
        for i in issues:
            print(f"    - {i}")
    else:
        print("\n  🎉 All tests within tolerance!")


if __name__ == "__main__":
    main()

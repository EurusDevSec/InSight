"""Quick E2E test for all Vision Service endpoints."""
import json
import sys
import requests

BASE_URL = "http://localhost:8000"
IMAGE_PATH = "data/poc/raw/poc_pho_bo_001_main.jpg"


def test_health():
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    resp = requests.get(f"{BASE_URL}/health")
    data = resp.json()
    print(json.dumps(data, indent=2))
    assert data["status"] == "UP"
    assert data["model_loaded"] is True
    print("PASSED\n")
    return data


def test_depth():
    print("=" * 60)
    print("TEST 2: Depth Estimation")
    print("=" * 60)
    with open(IMAGE_PATH, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/api/vision/depth",
            files={"image": ("test.jpg", f, "image/jpeg")},
        )
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Inference time: {data['inference_time_ms']:.0f}ms")
    print(f"  Image size: {data['image_size']}")
    print(f"  Depth stats: {json.dumps(data['depth_stats'], indent=4)}")
    print(f"  Base64 length: {len(data['depth_map_base64'])} chars")
    assert resp.status_code == 200
    assert data["inference_time_ms"] > 0
    assert len(data["depth_map_base64"]) > 0
    print("PASSED\n")
    return data


def test_reference():
    print("=" * 60)
    print("TEST 3: Reference Object Detection")
    print("=" * 60)
    with open(IMAGE_PATH, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/api/vision/detect-reference",
            files={"image": ("test.jpg", f, "image/jpeg")},
        )
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Total detected: {data['total_detected']}")
    print(f"  Model type: {data['model_type']}")
    print(f"  Best scale factor: {data['best_scale_factor']}")
    for obj in data["objects"]:
        print(f"  - {obj['class_name']}: conf={obj['confidence']:.3f}")
        print(f"    real: {obj['real_width_cm']}cm x {obj['real_height_cm']}cm")
        print(f"    scale: {obj['pixels_per_cm']:.2f} px/cm")
    assert resp.status_code == 200
    print("PASSED\n")
    return data


def test_depth_invalid():
    print("=" * 60)
    print("TEST 4: Depth — Invalid File Type")
    print("=" * 60)
    resp = requests.post(
        f"{BASE_URL}/api/vision/depth",
        files={"image": ("test.txt", b"not an image", "text/plain")},
    )
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.json()}")
    assert resp.status_code == 400
    print("PASSED\n")


def main():
    print("\n" + "=" * 60)
    print("   InSight Vision Service — E2E Endpoint Tests")
    print("=" * 60 + "\n")

    try:
        health = test_health()
        depth = test_depth()
        ref = test_reference()
        test_depth_invalid()

        print("=" * 60)
        print("   ALL TESTS PASSED!")
        print("=" * 60)
        print(f"\n  Summary:")
        print(f"  - Health: {health['status']}, device={health['device']}")
        print(f"  - Depth: {depth['inference_time_ms']:.0f}ms inference")
        print(f"  - Reference: {ref['total_detected']} objects detected ({ref['model_type']})")
        print(f"  - Error handling: Invalid file type returns 400")

    except requests.ConnectionError:
        print("ERROR: Cannot connect to server at localhost:8000")
        print("Make sure service is running: python src/vision-service/main.py")
        sys.exit(1)
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
POC: Test Depth Anything V2 với ảnh mẫu
Chạy: python scripts/poc_depth_test.py <image_path>

Ví dụ:
    python scripts/poc_depth_test.py data/poc/raw/poc_pho_bo_001_main.jpg
"""

import sys
from pathlib import Path


def test_depth_estimation(image_path: str, output_dir: str = "data/poc/depth_output"):
    print("🔄 Loading Depth Anything V2...")

    try:
        import torch
        from transformers import pipeline
        from PIL import Image

        # Kiểm tra file tồn tại
        if not Path(image_path).exists():
            print(f"❌ Không tìm thấy file: {image_path}")
            return False

        # Tạo output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Detect device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖥️  Device: {device.upper()}")

        # Load model (sẽ download lần đầu ~350MB)
        print("📦 Loading model (có thể mất vài phút lần đầu)...")
        pipe = pipeline(
            task="depth-estimation",
            model="depth-anything/Depth-Anything-V2-Small-hf",
            device=device,
        )

        print("✅ Model loaded successfully!")

        # Load image
        image = Image.open(image_path).convert("RGB")
        print(f"📷 Input image: {image.size[0]}x{image.size[1]}")

        # Run inference
        print("🔄 Running depth estimation...")
        result = pipe(image)

        depth_map = result["depth"]
        print(f"✅ Depth map generated: {depth_map.size}")

        # Save output
        input_name = Path(image_path).stem
        output_path = Path(output_dir) / f"{input_name}_depth.png"
        depth_map.save(output_path)
        print(f"💾 Saved depth map to: {output_path}")

        # Hiển thị thông tin thêm
        print("\n📊 Depth map statistics:")
        import numpy as np

        depth_array = np.array(depth_map)
        print(f"   - Min value: {depth_array.min()}")
        print(f"   - Max value: {depth_array.max()}")
        print(f"   - Mean value: {depth_array.mean():.2f}")

        print("\n✅ POC Depth Test PASSED!")
        return True

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Cài đặt dependencies:")
        print("   pip install torch torchvision transformers pillow")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/poc_depth_test.py <image_path>")
        print("")
        print("Ví dụ:")
        print("  python scripts/poc_depth_test.py data/poc/raw/poc_pho_bo_001_main.jpg")
        print("")
        print("Yêu cầu:")
        print("  pip install torch torchvision transformers pillow")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "data/poc/depth_output"

    success = test_depth_estimation(image_path, output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

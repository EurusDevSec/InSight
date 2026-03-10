"""
Train YOLOv8 to detect Vietnamese tableware (bowls, spoons, chopsticks).
Fine-tune from YOLOv8s pretrained on COCO.

Task 2.2 - Reference Object Detection (Plan A: Custom Training)

Usage:
  python scripts/train_reference_detector.py
  python scripts/train_reference_detector.py --epochs 50 --batch 8

Requirements:
  pip install ultralytics
  Dataset must be prepared at data/poc/annotations/ in YOLO format.
"""

import argparse
from pathlib import Path

from ultralytics import YOLO


def train_reference_detector(
    dataset_yaml: str = "data/poc/annotations/dataset.yaml",
    model_variant: str = "yolov8s.pt",
    epochs: int = 100,
    img_size: int = 640,
    batch_size: int = 16,
    project: str = "runs/reference_detector",
    name: str = "v1",
):
    """
    Fine-tune YOLOv8 for Vietnamese tableware detection.

    Pretrained YOLOv8s already knows "bowl" (COCO 45) and "spoon" (COCO 44).
    Fine-tuning adds specific Vietnamese classes (bat_com, bat_pho_m, etc.)
    """
    print(f"Loading pretrained model: {model_variant}")
    model = YOLO(model_variant)

    print(f"Starting training...")
    print(f"  Dataset: {dataset_yaml}")
    print(f"  Epochs: {epochs}")
    print(f"  Image size: {img_size}")
    print(f"  Batch size: {batch_size}")

    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        project=project,
        name=name,
        # Augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        mosaic=1.0,
        # Training params
        patience=20,
        save=True,
        save_period=10,
        val=True,
        plots=True,
        verbose=True,
    )

    # Best model path
    best_model = Path(project) / name / "weights" / "best.pt"
    print(f"\nTraining complete!")
    print(f"  Best model: {best_model}")

    return best_model


def evaluate_model(model_path: str, dataset_yaml: str):
    """Evaluate trained model on validation set."""
    model = YOLO(model_path)
    results = model.val(data=dataset_yaml)

    print(f"\nEvaluation Results:")
    for key, value in results.results_dict.items():
        print(f"  {key}: {value}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 for Vietnamese tableware detection"
    )
    parser.add_argument(
        "--dataset",
        default="data/poc/annotations/dataset.yaml",
        help="Path to YOLO dataset YAML",
    )
    parser.add_argument(
        "--model", default="yolov8s.pt", help="Pretrained model"
    )
    parser.add_argument(
        "--epochs", type=int, default=100, help="Training epochs"
    )
    parser.add_argument(
        "--batch", type=int, default=16, help="Batch size"
    )
    parser.add_argument(
        "--img-size", type=int, default=640, help="Image size"
    )
    parser.add_argument(
        "--project",
        default="runs/reference_detector",
        help="Output project directory",
    )
    parser.add_argument(
        "--name", default="v1", help="Run name"
    )

    args = parser.parse_args()

    best_model = train_reference_detector(
        dataset_yaml=args.dataset,
        model_variant=args.model,
        epochs=args.epochs,
        img_size=args.img_size,
        batch_size=args.batch,
        project=args.project,
        name=args.name,
    )

    if best_model.exists():
        evaluate_model(str(best_model), args.dataset)
    else:
        print(f"Warning: Best model not found at {best_model}")


if __name__ == "__main__":
    main()

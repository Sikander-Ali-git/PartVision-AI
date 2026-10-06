#!/usr/bin/env python3
"""
scripts/predict.py
Command-line interface for the PartVision V3 production inference engine.

Usage:
    python scripts/predict.py --source path/to/image.jpg
    python scripts/predict.py --source path/to/image.jpg --conf 0.25 --iou 0.7 --imgsz 512 --output reports/inference/
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path so 'src' can be imported cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.engine import PartVisionInferenceEngine
from src.inference.visualize import save_annotated_image


def parse_args():
    parser = argparse.ArgumentParser(
        description="PartVision AI — V3 Production Model Inference CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to an input image file"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/partvision_v3_yolo11n_seg_best.pt",
        help="Path to the frozen YOLO11n-seg checkpoint"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence cutoff threshold [0.0 - 1.0]"
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.7,
        help="NMS IoU threshold [0.0 - 1.0]"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=512,
        help="Inference square resolution"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/inference",
        help="Directory to save structured JSON and annotated image output"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "mps", "cuda", "cpu"],
        help="Compute device for inference"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # 1. Validate inputs
    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists():
        print(f"Error: Source image not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    model_path = Path(args.model).expanduser().resolve()
    if not model_path.exists():
        print(f"Error: Model checkpoint not found: {model_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Initialize inference engine (model loaded once)
    try:
        engine = PartVisionInferenceEngine(
            model_path=model_path,
            device=args.device
        )
    except Exception as e:
        print(f"Error initializing inference engine: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Run inference & generate visualization
    try:
        result, annotated_img = engine.predict_and_visualize(
            image=source_path,
            conf=args.conf,
            iou=args.iou,
            imgsz=args.imgsz
        )
    except Exception as e:
        print(f"Error executing inference: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Save JSON output and annotated image
    stem = source_path.stem
    json_path = output_dir / f"{stem}_result.json"
    annotated_path = output_dir / f"{stem}_annotated.jpg"

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(result.to_json(indent=2))

    save_annotated_image(annotated_img, annotated_path)

    # 5. Print concise CLI output as specified
    print("PartVision AI")
    print(f"Model: {result.model.name} {result.model.version.upper()}")
    print(f"Device: {result.inference.device}")
    print(f"Latency: {result.latency_ms:.1f} ms" if result.latency_ms else "")
    print()
    print("Detected parts:")
    if result.detections:
        for idx, det in enumerate(result.detections, start=1):
            pct = det.confidence * 100
            print(f"{idx}. {det.class_name} — {pct:.1f}%")
    else:
        print("  (No parts detected above confidence threshold)")
    print()
    print(f"Total detections: {result.summary.detection_count}")
    print(f"JSON saved:      {json_path}")
    print(f"Annotated image: {annotated_path}")


if __name__ == "__main__":
    main()

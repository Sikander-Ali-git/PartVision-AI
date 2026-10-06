#!/usr/bin/env python3
"""
scripts/benchmark_inference.py
Runs the production inference validation and latency smoke test on Apple Silicon M3
across multiple unseen V3 test images.
"""

import sys
import time
import json
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.engine import PartVisionInferenceEngine
from src.inference.schemas import InferenceResult
from src.inference.utils import FROZEN_V3_CLASSES
from src.inference.visualize import save_annotated_image


TEST_IMAGES_DIR = PROJECT_ROOT / "data" / "processed" / "partvision-v3" / "images" / "test"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "inference" / "smoke_test"
REPORTS_DIR = PROJECT_ROOT / "reports"

CANDIDATE_IMAGES = [
    "hitl_Car_damages_1033.png",
    "hitl_Car_damages_1050.png",
    "hitl_Car_damages_1052.png",
    "hitl_Car_damages_1057.png",
    "hitl_Car_damages_1068.png",
    "car87_jpg.rf.27fc37a7f231e296a3b36ba606e9261c.jpg",
    "car42_jpg.rf.26816b314b704b50cd0270a11bc3c2ee.jpg",
]


def run_benchmark():
    print("=" * 70)
    print("PartVision AI — Milestone 6A: Production Inference Smoke Test")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Select existing test images
    test_paths = []
    for fname in CANDIDATE_IMAGES:
        p = TEST_IMAGES_DIR / fname
        if p.exists():
            test_paths.append(p)

    if len(test_paths) < 5:
        # Fallback to any test images
        all_test = sorted([
            f for f in TEST_IMAGES_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith("._")
        ])
        test_paths = all_test[:6]

    print(f"Selected {len(test_paths)} real unseen test images for evaluation:")
    for p in test_paths:
        print(f"  - {p.name}")

    # 2. Measure model loading time
    print("\n[*] Initializing PartVisionInferenceEngine...")
    t_load_start = time.perf_counter()
    engine = PartVisionInferenceEngine(
        model_path="models/partvision_v3_yolo11n_seg_best.pt",
        device="auto"
    )
    total_load_time_ms = (time.perf_counter() - t_load_start) * 1000

    print(f"  Device Selected:     {engine.device}")
    print(f"  Model Load Duration: {total_load_time_ms:.2f} ms ({total_load_time_ms / 1000:.3f} s)")

    # 3. Warm-up inference
    print("\n[*] Running warm-up inference...")
    _ = engine.predict(test_paths[0], conf=0.25)

    # 4. Timed Inference and Comprehensive Validation
    print("\n[*] Running timed inference across test set...")
    latencies = []
    validation_records = []

    for idx, img_path in enumerate(test_paths, start=1):
        t0 = time.perf_counter()
        result, annotated_img = engine.predict_and_visualize(img_path, conf=0.25, iou=0.7, imgsz=512)
        latency = (time.perf_counter() - t0) * 1000
        latencies.append(latency)

        # Verification 1: Valid schema serialization & deserialization
        json_str = result.to_json(indent=2)
        validated_result = InferenceResult.model_validate_json(json_str)

        # Verification 2: Classes match taxonomy
        w = result.image.width
        h = result.image.height
        for det in result.detections:
            assert 0 <= det.class_id < 19, f"Invalid class ID: {det.class_id}"
            assert det.class_name in FROZEN_V3_CLASSES, f"Class name {det.class_name} not in taxonomy"
            assert FROZEN_V3_CLASSES[det.class_id] == det.class_name
            assert 0.0 <= det.confidence <= 1.0, f"Confidence {det.confidence} out of range"

            # Verification 3: Bounding box within boundaries
            assert 0.0 <= det.bbox.x1 <= w
            assert 0.0 <= det.bbox.y1 <= h
            assert 0.0 <= det.bbox.x2 <= w
            assert 0.0 <= det.bbox.y2 <= h
            assert det.bbox.x1 <= det.bbox.x2
            assert det.bbox.y1 <= det.bbox.y2

            # Verification 4: Polygon mask coordinates within boundaries
            if det.mask:
                assert det.mask.point_count >= 3
                for pt in det.mask.points:
                    assert 0.0 <= pt[0] <= w
                    assert 0.0 <= pt[1] <= h

        # Save artifacts
        json_out_path = OUTPUT_DIR / f"{img_path.stem}_result.json"
        with open(json_out_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        img_out_path = OUTPUT_DIR / f"{img_path.stem}_annotated.jpg"
        save_annotated_image(annotated_img, img_out_path)

        record = {
            "image": img_path.name,
            "dimensions": f"{w}x{h}",
            "latency_ms": round(latency, 2),
            "detection_count": result.summary.detection_count,
            "detected_classes": result.summary.detected_classes,
            "json_output": json_out_path.name,
            "annotated_image": img_out_path.name
        }
        validation_records.append(record)
        print(f"  [{idx}/{len(test_paths)}] {img_path.name:<45} -> {result.summary.detection_count:2d} parts in {latency:6.2f} ms")

    # 5. Statistics
    latencies_np = np.array(latencies)
    avg_latency = float(np.mean(latencies_np))
    min_latency = float(np.min(latencies_np))
    max_latency = float(np.max(latencies_np))
    std_latency = float(np.std(latencies_np))

    performance_summary = {
        "benchmark_label": "Local M3 smoke-test performance",
        "device": engine.device,
        "model_checkpoint": engine.model_path.name,
        "model_loading_time_ms": round(total_load_time_ms, 2),
        "model_loading_time_seconds": round(total_load_time_ms / 1000, 3),
        "images_evaluated_count": len(test_paths),
        "latency_metrics_ms": {
            "average": round(avg_latency, 2),
            "minimum": round(min_latency, 2),
            "maximum": round(max_latency, 2),
            "std_dev": round(std_latency, 2)
        },
        "throughput_fps": round(1000.0 / avg_latency, 2),
        "validation_records": validation_records
    }

    perf_json_path = REPORTS_DIR / "inference_performance.json"
    with open(perf_json_path, "w", encoding="utf-8") as f:
        json.dump(performance_summary, f, indent=2)

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY (Local M3 smoke-test performance)")
    print("=" * 70)
    print(f"Device:                 {engine.device.upper()}")
    print(f"Model Load Time:        {total_load_time_ms:.2f} ms ({total_load_time_ms/1000:.3f} s)")
    print(f"Average Inference Time: {avg_latency:.2f} ms")
    print(f"Minimum Inference Time: {min_latency:.2f} ms")
    print(f"Maximum Inference Time: {max_latency:.2f} ms")
    print(f"Throughput (Estimated): {1000.0/avg_latency:.1f} FPS")
    print(f"Results Saved:          {perf_json_path}")
    print(f"Sample Outputs:         {OUTPUT_DIR}")
    print("=" * 70)

    return performance_summary


if __name__ == "__main__":
    run_benchmark()

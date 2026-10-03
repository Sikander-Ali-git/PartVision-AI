#!/usr/bin/env python3
"""
scripts/train_baseline.py
Trains the baseline YOLO11n-seg model on Carparts-Seg dataset:
- Architecture: YOLO11n-seg (pretrained weights)
- Epochs: 3
- Image size: 640
- Batch size: 16
- Workers: 0
- Device: mps (Apple Silicon GPU acceleration)
- Pretrained: True
- Output directory: runs/partvision_v1/

Also runs full validation and exports:
- reports/baseline_metrics.txt
- reports/baseline_metrics.json
"""

import os
import sys
import time
import json
import shutil
import torch

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["COPYFILE_DISABLE"] = "1"

from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_YAML = os.path.join(BASE_DIR, "data", "dataset.yaml")
RUNS_DIR = os.path.join(BASE_DIR, "runs")
RUN_NAME = "partvision_v1"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
MODELS_DIR = os.path.join(BASE_DIR, "models")

def get_disk_info(path):
    stat = shutil.disk_usage(path)
    free_gb = stat.free / (1024 ** 3)
    total_gb = stat.total / (1024 ** 3)
    used_gb = stat.used / (1024 ** 3)
    return {
        "free_gb": f"{free_gb:.2f} GB",
        "used_gb": f"{used_gb:.2f} GB",
        "total_gb": f"{total_gb:.2f} GB",
        "free_bytes": stat.free
    }

def main():
    print("=" * 60)
    print("PartVision AI — Baseline Training (YOLO11n-seg)")
    print("=" * 60)

    # 1. Environment & Hardware Checks
    print(f"PyTorch version: {torch.__version__}")
    mps_available = torch.backends.mps.is_available()
    print(f"Apple Silicon MPS available: {mps_available}")
    device = "mps" if mps_available else "cpu"
    print(f"Selected training device: {device}")

    # 2. Disk Space Checks
    disk_before = get_disk_info(BASE_DIR)
    print(f"Disk space before training: Free={disk_before['free_gb']}, Used={disk_before['used_gb']}")
    if disk_before["free_bytes"] < 5 * (1024 ** 3):
        print("ERROR: Insufficient disk space (< 5 GB). Halting for safety.")
        sys.exit(1)

    # 3. Model Initialization
    pretrained_model_path = os.path.join(MODELS_DIR, "yolo11n-seg.pt")
    if os.path.exists(pretrained_model_path):
        print(f"Loading local pretrained model from: {pretrained_model_path}")
        model = YOLO(pretrained_model_path)
    elif os.path.exists("yolo11n-seg.pt"):
        print("Loading local yolo11n-seg.pt...")
        model = YOLO("yolo11n-seg.pt")
    else:
        print("Initializing YOLO11n-seg (pretrained from Ultralytics)...")
        model = YOLO("yolo11n-seg.pt")

    # 4. Standard Ultralytics Baseline Training
    batch_size = 16
    print(f"Starting training with: epochs=3, imgsz=640, batch={batch_size}, workers=0, device={device}...")
    
    start_time = time.time()
    try:
        results = model.train(
            data=DATA_YAML,
            epochs=3,
            imgsz=640,
            batch=batch_size,
            workers=0,
            device=device,
            pretrained=True,
            project=RUNS_DIR,
            name=RUN_NAME,
            exist_ok=True,
            verbose=True
        )
    except Exception as e:
        if "out of memory" in str(e).lower() and batch_size > 8:
            print(f"OOM detected with batch {batch_size}. Retrying with batch 8...")
            batch_size = 8
            results = model.train(
                data=DATA_YAML,
                epochs=3,
                imgsz=640,
                batch=batch_size,
                workers=0,
                device=device,
                pretrained=True,
                project=RUNS_DIR,
                name=RUN_NAME,
                exist_ok=True,
                verbose=True
            )
        else:
            raise e

    training_duration_sec = time.time() - start_time
    minutes, seconds = divmod(training_duration_sec, 60)
    print(f"\nTraining completed in {int(minutes)}m {seconds:.1f}s ({training_duration_sec:.2f}s).")

    # 5. Validation on Validation Set using best weights
    best_weights_path = os.path.join(RUNS_DIR, RUN_NAME, "weights", "best.pt")
    if not os.path.exists(best_weights_path):
        best_weights_path = os.path.join(RUNS_DIR, RUN_NAME, "weights", "last.pt")
    print(f"\nRunning evaluation on validation set with weights: {best_weights_path}...")
    
    val_model = YOLO(best_weights_path)
    val_metrics = val_model.val(
        data=DATA_YAML,
        split="val",
        imgsz=640,
        batch=batch_size,
        workers=0,
        device=device,
        project=RUNS_DIR,
        name=f"{RUN_NAME}_val",
        exist_ok=True
    )

    # 6. Extract Metrics
    box = val_metrics.box
    seg = val_metrics.seg
    names = val_metrics.names
    results_dict = val_metrics.results_dict

    metrics_dict = {
        "model": "YOLO11n-seg",
        "checkpoint": best_weights_path,
        "device": device,
        "epochs": 3,
        "imgsz": 640,
        "batch_size": batch_size,
        "workers": 0,
        "training_duration_seconds": training_duration_sec,
        "training_duration_formatted": f"{int(minutes)}m {seconds:.1f}s",
        "ultralytics_results_dict": {k: float(v) for k, v in results_dict.items()},
        "detection_box": {
            "precision": float(box.mp),
            "recall": float(box.mr),
            "map50": float(box.map50),
            "map50_95": float(box.map)
        },
        "segmentation_mask": {
            "precision": float(seg.mp),
            "recall": float(seg.mr),
            "map50": float(seg.map50),
            "map50_95": float(seg.map)
        },
        "per_class_metrics": {}
    }

    # Per-class metrics
    for idx_int, cname in names.items():
        idx = int(idx_int)
        # class_result returns (p, r, ap50, ap)
        try:
            b_p, b_r, b_map50, b_map = box.class_result(idx)
        except Exception:
            b_p, b_r, b_map50, b_map = None, None, None, None

        try:
            s_p, s_r, s_map50, s_map = seg.class_result(idx)
        except Exception:
            s_p, s_r, s_map50, s_map = None, None, None, None

        metrics_dict["per_class_metrics"][cname] = {
            "class_id": idx,
            "box": {
                "precision": float(b_p) if b_p is not None else None,
                "recall": float(b_r) if b_r is not None else None,
                "map50": float(b_map50) if b_map50 is not None else None,
                "map50_95": float(b_map) if b_map is not None else None
            },
            "seg": {
                "precision": float(s_p) if s_p is not None else None,
                "recall": float(s_r) if s_r is not None else None,
                "map50": float(s_map50) if s_map50 is not None else None,
                "map50_95": float(s_map) if s_map is not None else None
            }
        }

    # Save metrics JSON
    json_path = os.path.join(REPORTS_DIR, "baseline_metrics.json")
    with open(json_path, "w") as f:
        json.dump(metrics_dict, f, indent=2)
    print(f"Metrics JSON saved to: {json_path}")

    # Save metrics TXT
    txt_path = os.path.join(REPORTS_DIR, "baseline_metrics.txt")
    with open(txt_path, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("PartVision AI — Milestone 1 Baseline Evaluation Metrics\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Model Architecture : YOLO11n-seg (pretrained)\n")
        f.write(f"Weights Used       : {best_weights_path}\n")
        f.write(f"Device             : {device}\n")
        f.write(f"Epochs             : 3\n")
        f.write(f"Batch Size         : {batch_size}\n")
        f.write(f"Image Size         : 640\n")
        f.write(f"Training Duration  : {metrics_dict['training_duration_formatted']} ({training_duration_sec:.2f}s)\n\n")

        f.write("-" * 80 + "\n")
        f.write("OVERALL DETECTION (BOX) METRICS:\n")
        f.write(f"  Precision (B)    : {box.mp:.6f}\n")
        f.write(f"  Recall (B)       : {box.mr:.6f}\n")
        f.write(f"  mAP50 (B)        : {box.map50:.6f}\n")
        f.write(f"  mAP50-95 (B)     : {box.map:.6f}\n\n")

        f.write("OVERALL SEGMENTATION (MASK) METRICS:\n")
        f.write(f"  Precision (M)    : {seg.mp:.6f}\n")
        f.write(f"  Recall (M)       : {seg.mr:.6f}\n")
        f.write(f"  mAP50 (M)        : {seg.map50:.6f}\n")
        f.write(f"  mAP50-95 (M)     : {seg.map:.6f}\n\n")

        f.write("-" * 80 + "\n")
        f.write("PER-CLASS VALIDATION METRICS:\n")
        f.write(f"{'Class Name':<20} {'Box P':<9} {'Box R':<9} {'Box mAP50':<11} {'Box mAP':<10} {'Seg P':<9} {'Seg R':<9} {'Seg mAP50':<11} {'Seg mAP':<10}\n")
        f.write("-" * 98 + "\n")
        for cname, pdata in metrics_dict["per_class_metrics"].items():
            bp = f"{pdata['box']['precision']:.4f}" if pdata['box']['precision'] is not None else "-"
            br = f"{pdata['box']['recall']:.4f}" if pdata['box']['recall'] is not None else "-"
            bm50 = f"{pdata['box']['map50']:.4f}" if pdata['box']['map50'] is not None else "-"
            bm = f"{pdata['box']['map50_95']:.4f}" if pdata['box']['map50_95'] is not None else "-"

            sp = f"{pdata['seg']['precision']:.4f}" if pdata['seg']['precision'] is not None else "-"
            sr = f"{pdata['seg']['recall']:.4f}" if pdata['seg']['recall'] is not None else "-"
            sm50 = f"{pdata['seg']['map50']:.4f}" if pdata['seg']['map50'] is not None else "-"
            sm = f"{pdata['seg']['map50_95']:.4f}" if pdata['seg']['map50_95'] is not None else "-"

            f.write(f"{cname:<20} {bp:<9} {br:<9} {bm50:<11} {bm:<10} {sp:<9} {sr:<9} {sm50:<11} {sm:<10}\n")
        f.write("\n")

    print(f"Metrics report saved to: {txt_path}")

    # Check disk space after
    disk_after = get_disk_info(BASE_DIR)
    print(f"Disk space after training: Free={disk_after['free_gb']}, Used={disk_after['used_gb']}")
    print("=== Step 6 & Step 7 Completed Successfully ===")

if __name__ == "__main__":
    main()

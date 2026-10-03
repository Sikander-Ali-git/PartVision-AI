#!/usr/bin/env python3
"""
scripts/train_v2.py
Trains YOLO11n-seg on the Carparts-V2 dataset (13 classes):
- Architecture: YOLO11n-seg (pretrained weights)
- Epochs: 10
- Image size: 512
- Batch size: 8
- Workers: 0
- Device: mps (Apple Silicon GPU acceleration)
- Pretrained: True
- Output directory: runs/partvision_v2/
- Best weights: models/partvision_v2_yolo11n_seg_best.pt

Also runs evaluation on the validation split and exports:
- reports/v2_baseline_metrics.txt
- reports/v2_baseline_metrics.json
- reports/v2_training_curves.png
"""

import os
import sys
import time
import json
import shutil
import csv
import torch

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["COPYFILE_DISABLE"] = "1"

import matplotlib.pyplot as plt
import pandas as pd
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_YAML = os.path.join(BASE_DIR, "data", "processed", "carparts-v2", "carparts-v2.yaml")
RUNS_DIR = os.path.join(BASE_DIR, "runs")
RUN_NAME = "partvision_v2"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
MODELS_DIR = os.path.join(BASE_DIR, "models")
BEST_WEIGHTS_EXPORT = os.path.join(MODELS_DIR, "partvision_v2_yolo11n_seg_best.pt")

def get_disk_info(path):
    stat = shutil.disk_usage(path)
    free_gb = stat.free / (1024 ** 3)
    used_gb = stat.used / (1024 ** 3)
    return {
        "free_gb": f"{free_gb:.2f} GB",
        "used_gb": f"{used_gb:.2f} GB",
        "free_bytes": stat.free
    }

def generate_training_curves(results_csv_path, output_png_path):
    """Parses Ultralytics results.csv and plots training curves."""
    if not os.path.exists(results_csv_path):
        print(f"Warning: results.csv not found at {results_csv_path}")
        return

    df = pd.read_csv(results_csv_path)
    # Strip whitespace from columns
    df.columns = [c.strip() for c in df.columns]

    epochs = df["epoch"] if "epoch" in df.columns else range(1, len(df) + 1)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Training Losses
    ax1 = axes[0, 0]
    if "train/box_loss" in df.columns:
        ax1.plot(epochs, df["train/box_loss"], label="Train Box Loss", marker="o", color="#1f77b4")
    if "train/seg_loss" in df.columns:
        ax1.plot(epochs, df["train/seg_loss"], label="Train Seg Loss", marker="s", color="#ff7f0e")
    if "train/cls_loss" in df.columns:
        ax1.plot(epochs, df["train/cls_loss"], label="Train Cls Loss", marker="^", color="#2ca02c")
    ax1.set_title("Training Losses per Epoch", fontweight="bold")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend()

    # 2. Validation Losses
    ax2 = axes[0, 1]
    if "val/box_loss" in df.columns:
        ax2.plot(epochs, df["val/box_loss"], label="Val Box Loss", marker="o", color="#1f77b4")
    if "val/seg_loss" in df.columns:
        ax2.plot(epochs, df["val/seg_loss"], label="Val Seg Loss", marker="s", color="#ff7f0e")
    if "val/cls_loss" in df.columns:
        ax2.plot(epochs, df["val/cls_loss"], label="Val Cls Loss", marker="^", color="#2ca02c")
    ax2.set_title("Validation Losses per Epoch", fontweight="bold")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Loss")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend()

    # 3. Detection Metrics (Box)
    ax3 = axes[1, 0]
    if "metrics/mAP50(B)" in df.columns:
        ax3.plot(epochs, df["metrics/mAP50(B)"], label="Box mAP50", marker="o", color="#d62728")
    if "metrics/mAP50-95(B)" in df.columns:
        ax3.plot(epochs, df["metrics/mAP50-95(B)"], label="Box mAP50-95", marker="s", color="#9467bd")
    if "metrics/precision(B)" in df.columns:
        ax3.plot(epochs, df["metrics/precision(B)"], label="Box Precision", linestyle=":", color="#8c564b")
    if "metrics/recall(B)" in df.columns:
        ax3.plot(epochs, df["metrics/recall(B)"], label="Box Recall", linestyle="--", color="#e377c2")
    ax3.set_title("Detection Box Metrics per Epoch", fontweight="bold")
    ax3.set_xlabel("Epoch")
    ax3.set_ylabel("Score")
    ax3.grid(True, linestyle="--", alpha=0.5)
    ax3.legend()

    # 4. Segmentation Metrics (Mask)
    ax4 = axes[1, 1]
    if "metrics/mAP50(M)" in df.columns:
        ax4.plot(epochs, df["metrics/mAP50(M)"], label="Mask mAP50", marker="o", color="#d62728")
    if "metrics/mAP50-95(M)" in df.columns:
        ax4.plot(epochs, df["metrics/mAP50-95(M)"], label="Mask mAP50-95", marker="s", color="#9467bd")
    if "metrics/precision(M)" in df.columns:
        ax4.plot(epochs, df["metrics/precision(M)"], label="Mask Precision", linestyle=":", color="#8c564b")
    if "metrics/recall(M)" in df.columns:
        ax4.plot(epochs, df["metrics/recall(M)"], label="Mask Recall", linestyle="--", color="#e377c2")
    ax4.set_title("Segmentation Mask Metrics per Epoch", fontweight="bold")
    ax4.set_xlabel("Epoch")
    ax4.set_ylabel("Score")
    ax4.grid(True, linestyle="--", alpha=0.5)
    ax4.legend()

    plt.suptitle("PartVision AI — V2 Controlled Experiment Training Curves (10 Epochs, imgsz 512, batch 8)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_png_path, dpi=200)
    plt.close()
    print(f"Generated training curves plot: {output_png_path}")

def main():
    print("=" * 70)
    print("PartVision AI — Milestone 3: V2 Model Training Experiment")
    print("=" * 70)

    # 1. Hardware and environment checks
    mps_available = torch.backends.mps.is_available()
    device = "mps" if mps_available else "cpu"
    print(f"PyTorch version: {torch.__version__}")
    print(f"Device: {device} (Apple Silicon MPS available: {mps_available})")

    disk_info = get_disk_info(BASE_DIR)
    print(f"Disk space: Free={disk_info['free_gb']}, Used={disk_info['used_gb']}")
    if disk_info["free_bytes"] < 5 * (1024 ** 3):
        print("ERROR: Less than 5 GB available disk space. Halting.")
        sys.exit(1)

    # 2. Model Initialization (Pretrained YOLO11n-seg)
    pretrained_path = os.path.join(MODELS_DIR, "yolo11n-seg.pt")
    if not os.path.exists(pretrained_path):
        pretrained_path = "yolo11n-seg.pt"
    print(f"Loading pretrained base model: {pretrained_path}")
    model = YOLO(pretrained_path)

    # 3. Training execution
    epochs = 10
    imgsz = 512
    batch = 8
    workers = 0

    print(f"\nStarting training on Carparts-V2:")
    print(f"  Dataset: {DATA_YAML}")
    print(f"  Epochs: {epochs}")
    print(f"  Image Size: {imgsz}")
    print(f"  Batch Size: {batch}")
    print(f"  Workers: {workers}")
    print(f"  Device: {device}")
    print(f"  Standard Ultralytics configuration (no custom loss/weighting)")

    start_time = time.time()
    train_results = model.train(
        data=DATA_YAML,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        device=device,
        pretrained=True,
        project=RUNS_DIR,
        name=RUN_NAME,
        exist_ok=True,
        verbose=True
    )
    training_duration_sec = time.time() - start_time
    minutes, seconds = divmod(training_duration_sec, 60)
    print(f"\nTraining completed in {int(minutes)}m {seconds:.1f}s ({training_duration_sec:.2f}s).")

    # 4. Copy best checkpoint to models/partvision_v2_yolo11n_seg_best.pt
    run_best_weights = os.path.join(RUNS_DIR, RUN_NAME, "weights", "best.pt")
    if os.path.exists(run_best_weights):
        shutil.copy2(run_best_weights, BEST_WEIGHTS_EXPORT)
        print(f"Saved best model checkpoint to: {BEST_WEIGHTS_EXPORT}")
    else:
        run_last_weights = os.path.join(RUNS_DIR, RUN_NAME, "weights", "last.pt")
        shutil.copy2(run_last_weights, BEST_WEIGHTS_EXPORT)
        print(f"Saved last model checkpoint to: {BEST_WEIGHTS_EXPORT}")

    # 5. Generate training curves
    results_csv = os.path.join(RUNS_DIR, RUN_NAME, "results.csv")
    training_curves_png = os.path.join(REPORTS_DIR, "v2_training_curves.png")
    generate_training_curves(results_csv, training_curves_png)

    # Also copy Ultralytics default results.png if available
    ultra_results_png = os.path.join(RUNS_DIR, RUN_NAME, "results.png")
    if os.path.exists(ultra_results_png) and not os.path.exists(training_curves_png):
        shutil.copy2(ultra_results_png, training_curves_png)

    # 6. Explicit Validation on Carparts-V2 Validation Split
    print(f"\nRunning evaluation on V2 validation split with: {BEST_WEIGHTS_EXPORT}...")
    val_model = YOLO(BEST_WEIGHTS_EXPORT)
    val_metrics = val_model.val(
        data=DATA_YAML,
        split="val",
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        device=device,
        project=RUNS_DIR,
        name=f"{RUN_NAME}_val",
        exist_ok=True
    )

    box = val_metrics.box
    seg = val_metrics.seg
    names = val_metrics.names
    results_dict = val_metrics.results_dict

    # 7. Extract metrics
    metrics_data = {
        "model": "YOLO11n-seg",
        "taxonomy": "V2 (13 classes)",
        "checkpoint": BEST_WEIGHTS_EXPORT,
        "device": device,
        "epochs": epochs,
        "imgsz": imgsz,
        "batch_size": batch,
        "workers": workers,
        "training_duration_seconds": training_duration_sec,
        "training_duration_formatted": f"{int(minutes)}m {seconds:.1f}s",
        "parameters": 2836373, # YOLO11n-seg for 13 classes
        "model_file_size_bytes": os.path.getsize(BEST_WEIGHTS_EXPORT),
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

    for idx_int, cname in names.items():
        idx = int(idx_int)
        try:
            b_p, b_r, b_map50, b_map = box.class_result(idx)
        except Exception:
            b_p, b_r, b_map50, b_map = None, None, None, None

        try:
            s_p, s_r, s_map50, s_map = seg.class_result(idx)
        except Exception:
            s_p, s_r, s_map50, s_map = None, None, None, None

        metrics_data["per_class_metrics"][cname] = {
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

    # Save JSON metrics
    json_path = os.path.join(REPORTS_DIR, "v2_baseline_metrics.json")
    with open(json_path, "w") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"V2 Metrics JSON saved to: {json_path}")

    # Save TXT metrics
    txt_path = os.path.join(REPORTS_DIR, "v2_baseline_metrics.txt")
    with open(txt_path, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("PartVision AI — Milestone 3 V2 Controlled Experiment Evaluation Metrics\n")
        f.write("Taxonomy: 13 Unified Classes | YOLO11n-seg | 10 Epochs | imgsz 512 | batch 8\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Model Architecture : YOLO11n-seg (pretrained)\n")
        f.write(f"Weights Used       : {BEST_WEIGHTS_EXPORT}\n")
        f.write(f"Device             : {device}\n")
        f.write(f"Epochs             : {epochs}\n")
        f.write(f"Batch Size         : {batch}\n")
        f.write(f"Image Size         : {imgsz}\n")
        f.write(f"Training Duration  : {metrics_data['training_duration_formatted']} ({training_duration_sec:.2f}s)\n\n")

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
        f.write("PER-CLASS VALIDATION METRICS (13 CLASSES):\n")
        f.write(f"{'Class Name':<16} {'Box P':<9} {'Box R':<9} {'Box mAP50':<11} {'Box mAP':<10} {'Seg P':<9} {'Seg R':<9} {'Seg mAP50':<11} {'Seg mAP':<10}\n")
        f.write("-" * 94 + "\n")
        for cname, pdata in metrics_data["per_class_metrics"].items():
            bp = f"{pdata['box']['precision']:.4f}" if pdata['box']['precision'] is not None else "-"
            br = f"{pdata['box']['recall']:.4f}" if pdata['box']['recall'] is not None else "-"
            bm50 = f"{pdata['box']['map50']:.4f}" if pdata['box']['map50'] is not None else "-"
            bm = f"{pdata['box']['map50_95']:.4f}" if pdata['box']['map50_95'] is not None else "-"

            sp = f"{pdata['seg']['precision']:.4f}" if pdata['seg']['precision'] is not None else "-"
            sr = f"{pdata['seg']['recall']:.4f}" if pdata['seg']['recall'] is not None else "-"
            sm50 = f"{pdata['seg']['map50']:.4f}" if pdata['seg']['map50'] is not None else "-"
            sm = f"{pdata['seg']['map50_95']:.4f}" if pdata['seg']['map50_95'] is not None else "-"

            f.write(f"{cname:<16} {bp:<9} {br:<9} {bm50:<11} {bm:<10} {sp:<9} {sr:<9} {sm50:<11} {sm:<10}\n")
        f.write("\n")

    print(f"V2 Metrics report saved to: {txt_path}")
    print("=== Training & Validation Completed Successfully ===")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
scripts/predict_test_v3.py
Runs inference on unseen test images using the trained V3 model (19 classes).
- Model: models/partvision_v3_yolo11n_seg_best.pt
- Confidence threshold: 0.25
- Output directory: reports/v3_test_predictions/

Generates:
- Individual prediction images
- reports/v3_test_predictions/prediction_summary.json
- reports/v3_test_predictions/v3_test_prediction_grid.png
"""

import os
import sys
import json
from pathlib import Path
import cv2
import numpy as np
import torch

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["COPYFILE_DISABLE"] = "1"

import matplotlib.pyplot as plt
from ultralytics import YOLO

BASE_DIR = Path("/Volumes/Toshiba 1TB/PartVision")
TEST_IMAGES_DIR = BASE_DIR / "data" / "processed" / "partvision-v3" / "images" / "test"
TEST_LABELS_DIR = BASE_DIR / "data" / "processed" / "partvision-v3" / "labels" / "test"
OUTPUT_DIR = BASE_DIR / "reports" / "v3_test_predictions"
WEIGHTS_PATH = BASE_DIR / "models" / "partvision_v3_yolo11n_seg_best.pt"

V3_CLASSES = [
    "back_bumper",    # 0
    "back_door",      # 1
    "back_glass",     # 2
    "back_light",     # 3
    "fender",         # 4
    "front_bumper",   # 5
    "front_door",     # 6
    "front_glass",    # 7
    "front_light",    # 8
    "grille",         # 9
    "hood",           # 10
    "mirror",         # 11
    "quarter_panel",  # 12
    "rocker_panel",   # 13
    "roof",           # 14
    "side_window",    # 15
    "tailgate",       # 16
    "trunk",          # 17
    "wheel",          # 18
]

# 19 distinct RGB colors
COLORS_19 = [
    (230, 25, 75),   # 0 back_bumper
    (60, 180, 75),   # 1 back_door
    (255, 225, 25),  # 2 back_glass
    (0, 130, 200),   # 3 back_light
    (245, 130, 48),  # 4 fender
    (145, 30, 180),  # 5 front_bumper
    (70, 240, 240),  # 6 front_door
    (240, 50, 230),  # 7 front_glass
    (210, 245, 60),  # 8 front_light
    (250, 190, 212), # 9 grille
    (0, 128, 128),   # 10 hood
    (220, 190, 255), # 11 mirror
    (170, 110, 40),  # 12 quarter_panel
    (255, 250, 200), # 13 rocker_panel
    (128, 0, 0),     # 14 roof
    (170, 255, 195), # 15 side_window
    (128, 128, 0),   # 16 tailgate
    (255, 215, 180), # 17 trunk
    (0, 0, 128),     # 18 wheel
]

def draw_prediction(img_bgr, result, class_names):
    overlay = img_bgr.copy()
    alpha = 0.45
    h, w = img_bgr.shape[:2]

    detections = []
    if result.masks is not None and result.boxes is not None:
        boxes = result.boxes
        masks = result.masks.xy

        for i, (box, poly) in enumerate(zip(boxes, masks)):
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            cname = class_names.get(cls_id, str(cls_id))
            xyxy = [float(x) for x in box.xyxy[0].tolist()]

            color_rgb = COLORS_19[cls_id % len(COLORS_19)]
            color_bgr = (int(color_rgb[2]), int(color_rgb[1]), int(color_rgb[0]))

            if len(poly) > 0:
                pts = np.array(poly, dtype=np.int32)
                cv2.fillPoly(overlay, [pts], color_bgr)
                cv2.polylines(img_bgr, [pts], isClosed=True, color=color_bgr, thickness=2)

            detections.append({
                "detection_id": i + 1,
                "class_id": cls_id,
                "class_name": cname,
                "confidence": round(conf, 4),
                "box_xyxy": [round(x, 2) for x in xyxy],
                "polygon_points_count": len(poly)
            })

    # Blend polygon masks
    cv2.addWeighted(overlay, alpha, img_bgr, 1 - alpha, 0, img_bgr)

    # Draw bounding boxes and labels on top
    if result.boxes is not None:
        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            cname = class_names.get(cls_id, str(cls_id))
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]

            color_rgb = COLORS_19[cls_id % len(COLORS_19)]
            color_bgr = (int(color_rgb[2]), int(color_rgb[1]), int(color_rgb[0]))

            # Box outline
            cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color_bgr, 1)

            # Label banner
            label = f"{cname} {conf:.2f}"
            (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            ty = max(y1, th + 4)
            cv2.rectangle(img_bgr, (x1, ty - th - 4), (x1 + tw + 4, ty + 2), color_bgr, -1)
            cv2.putText(img_bgr, label, (x1 + 2, ty - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    return img_bgr, detections

def select_diverse_test_images(focus_classes):
    """Finds test images covering the target focus classes."""
    test_files = sorted([
        f for f in TEST_IMAGES_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith("._")
    ])

    selected = []
    covered_classes = set()

    # Prioritize images containing target focus classes
    for target in focus_classes:
        tgt_id = V3_CLASSES.index(target)
        for img_p in test_files:
            if img_p in selected:
                continue
            lbl_p = TEST_LABELS_DIR / f"{img_p.stem}.txt"
            if lbl_p.exists():
                with open(lbl_p, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.strip().split("\n")
                    class_ids = [int(l.split()[0]) for l in lines if l.strip()]
                    if tgt_id in class_ids:
                        selected.append(img_p)
                        covered_classes.update([V3_CLASSES[cid] for cid in class_ids if cid < len(V3_CLASSES)])
                        break

    # Fill up to 12 images if needed
    for img_p in test_files:
        if len(selected) >= 12:
            break
        if img_p not in selected:
            selected.append(img_p)

    return selected[:12]

def run_predictions():
    print("=" * 70)
    print("PartVision AI — V3 Model Test Inference & Predictions")
    print("=" * 70)

    if not WEIGHTS_PATH.exists():
        print(f"ERROR: Model checkpoint not found at {WEIGHTS_PATH}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading trained V3 model: {WEIGHTS_PATH}")
    model = YOLO(str(WEIGHTS_PATH))
    class_names = model.names

    focus_classes = [
        "fender", "grille", "quarter_panel", "rocker_panel",
        "roof", "side_window", "trunk", "wheel", "mirror"
    ]

    selected_images = select_diverse_test_images(focus_classes)
    print(f"Selected {len(selected_images)} diverse test images covering focus classes:")
    for p in selected_images:
        print(f"  - {p.name}")

    summary_records = []
    annotated_images_for_grid = []

    for img_path in selected_images:
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            continue

        h, w = img_bgr.shape[:2]

        results = model.predict(
            source=str(img_path),
            conf=0.25,
            imgsz=512,
            device="mps" if torch.backends.mps.is_available() else "cpu",
            verbose=False
        )
        res = results[0]

        annotated_bgr, detections = draw_prediction(img_bgr, res, class_names)

        # Save individual prediction image
        out_img_path = OUTPUT_DIR / f"pred_{img_path.name}"
        cv2.imwrite(str(out_img_path), annotated_bgr)

        # Record summary
        det_classes = [d["class_name"] for d in detections]
        summary_records.append({
            "image_filename": img_path.name,
            "saved_prediction": out_img_path.name,
            "dimensions": f"{w}x{h}",
            "detection_count": len(detections),
            "detected_classes": det_classes,
            "detections": detections
        })

        # Save for grid in RGB
        annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
        annotated_images_for_grid.append((img_path.stem, annotated_rgb, det_classes))

    # Save prediction summary JSON
    summary_path = OUTPUT_DIR / "prediction_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "model_checkpoint": str(WEIGHTS_PATH),
            "confidence_threshold": 0.25,
            "total_test_images_evaluated": len(summary_records),
            "focus_classes_targeted": focus_classes,
            "predictions": summary_records
        }, f, indent=2)
    print(f"\nSaved prediction summary to: {summary_path}")

    # Create 3x4 or 4x3 Grid Plot
    n_imgs = len(annotated_images_for_grid)
    cols = 4
    rows = (n_imgs + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(20, 5 * rows))
    axes = axes.flatten()

    for idx, (stem, img_rgb, classes_found) in enumerate(annotated_images_for_grid):
        ax = axes[idx]
        ax.imshow(img_rgb)
        cls_summary = ", ".join(list(dict.fromkeys(classes_found))[:4])
        if len(classes_found) > 4:
            cls_summary += f" (+{len(classes_found)-4})"
        ax.set_title(f"{stem}\n[{cls_summary if cls_summary else 'No Detections'}]", fontsize=9, fontweight="bold")
        ax.axis("off")

    for idx in range(n_imgs, len(axes)):
        axes[idx].axis("off")

    plt.suptitle("PartVision AI — V3 Model Predictions on Unseen Test Split (conf=0.25, imgsz=512)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    grid_out_path = OUTPUT_DIR / "v3_test_prediction_grid.png"
    plt.savefig(grid_out_path, dpi=200)
    plt.close()
    print(f"Saved prediction grid to: {grid_out_path}")

    print("\n=== Test Prediction Suite Completed ===")

if __name__ == "__main__":
    run_predictions()

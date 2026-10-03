#!/usr/bin/env python3
"""
scripts/predict_test.py
Runs inference on unseen test images from Carparts-Seg using the trained YOLO11n-seg model.
- Confidence threshold: 0.25
- Saves annotated prediction images to reports/test_predictions/
- Saves prediction summary JSON to reports/test_predictions/prediction_summary.json
- Generates a visual prediction grid: reports/test_predictions/test_prediction_grid.png
"""

import os
import sys
import json
import random
import cv2
import numpy as np

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["COPYFILE_DISABLE"] = "1"

import matplotlib.pyplot as plt
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_IMAGES_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-seg", "images", "test")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "test_predictions")
WEIGHTS_PATH = os.path.join(BASE_DIR, "models", "baseline_yolo11n_seg_best.pt")

if not os.path.exists(WEIGHTS_PATH):
    WEIGHTS_PATH = os.path.join(BASE_DIR, "runs", "partvision_v1", "weights", "best.pt")

COLORS = [
    (230, 25, 75),   (60, 180, 75),   (255, 225, 25),  (0, 130, 200),
    (245, 130, 48),  (145, 30, 180),  (70, 240, 240),  (240, 50, 230),
    (210, 245, 60),  (250, 190, 212), (0, 128, 128),   (220, 190, 255),
    (170, 110, 40),  (255, 250, 200), (128, 0, 0),     (170, 255, 195),
    (128, 128, 0),   (255, 215, 180), (0, 128, 128),   (128, 128, 128),
    (255, 105, 180), (30, 144, 255),  (50, 205, 50)
]

def draw_prediction(img_bgr, result, class_names):
    overlay = img_bgr.copy()
    alpha = 0.45
    h, w = img_bgr.shape[:2]

    detections = []
    if result.masks is not None and result.boxes is not None:
        boxes = result.boxes
        masks = result.masks.xy  # list of polygon coordinates per detection

        for i, (box, poly) in enumerate(zip(boxes, masks)):
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            cname = class_names.get(cls_id, str(cls_id))
            xyxy = [float(x) for x in box.xyxy[0].tolist()]

            color = COLORS[cls_id % len(COLORS)]
            color_bgr = (int(color[2]), int(color[1]), int(color[0]))

            # Fill mask
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

    # Blend overlay
    blended = cv2.addWeighted(overlay, alpha, img_bgr, 1 - alpha, 0)

    # Draw labels
    for det in detections:
        box = det["box_xyxy"]
        x1, y1 = int(box[0]), int(box[1])
        label = f"{det['class_name']} {det['confidence']:.2f}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.45
        thickness = 1
        (tw, th), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        tx = max(2, min(w - tw - 4, x1))
        ty = max(th + 4, min(h - 4, y1))

        cv2.rectangle(blended, (tx - 2, ty - th - 2), (tx + tw + 2, ty + baseline), (0, 0, 0), -1)
        cv2.putText(blended, label, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    return blended, detections

def main():
    print("=" * 60)
    print("PartVision AI — Test Predictions & Inference")
    print("=" * 60)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Loading trained weights: {WEIGHTS_PATH}")
    model = YOLO(WEIGHTS_PATH)
    class_names = model.names

    all_test_files = sorted([
        f for f in os.listdir(TEST_IMAGES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png")) and not f.startswith(".")
    ])
    print(f"Found {len(all_test_files)} total test images.")

    # Select 8 diverse test samples deterministically
    random.seed(101)
    selected_files = random.sample(all_test_files, min(8, len(all_test_files)))

    summary = {
        "model_weights": WEIGHTS_PATH,
        "confidence_threshold": 0.25,
        "test_images_count": len(selected_files),
        "predictions": []
    }

    grid_images = []

    for fname in selected_files:
        img_path = os.path.join(TEST_IMAGES_DIR, fname)
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            continue

        results = model.predict(
            source=img_path,
            conf=0.25,
            device="mps",
            save=False,
            verbose=False
        )
        result = results[0]

        annotated_bgr, detections = draw_prediction(img_bgr, result, class_names)
        
        # Save individual prediction
        out_name = f"{os.path.splitext(fname)[0]}_pred.jpg"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        cv2.imwrite(out_path, annotated_bgr)

        summary["predictions"].append({
            "image_filename": fname,
            "saved_prediction": out_name,
            "detected_parts_count": len(detections),
            "detections": detections
        })

        # Save for grid
        annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
        grid_images.append((fname, annotated_rgb, len(detections)))
        print(f"Processed {fname}: {len(detections)} parts detected.")

    # Save summary JSON
    summary_path = os.path.join(OUTPUT_DIR, "prediction_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nPrediction summary saved to: {summary_path}")

    # Create visual prediction grid (2 rows x 4 cols)
    grid_path = os.path.join(OUTPUT_DIR, "test_prediction_grid.png")
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    for idx, ax in enumerate(axes.flat):
        if idx < len(grid_images):
            fname, rgb_img, count = grid_images[idx]
            ax.imshow(rgb_img)
            ax.set_title(f"{fname[:22]}... ({count} parts)", fontsize=10, pad=6)
        ax.axis("off")

    plt.suptitle("PartVision AI — YOLO11n-seg Test Set Predictions (conf >= 0.25)", fontsize=15, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(grid_path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Test prediction visual grid saved to: {grid_path}")
    print("=== Step 8 Completed Successfully ===")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
scripts/visualize_dataset.py
Visualizes ground truth segmentation masks on sample images from Carparts-Seg.
Saves a representative sample grid to reports/dataset_sample_grid.png.
"""

import os
import sys

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["COPYFILE_DISABLE"] = "1"

import yaml
import random
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-seg")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
YAML_FILE = os.path.join(DATASET_DIR, "carparts-seg.yaml")
OUTPUT_GRID = os.path.join(REPORTS_DIR, "dataset_sample_grid.png")

# Distinct color palette for 23 classes
COLORS = [
    (230, 25, 75),   (60, 180, 75),   (255, 225, 25),  (0, 130, 200),
    (245, 130, 48),  (145, 30, 180),  (70, 240, 240),  (240, 50, 230),
    (210, 245, 60),  (250, 190, 212), (0, 128, 128),   (220, 190, 255),
    (170, 110, 40),  (255, 250, 200), (128, 0, 0),     (170, 255, 195),
    (128, 128, 0),   (255, 215, 180), (0, 0, 128),     (128, 128, 128),
    (255, 105, 180), (30, 144, 255),  (50, 205, 50)
]

def load_yaml(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    names = data.get("names", {})
    if isinstance(names, list):
        return {i: name for i, name in enumerate(names)}
    return {int(k): v for k, v in names.items()}

def parse_label(label_path, img_w, img_h):
    polygons = []
    if not os.path.exists(label_path):
        return polygons
    with open(label_path, "r") as f:
        for line in f:
            tokens = line.strip().split()
            if len(tokens) < 7:
                continue
            cls_id = int(tokens[0])
            coords = [float(x) for x in tokens[1:]]
            pts = []
            for i in range(0, len(coords), 2):
                x = int(round(coords[i] * img_w))
                y = int(round(coords[i + 1] * img_h))
                pts.append([x, y])
            if len(pts) >= 3:
                polygons.append((cls_id, np.array(pts, dtype=np.int32)))
    return polygons

def draw_annotations(img_bgr, polygons, class_names):
    overlay = img_bgr.copy()
    alpha = 0.45

    for cls_id, pts in polygons:
        color = COLORS[cls_id % len(COLORS)]
        # BGR format for cv2
        color_bgr = (int(color[2]), int(color[1]), int(color[0]))
        cv2.fillPoly(overlay, [pts], color_bgr)
        cv2.polylines(img_bgr, [pts], isClosed=True, color=color_bgr, thickness=2)

    # Blend overlay with original
    blended = cv2.addWeighted(overlay, alpha, img_bgr, 1 - alpha, 0)

    # Add text labels at centroid of each polygon
    for cls_id, pts in polygons:
        M = cv2.moments(pts)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = pts[0]
        
        cname = class_names.get(cls_id, str(cls_id))
        label_text = cname
        
        # Draw small background tag for text readability
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1
        (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        tx = max(2, min(img_bgr.shape[1] - tw - 4, cx - tw // 2))
        ty = max(th + 4, min(img_bgr.shape[0] - 4, cy))
        
        cv2.rectangle(blended, (tx - 2, ty - th - 2), (tx + tw + 2, ty + baseline), (0, 0, 0), -1)
        cv2.putText(blended, label_text, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    return blended

def select_representative_samples(dataset_dir, num_samples=9):
    train_img_dir = os.path.join(dataset_dir, "images", "train")
    train_lbl_dir = os.path.join(dataset_dir, "labels", "train")

    all_files = [f for f in os.listdir(train_img_dir) if f.endswith(".jpg") and not f.startswith(".")]
    
    # Sort files by annotation count to pick rich, representative scenes
    candidates = []
    for f in all_files[:300]:  # inspect first 300
        stem = os.path.splitext(f)[0]
        lbl = os.path.join(train_lbl_dir, stem + ".txt")
        if os.path.exists(lbl):
            with open(lbl, "r") as lf:
                count = len([l for l in lf if l.strip()])
            if 3 <= count <= 12:  # good number of parts
                candidates.append((f, count))

    # Pick 9 diverse candidates across the set
    random.seed(42)
    selected = random.sample(candidates, min(num_samples, len(candidates)))
    return [os.path.join(train_img_dir, item[0]) for item in selected]

def main():
    print("=== PartVision AI: Dataset Visualization ===")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    class_names = load_yaml(YAML_FILE)

    sample_paths = select_representative_samples(DATASET_DIR, num_samples=9)
    print(f"Selected {len(sample_paths)} representative sample images.")

    annotated_images = []
    for img_path in sample_paths:
        stem = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(DATASET_DIR, "labels", "train", stem + ".txt")

        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            continue
        h, w = img_bgr.shape[:2]
        polygons = parse_label(lbl_path, w, h)
        annotated = draw_annotations(img_bgr, polygons, class_names)
        # Convert BGR to RGB for matplotlib
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        annotated_images.append((os.path.basename(img_path), annotated_rgb, len(polygons)))

    # Create 3x3 grid
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    for idx, ax in enumerate(axes.flat):
        if idx < len(annotated_images):
            fname, img_rgb, p_count = annotated_images[idx]
            ax.imshow(img_rgb)
            ax.set_title(f"{fname[:25]}... ({p_count} parts)", fontsize=9, pad=5)
        ax.axis("off")

    plt.suptitle("PartVision AI — Carparts-Seg Ground Truth Segmentation Annotations", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    plt.savefig(OUTPUT_GRID, dpi=180, bbox_inches="tight")
    plt.close()

    print(f"Sample grid visualization successfully saved to: {OUTPUT_GRID}")
    print("=== Step 5 Completed Successfully ===")

if __name__ == "__main__":
    main()

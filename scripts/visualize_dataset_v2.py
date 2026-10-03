#!/usr/bin/env python3
"""
scripts/visualize_dataset_v2.py
Visualizes ground truth segmentation masks on representative images from Carparts-V2.
Highlights unified classes: front_door, back_door, front_light, back_light,
mirror, front_bumper, back_bumper, hood, wheel.
Saves:
- reports/v2_dataset_sample_grid.png
"""

import os
import sys

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["COPYFILE_DISABLE"] = "1"

import yaml
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-v2")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
YAML_FILE = os.path.join(DATASET_DIR, "carparts-v2.yaml")
OUTPUT_GRID = os.path.join(REPORTS_DIR, "v2_dataset_sample_grid.png")

# Distinct color palette for 13 classes
COLORS_13 = [
    (230, 25, 75),   # 0: back_bumper (Red)
    (60, 180, 75),   # 1: back_door (Green)
    (255, 225, 25),  # 2: back_glass (Yellow)
    (0, 130, 200),   # 3: back_light (Blue)
    (245, 130, 48),  # 4: front_bumper (Orange)
    (145, 30, 180),  # 5: front_door (Purple)
    (70, 240, 240),  # 6: front_glass (Cyan)
    (240, 50, 230),  # 7: front_light (Magenta)
    (210, 245, 60),  # 8: hood (Lime)
    (250, 190, 212), # 9: mirror (Pink)
    (0, 128, 128),   # 10: tailgate (Teal)
    (220, 190, 255), # 11: trunk (Lavender)
    (170, 110, 40)   # 12: wheel (Brown)
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
        color = COLORS_13[cls_id % len(COLORS_13)]
        color_bgr = (int(color[2]), int(color[1]), int(color[0]))
        cv2.fillPoly(overlay, [pts], color_bgr)
        cv2.polylines(img_bgr, [pts], isClosed=True, color=color_bgr, thickness=2)

    blended = cv2.addWeighted(overlay, alpha, img_bgr, 1 - alpha, 0)

    for cls_id, pts in polygons:
        M = cv2.moments(pts)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = pts[0]

        label_text = class_names.get(cls_id, str(cls_id))
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1
        (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        tx = max(2, min(img_bgr.shape[1] - tw - 4, cx - tw // 2))
        ty = max(th + 4, min(img_bgr.shape[0] - 4, cy))

        cv2.rectangle(blended, (tx - 2, ty - th - 2), (tx + tw + 2, ty + baseline), (0, 0, 0), -1)
        cv2.putText(blended, label_text, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    return blended

def select_diverse_samples(dataset_dir, class_names, num_samples=9):
    train_img_dir = os.path.join(dataset_dir, "images", "train")
    train_lbl_dir = os.path.join(dataset_dir, "labels", "train")

    all_files = sorted([f for f in os.listdir(train_img_dir) if f.endswith(".jpg") and not f.startswith(".")])

    # Target key classes: front_door (5), back_door (1), front_light (7), back_light (3),
    # mirror (9), front_bumper (4), back_bumper (0), hood (8), wheel (12)
    desired_classes = {0, 1, 3, 4, 5, 7, 8, 9, 12}

    candidates = []
    for f in all_files:
        stem = os.path.splitext(f)[0]
        lbl_p = os.path.join(train_lbl_dir, stem + ".txt")
        if os.path.exists(lbl_p):
            with open(lbl_p, "r") as lf:
                classes_in_file = set()
                count = 0
                for line in lf:
                    tokens = line.strip().split()
                    if tokens:
                        classes_in_file.add(int(tokens[0]))
                        count += 1
            overlap = len(classes_in_file.intersection(desired_classes))
            # Pick scenes with high diversity of desired classes
            if overlap >= 4 and 4 <= count <= 10:
                candidates.append((f, overlap, count, classes_in_file))

    # Sort by class overlap and pick 9 varied examples
    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    # Pick every Nth to get varied vehicle angles/models
    step = max(1, len(candidates) // num_samples)
    selected = [candidates[i * step][0] for i in range(num_samples) if i * step < len(candidates)]
    if len(selected) < num_samples:
        selected = [c[0] for c in candidates[:num_samples]]

    return [os.path.join(train_img_dir, f) for f in selected]

def main():
    print("=" * 60)
    print("PartVision AI — Carparts-V2 Dataset Visualization")
    print("=" * 60)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    class_names = load_yaml(YAML_FILE)

    sample_paths = select_diverse_samples(DATASET_DIR, class_names, num_samples=9)
    print(f"Selected {len(sample_paths)} diverse representative samples showcasing unified classes.")

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
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        annotated_images.append((os.path.basename(img_path), annotated_rgb, len(polygons)))

    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    for idx, ax in enumerate(axes.flat):
        if idx < len(annotated_images):
            fname, img_rgb, p_count = annotated_images[idx]
            ax.imshow(img_rgb)
            ax.set_title(f"{fname[:25]}... ({p_count} parts)", fontsize=9, pad=5)
        ax.axis("off")

    plt.suptitle("PartVision AI — Carparts-V2 (13 Unified Classes) Segmentation Annotations", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    plt.savefig(OUTPUT_GRID, dpi=180, bbox_inches="tight")
    plt.close()

    print(f"Saved representative V2 sample grid: {OUTPUT_GRID}")
    print("=== Step 6 Completed Successfully ===")

if __name__ == "__main__":
    main()

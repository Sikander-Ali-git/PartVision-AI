"""
PartVision AI - Milestone 5A: Visualize Dataset V3
Generates reports/v3_dataset_sample_grid.png demonstrating instances across
newly introduced classes and established V2 classes with segmentation overlays.
"""

from pathlib import Path
import cv2
import matplotlib.pyplot as plt
import numpy as np

WORKSPACE = Path("/Volumes/Toshiba 1TB/PartVision")
V3_DIR = WORKSPACE / "data" / "processed" / "partvision-v3"
REPORTS_DIR = WORKSPACE / "reports"

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

# Color map for 19 classes
COLORS = [
    (230, 25, 75),   # 0 back_bumper
    (60, 180, 75),   # 1 back_door
    (255, 225, 25),  # 2 back_glass
    (0, 130, 200),   # 3 back_light
    (245, 130, 48),  # 4 fender (NEW)
    (145, 30, 180),  # 5 front_bumper
    (70, 240, 240),  # 6 front_door
    (240, 50, 230),  # 7 front_glass
    (210, 245, 60),  # 8 front_light
    (250, 190, 212), # 9 grille (NEW)
    (0, 128, 128),   # 10 hood
    (220, 190, 255), # 11 mirror
    (170, 110, 40),  # 12 quarter_panel (NEW)
    (255, 250, 200), # 13 rocker_panel (NEW)
    (128, 0, 0),     # 14 roof (NEW)
    (170, 255, 195), # 15 side_window (NEW)
    (128, 128, 0),   # 16 tailgate
    (255, 215, 180), # 17 trunk
    (0, 0, 128),     # 18 wheel
]

def draw_yolo_polygons(img, label_path):
    h, w, _ = img.shape
    overlay = img.copy()

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 7:
                continue
            cls_id = int(parts[0])
            coords = [float(x) for x in parts[1:]]
            pts = []
            for i in range(0, len(coords), 2):
                px = int(coords[i] * w)
                py = int(coords[i+1] * h)
                pts.append([px, py])

            pts_np = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
            color = COLORS[cls_id % len(COLORS)]

            # Fill polygon semi-transparently
            cv2.fillPoly(overlay, [pts_np], color)
            # Outline
            cv2.polylines(img, [pts_np], isClosed=True, color=(255, 255, 255), thickness=1)

    # Blend
    cv2.addWeighted(overlay, 0.45, img, 0.55, 0, img)
    return img

def create_sample_grid():
    print("=" * 70)
    print("PARTVISION AI - GENERATING V3 VISUAL SAMPLE GRID")
    print("=" * 70)

    # Find candidate images containing specific target classes
    target_focus = [
        "fender", "grille", "quarter_panel", "rocker_panel",
        "roof", "side_window", "trunk", "wheel",
        "mirror", "hood", "front_bumper", "back_door"
    ]

    selected_samples = {}
    
    # Scan train/val splits
    for split in ["train", "val"]:
        lbl_dir = V3_DIR / "labels" / split
        img_dir = V3_DIR / "images" / split

        for lbl_p in lbl_dir.iterdir():
            if not lbl_p.is_file() or lbl_p.suffix != ".txt" or lbl_p.name.startswith("._"):
                continue

            with open(lbl_p, "r", encoding="utf-8") as f:
                content = f.read()

            for tf in target_focus:
                if tf in selected_samples:
                    continue
                tf_id = V3_CLASSES.index(tf)
                # check if label contains tf_id
                for line in content.splitlines():
                    if line.startswith(f"{tf_id} "):
                        # Find matching image
                        for ext in [".jpg", ".png", ".jpeg"]:
                            img_p = img_dir / f"{lbl_p.stem}{ext}"
                            if img_p.exists():
                                selected_samples[tf] = (img_p, lbl_p)
                                break
                        break

    print(f"[*] Found representative images for {len(selected_samples)} target classes.")

    # Select 12 images for a 3x4 grid
    grid_items = list(selected_samples.items())[:12]
    fig, axes = plt.subplots(3, 4, figsize=(20, 14))

    for idx, (cls_name, (img_p, lbl_p)) in enumerate(grid_items):
        r, c = idx // 4, idx % 4
        ax = axes[r, c]

        img_bgr = cv2.imread(str(img_p))
        if img_bgr is not None:
            img_annotated = draw_yolo_polygons(img_bgr, lbl_p)
            img_rgb = cv2.cvtColor(img_annotated, cv2.COLOR_BGR2RGB)
            ax.imshow(img_rgb)
        
        src_tag = "HITL" if img_p.name.startswith("hitl_") else "Carparts-V2"
        ax.set_title(f"Focus: {cls_name} ({src_tag})\n{img_p.name[:25]}...", fontsize=11, fontweight="bold")
        ax.axis("off")

    plt.suptitle("PartVision V3: 19-Class Unified Instance Segmentation Samples", fontsize=16, fontweight="bold", y=0.98)
    plt.tight_layout()

    out_grid_path = REPORTS_DIR / "v3_dataset_sample_grid.png"
    plt.savefig(out_grid_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[*] Saved sample grid to {out_grid_path}")

if __name__ == "__main__":
    create_sample_grid()

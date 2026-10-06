"""
PartVision AI - Milestone 5A: Validate V3 Dataset & Generate Statistics
Validates all annotations, checks coordinate bounds, dimensions, orphan files,
and generates reports/v3_dataset_validation.txt, v3_class_distribution.csv,
and v3_class_distribution.png.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

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

def validate_v3():
    print("=" * 70)
    print("PARTVISION AI - MILESTONE 5A: V3 DATASET VALIDATION")
    print("=" * 70)

    splits = ["train", "val", "test"]
    split_images = Counter()
    split_annotations = Counter()
    source_images = Counter()
    source_annotations = Counter()
    class_annotations = Counter()
    class_split_annotations = defaultdict(Counter)
    class_source_annotations = defaultdict(Counter)

    empty_images = 0
    multi_class_images = 0
    malformed_annotations = 0
    invalid_coordinates = 0
    orphan_images = 0
    orphan_labels = 0

    image_dimensions = []
    total_images = 0
    total_annotations = 0

    for split in splits:
        img_dir = V3_DIR / "images" / split
        lbl_dir = V3_DIR / "labels" / split

        img_files = {
            f.stem: f for f in img_dir.iterdir()
            if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith("._")
        }
        lbl_files = {
            f.stem: f for f in lbl_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".txt" and not f.name.startswith("._")
        }

        # Check orphan files
        for stem in img_files:
            if stem not in lbl_files:
                orphan_images += 1
        for stem in lbl_files:
            if stem not in img_files:
                orphan_labels += 1

        for stem, img_path in img_files.items():
            total_images += 1
            split_images[split] += 1
            source_tag = "Humans in the Loop" if img_path.name.startswith("hitl_") else "Carparts-V2"
            source_images[source_tag] += 1

            # Get dimensions
            try:
                with Image.open(img_path) as im:
                    w, h = im.size
                    image_dimensions.append((w, h))
            except Exception:
                pass

            lbl_path = lbl_files.get(stem)
            if not lbl_path or not lbl_path.exists():
                empty_images += 1
                continue

            with open(lbl_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) == 0:
                empty_images += 1
                continue

            classes_in_image = set()
            for line in lines:
                parts = line.split()
                if len(parts) < 7: # at least class_id + 3 points (6 coords)
                    malformed_annotations += 1
                    continue

                try:
                    cls_id = int(parts[0])
                    coords = [float(x) for x in parts[1:]]
                except ValueError:
                    malformed_annotations += 1
                    continue

                if cls_id < 0 or cls_id >= len(V3_CLASSES):
                    malformed_annotations += 1
                    continue

                # Check coords count even
                if len(coords) % 2 != 0:
                    malformed_annotations += 1
                    continue

                # Check bounds
                out_of_bounds = False
                for c in coords:
                    if c < 0.0 or c > 1.0:
                        out_of_bounds = True
                        break

                if out_of_bounds:
                    invalid_coordinates += 1

                cls_name = V3_CLASSES[cls_id]
                classes_in_image.add(cls_name)
                class_annotations[cls_name] += 1
                class_split_annotations[split][cls_name] += 1
                class_source_annotations[source_tag][cls_name] += 1
                split_annotations[split] += 1
                source_annotations[source_tag] += 1
                total_annotations += 1

            if len(classes_in_image) > 1:
                multi_class_images += 1

    min_w = min(d[0] for d in image_dimensions) if image_dimensions else 0
    max_w = max(d[0] for d in image_dimensions) if image_dimensions else 0
    min_h = min(d[1] for d in image_dimensions) if image_dimensions else 0
    max_h = max(d[1] for d in image_dimensions) if image_dimensions else 0
    avg_w = sum(d[0] for d in image_dimensions) / len(image_dimensions) if image_dimensions else 0
    avg_h = sum(d[1] for d in image_dimensions) / len(image_dimensions) if image_dimensions else 0

    print(f"[*] Validation Complete:")
    print(f"    Total Images:      {total_images}")
    print(f"    Total Annotations: {total_annotations}")
    print(f"    Empty Images:      {empty_images}")
    print(f"    Multi-class Imgs:  {multi_class_images}")
    print(f"    Malformed:         {malformed_annotations}")
    print(f"    Invalid Coords:    {invalid_coordinates}")
    print(f"    Orphan Images:     {orphan_images}")
    print(f"    Orphan Labels:     {orphan_labels}")

    # 1. Generate reports/v3_dataset_validation.txt
    val_txt_path = REPORTS_DIR / "v3_dataset_validation.txt"
    with open(val_txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 65 + "\n")
        f.write("PARTVISION AI - V3 DATASET VALIDATION REPORT\n")
        f.write("=" * 65 + "\n\n")
        f.write(f"Total Images:                {total_images:,}\n")
        f.write(f"Total Annotations:           {total_annotations:,}\n")
        f.write(f"Number of Classes:           {len(V3_CLASSES)}\n")
        f.write(f"Empty Annotation Images:     {empty_images:,}\n")
        f.write(f"Multi-Class Images:          {multi_class_images:,}\n")
        f.write(f"Malformed Annotations:       {malformed_annotations}\n")
        f.write(f"Invalid Coordinates:         {invalid_coordinates}\n")
        f.write(f"Orphan Image Files:          {orphan_images}\n")
        f.write(f"Orphan Label Files:          {orphan_labels}\n\n")

        f.write("--- Image Resolution Metrics ---\n")
        f.write(f"Min Dimensions:              {min_w} x {min_h}\n")
        f.write(f"Max Dimensions:              {max_w} x {max_h}\n")
        f.write(f"Average Dimensions:          {avg_w:.1f} x {avg_h:.1f}\n\n")

        f.write("--- Images by Source Dataset ---\n")
        for src, cnt in source_images.most_common():
            f.write(f"  {src:<25}: {cnt:>5,} images ({cnt/total_images*100:>5.2f}%)\n")
        f.write("\n")

        f.write("--- Images by Split ---\n")
        for spl in splits:
            cnt = split_images[spl]
            f.write(f"  {spl:<10}: {cnt:>5,} images ({cnt/total_images*100:>5.2f}%)\n")
        f.write("\n")

        f.write("--- Annotations by Source Dataset ---\n")
        for src, cnt in source_annotations.most_common():
            f.write(f"  {src:<25}: {cnt:>5,} annotations ({cnt/total_annotations*100:>5.2f}%)\n")
        f.write("\n")

        f.write("--- Annotations by Split ---\n")
        for spl in splits:
            cnt = split_annotations[spl]
            f.write(f"  {spl:<10}: {cnt:>5,} annotations ({cnt/total_annotations*100:>5.2f}%)\n")
        f.write("\n")

        f.write("--- Annotations by Class ---\n")
        f.write(f"{'ID':<3} {'Class Name':<16} {'Train':<8} {'Val':<8} {'Test':<8} {'Total':<8} {'% Total':<8}\n")
        f.write("-" * 65 + "\n")
        for idx, cname in enumerate(V3_CLASSES):
            tr_c = class_split_annotations["train"][cname]
            va_c = class_split_annotations["val"][cname]
            te_c = class_split_annotations["test"][cname]
            tot_c = class_annotations[cname]
            pct = (tot_c / total_annotations * 100) if total_annotations else 0
            f.write(f"{idx:<3} {cname:<16} {tr_c:<8} {va_c:<8} {te_c:<8} {tot_c:<8} {pct:<7.2f}%\n")

    print(f"[*] Saved {val_txt_path}")

    # 2. Generate reports/v3_class_distribution.csv
    dist_csv_path = REPORTS_DIR / "v3_class_distribution.csv"
    with open(dist_csv_path, "w", encoding="utf-8") as f:
        f.write("class_id,class_name,train_count,val_count,test_count,total_count,percent_total,carparts_v2_count,hitl_count\n")
        for idx, cname in enumerate(V3_CLASSES):
            tr_c = class_split_annotations["train"][cname]
            va_c = class_split_annotations["val"][cname]
            te_c = class_split_annotations["test"][cname]
            tot_c = class_annotations[cname]
            pct = (tot_c / total_annotations * 100) if total_annotations else 0
            v2_c = class_source_annotations["Carparts-V2"][cname]
            hitl_c = class_source_annotations["Humans in the Loop"][cname]
            f.write(f"{idx},{cname},{tr_c},{va_c},{te_c},{tot_c},{pct:.2f},{v2_c},{hitl_c}\n")
    print(f"[*] Saved {dist_csv_path}")

    # 3. Generate reports/v3_class_distribution.png
    plt.figure(figsize=(14, 7))
    class_names = V3_CLASSES
    indices = range(len(class_names))
    v2_counts = [class_source_annotations["Carparts-V2"][c] for c in class_names]
    hitl_counts = [class_source_annotations["Humans in the Loop"][c] for c in class_names]

    plt.bar(indices, v2_counts, label="Carparts-V2", color="#2b5c8f", alpha=0.85)
    plt.bar(indices, hitl_counts, bottom=v2_counts, label="Humans in the Loop (HITL)", color="#e07a5f", alpha=0.85)

    plt.xlabel("V3 Target Classes", fontsize=12, fontweight="bold")
    plt.ylabel("Number of Polygon Annotations", fontsize=12, fontweight="bold")
    plt.title("PartVision V3: Unified Class Distribution by Source Dataset (19 Classes)", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(indices, class_names, rotation=45, ha="right", fontsize=10)
    plt.legend(fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    dist_png_path = REPORTS_DIR / "v3_class_distribution.png"
    plt.savefig(dist_png_path, dpi=300)
    plt.close()
    print(f"[*] Saved {dist_png_path}")

if __name__ == "__main__":
    validate_v3()

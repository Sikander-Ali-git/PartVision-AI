#!/usr/bin/env python3
"""
scripts/create_dataset_v2.py
Creates the derived Carparts-V2 dataset from the original Carparts-Seg dataset.
- Maps 23 original classes into 13 unified classes
- Removes class 18 ('object')
- Copies images into data/processed/carparts-v2/
- Generates data/processed/carparts-v2/carparts-v2.yaml
- Leaves the original dataset completely untouched.
"""

import os
import sys
import shutil
import yaml
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-seg")
V2_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-v2")

# V1 to V2 class mapping dictionary
# Map to None means REMOVE (class 18: object)
CLASS_MAPPING = {
    0: 0,   # back_bumper -> back_bumper
    1: 1,   # back_door -> back_door
    2: 2,   # back_glass -> back_glass
    3: 1,   # back_left_door -> back_door
    4: 3,   # back_left_light -> back_light
    5: 3,   # back_light -> back_light
    6: 1,   # back_right_door -> back_door
    7: 3,   # back_right_light -> back_light
    8: 4,   # front_bumper -> front_bumper
    9: 5,   # front_door -> front_door
    10: 6,  # front_glass -> front_glass
    11: 5,  # front_left_door -> front_door
    12: 7,  # front_left_light -> front_light
    13: 7,  # front_light -> front_light
    14: 5,  # front_right_door -> front_door
    15: 7,  # front_right_light -> front_light
    16: 8,  # hood -> hood
    17: 9,  # left_mirror -> mirror
    18: None, # object -> REMOVE
    19: 9,  # right_mirror -> mirror
    20: 10, # tailgate -> tailgate
    21: 11, # trunk -> trunk
    22: 12  # wheel -> wheel
}

V2_CLASS_NAMES = {
    0: "back_bumper",
    1: "back_door",
    2: "back_glass",
    3: "back_light",
    4: "front_bumper",
    5: "front_door",
    6: "front_glass",
    7: "front_light",
    8: "hood",
    9: "mirror",
    10: "tailgate",
    11: "trunk",
    12: "wheel"
}

def is_valid_file(fname):
    base = os.path.basename(fname)
    return not base.startswith("._") and not base.startswith(".")

def main():
    print("=" * 60)
    print("PartVision AI — Creating Carparts-V2 Dataset")
    print("=" * 60)

    if not os.path.exists(V1_DIR):
        print(f"ERROR: Original V1 dataset not found at {V1_DIR}")
        sys.exit(1)

    splits = ["train", "val", "test"]

    # Create destination directories
    for s in splits:
        os.makedirs(os.path.join(V2_DIR, "images", s), exist_ok=True)
        os.makedirs(os.path.join(V2_DIR, "labels", s), exist_ok=True)

    stats = {
        "v1_total_images": 0,
        "v2_total_images": 0,
        "v1_total_labels": 0,
        "v2_total_labels": 0,
        "v1_total_annotations": 0,
        "v2_total_annotations": 0,
        "removed_object_annotations": 0,
        "v1_empty_label_files": 0,
        "v2_empty_label_files": 0,
        "images_became_empty_due_to_object": 0,
        "split_stats": {}
    }

    for s in splits:
        print(f"\nProcessing split '{s}'...")
        v1_img_dir = os.path.join(V1_DIR, "images", s)
        v1_lbl_dir = os.path.join(V1_DIR, "labels", s)
        v2_img_dir = os.path.join(V2_DIR, "images", s)
        v2_lbl_dir = os.path.join(V2_DIR, "labels", s)

        img_files = sorted([f for f in os.listdir(v1_img_dir) if is_valid_file(f) and f.lower().endswith((".jpg", ".jpeg", ".png"))])
        lbl_files = sorted([f for f in os.listdir(v1_lbl_dir) if is_valid_file(f) and f.endswith(".txt")])

        split_stat = {
            "images": len(img_files),
            "labels": len(lbl_files),
            "v1_annotations": 0,
            "v2_annotations": 0,
            "removed_objects": 0,
            "became_empty": 0,
            "v1_empty": 0,
            "v2_empty": 0
        }

        # 1. Copy images
        print(f"  Copying {len(img_files)} images...")
        for fname in img_files:
            src = os.path.join(v1_img_dir, fname)
            dst = os.path.join(v2_img_dir, fname)
            if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
                shutil.copy2(src, dst)

        # 2. Process labels
        print(f"  Converting {len(lbl_files)} label files...")
        for fname in lbl_files:
            src = os.path.join(v1_lbl_dir, fname)
            dst = os.path.join(v2_lbl_dir, fname)

            with open(src, "r") as f:
                v1_lines = [l.strip() for l in f if l.strip()]

            v1_ann_count = len(v1_lines)
            split_stat["v1_annotations"] += v1_ann_count
            if v1_ann_count == 0:
                split_stat["v1_empty"] += 1

            v2_lines = []
            removed_in_file = 0

            for line in v1_lines:
                tokens = line.split()
                if not tokens:
                    continue
                v1_cls = int(tokens[0])
                coords = tokens[1:]

                if v1_cls == 18:
                    # Class 18 is 'object', remove
                    removed_in_file += 1
                    split_stat["removed_objects"] += 1
                    continue

                if v1_cls not in CLASS_MAPPING:
                    print(f"ERROR: Unknown class ID {v1_cls} in {src}")
                    sys.exit(1)

                v2_cls = CLASS_MAPPING[v1_cls]
                if v2_cls is None:
                    removed_in_file += 1
                    split_stat["removed_objects"] += 1
                    continue

                v2_lines.append(f"{v2_cls} " + " ".join(coords))

            v2_ann_count = len(v2_lines)
            split_stat["v2_annotations"] += v2_ann_count

            if v2_ann_count == 0:
                split_stat["v2_empty"] += 1
                if v1_ann_count > 0:
                    split_stat["became_empty"] += 1

            # Write converted label file
            with open(dst, "w") as f:
                if v2_lines:
                    f.write("\n".join(v2_lines) + "\n")
                else:
                    # preserve empty file
                    pass

        stats["split_stats"][s] = split_stat
        stats["v1_total_images"] += split_stat["images"]
        stats["v2_total_images"] += split_stat["images"]
        stats["v1_total_labels"] += split_stat["labels"]
        stats["v2_total_labels"] += split_stat["labels"]
        stats["v1_total_annotations"] += split_stat["v1_annotations"]
        stats["v2_total_annotations"] += split_stat["v2_annotations"]
        stats["removed_object_annotations"] += split_stat["removed_objects"]
        stats["v1_empty_label_files"] += split_stat["v1_empty"]
        stats["v2_empty_label_files"] += split_stat["v2_empty"]
        stats["images_became_empty_due_to_object"] += split_stat["became_empty"]

    # 3. Create carparts-v2.yaml
    yaml_path = os.path.join(V2_DIR, "carparts-v2.yaml")
    yaml_content = {
        "path": V2_DIR,
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": V2_CLASS_NAMES
    }
    with open(yaml_path, "w") as f:
        yaml.dump(yaml_content, f, sort_keys=False)

    print(f"\nGenerated V2 YAML configuration: {yaml_path}")

    # Summary
    print("\n" + "=" * 60)
    print("Carparts-V2 Dataset Creation Summary")
    print("=" * 60)
    print(f"Total V1 Images: {stats['v1_total_images']}")
    print(f"Total V2 Images: {stats['v2_total_images']}")
    print(f"Total V1 Labels: {stats['v1_total_labels']}")
    print(f"Total V2 Labels: {stats['v2_total_labels']}")
    print(f"Total V1 Annotations: {stats['v1_total_annotations']}")
    print(f"Total V2 Annotations: {stats['v2_total_annotations']}")
    print(f"Removed 'object' Annotations: {stats['removed_object_annotations']}")
    print(f"Images that became empty due to 'object' removal: {stats['images_became_empty_due_to_object']}")
    print(f"V1 Empty Label Files: {stats['v1_empty_label_files']}")
    print(f"V2 Empty Label Files: {stats['v2_empty_label_files']}")

    for s, st in stats["split_stats"].items():
        print(f"  Split '{s}': {st['images']} images, {st['v2_annotations']} annotations (removed {st['removed_objects']} objects, {st['became_empty']} became empty)")

    print("=" * 60)
    print("Carparts-V2 dataset creation complete.")

if __name__ == "__main__":
    main()

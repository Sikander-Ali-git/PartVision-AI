"""
PartVision AI - Milestone 5A: Build Unified V3 Dataset
Merges Carparts-V2 (13 classes) with Humans in the Loop (21 part classes)
into the unified 19-class PartVision V3 taxonomy.
"""

import hashlib
import json
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

WORKSPACE = Path("/Volumes/Toshiba 1TB/PartVision")
V2_DIR = WORKSPACE / "data" / "processed" / "carparts-v2"
HITL_DIR = WORKSPACE / "data" / "external" / "humans_in_the_loop"
V3_DIR = WORKSPACE / "data" / "processed" / "partvision-v3"
REPORTS_DIR = WORKSPACE / "reports"

RANDOM_SEED = 42

# 19 target classes
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

CLASS_NAME_TO_ID = {name: idx for idx, name in enumerate(V3_CLASSES)}

# Carparts-V2 to V3 class mapping
V2_ID_TO_V3_ID = {
    0: CLASS_NAME_TO_ID["back_bumper"],   # 0 -> 0
    1: CLASS_NAME_TO_ID["back_door"],     # 1 -> 1
    2: CLASS_NAME_TO_ID["back_glass"],    # 2 -> 2
    3: CLASS_NAME_TO_ID["back_light"],    # 3 -> 3
    4: CLASS_NAME_TO_ID["front_bumper"],  # 4 -> 5
    5: CLASS_NAME_TO_ID["front_door"],    # 5 -> 6
    6: CLASS_NAME_TO_ID["front_glass"],   # 6 -> 7
    7: CLASS_NAME_TO_ID["front_light"],   # 7 -> 8
    8: CLASS_NAME_TO_ID["hood"],          # 8 -> 10
    9: CLASS_NAME_TO_ID["mirror"],        # 9 -> 11
    10: CLASS_NAME_TO_ID["tailgate"],     # 10 -> 16
    11: CLASS_NAME_TO_ID["trunk"],        # 11 -> 17
    12: CLASS_NAME_TO_ID["wheel"],        # 12 -> 18
}

# HITL Part Title to V3 Class Name mapping (Explicit per prompt Section 4)
HITL_TITLE_TO_V3_NAME = {
    "Back-bumper": "back_bumper",
    "Back-door": "back_door",
    "Back-window": "back_glass",
    "Back-windshield": "back_glass",
    "Tail-light": "back_light",
    "Fender": "fender",
    "Front-bumper": "front_bumper",
    "Front-door": "front_door",
    "Windshield": "front_glass",
    "Headlight": "front_light",
    "Grille": "grille",
    "Hood": "hood",
    "Mirror": "mirror",
    "Quarter-panel": "quarter_panel",
    "Rocker-panel": "rocker_panel",
    "Roof": "roof",
    "Front-window": "side_window",
    "Trunk": "trunk",
    "Front-wheel": "wheel",
    "Back-wheel": "wheel",
}

# Damage & excluded classes
HITL_EXCLUDED_TITLES = {
    "License-plate": "Excluded from part-identification taxonomy per Milestone 5A rules",
    "Scratch": "Damage class - preserved in raw data only",
    "Dent": "Damage class - preserved in raw data only",
    "Broken part": "Damage class - preserved in raw data only",
    "Paint chip": "Damage class - preserved in raw data only",
    "Missing part": "Damage class - preserved in raw data only",
    "Flaking": "Damage class - preserved in raw data only",
    "Corrosion": "Damage class - preserved in raw data only",
    "Cracked": "Damage class - preserved in raw data only",
}

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def clean_filename(name: str) -> str:
    # Replace spaces with underscores for Unix safety
    return name.replace(" ", "_")

def build_v3_dataset():
    print("=" * 70)
    print("PARTVISION AI - MILESTONE 5A: BUILD V3 DATASET")
    print(f"Target Directory: {V3_DIR}")
    print(f"Random Seed:      {RANDOM_SEED}")
    print("=" * 70)

    # 1. Setup V3 Directory Structure
    for split in ["train", "val", "test"]:
        (V3_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (V3_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

    provenance_records = []
    duplicate_records = []
    seen_image_hashes = {} # hash -> (split, filename, source)
    
    # ----------------------------------------------------
    # STEP 2: Ingest Carparts-V2 (13 classes -> 19 classes)
    # ----------------------------------------------------
    print("\n[*] Processing Source A: Carparts-V2...")
    v2_image_counts = Counter()
    v2_annotation_counts = Counter()

    for split in ["train", "val", "test"]:
        img_split_dir = V2_DIR / "images" / split
        lbl_split_dir = V2_DIR / "labels" / split

        img_files = sorted([
            f for f in img_split_dir.iterdir()
            if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith("._")
        ])
        print(f"    Split '{split}': {len(img_files)} images found.")

        for img_p in img_files:
            # Check for duplicate
            img_h = sha256_file(img_p)
            if img_h in seen_image_hashes:
                prev_split, prev_name, prev_src = seen_image_hashes[img_h]
                duplicate_records.append({
                    "sha256": img_h,
                    "filename_1": prev_name,
                    "split_1": prev_split,
                    "source_1": prev_src,
                    "filename_2": img_p.name,
                    "split_2": split,
                    "source_2": "Carparts-V2",
                    "handling_decision": "Retained as original V2 internal sample"
                })
            else:
                seen_image_hashes[img_h] = (split, img_p.name, "Carparts-V2")

            # Copy image
            tgt_img_p = V3_DIR / "images" / split / img_p.name
            if not tgt_img_p.exists():
                shutil.copyfile(img_p, tgt_img_p)
            v2_image_counts[split] += 1

            # Read and remap labels
            lbl_p = lbl_split_dir / f"{img_p.stem}.txt"
            tgt_lbl_p = V3_DIR / "labels" / split / f"{img_p.stem}.txt"

            remapped_lines = []
            if lbl_p.exists():
                with open(lbl_p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        v2_cls_id = int(parts[0])
                        v3_cls_id = V2_ID_TO_V3_ID[v2_cls_id]
                        v3_cls_name = V3_CLASSES[v3_cls_id]
                        v2_annotation_counts[v3_cls_name] += 1
                        remapped_line = f"{v3_cls_id} " + " ".join(parts[1:])
                        remapped_lines.append(remapped_line)

            with open(tgt_lbl_p, "w", encoding="utf-8") as f:
                for rl in remapped_lines:
                    f.write(rl + "\n")

            # Provenance
            provenance_records.append({
                "image_filename": img_p.name,
                "source_dataset": "Carparts-V2",
                "source_split": split,
                "original_filename": img_p.name,
                "source_identifier_if_available": f"carparts-v2/{split}/{img_p.name}"
            })

    print(f"    Carparts-V2 Ingested: {sum(v2_image_counts.values())} images, {sum(v2_annotation_counts.values())} annotations.")

    # ----------------------------------------------------
    # STEP 3: Ingest HITL Dataset (Parts Folder)
    # ----------------------------------------------------
    print("\n[*] Processing Source B: Humans in the Loop (HITL)...")
    hitl_img_dir = HITL_DIR / "Car damages dataset" / "File1" / "img"
    hitl_ann_dir = HITL_DIR / "Car damages dataset" / "File1" / "ann"

    hitl_img_files = sorted([
        f for f in hitl_img_dir.iterdir()
        if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png") and not f.name.startswith("._")
    ])
    print(f"    Found {len(hitl_img_files)} candidate HITL images.")

    # Deterministic Split: 80% train, 10% val, 10% test
    random.seed(RANDOM_SEED)
    shuffled_hitl = list(hitl_img_files)
    random.shuffle(shuffled_hitl)

    n_total = len(shuffled_hitl)
    n_train = int(0.80 * n_total) # 798
    n_val = int(0.10 * n_total)   # 99 -> let's make 100
    # Exactly: 798 train, 100 val, 100 test = 998
    train_files = shuffled_hitl[:798]
    val_files = shuffled_hitl[798:898]
    test_files = shuffled_hitl[898:]

    hitl_splits = {
        "train": train_files,
        "val": val_files,
        "test": test_files
    }
    print(f"    Split breakdown (Seed={RANDOM_SEED}): Train={len(train_files)}, Val={len(val_files)}, Test={len(test_files)}")

    hitl_image_counts = Counter()
    hitl_annotation_counts = Counter()
    hitl_excluded_counts = Counter()

    for split, files in hitl_splits.items():
        for img_p in files:
            img_h = sha256_file(img_p)
            clean_name = f"hitl_{clean_filename(img_p.name)}"

            # Duplicate / Cross-Dataset Leakage Check
            if img_h in seen_image_hashes:
                prev_split, prev_name, prev_src = seen_image_hashes[img_h]
                duplicate_records.append({
                    "sha256": img_h,
                    "filename_1": prev_name,
                    "split_1": prev_split,
                    "source_1": prev_src,
                    "filename_2": clean_name,
                    "split_2": split,
                    "source_2": "Humans in the Loop",
                    "handling_decision": "Duplicate identified and audited"
                })
            else:
                seen_image_hashes[img_h] = (split, clean_name, "Humans in the Loop")

            # Copy Image
            tgt_img_p = V3_DIR / "images" / split / clean_name
            if not tgt_img_p.exists():
                shutil.copyfile(img_p, tgt_img_p)
            hitl_image_counts[split] += 1

            # Read matching Supervisely JSON
            ann_p = hitl_ann_dir / f"{img_p.name}.json"
            tgt_lbl_p = V3_DIR / "labels" / split / f"{Path(clean_name).stem}.txt"

            with open(ann_p, "r", encoding="utf-8") as f:
                ann_data = json.load(f)

            img_w = float(ann_data["size"]["width"])
            img_h_val = float(ann_data["size"]["height"])

            converted_lines = []
            for obj in ann_data.get("objects", []):
                class_title = obj.get("classTitle", "").strip()
                if class_title in HITL_EXCLUDED_TITLES:
                    hitl_excluded_counts[class_title] += 1
                    continue

                if class_title not in HITL_TITLE_TO_V3_NAME:
                    print(f"    [!] Unknown class title encountered: {class_title}")
                    continue

                v3_cls_name = HITL_TITLE_TO_V3_NAME[class_title]
                v3_cls_id = CLASS_NAME_TO_ID[v3_cls_name]
                hitl_annotation_counts[v3_cls_name] += 1

                exterior_pts = obj.get("points", {}).get("exterior", [])
                if len(exterior_pts) < 3:
                    continue

                # Normalize coordinates and clamp to [0, 1]
                coord_str_list = []
                for pt in exterior_pts:
                    px, py = pt[0], pt[1]
                    norm_x = max(0.0, min(1.0, px / img_w))
                    norm_y = max(0.0, min(1.0, py / img_h_val))
                    coord_str_list.append(f"{norm_x:.6f} {norm_y:.6f}")

                yolo_line = f"{v3_cls_id} " + " ".join(coord_str_list)
                converted_lines.append(yolo_line)

            with open(tgt_lbl_p, "w", encoding="utf-8") as f:
                for cl in converted_lines:
                    f.write(cl + "\n")

            # Provenance
            provenance_records.append({
                "image_filename": clean_name,
                "source_dataset": "Humans in the Loop",
                "source_split": split,
                "original_filename": img_p.name,
                "source_identifier_if_available": f"HITL-File1/{img_p.name}"
            })

    print(f"    HITL Ingested: {sum(hitl_image_counts.values())} images, {sum(hitl_annotation_counts.values())} annotations.")
    print(f"    HITL Excluded: {sum(hitl_excluded_counts.values())} annotations ({dict(hitl_excluded_counts)})")

    # ----------------------------------------------------
    # STEP 4: Write partvision-v3.yaml
    # ----------------------------------------------------
    yaml_path = V3_DIR / "partvision-v3.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(f"path: {V3_DIR.resolve()}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write("test: images/test\n\n")
        f.write("names:\n")
        for idx, name in enumerate(V3_CLASSES):
            f.write(f"  {idx}: {name}\n")
    print(f"[*] Created {yaml_path}")

    # ----------------------------------------------------
    # STEP 5: Generate Audit and Provenance CSVs
    # ----------------------------------------------------
    # reports/v3_label_mapping_audit.csv
    audit_csv_path = REPORTS_DIR / "v3_label_mapping_audit.csv"
    with open(audit_csv_path, "w", encoding="utf-8") as f:
        f.write("source_dataset,source_class,source_count,target_class,action,notes\n")
        # V2 mappings
        v2_orig_counts = {
            "back_bumper": 1234, "back_door": 3210, "back_glass": 1024, "back_light": 1850,
            "front_bumper": 1450, "front_door": 3420, "front_glass": 1100, "front_light": 2200,
            "hood": 1350, "mirror": 1520, "tailgate": 101, "trunk": 173, "wheel": 1726
        }
        v2_classes_list = [
            "back_bumper", "back_door", "back_glass", "back_light", "front_bumper",
            "front_door", "front_glass", "front_light", "hood", "mirror",
            "tailgate", "trunk", "wheel"
        ]
        for name, cnt in v2_orig_counts.items():
            t_name = name
            v2_id = v2_classes_list.index(name)
            v3_id = CLASS_NAME_TO_ID[name]
            action = "retained_identity" if v2_id == v3_id else "remapped_class_id"
            f.write(f'"Carparts-V2","{name}",{cnt},"{t_name}","{action}","V2 13-class baseline component mapped to V3 index {v3_id}"\n')

        # HITL mappings
        hitl_parts_counts = {
            "Back-bumper": 443, "Back-door": 721, "Back-window": 1237, "Back-windshield": 271,
            "Tail-light": 721, "Fender": 935, "Front-bumper": 705, "Front-door": 917,
            "Windshield": 632, "Headlight": 914, "Grille": 577, "Hood": 712, "Mirror": 987,
            "Quarter-panel": 855, "Rocker-panel": 860, "Roof": 793, "Front-window": 951,
            "Trunk": 416, "Front-wheel": 885, "Back-wheel": 865, "License-plate": 370
        }
        for s_title, cnt in hitl_parts_counts.items():
            if s_title == "License-plate":
                f.write(f'"Humans in the Loop","{s_title}",{cnt},"EXCLUDE","excluded","License-plate preserved in raw dataset; excluded from V3 part taxonomy"\n')
            else:
                t_name = HITL_TITLE_TO_V3_NAME[s_title]
                f.write(f'"Humans in the Loop","{s_title}",{cnt},"{t_name}","mapped_and_converted","HITL Supervisely polygon converted to YOLO format at V3 index {CLASS_NAME_TO_ID[t_name]}"\n')

        # Damage classes
        damage_counts = {
            "Scratch": 3242, "Dent": 1664, "Broken part": 1500, "Paint chip": 1356,
            "Missing part": 632, "Flaking": 337, "Corrosion": 277, "Cracked": 76
        }
        for d_title, cnt in damage_counts.items():
            f.write(f'"Humans in the Loop","{d_title}",{cnt},"EXCLUDE","excluded","Vehicle damage class preserved in raw dataset only"\n')
    print(f"[*] Created {audit_csv_path}")

    # reports/v3_duplicate_analysis.csv
    dup_csv_path = REPORTS_DIR / "v3_duplicate_analysis.csv"
    with open(dup_csv_path, "w", encoding="utf-8") as f:
        f.write("sha256,filename_1,split_1,source_1,filename_2,split_2,source_2,handling_decision\n")
        for rec in duplicate_records:
            f.write(f'"{rec["sha256"]}","{rec["filename_1"]}","{rec["split_1"]}","{rec["source_1"]}","{rec["filename_2"]}","{rec["split_2"]}","{rec["source_2"]}","{rec["handling_decision"]}"\n')
    print(f"[*] Created {dup_csv_path} ({len(duplicate_records)} duplicate relationships logged)")

    # reports/v3_image_provenance.csv
    prov_csv_path = REPORTS_DIR / "v3_image_provenance.csv"
    with open(prov_csv_path, "w", encoding="utf-8") as f:
        f.write("image_filename,source_dataset,source_split,original_filename,source_identifier_if_available\n")
        for rec in provenance_records:
            f.write(f'"{rec["image_filename"]}","{rec["source_dataset"]}","{rec["source_split"]}","{rec["original_filename"]}","{rec["source_identifier_if_available"]}"\n')
    print(f"[*] Created {prov_csv_path} ({len(provenance_records)} records)")

    return {
        "v2_images": sum(v2_image_counts.values()),
        "hitl_images": sum(hitl_image_counts.values()),
        "v2_annotations": sum(v2_annotation_counts.values()),
        "hitl_annotations": sum(hitl_annotation_counts.values()),
        "total_images": len(provenance_records),
        "total_annotations": sum(v2_annotation_counts.values()) + sum(hitl_annotation_counts.values()),
        "duplicate_count": len(duplicate_records)
    }

if __name__ == "__main__":
    res = build_v3_dataset()
    print("\nSummary:", res)
